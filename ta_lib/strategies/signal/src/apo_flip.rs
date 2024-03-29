use base::prelude::*;
use core::prelude::*;
use momentum::apo;

const APO_ZERO: f32 = 0.0;

pub struct APOFlipSignal {
    short_period: usize,
    long_period: usize,
}

impl APOFlipSignal {
    pub fn new(short_period: f32, long_period: f32) -> Self {
        Self {
            short_period: short_period as usize,
            long_period: long_period as usize,
        }
    }
}

impl Signal for APOFlipSignal {
    fn lookback(&self) -> usize {
        std::cmp::max(self.short_period, self.long_period)
    }

    fn generate(&self, data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        let apo = apo(&data.close, self.short_period, self.long_period);

        (apo.cross_over(&APO_ZERO), apo.cross_under(&APO_ZERO))
    }
}
