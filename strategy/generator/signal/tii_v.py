from dataclasses import dataclass

from core.models.parameter import Parameter, StaticParameter

from .base import Signal, SignalType


@dataclass(frozen=True)
class TiiVSignal(Signal):
    type: SignalType = SignalType.TiiV
    major_period: Parameter = StaticParameter(8.0)
    minor_period: Parameter = StaticParameter(2.0)
