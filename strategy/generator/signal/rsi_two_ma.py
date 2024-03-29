from dataclasses import dataclass

from core.models.moving_average import MovingAverageType
from core.models.parameter import (
    CategoricalParameter,
    Parameter,
    RandomParameter,
    StaticParameter,
)
from core.models.smooth import Smooth

from .base import Signal, SignalType


@dataclass(frozen=True)
class Rsi2MaSignal(Signal):
    type: SignalType = SignalType.Rsi2Ma
    smooth_type: Parameter = StaticParameter(Smooth.SMMA)
    rsi_period: Parameter = StaticParameter(2.0)
    threshold: Parameter = RandomParameter(0.0, 3.0, 1.0)
    ma: Parameter = CategoricalParameter(MovingAverageType)
    short_period: Parameter = RandomParameter(20.0, 50.0, 5.0)
    long_period: Parameter = RandomParameter(30.0, 50.0, 5.0)
