import asyncio
from typing import Dict, Optional, Type, Union
from analytics.abstract_analytics import AbstractAnalytics
from core.event_dispatcher import register_handler
from core.events.ohlcv import OHLCVEvent
from core.events.portfolio import PortfolioPerformanceEvent
from core.events.position import EvaluateExitConditions, PositionClosed, OrderFilled, LongPositionOpened, ShortPositionOpened, PositionSide
from core.events.strategy import GoLong, GoShort
from core.position import Position
from datasource.abstract_datasource import AbstractDatasource
from .abstract_portfolio_manager import AbstractPortfolioManager


class PortfolioManager(AbstractPortfolioManager):
    def __init__(self, datasource: Type[AbstractDatasource], analytics: Type[AbstractAnalytics], risk_per_trade: float = 0.001):
        super().__init__()
        self.datasource = datasource
        self.analytics = analytics
        self.risk_per_trade = risk_per_trade
        self.closed_positions: Dict[str, Position] = {}
        self.active_positions: Dict[str, Position] = {}

        self.active_positions_lock = asyncio.Lock()
        self.closed_positions_lock = asyncio.Lock()

    @register_handler(OHLCVEvent)
    async def _on_market(self, event: OHLCVEvent):
        symbol = event.symbol
        timeframe = event.timeframe

        if symbol not in self.active_positions:
            return

        async with self.active_positions_lock:
            position = self.active_positions[symbol]

        if position is None or not len(position.orders):
            return

        await self.dispatcher.dispatch(
            EvaluateExitConditions(
                symbol=symbol,
                timeframe=timeframe,
                side=position.side,
                size=position.size,
                entry=position.entry_price,
                stop_loss=position.stop_loss_price,
                take_profit=position.take_profit_price,
                risk=self.risk_per_trade,
                ohlcv=event.ohlcv
            )
        )

    @register_handler(GoLong)
    async def _on_go_long(self, event: GoLong):
        await self.handle_position(PositionSide.LONG, event)

    @register_handler(GoShort)
    async def _on_go_short(self, event: GoShort):
        await self.handle_position(PositionSide.SHORT, event)

    @register_handler(OrderFilled)
    async def _on_order_filled(self, event: OrderFilled):
        symbol = event.symbol

        if symbol not in self.active_positions:
            return

        async with self.active_positions_lock:
            self.active_positions[symbol].add_order(event.order)

    @register_handler(PositionClosed)
    async def _on_closed_position(self, event: PositionClosed):
        symbol = event.symbol

        if symbol not in self.active_positions:
            return

        async with self.active_positions_lock:
            position = self.active_positions.pop(symbol, None)

            if position is None:
                return

            position.close_position(event.exit_price)

        async with self.closed_positions_lock:
            closed_key = f"{symbol}_{position.closed_timestamp}"

            if closed_key not in self.closed_positions:
                self.closed_positions[closed_key] = position

        strategy_id = f'{position.symbol}_{position.timeframe}{position.strategy}'

        closed_positions_list = list(filter(lambda x: f'{x.symbol}_{x.timeframe}{x.strategy}' == strategy_id, self.closed_positions.values()))

        if not len(closed_positions_list):
            return

        account_size = await self.datasource.account_size()
        performance = await asyncio.to_thread(self.analytics.calculate, account_size, closed_positions_list)

        await self.dispatcher.dispatch(PortfolioPerformanceEvent(strategy_id=strategy_id, performance=performance))

    async def handle_position(self, position_side, event: Union[GoLong, GoShort]):
        if event.symbol in self.active_positions:
            return

        account_size = await self.datasource.account_size()
        trading_fee, min_position_size, price_precision = await self.datasource.fee_and_precisions(event.symbol)

        async with self.active_positions_lock:
            position = self.create_position(position_side, account_size, trading_fee, min_position_size, price_precision, event)
            self.active_positions[event.symbol] = position

        await self.dispatcher.dispatch(self.create_open_position_event(position_side, event))

    def create_position(self, position_side, account_size, trading_fee, min_position_size, price_precision, event: Union[GoLong, GoShort]) -> Position:
        stop_loss_price = round(event.stop_loss, price_precision) if event.stop_loss else None
        take_profit_price = round(event.take_profit, price_precision) if event.take_profit else None
        size = self.calculate_position_size(account_size, event.entry, trading_fee, min_position_size, price_precision, stop_loss_price)

        return Position(symbol=event.symbol, timeframe=event.timeframe, strategy=event.strategy, size=size, entry=event.entry, side=position_side, stop_loss=stop_loss_price, take_profit=take_profit_price)

    def create_open_position_event(self, position_side: PositionSide, event: Union[GoLong, GoShort]) -> Union[LongPositionOpened, ShortPositionOpened]:
        position = self.active_positions[event.symbol]

        if position_side == PositionSide.LONG:
            return LongPositionOpened(
                symbol=event.symbol,
                timeframe=event.timeframe,
                size=position.size,
                entry=position.entry_price,
                stop_loss=position.stop_loss_price,
                take_profit=position.take_profit_price
            )
        else:
            return ShortPositionOpened(
                symbol=event.symbol,
                timeframe=event.timeframe,
                size=position.size,
                entry=position.entry_price,
                stop_loss=position.stop_loss_price,
                take_profit=position.take_profit_price
            )

    def calculate_position_size(
        self,
        account_size: float,
        entry_price: float,
        trading_fee: float,
        min_position_size: float,
        price_precision: int,
        stop_loss_price: Optional[float] = None
    ) -> float:
        risk_amount = self.risk_per_trade * account_size

        if stop_loss_price and entry_price:
            price_difference = abs(entry_price - stop_loss_price) * (1 + trading_fee)
        else:
            price_difference = 1

        if price_difference != 0:
            position_size = risk_amount / price_difference
        else:
            position_size = 1

        adjusted_position_size = max(position_size, min_position_size)
        rounded_position_size = round(adjusted_position_size, price_precision)

        return rounded_position_size