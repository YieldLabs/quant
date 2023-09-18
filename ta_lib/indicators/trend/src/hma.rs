use core::series::Series;

pub fn hma(source: &[f32], period: usize) -> Series<f32> {
    let source = Series::from(source);

    let hma = source.hma(period);

    hma
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hma() {
        let source = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let expected = vec![0.0, 0.0, 3.0000002, 4.0, 4.9999995];

        let result: Vec<f32> = hma(&source, 3).into();

        assert_eq!(result, expected);
    }
}
