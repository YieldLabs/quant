mod bitwise;
mod cmp;
mod cross;
mod extremum;
mod from;
mod macros;
mod math;
mod ops;
mod series;
mod smoothing;
mod traits;

pub mod prelude {
    pub use crate::iff;
    pub use crate::series::Series;
    pub use crate::smoothing::Smooth;
    pub use crate::traits::*;
}

pub use prelude::*;
