import asyncio
import logging
from typing import Union

from core.actors import Actor
from core.events.backtest import BacktestEnded
from core.events.position import (
    BrokerPositionClosed,
    BrokerPositionOpened,
    PositionClosed,
    PositionCloseRequested,
    PositionInitialized,
    PositionOpened,
)
from core.events.risk import RiskThresholdBreached
from core.events.signal import (
    GoLongSignalReceived,
    GoShortSignalReceived,
)
from core.interfaces.abstract_config import AbstractConfig
from core.interfaces.abstract_position_factory import AbstractPositionFactory
from core.models.position_side import PositionSide
from core.models.symbol import Symbol
from core.models.timeframe import Timeframe

from ._sm import LONG_TRANSITIONS, SHORT_TRANSITIONS, PositionStateMachine
from ._state import PositionStorage

SignalEvent = Union[GoLongSignalReceived, GoShortSignalReceived]
BrokerPositionEvent = Union[BrokerPositionOpened, BrokerPositionClosed]
ExitSignal = Union[RiskThresholdBreached, BacktestEnded]

PositionEvent = Union[SignalEvent, ExitSignal, BrokerPositionEvent]

logger = logging.getLogger(__name__)


class PositionActor(Actor):
    _EVENTS = [
        GoLongSignalReceived,
        GoShortSignalReceived,
        BacktestEnded,
        BrokerPositionOpened,
        BrokerPositionClosed,
        RiskThresholdBreached,
    ]

    def __init__(
        self,
        symbol: Symbol,
        timeframe: Timeframe,
        position_factory: AbstractPositionFactory,
        config_service: AbstractConfig,
    ):
        super().__init__(symbol, timeframe)
        self.position_factory = position_factory

        self.long_sm = PositionStateMachine(self, LONG_TRANSITIONS)
        self.short_sm = PositionStateMachine(self, SHORT_TRANSITIONS)
        self.state = PositionStorage()
        self.config = config_service.get("position")

    def pre_receive(self, event: PositionEvent) -> bool:
        symbol, timeframe = self._get_event_key(event)
        return self._symbol == symbol and self._timeframe == timeframe

    async def on_receive(self, event):
        symbol, _ = self._get_event_key(event)

        if hasattr(event, "position"):
            if event.position.side == PositionSide.LONG:
                await self.long_sm.process_event(symbol, event)
            if event.position.side == PositionSide.SHORT:
                await self.short_sm.process_event(symbol, event)
        else:
            await asyncio.gather(
                *[
                    self.long_sm.process_event(symbol, event),
                    self.short_sm.process_event(symbol, event),
                ]
            )

    async def handle_signal_received(self, event: SignalEvent) -> bool:
        async def create_and_store_position(event: SignalEvent):
            position = await self.position_factory.create_position(
                event.signal,
                event.ohlcv,
                event.entry_price,
                event.stop_loss,
                event.take_profit,
            )

            await self.state.store_position(position)
            await self.tell(PositionInitialized(position))
            return True

        symbol, timeframe = self._get_event_key(event)
        long_position, short_position = await self.state.retrieve_position(
            symbol, timeframe
        )

        if not long_position and isinstance(event, GoLongSignalReceived):
            return await create_and_store_position(event)

        if not short_position and isinstance(event, GoShortSignalReceived):
            return await create_and_store_position(event)

        return False

    async def handle_position_opened(self, event: BrokerPositionOpened) -> bool:
        await self.state.update_stored_position(event.position)
        await self.tell(PositionOpened(event.position))
        return True

    async def handle_position_closed(self, event: BrokerPositionClosed) -> bool:
        await self.state.close_stored_position(event.position)
        await self.tell(PositionClosed(event.position))
        return True

    async def handle_exit_received(self, event: ExitSignal) -> bool:
        if isinstance(event, RiskThresholdBreached):
            await self.state.update_stored_position(event.position)
            await self.tell(PositionCloseRequested(event.position, event.exit_price))
            return True

        symbol, timeframe = self._get_event_key(event)
        long_position, short_position = await self.state.retrieve_position(
            symbol, timeframe
        )

        if isinstance(event, BacktestEnded) and any([long_position, short_position]):
            if long_position:
                await self.tell(PositionCloseRequested(long_position, event.exit_price))

            if short_position:
                await self.tell(
                    PositionCloseRequested(short_position, event.exit_price)
                )

            return True

        return False

    @staticmethod
    def _get_event_key(event: PositionEvent):
        signal = (
            event.signal
            if hasattr(event, "signal")
            else event.position.signal
            if hasattr(event, "position")
            else event
        )

        return (signal.symbol, signal.timeframe)
