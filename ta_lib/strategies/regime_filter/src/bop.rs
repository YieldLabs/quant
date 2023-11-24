use base::{OHLCVSeries, Regime};
use core::Series;
use momentum::bop;

const BOP_FILTER: f32 = 0.0;

pub struct BOPFilter {
    smoothing_period: usize,
}

impl BOPFilter {
    pub fn new(smoothing_period: f32) -> Self {
        Self {
            smoothing_period: smoothing_period as usize,
        }
    }
}

impl Regime for BOPFilter {
    fn lookback(&self) -> usize {
        self.smoothing_period
    }

    fn apply(&self, data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        let bop = bop(
            &data.open,
            &data.high,
            &data.low,
            &data.close,
            self.smoothing_period,
        );

        (bop.sgt(BOP_FILTER), bop.slt(BOP_FILTER))
    }
}