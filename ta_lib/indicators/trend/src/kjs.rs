use core::prelude::*;

pub fn kjs(high: &Series<f32>, low: &Series<f32>, period: usize) -> Series<f32> {
    0.5 * (low.lowest(period) + high.highest(period))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_kjs() {
        let high = Series::from([2.0859, 2.0881, 2.0889, 2.0896, 2.0896, 2.0907]);
        let low = Series::from([2.0846, 2.0846, 2.0881, 2.0886, 2.0865, 2.0875]);
        let expected = vec![2.08525, 2.08635, 2.08675, 2.0871, 2.08805, 2.0886];

        let result: Vec<f32> = kjs(&high, &low, 3).into();

        assert_eq!(result, expected);
    }
}
