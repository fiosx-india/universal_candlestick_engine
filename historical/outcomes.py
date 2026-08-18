import numpy as np
import pandas as pd

HORIZON_BARS = {
    "1H": 1, "2H": 2, "4H": 4,
    "1D": 1, "2D": 2, "3D": 3, "5D": 5, "7D": 7, "15D": 15,
}


def forward_outcomes(df, occurrence_indices, horizon):
    bars = HORIZON_BARS.get(horizon)
    if bars is None:
        return None

    closes = pd.to_numeric(df["Close"], errors="coerce")
    returns = []

    for idx in occurrence_indices:
        try:
            pos = df.index.get_loc(idx)
            if not isinstance(pos, (int, np.integer)):
                continue
        except KeyError:
            continue

        if pos + bars >= len(df):
            continue

        start = float(closes.iloc[pos])
        end = float(closes.iloc[pos + bars])
        if start <= 0:
            continue
        returns.append(end / start - 1.0)

    if not returns:
        return None

    arr = np.asarray(returns, dtype=float)
    bull = float((arr > 0.002).mean())
    bear = float((arr < -0.002).mean())
    side = max(0.0, 1.0 - bull - bear)

    return {
        "horizon": horizon,
        "samples": int(len(arr)),
        "bullish_probability": bull,
        "bearish_probability": bear,
        "sideways_probability": side,
        "median_return": float(np.median(arr)),
        "win_rate": float((arr > 0).mean()),
    }
