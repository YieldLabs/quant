use core::series::Series;

pub fn bullish(open: &[f64], close: &[f64]) -> Vec<bool> {
    let open = Series::from(open);
    let close = Series::from(close);

    (close.lt_series(&open)
        & close.shift(1).gt_series(&open.shift(1))
        & close.shift(2).gt_series(&open.shift(2))
        & close.lt_series(&open.shift(1))
        & close.gt_series(&close.shift(2))
        & open.shift(1).gt_series(&close.shift(2)))
    .into()
}

pub fn bearish(open: &[f64], close: &[f64]) -> Vec<bool> {
    let open = Series::from(open);
    let close = Series::from(close);

    (close.gt_series(&open)
        & close.shift(1).lt_series(&open.shift(1))
        & close.shift(2).lt_series(&open.shift(2))
        & close.gt_series(&open.shift(1))
        & close.lt_series(&close.shift(2))
        & open.shift(1).lt_series(&close.shift(2)))
    .into()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tasuki_bullish() {
        let open = vec![4.0, 4.0, 4.0, 4.0, 4.0];
        let close = vec![2.0, 2.5, 2.0, 1.5, 2.0];
        let expected = vec![false, false, false, false, false];

        let result = bullish(&open, &close);

        assert_eq!(result, expected);
    }

    #[test]
    fn test_tasuki_bearish() {
        let open = vec![4.0, 4.0, 4.0, 4.0, 4.0];
        let close = vec![2.0, 2.5, 2.0, 1.5, 2.0];
        let expected = vec![false, false, false, false, false];

        let result = bearish(&open, &close);

        assert_eq!(result, expected);
    }
}
