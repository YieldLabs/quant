import asyncio
import logging

from core.commands.broker import ClosePosition, OpenPosition, UpdateSettings
from core.event_decorators import command_handler, query_handler
from core.interfaces.abstract_config import AbstractConfig
from core.interfaces.abstract_event_manager import AbstractEventManager
from core.interfaces.abstract_exhange_factory import AbstractExchangeFactory
from core.models.exchange import ExchangeType
from core.models.order import Order, OrderStatus
from core.queries.account import GetBalance
from core.queries.broker import GetSymbol, GetSymbols
from core.queries.position import GetClosePosition, GetOpenPosition

from ._twap import TWAP

logger = logging.getLogger(__name__)


class SmartRouter(AbstractEventManager):
    def __init__(
        self, exchange_factory: AbstractExchangeFactory, config_service: AbstractConfig
    ):
        super().__init__()
        self.exchange_factory = exchange_factory
        self.exchange = self.exchange_factory.create(ExchangeType.BYBIT)
        self.entry_price = TWAP(config_service)
        self.config = config_service.get("position")

    @query_handler(GetOpenPosition)
    def get_open_position(self, query: GetOpenPosition):
        position = query.position

        broker_position = self.exchange.fetch_position(
            position.signal.symbol, position.side
        )

        logging.info(f"Broker position: {broker_position}")

        if not broker_position:
            return Order(status=OrderStatus.FAILED, price=0, size=0)
        else:
            return Order(
                status=OrderStatus.EXECUTED,
                size=broker_position["position_size"],
                price=broker_position["entry_price"],
            )

    @query_handler(GetClosePosition)
    def get_close_position(self, query: GetClosePosition):
        position = query.position

        symbol = position.signal.symbol

        trade = self.exchange.fetch_trade(symbol)

        logging.info(f"Trade: {trade}")

        if not trade:
            return Order(status=OrderStatus.FAILED, price=0, size=0)

        return Order(
            status=OrderStatus.CLOSED, size=trade["amount"], price=trade["price"]
        )

    @query_handler(GetSymbols)
    def get_symbols(self, _query: GetSymbols):
        return self.exchange.fetch_future_symbols()

    @query_handler(GetSymbol)
    def get_symbol(self, query: GetSymbol):
        symbols = self.exchange.fetch_future_symbols()

        return next((symbol for symbol in symbols if symbol.name == query.symbol), None)

    @query_handler(GetBalance)
    def get_account_balance(self, query: GetBalance):
        return self.exchange.fetch_account_balance(query.currency)

    @command_handler(UpdateSettings)
    def update_symbol_settings(self, command: UpdateSettings):
        self.exchange.update_symbol_settings(
            command.symbol, command.position_mode, command.margin_mode, command.leverage
        )

    @command_handler(OpenPosition)
    async def open_position(self, command: OpenPosition):
        position = command.position

        logger.info(f"Try to open position: {position}")

        symbol = position.signal.symbol
        position_size = position.size
        stop_loss = position.stop_loss_price
        entry_price = position.entry_price

        distance_to_stop_loss = abs(entry_price - stop_loss)

        min_size = symbol.min_position_size
        entry_timeout = self.config["entry_timeout"]

        num_orders = min(
            max(1, int(position_size / min_size)), self.config["max_order_slice"]
        )
        size = round(position_size / num_orders, symbol.position_precision)
        order_counter = 0
        num_order_breach = 0
        num_open_order_attempts = 0

        logging.info(f"Theo price: {entry_price}")

        for price in self.entry_price.calculate(symbol, self.exchange):
            logging.info(f"Algo price: {price}")

            current_distance_to_stop_loss = abs(stop_loss - price)

            threshold_breach = (
                self.config["stop_loss_threshold"] * distance_to_stop_loss
                > current_distance_to_stop_loss
            )

            if threshold_breach:
                logging.info(
                    f"Order risk breached: ENTR: {entry_price}, STPLS: {stop_loss}, THEO_DSTNC: {distance_to_stop_loss}, ALG_DSTNC: {current_distance_to_stop_loss}"
                )

                num_order_breach += 1

                if num_order_breach >= self.config["max_order_breach"]:
                    break

                await asyncio.sleep(3)

                continue

            order_id = self.exchange.create_limit_order(
                symbol, position.side, size, price
            )

            if order_id and self.exchange.has_order(order_id, symbol):
                order_counter += 1
                num_open_order_attempts = max(0, num_open_order_attempts - 1)

                logging.info(f"Opened order: {order_id} with price: {price}")
            else:
                num_open_order_attempts += 1

            if order_counter >= num_orders:
                logging.info(f"All orders are filled: {order_counter}")

                break

            if num_open_order_attempts >= self.config["max_open_order_attempts"]:
                break

            await asyncio.sleep(entry_timeout)

    @command_handler(ClosePosition)
    def close_position(self, command: ClosePosition):
        position = command.position
        symbol = position.signal.symbol
        side = position.side

        self.exchange.close_position(symbol, side)
