from dataclasses import dataclass, field

from core.models.ohlcv import OHLCV
from core.models.symbol import Symbol
from core.models.timeframe import Timeframe

from .base import Event, EventGroup, EventMeta


@dataclass(frozen=True)
class MarketEvent(Event):
    meta: EventMeta = field(
        default_factory=lambda: EventMeta(priority=4, group=EventGroup.market),
        init=False,
    )


@dataclass(frozen=True)
class NewMarketDataReceived(MarketEvent):
    symbol: Symbol
    timeframe: Timeframe
    ohlcv: OHLCV
    closed: bool
