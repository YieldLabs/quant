use serde::Deserialize;

#[derive(Deserialize)]
#[serde(tag = "type")]
pub enum PulseConfig {
    Adx {
        smooth_type: f32,
        adx_period: f32,
        di_period: f32,
        threshold: f32,
    },
    Braid {
        smooth_type: f32,
        fast_period: f32,
        slow_period: f32,
        open_period: f32,
        strength: f32,
        atr_period: f32,
    },
    Dumb {
        period: f32,
    },
    Chop {
        atr_period: f32,
        period: f32,
        threshold: f32,
    },
    Nvol {
        smooth_type: f32,
        period: f32,
    },
    Vo {
        smooth_type: f32,
        fast_period: f32,
        slow_period: f32,
    },
    Tdfi {
        smooth_type: f32,
        period: f32,
        n: f32,
    },
}
