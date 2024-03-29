from dataclasses import dataclass
from enum import Enum

from core.models.indicator import Indicator


class SignalType(Enum):
    AoFlip = "AoFlip"
    ApoFlip = "ApoFlip"
    AoSaucer = "AoSaucer"
    BopFlip = "BopFlip"
    CeFlip = "CeFlip"
    CcFlip = "CcFlip"
    CfoFlip = "CfoFlip"
    DiFlip = "DiFlip"
    DiCross = "DiCross"
    DmiCross = "DmiCross"
    HighLow = "HighLow"
    Ma3Cross = "Ma3Cross"
    MaTestingGround = "MaTestingGround"
    MaQuadruple = "MaQuadruple"
    MaSurpass = "MaSurpass"
    MacdFlip = "MacdFlip"
    MacdBb = "MacdBb"
    MacdCross = "MacdCross"
    MacdColorSwitch = "MacdColorSwitch"
    RsiNeutralityCross = "RsiNeutralityCross"
    RsiNeutralityPullback = "RsiNeutralityPullback"
    RsiNeutralityRejection = "RsiNeutralityRejection"
    RsiSup = "RsiSup"
    Rsi2Ma = "Rsi2Ma"
    RsiMaPullback = "RsiMaPullback"
    Dch2Ma = "Dch2Ma"
    KstCross = "KstCross"
    RocFlip = "RocFlip"
    RsiV = "RsiV"
    SnAtr = "SnAtr"
    SupFlip = "SupFlip"
    SupPullBack = "SupPullBack"
    StcFlip = "StcFlip"
    StcUturn = "StcUturn"
    StochCross = "StochCross"
    TrendCandle = "TrendCandle"
    TiiCross = "TiiCross"
    TiiV = "TiiV"
    TrixFlip = "TrixFlip"
    TrixCross = "TrixCross"
    TsiFlip = "TsiFlip"
    TsiCross = "TsiCross"
    QstickFlip = "QstickFlip"
    QstickCross = "QstickCross"
    ViCross = "ViCross"
    VwapBb = "VwapBb"
    VwapCross = "VwapCross"

    def __str__(self):
        return self.value.upper()


@dataclass(frozen=True)
class Signal(Indicator):
    type: SignalType
