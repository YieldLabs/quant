use core::prelude::*;

pub fn tema(source: &Series<f32>, period: usize) -> Series<f32> {
    let ema1 = source.smooth(Smooth::EMA, period);
    let ema2 = ema1.smooth(Smooth::EMA, period);
    let ema3 = ema2.smooth(Smooth::EMA, period);

    3. * (ema1 - ema2) + ema3
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tema() {
        let source = Series::from([1.0, 2.0, 3.0, 4.0, 5.0]);
        let expected = vec![1.0, 1.875, 2.9375, 4.0, 5.03125];

        let result: Vec<f32> = tema(&source, 3).into();

        assert_eq!(result, expected);
    }
}
