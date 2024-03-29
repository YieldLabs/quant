use core::prelude::*;

pub fn dema(source: &Series<f32>, period: usize) -> Series<f32> {
    let ema = source.smooth(Smooth::EMA, period);

    2. * &ema - ema.smooth(Smooth::EMA, period)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dema() {
        let source = Series::from([1.0, 2.0, 3.0, 4.0, 5.0]);
        let expected = vec![1.0, 1.75, 2.75, 3.8125, 4.875];

        let result: Vec<f32> = dema(&source, 3).into();

        assert_eq!(result, expected);
    }
}
