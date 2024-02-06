from dataclasses import dataclass

from core.models.parameter import (
    Parameter,
    RandomParameter,
    StaticParameter,
)
from core.models.smooth import Smooth

from .base import Signal, SignalType


@dataclass(frozen=True)
class RsiNautralityCrossSignal(Signal):
    type: SignalType = SignalType.RsiNeutralityCross
    smooth_type: Parameter = StaticParameter(Smooth.SMMA)
    rsi_period: Parameter = StaticParameter(14.0)
    threshold: Parameter = RandomParameter(0.0, 3.0, 1.0)
