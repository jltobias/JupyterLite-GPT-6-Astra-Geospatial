//! Pure arithmetic export: no browser APIs, allocation or third-party crates.
#[no_mangle]
pub extern "C" fn exposure_sum(count: u32, x: f64, y: f64, decay_m: f64) -> f64 {
    if !x.is_finite() || !y.is_finite() || decay_m <= 0.0 || !decay_m.is_finite() {
        return f64::NAN;
    }
    let mut sum = 0.0;
    for i in 0..count {
        let px = ((i * 37 % 2000) as f64) - x;
        let py = ((i * 71 % 2000) as f64) - y;
        sum += 1.0 / (1.0 + (px*px + py*py)/(decay_m*decay_m));
    }
    sum
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn empty_and_origin() {
        assert_eq!(exposure_sum(0,0.,0.,100.),0.);
        assert_eq!(exposure_sum(1,0.,0.,100.),1.);
        assert!(exposure_sum(1,0.,0.,0.).is_nan());
    }
}
