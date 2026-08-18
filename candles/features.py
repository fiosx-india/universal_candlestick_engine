import pandas as pd


def add_candle_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add reusable candle, volume and volatility features without mutating input."""
    x = df.copy()

    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in x.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    x["Body"] = (x["Close"] - x["Open"]).abs()
    x["Range"] = (x["High"] - x["Low"]).clip(lower=1e-12)
    x["UpperWick"] = x["High"] - x[["Open", "Close"]].max(axis=1)
    x["LowerWick"] = x[["Open", "Close"]].min(axis=1) - x["Low"]
    x["BodyRatio"] = (x["Body"] / x["Range"]).clip(0, 1)

    x["Bullish"] = x["Close"] > x["Open"]
    x["Bearish"] = x["Close"] < x["Open"]

    x["VolumeMA"] = x["Volume"].rolling(20, min_periods=5).mean()
    x["RVOL"] = x["Volume"] / x["VolumeMA"].replace(0, pd.NA)

    # True range is kept simple because the engine's input is already OHLCV.
    prev_close = x["Close"].shift(1)
    tr_components = pd.concat(
        [
            (x["High"] - x["Low"]).abs(),
            (x["High"] - prev_close).abs(),
            (x["Low"] - prev_close).abs(),
        ],
        axis=1,
    )
    x["TR"] = tr_components.max(axis=1)
    x["ATR"] = x["TR"].rolling(14, min_periods=5).mean()

    # Normalised range helps compare candles across price levels.
    x["RangePct"] = x["Range"] / x["Close"].replace(0, pd.NA)

    return x
