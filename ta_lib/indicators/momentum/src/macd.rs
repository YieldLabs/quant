use core::prelude::*;

pub fn macd(
    source: &Series<f32>,
    smooth_type: Smooth,
    fast_period: usize,
    slow_period: usize,
    signal_period: usize,
) -> (Series<f32>, Series<f32>, Series<f32>) {
    let macd_line =
        source.smooth(smooth_type, fast_period) - source.smooth(smooth_type, slow_period);

    let signal_line = macd_line.smooth(smooth_type, signal_period);

    let histogram = &macd_line - &signal_line;

    (macd_line, signal_line, histogram)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_macd() {
        let source = Series::from([2.0, 4.0, 6.0, 8.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0]);
        let fast_period = 3;
        let slow_period = 5;
        let signal_period = 4;
        let epsilon = 0.001;
        let expected_macd_line = [
            0.0, 0.33333, 0.72222, 1.0648, 1.334877, 1.035751, 0.596751, 0.184292, -0.150576,
            -0.403769,
        ];
        let expected_signal_line = [
            0.0, 0.13333, 0.36888, 0.6472, 0.9223, 0.9676, 0.8193, 0.5653, 0.2789, 0.0058,
        ];
        let expected_histogram = [
            0.0, 0.1999, 0.3533, 0.4175, 0.4125, 0.068, -0.2222, -0.381, -0.4295, -0.4096,
        ];

        let (macd_line, signal_line, histogram) = macd(
            &source,
            Smooth::EMA,
            fast_period,
            slow_period,
            signal_period,
        );

        let result_macd_line: Vec<f32> = macd_line.into();
        let result_signal_line: Vec<f32> = signal_line.into();
        let result_histogram: Vec<f32> = histogram.into();

        for i in 0..source.len() {
            assert!(
                (result_macd_line[i] - expected_macd_line[i]).abs() < epsilon,
                "at position {}: {} != {}",
                i,
                result_macd_line[i],
                expected_macd_line[i]
            );

            assert!(
                (result_signal_line[i] - expected_signal_line[i]).abs() < epsilon,
                "at position {}: {} != {}",
                i,
                result_signal_line[i],
                expected_signal_line[i]
            );

            assert!(
                (result_histogram[i] - expected_histogram[i]).abs() < epsilon,
                "at position {}: {} != {}",
                i,
                result_histogram[i],
                expected_histogram[i]
            );
        }
    }
}
