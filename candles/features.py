import pandas as pd

def add_candle_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["Body"] = (x["Close"] - x["Open"]).abs()
    x["Range"] = (x["High"] - x["Low"]).clip(lower=1e-12)
    x["UpperWick"] = x["High"] - x[["Open","Close"]].max(axis=1)
    x["LowerWick"] = x[["Open","Close"]].min(axis=1) - x["Low"]
    x["BodyRatio"] = x["Body"] / x["Range"]
    x["Bullish"] = x["Close"] > x["Open"]
    x["Bearish"] = x["Close"] < x["Open"]
    x["VolumeMA"] = x["Volume"].rolling(20).mean()
    x["RVOL"] = x["Volume"] / x["VolumeMA"].replace(0, pd.NA)
    x["TR"] = x["Range"]
    x["ATR"] = x["TR"].rolling(14).mean()
    return x
