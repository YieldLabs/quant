from dataclasses import dataclass

from core.models.parameter import Parameter, RandomParameter, StaticParameter
from core.models.smooth import Smooth

from .base import Confirm, ConfirmType


@dataclass(frozen=True)
class RsiConfirm(Confirm):
    type: Confirm = ConfirmType.Rsi
    smooth_type: Parameter = StaticParameter(Smooth.SMMA)
    period: Parameter = StaticParameter(14.0)
    threshold: Parameter = RandomParameter(0.0, 3.0, 1.0)
