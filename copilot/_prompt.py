system_prompt = """
You are an effective quantitative analysis assistant. Your job is to help interpret data, perform statistical analyses, technical analyses and provide insights based on numerical information.
"""
signal_risk_prompt = """
Evaluate the risk for an open {side} position within the {timeframe} timeframe using the provided data:

1. Candlestick Data:
  - Previous Bar: {prev_bar}
  - Current Bar: {curr_bar}

Risk Evaluation Framework:
Step-by-Step Analysis:

1. **Candlestick Analysis**:
  - **Analyze Price Movement**:
    - If the price is trending upwards, higher risk for SHORT, lower risk for LONG.
    - If the price is trending downwards, lower risk for SHORT, higher risk for LONG.
  - **Evaluate Real Body Normalized**:
    - High value indicates strong movement, higher risk if against the position side.
    - Low value indicates weak movement, lower risk if against the position side.
  - **Assess Body Range Ratio**:
    - High ratio indicates significant body, higher risk if against the position side.
    - Low ratio indicates insignificant body, lower risk if against the position side.
  - **Calculate Body Shadow Ratio**:
    - High ratio indicates strong pressure, higher risk if against the position side.
    - Low ratio indicates weak pressure, lower risk if against the position side.

2. **Anomaly Detection**:
  - **Identify Price Anomalies**:
    - Significant deviation from normal patterns: Higher risk for both sides.
    - No significant deviation: Lower risk for both sides.

Risk Level Explanation:
- **NONE**: No significant risk factors.
- **VERY_LOW**: Minor risk factors, generally favorable.
- **LOW**: Some risk factors, not significant enough to deter.
- **MODERATE**: Noticeable risk factors, caution advised.
- **HIGH**: Significant risk factors, high caution or avoidance advised.
- **VERY_HIGH**: Major risk factors, generally unfavorable.

Final Output:
1. Overall Risk Level for {side} position: NONE, VERY_LOW, LOW, MODERATE, HIGH, VERY_HIGH
2. Take Profit (TP) and Stop Loss (SL) predictions for {side} position based on risk level and market data.

Result Format:
RISK_LEVEL: [Risk Level], TP: [Take Profit Value], SL: [Stop Loss Value]
Return the result only.
"""
signal_risk_pattern = r"RISK_LEVEL: (NONE|LOW|VERY_LOW|LOW|MODERATE|HIGH|VERY_HIGH), TP: ([\d.]+), SL: ([\d.]+)"
