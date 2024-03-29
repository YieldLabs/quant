use core::prelude::*;

pub fn dpo(source: &Series<f32>, smooth_type: Smooth, period: usize) -> Series<f32> {
    let k = period / 2 + 1;

    source - source.smooth(smooth_type, period).shift(k)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dpo() {
        let source = Series::from([2.0846, 2.0881, 2.0889, 2.0896, 2.0875, 2.0904, 2.0909]);
        let period = 3;
        let expected = vec![
            0.0,
            0.0,
            0.0043001175,
            0.003250122,
            0.000300169,
            0.0015332699,
            0.0022332668,
        ];

        let result: Vec<f32> = dpo(&source, Smooth::SMA, period).into();

        assert_eq!(result, expected);
    }
}
