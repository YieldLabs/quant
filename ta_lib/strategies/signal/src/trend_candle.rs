use base::prelude::*;
use core::prelude::*;
use shared::{trend_candle_indicator, TrendCandleType};

const DEFAULT_LOOKBACK: usize = 13;

pub struct TrendCandleSignal {
    candle: TrendCandleType,
}

impl TrendCandleSignal {
    pub fn new(candle: TrendCandleType) -> Self {
        Self { candle }
    }
}

impl Signal for TrendCandleSignal {
    fn lookback(&self) -> usize {
        DEFAULT_LOOKBACK
    }

    fn generate(&self, data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        trend_candle_indicator(&self.candle, data)
    }
}
