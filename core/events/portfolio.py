from dataclasses import dataclass, field

from .base_event import Event, EventMeta

from ..models.portfolio import AdvancedPortfolioPerformance, BasicPortfolioPerformance
from ..models.strategy import Strategy


@dataclass(frozen=True)
class PortfolioPerformanceUpdated(Event):
    strategy: Strategy
    basic: BasicPortfolioPerformance
    advanced: AdvancedPortfolioPerformance
    meta: EventMeta = field(default_factory=lambda: EventMeta(priority=8))
