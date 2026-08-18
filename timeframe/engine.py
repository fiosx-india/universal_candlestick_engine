from ..data.provider import fetch_ohlcv
from ..data.resampler import resample_ohlcv
from ..data.normalizer import normalize_ohlcv
from .registry import normalize_timeframe

def load_timeframe(symbol: str, timeframe: str, period: str = "2y"):
    tf = normalize_timeframe(timeframe)
    if tf in {"1m","5m","15m","30m"}:
        native = tf.lower()
        return normalize_ohlcv(fetch_ohlcv(symbol, period="60d" if tf != "1m" else "7d", interval=native))
    if tf == "45M":
        base = normalize_ohlcv(fetch_ohlcv(symbol, period="60d", interval="15m"))
        return resample_ohlcv(base, "45M") if "45M" in {"45M"} else base
    if tf == "1H":
        return normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1h"))
    if tf == "1D":
        return normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1d"))
    if tf == "1W":
        return normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1wk"))
    if tf == "1M":
        return normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1mo"))
    # Higher synthetic timeframes use a sensible base.
    if tf.endswith("H"):
        base = normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1h"))
    elif tf.endswith("D"):
        base = normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1d"))
    elif tf.endswith("W"):
        base = normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1wk"))
    elif tf.endswith("M"):
        base = normalize_ohlcv(fetch_ohlcv(symbol, period=period, interval="1mo"))
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    return resample_ohlcv(base, tf)
