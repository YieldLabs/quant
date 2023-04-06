from alerts.abstract_alert import AbstractAlert
from ta.volume.mfi import MoneyFlowIndex


class MoneyFlowIndexAlerts(AbstractAlert):
    def __init__(self, period=14, overbought_level=80, oversold_level=20):
        super().__init__()
        self.mfi = MoneyFlowIndex(period)
        self.overbought_level = overbought_level
        self.oversold_level = oversold_level

    def alert(self, data):
        data['mfi'] = self.mfi.call(data)

        return data['mfi'] < self.oversold_level, data['mfi'] > self.overbought_level
    
    def __str__(self) -> str:
        return f'MFIALERT{self.mfi}_{self.overbought_level}_{self.oversold_level}'
