from dataclasses import dataclass

from core.models.moving_average import MovingAverageType
from core.models.parameter import CategoricalParameter, Parameter, RandomParameter

from .base import Signal, SignalType


@dataclass(frozen=True)
class Ma3CrossSignal(Signal):
    type: SignalType = SignalType.Ma3Cross
    ma: Parameter = CategoricalParameter(MovingAverageType)
    short_period: Parameter = RandomParameter(5.0, 20.0, 5.0)
    medium_period: Parameter = RandomParameter(25.0, 80.0, 5.0)
    long_period: Parameter = RandomParameter(85.0, 200.0, 5.0)
