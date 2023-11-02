use core::Series;

pub fn bullish(
    open: &Series<f32>,
    high: &Series<f32>,
    low: &Series<f32>,
    close: &Series<f32>,
) -> Series<bool> {
    high.shift(2).gt(&high.shift(3))
        & low.shift(2).lt(&low.shift(3))
        & close.shift(2).lt(&open.shift(2))
        & high.shift(1).lt(&high.shift(2))
        & low.shift(1).gt(&low.shift(2))
        & high.gt(&high.shift(1))
}

pub fn bearish(
    open: &Series<f32>,
    high: &Series<f32>,
    low: &Series<f32>,
    close: &Series<f32>,
) -> Series<bool> {
    high.shift(2).gt(&high.shift(3))
        & low.shift(2).lt(&low.shift(3))
        & close.shift(2).lt(&open.shift(2))
        & high.shift(1).lt(&high.shift(2))
        & low.shift(1).gt(&low.shift(2))
        & low.lt(&low.shift(1))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_three_one_two_bullish() {
        let open = Series::from([4.0, 3.0, 4.0, 3.0, 4.0]);
        let high = Series::from([4.5, 3.5, 4.5, 3.5, 4.5]);
        let low = Series::from([4.0, 3.0, 4.0, 3.0, 4.0]);
        let close = Series::from([4.5, 3.5, 4.5, 3.5, 4.5]);
        let expected = vec![false, false, false, false, false];

        let result: Vec<bool> = bullish(&open, &high, &low, &close).into();

        assert_eq!(result, expected);
    }

    #[test]
    fn test_three_one_two_bearish() {
        let open = Series::from([4.0, 3.0, 4.0, 3.0, 4.0]);
        let high = Series::from([4.0, 3.0, 4.0, 3.0, 4.0]);
        let low = Series::from([3.5, 2.5, 3.5, 2.5, 3.5]);
        let close = Series::from([3.5, 2.5, 3.5, 2.5, 3.5]);
        let expected = vec![false, false, false, false, false];

        let result: Vec<bool> = bearish(&open, &high, &low, &close).into();

        assert_eq!(result, expected);
    }
}
