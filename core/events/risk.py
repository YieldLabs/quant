from dataclasses import dataclass, field

from core.models.position import Position

from .base import Event, EventGroup, EventMeta


@dataclass(frozen=True)
class RiskEvent(Event):
    position: Position
    meta: EventMeta = field(
        default_factory=lambda: EventMeta(priority=1, group=EventGroup.risk), init=False
    )


@dataclass(frozen=True)
class RiskThresholdBreached(RiskEvent):
    exit_price: float
