import numpy as np

from models import PatternResult
from structures.pivots import linear_slope


def _result(name, direction, tf, score, state="FORMING", **details):
    return PatternResult(
        name=name,
        direction=direction,
        state=state,
        confidence=round(float(score), 4),
        score=round(float(score), 4),
        timeframe=tf,
        details=details,
    )


def detect_structure_patterns(df, timeframe="") -> list[PatternResult]:
    """
    Lightweight structure detector.

    It deliberately labels structure as FORMING unless a simple breakout/
    confirmation condition is observable in the available window. This avoids
    presenting every geometric resemblance as a confirmed trade signal.
    """
    if len(df) < 30:
        return []

    c = df["Close"].to_numpy(dtype=float)
    h = df["High"].to_numpy(dtype=float)
    l = df["Low"].to_numpy(dtype=float)

    n = min(80, len(df))
    cc, hh, ll = c[-n:], h[-n:], l[-n:]
    out = []

    half = n // 2
    if half < 5:
        return out

    # W / M: compare separated extrema and require a meaningful recovery.
    lo1 = int(np.argmin(ll[:half]))
    lo2 = half + int(np.argmin(ll[half:]))
    if ll[lo1] > 0 and abs(ll[lo1] - ll[lo2]) / ll[lo1] < 0.025:
        neckline = float(np.max(hh[lo1:lo2 + 1]))
        confirmed = cc[-1] > neckline
        out.append(_result(
            "W Pattern", "BULLISH", timeframe,
            0.78 if confirmed else 0.68,
            state="CONFIRMED" if confirmed else "FORMING",
            first_bottom=float(ll[lo1]), second_bottom=float(ll[lo2]),
            neckline=neckline,
        ))

    hi1 = int(np.argmax(hh[:half]))
    hi2 = half + int(np.argmax(hh[half:]))
    if hh[hi1] > 0 and abs(hh[hi1] - hh[hi2]) / hh[hi1] < 0.025:
        neckline = float(np.min(ll[hi1:hi2 + 1]))
        confirmed = cc[-1] < neckline
        out.append(_result(
            "M Pattern", "BEARISH", timeframe,
            0.78 if confirmed else 0.68,
            state="CONFIRMED" if confirmed else "FORMING",
            first_top=float(hh[hi1]), second_top=float(hh[hi2]),
            neckline=neckline,
        ))

    # Slope-based structures.
    hs = float(linear_slope(hh))
    ls = float(linear_slope(ll))
    price_scale = max(float(np.mean(cc)), 1e-12)
    slope_tol = price_scale * 0.0005

    if hs < 0 and ls > 0:
        out.append(_result("Symmetrical Triangle", "SIDEWAYS", timeframe, 0.62,
                            high_slope=hs, low_slope=ls))
    if hs > 0 and ls > 0 and hs < ls:
        out.append(_result("Rising Wedge", "BEARISH", timeframe, 0.62,
                            high_slope=hs, low_slope=ls))
    if hs < 0 and ls < 0 and hs > ls:
        out.append(_result("Falling Wedge", "BULLISH", timeframe, 0.62,
                            high_slope=hs, low_slope=ls))
    if abs(hs) < slope_tol and ls > 0:
        out.append(_result("Ascending Triangle", "BULLISH", timeframe, 0.61,
                            high_slope=hs, low_slope=ls))
    if hs < 0 and abs(ls) < slope_tol:
        out.append(_result("Descending Triangle", "BEARISH", timeframe, 0.61,
                            high_slope=hs, low_slope=ls))
    if hs > 0 and ls < 0:
        out.append(_result("Broadening Formation", "SIDEWAYS", timeframe, 0.58,
                            high_slope=hs, low_slope=ls))

    # Rounded structure: keep it conservative.
    if n >= 50:
        mid = float(np.mean(cc[n // 2 - 5:n // 2 + 5]))
        left = float(np.mean(cc[:8]))
        right = float(np.mean(cc[-8:]))
        if mid < left and mid < right and abs(left - right) / max(left, 1e-12) < 0.08:
            out.append(_result("Rounding Bottom", "BULLISH", timeframe, 0.64,
                                left=left, midpoint=mid, right=right))

    return out
