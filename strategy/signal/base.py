from dataclasses import dataclass
from enum import Enum

from core.models.indicator import Indicator


class SignalType(Enum):
    AoFlip = "AoFlip"
    CcFlip = "CcFlip"
    DiFlip = "DiFlip"
    DiCross = "DiCross"
    Ma3Cross = "Ma3Cross"
    MacdFlip = "MacdFlip"
    MacdCross = "MacdCross"
    MacdColorSwitch = "MacdColorSwitch"
    RsiNeutralityCross = "RsiNeutralityCross"
    RsiNeutralityPullback = "RsiNeutralityPullback"
    RsiNeutralityRejection = "RsiNeutralityRejection"
    Rsi2Ma = "Rsi2Ma"
    RsiMaPullback = "RsiMaPullback"
    Dch2Ma = "Dch2Ma"
    RocFlip = "RocFlip"
    RsiV = "RsiV"
    SnAtr = "SnAtr"
    SupFlip = "SupFlip"
    SupPullBack = "SupPullBack"
    StcFlip = "StcFlip"
    TestGround = "TestGround"
    TrendCandle = "TrendCandle"
    TIICross = "TIICross"
    TiiV = "TiiV"
    TrixFlip = "TrixFlip"
    TsiFlip = "TsiFlip"
    TsiCross = "TsiCross"
    QstickFlip = "QstickFlip"
    QstickCross = "QstickCross"
    Quadruple = "Quadruple"

    def __str__(self):
        return self.value.upper()


@dataclass(frozen=True)
class BaseSignal(Indicator):
    type: SignalType
