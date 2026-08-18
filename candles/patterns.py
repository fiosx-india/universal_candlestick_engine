import pandas as pd

from candles.features import add_candle_features
from models import PatternResult


def _safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def detect_candlestick_patterns(df: pd.DataFrame, timeframe: str = "") -> list[PatternResult]:
    """
    Detect candle patterns on the latest completed bar.

    The detector intentionally reports structural evidence only. Trend,
    volume, volatility and multi-timeframe confirmation belong to context
    layers and should not be hard-coded into individual candle names.
    """
    x = add_candle_features(df)
    if len(x) < 3:
        return []

    r = x.iloc[-1]
    p = x.iloc[-2]
    patterns: list[PatternResult] = []

    body = max(_safe_float(r.Body), 1e-12)
    range_ = max(_safe_float(r.Range), 1e-12)
    body_ratio = _safe_float(r.BodyRatio)
    upper = _safe_float(r.UpperWick)
    lower = _safe_float(r.LowerWick)
    rvol = _safe_float(r.RVOL, 1.0)

    def add(name, direction, confidence, **details):
        patterns.append(
            PatternResult(
                name=name,
                direction=direction,
                state="CONFIRMED",
                confidence=round(float(confidence), 4),
                score=round(float(confidence), 4),
                timeframe=timeframe,
                details=details,
            )
        )

    # Single-candle patterns.
    if body_ratio <= 0.10:
        add("Doji", "SIDEWAYS", 0.60, body_ratio=body_ratio)

    if lower >= 2.0 * body and upper <= 0.75 * body and body_ratio <= 0.45:
        add("Hammer", "BULLISH", 0.72, lower_wick=lower, upper_wick=upper)

    if upper >= 2.0 * body and lower <= 0.75 * body and body_ratio <= 0.45:
        add("Shooting Star", "BEARISH", 0.72, lower_wick=lower, upper_wick=upper)

    if body_ratio >= 0.90:
        if bool(r.Bullish):
            add("Bullish Marubozu", "BULLISH", 0.76, body_ratio=body_ratio)
        elif bool(r.Bearish):
            add("Bearish Marubozu", "BEARISH", 0.76, body_ratio=body_ratio)

    # Two-candle patterns.
    prev_body = max(_safe_float(p.Body), 1e-12)
    if bool(r.Bullish) and bool(p.Bearish):
        if r.Open <= p.Close and r.Close >= p.Open:
            add("Bullish Engulfing", "BULLISH", 0.82,
                current_body=_safe_float(r.Body), previous_body=prev_body)

    if bool(r.Bearish) and bool(p.Bullish):
        if r.Open >= p.Close and r.Close <= p.Open:
            add("Bearish Engulfing", "BEARISH", 0.82,
                current_body=_safe_float(r.Body), previous_body=prev_body)

    if r.High < p.High and r.Low > p.Low:
        add("Inside Bar", "SIDEWAYS", 0.64,
            mother_high=_safe_float(p.High), mother_low=_safe_float(p.Low))

    # Three-candle patterns.
    if len(x) >= 4:
        a = x.iloc[-3]
        a_body = max(_safe_float(a.Body), 1e-12)

        if (
            bool(a.Bearish)
            and _safe_float(p.BodyRatio) < 0.50
            and bool(r.Bullish)
            and r.Close > (a.Open + a.Close) / 2.0
        ):
            add("Morning Star", "BULLISH", 0.75)

        if (
            bool(a.Bullish)
            and _safe_float(p.BodyRatio) < 0.50
            and bool(r.Bearish)
            and r.Close < (a.Open + a.Close) / 2.0
        ):
            add("Evening Star", "BEARISH", 0.75)

        # Require the fourth candle to break the preceding three-candle move.
        if (
            all(bool(x.iloc[-i].Bullish) for i in (3, 2, 1))
            and bool(r.Bearish)
            and r.Close < x.iloc[-2].Open
        ):
            add("Three Line Strike", "BEARISH", 0.64)

    # Attach observational volume information; it does not change the
    # pattern identity or direction.
    for pattern in patterns:
        pattern.details["rvol"] = round(rvol, 4)
        pattern.details["range_pct"] = round(_safe_float(r.RangePct), 6)

    return patterns
