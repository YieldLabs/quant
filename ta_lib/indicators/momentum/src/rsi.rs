use core::prelude::*;

pub fn rsi(source: &Series<f32>, smooth_type: Smooth, period: usize) -> Series<f32> {
    let len = source.len();

    let mom = source.change(1);
    let up = mom.max(&ZERO).smooth(smooth_type, period);
    let down = mom.min(&ZERO).negate().smooth(smooth_type, period);

    let oneh = Series::fill(SCALE, len);

    iff!(down.seq(&ZERO), oneh, SCALE - (SCALE / (1. + up / down)))
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_rsi_with_valid_data() {
        let source = Series::from([
            6.8445, 6.8560, 6.8565, 6.8590, 6.8530, 6.8575, 6.855, 6.858, 6.86, 6.8480, 6.8575,
            6.864, 6.8565, 6.8455, 6.8450, 6.8365, 6.8310, 6.8355, 6.8360, 6.8345, 6.8285, 6.8395,
        ]);
        let period = 3;
        let expected = [
            100.0, 100.0, 100.0, 100.0, 46.885506, 66.75195, 50.889442, 65.60162, 73.53246,
            23.915344, 57.76078, 71.00006, 46.02974, 25.950226, 25.200401, 14.512299, 10.280083,
            33.926575, 36.707954, 30.863396, 15.785042, 64.06485,
        ];

        let result: Vec<f32> = rsi(&source, Smooth::SMMA, period).into();

        assert_eq!(result, expected);
    }
}
