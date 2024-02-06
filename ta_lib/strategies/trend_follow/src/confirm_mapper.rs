use crate::smooth_mapper::map_to_smooth;
use base::prelude::*;
use confirm::*;
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(tag = "type")]
pub enum ConfirmConfig {
    Dpo {
        smooth_type: f32,
        period: f32,
    },
    Eom {
        smooth_type: f32,
        period: f32,
        divisor: f32,
    },
    Dumb {
        period: f32,
    },
    Rsi {
        smooth_type: f32,
        period: f32,
        threshold: f32,
    },
    Stc {
        smooth_type: f32,
        fast_period: f32,
        slow_period: f32,
        cycle: f32,
        d_first: f32,
        d_second: f32,
    },
}

pub fn map_to_confirm(config: ConfirmConfig) -> Box<dyn Confirm> {
    match config {
        ConfirmConfig::Dpo {
            smooth_type,
            period,
        } => Box::new(DPOConfirm::new(map_to_smooth(smooth_type as usize), period)),
        ConfirmConfig::Eom {
            smooth_type,
            period,
            divisor,
        } => Box::new(EOMConfirm::new(
            map_to_smooth(smooth_type as usize),
            period,
            divisor,
        )),
        ConfirmConfig::Dumb { period } => Box::new(DumbConfirm::new(period)),
        ConfirmConfig::Rsi {
            smooth_type,
            period,
            threshold,
        } => Box::new(RSIConfirm::new(
            map_to_smooth(smooth_type as usize),
            period,
            threshold,
        )),
        ConfirmConfig::Stc {
            smooth_type,
            fast_period,
            slow_period,
            cycle,
            d_first,
            d_second,
        } => Box::new(STCConfirm::new(
            map_to_smooth(smooth_type as usize),
            fast_period,
            slow_period,
            cycle,
            d_first,
            d_second,
        )),
    }
}
