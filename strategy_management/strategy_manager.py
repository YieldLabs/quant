import asyncio
from typing import List, Type

from core.abstract_event_manager import AbstractEventManager
from core.event_decorators import register_handler
from core.events.ohlcv import OHLCV, NewMarketDataReceived
from strategy.abstract_strategy import AbstractStrategy

from .strategy_storage import StrategyStorage
from .strategy_processor import StrategyProcessor


class StrategyManager(AbstractEventManager):
    MIN_LOOKBACK = 50

    def __init__(self, strategies: List[Type[AbstractStrategy]]):
        super().__init__()
        self.strategies = [StrategyProcessor(strategy) for strategy in strategies]
        self.storage = StrategyStorage(
            window_size=max(getattr(strategy, "lookback", self.MIN_LOOKBACK) for strategy in strategies)
        )

    @register_handler(NewMarketDataReceived)
    async def _on_ohlcv(self, event: NewMarketDataReceived) -> None:
        await self.storage.append(event.symbol, event.timeframe, event.ohlcv)

        if not await self.storage.can_process(event.symbol, event.timeframe):
            return

        strategy_events = await self.storage.get_window(event.symbol, event.timeframe)

        await self.process_strategies(strategy_events, event)

    async def process_strategies(self, window_events: List[OHLCV], event: NewMarketDataReceived) -> None:
        await asyncio.gather(*(strategy.process(window_events, event) for strategy in self.strategies))
