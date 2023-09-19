use base::{BaseStrategy, OHLCVSeries, Signals};
use core::series::Series;
use filter::{map_to_filter, FilterConfig};
use shared::{ma, MovingAverageType};
use stop_loss::ATRStopLoss;

pub struct CrossMAStrategy {
    short_period: usize,
    long_period: usize,
    smoothing: MovingAverageType,
}

impl CrossMAStrategy {
    pub fn new(
        smoothing: MovingAverageType,
        short_period: usize,
        long_period: usize,
        filter_config: FilterConfig,
        atr_period: usize,
        stop_loss_multi: f32,
    ) -> BaseStrategy<CrossMAStrategy, ATRStopLoss> {
        let mut lookback_period = std::cmp::max(short_period, long_period);
        let signal = CrossMAStrategy {
            short_period,
            long_period,
            smoothing,
        };

        let filter = map_to_filter(filter_config);

        lookback_period = std::cmp::max(lookback_period, filter.lookback());

        let stop_loss = ATRStopLoss {
            atr_period,
            multi: stop_loss_multi,
        };

        BaseStrategy::new(signal, filter, stop_loss, lookback_period)
    }
}

impl Signals for CrossMAStrategy {
    fn id(&self) -> String {
        format!(
            "CROSSMA_{}:{}:{}",
            self.smoothing, self.short_period, self.long_period
        )
    }

    fn entry(&self, data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        let short_ma = ma(&self.smoothing, data, self.short_period);
        let long_ma = ma(&self.smoothing, data, self.long_period);

        let long_signal = short_ma.cross_over(&long_ma);
        let short_signal = short_ma.cross_under(&long_ma);

        (long_signal, short_signal)
    }

    fn exit(&self, _data: &OHLCVSeries) -> (Series<bool>, Series<bool>) {
        (Series::empty(1), Series::empty(1))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use base::{Strategy, TradeAction, OHLCV};
    use filter::FilterConfig;
    use shared::MovingAverageType;

    #[test]
    fn test_crossmatrategy_new() {
        let strategy = CrossMAStrategy::new(
            MovingAverageType::SMA,
            50,
            100,
            FilterConfig::DUMB {},
            14,
            2.0,
        );
        assert_eq!(
            strategy.id(),
            "_STRTGCROSSMA_SMA:50:100_FLTRFDUMB_STPLSSATR_14:2.0"
        );
    }

    #[test]
    fn test_crossmastrategy_next_do_nothing() {
        let mut strat = CrossMAStrategy::new(
            MovingAverageType::SMA,
            50,
            100,
            FilterConfig::DUMB {},
            14,
            2.0,
        );

        for _i in 0..100 {
            strat.next(OHLCV {
                open: 2.0,
                high: 3.0,
                low: 2.0,
                close: 3.0,
                volume: 2000.0,
            });
        }

        let result = strat.next(OHLCV {
            open: 1.0,
            high: 1.0,
            low: 1.0,
            close: 1.0,
            volume: 20.0,
        });

        assert_eq!(result, TradeAction::DoNothing);
    }
}
