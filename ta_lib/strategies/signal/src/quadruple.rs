use base::{OHLCVSeries, Signal};
use core::Series;
use shared::{ma_indicator, MovingAverageType};

pub struct QuadrupleSignal {
    smoothing: MovingAverageType,
    period: usize,
}

impl QuadrupleSignal {
    pub fn new(smoothing: MovingAverageType, period: f32) -> Self {
        Self {
            smoothing,
            period: period as usize,
        }
    }
}

impl Signal for QuadrupleSignal {
    fn lookback(&self) -> usize {
        self.period
    }

    fn generate(&self, data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        let ma = ma_indicator(&self.smoothing, data, self.period);

        let long_signal = data.low.lt(&ma)
            & data.close.gt(&ma)
            & data.low.shift(1).lt(&ma.shift(1))
            & data.close.shift(1).gt(&ma.shift(1))
            & data.low.shift(2).lt(&ma.shift(2))
            & data.close.shift(2).gt(&ma.shift(2))
            & data.low.shift(3).lt(&ma.shift(3))
            & data.close.shift(3).gt(&ma.shift(3));

        let short_signal = data.high.gt(&ma)
            & data.close.lt(&ma)
            & data.high.shift(1).gt(&ma.shift(1))
            & data.close.shift(1).lt(&ma.shift(1))
            & data.high.shift(2).gt(&ma.shift(2))
            & data.close.shift(2).lt(&ma.shift(2))
            & data.high.shift(3).gt(&ma.shift(3))
            & data.close.shift(3).lt(&ma.shift(3));

        (long_signal, short_signal)
    }
}
