from ta.alerts.mfi_alerts import MoneyFlowIndexAlerts
from ta.indicators.zlema_indicator import ZeroLagEMAIndicator
from strategy.abstract_strategy import AbstractStrategy
from ta.patterns.engulfing_pattern import EngulfingPattern
from ta.patterns.harami_pattern import HaramiPattern

class EngulfingSMA(AbstractStrategy):
    def __init__(self, slow_sma_period=200, upper_barrier=80, lower_barrier=20, tolerance=0.002, retracement_pct=0.05):
        super().__init__()
        self.slow_sma = ZeroLagEMAIndicator(window=slow_sma_period)
        self.mfi = MoneyFlowIndexAlerts(overbought_level=upper_barrier, oversold_level=lower_barrier)
        self.upper_barrier = upper_barrier
        self.lower_barrier = lower_barrier
        self.tolerance = tolerance
        self.retracement_pct = retracement_pct

    def _add_indicators(self, ohlcv):
        data = ohlcv.copy()
        
        data['sma_slow'] = self.slow_sma.call(data)

        data['bullish_engulfing'] = EngulfingPattern.bullish(data)
        data['bearish_engulfing'] = EngulfingPattern.bearish(data)

        data['bullish_harami'] = HaramiPattern.bullish(data)
        data['bearish_harami'] = HaramiPattern.bearish(data)

        data['mfi_buy'], data['mfi_sell'] = self.mfi.alert(data)

        return data
    
    def _check_confirmation_candle(self, current_row, previous_row):
        buy_confirmation = (
            previous_row['close'] > current_row['sma_slow']
            and abs(previous_row['close'] - current_row['sma_slow']) / current_row['sma_slow'] <= self.tolerance
        )

        sell_confirmation = (
            previous_row['close'] < current_row['sma_slow']
            and abs(previous_row['close'] - current_row['sma_slow']) / current_row['sma_slow'] <= self.tolerance
        )
        
        return buy_confirmation, sell_confirmation

    def entry(self, ohlcv):
        if len(ohlcv) < 3:
            return False, False

        data = self._add_indicators(ohlcv)

        current_row = data.iloc[-1]
        previous_row = data.iloc[-2]

        buy_confirmation, sell_confirmation = self._check_confirmation_candle(current_row, previous_row)

        buy_signal = (
            buy_confirmation and
            (current_row['bullish_engulfing'] or current_row['bullish_harami']) and
            current_row['mfi_buy'] and
            (current_row['close'] >= current_row['sma_slow'] * (1 - self.retracement_pct))
        )

        sell_signal = (
            sell_confirmation and
            (current_row['bearish_engulfing'] or current_row['bearish_harami']) and
            current_row['mfi_sell'] and
            (current_row['close'] <= current_row['sma_slow'] * (1 + self.retracement_pct))
        )

        return buy_signal, sell_signal
    
    def exit(self, ohlcv):
        pass
    
    def __str__(self) -> str:
        return f'EngulfingSMA()'
