use base::prelude::*;
use core::prelude::*;
use momentum::di;

const ZERO_LINE: f32 = 0.0;

pub struct DIFlipSignal {
    smooth_type: Smooth,
    period: usize,
}

impl DIFlipSignal {
    pub fn new(smooth_type: Smooth, period: f32) -> Self {
        Self {
            smooth_type,
            period: period as usize,
        }
    }
}

impl Signal for DIFlipSignal {
    fn lookback(&self) -> usize {
        self.period
    }

    fn generate(&self, data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        let di = di(&data.close, self.smooth_type, self.period);

        (di.cross_over(&ZERO_LINE), di.cross_under(&ZERO_LINE))
    }
}
