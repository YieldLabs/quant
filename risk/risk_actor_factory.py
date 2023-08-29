from core.interfaces.abstract_risk_actor_factory import AbstractRiskActorFactory
from core.models.symbol import Symbol
from core.models.timeframe import Timeframe

from .risk_actor import RiskActor


class RiskActorFactory(AbstractRiskActorFactory):
    def __init__(self, risk_buffer: float):
        self.risk_buffer = risk_buffer
    
    def create_actor(self, symbol: Symbol, timeframe: Timeframe):
        return RiskActor(
            symbol,
            timeframe,
            self.risk_buffer,
        )
        