use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct TechAnalysis {
    pub rsi2: Vec<f32>,
    pub rsi14: Vec<f32>,
    pub macd: Vec<f32>,
    pub vo: Vec<f32>,
    pub nvol: Vec<f32>,
}