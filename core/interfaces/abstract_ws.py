from abc import ABC, abstractmethod

from core.models.symbol import Symbol
from core.models.timeframe import Timeframe


class AbstractWS(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def subscribe(self, symbol: Symbol, timeframe: Timeframe):
        pass
