from dataclasses import dataclass

from core.models.parameter import Parameter, StaticParameter

from .base import Signal, SignalType


@dataclass(frozen=True)
class VwapCrossSignal(Signal):
    type: SignalType = SignalType.VwapCross
    period: Parameter = StaticParameter(100.0)
