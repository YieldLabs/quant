from enum import Enum


class Smooth(Enum):
    EMA = 1
    SMA = 2
    SMMA = 3
    KAMA = 4
    HMA = 5
    WMA = 6
    ZLEMA = 7
    LSMA = 8

    def __str__(self):
        return self.name.upper()
