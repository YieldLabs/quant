from dataclasses import dataclass

from core.models.indicator import Indicator
from core.models.parameter import Parameter, RandomParameter, StaticParameter


@dataclass(frozen=True)
class CrossTIISignal(Indicator):
    major_period: Parameter = StaticParameter(14.0)
    minor_period: Parameter = StaticParameter(3.0)
    lower_barrier: Parameter = RandomParameter(30.0, 50.0, 5.0)
    upper_barrier: Parameter = RandomParameter(50.0, 70.0, 5.0)

    @property
    def parameters(self):
        return [
            self.major_period,
            self.minor_period,
            self.lower_barrier,
            self.upper_barrier,
        ]
