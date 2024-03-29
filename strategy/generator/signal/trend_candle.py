from dataclasses import dataclass

from core.models.candle import TrendCandleType
from core.models.parameter import CategoricalParameter, Parameter

from .base import Signal, SignalType


@dataclass(frozen=True)
class TrendCandleSignal(Signal):
    type: SignalType = SignalType.TrendCandle
    candle: Parameter = CategoricalParameter(TrendCandleType)
