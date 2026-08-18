import pandas as pd


def trend_state(df: pd.DataFrame) -> str:
    """Classify trend using price structure plus moving-average alignment."""
    if len(df) < 50:
        return "UNKNOWN"

    close = pd.to_numeric(df["Close"], errors="coerce")
    fast = close.rolling(20, min_periods=20).mean().iloc[-1]
    slow = close.rolling(50, min_periods=50).mean().iloc[-1]

    if pd.isna(fast) or pd.isna(slow) or slow == 0:
        return "UNKNOWN"

    spread = float(fast / slow - 1.0)
    slope = float(close.iloc[-1] / close.iloc[-10] - 1.0) if len(close) >= 10 else 0.0

    if spread > 0.002 and slope > 0:
        return "BULLISH"
    if spread < -0.002 and slope < 0:
        return "BEARISH"
    return "SIDEWAYS"
