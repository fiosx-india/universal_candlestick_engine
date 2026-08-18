import pandas as pd
import yfinance as yf
from ..exceptions import DataError

def fetch_ohlcv(symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    except Exception as exc:
        raise DataError(str(exc)) from exc
    if df is None or df.empty:
        raise DataError(f"No market data returned for {symbol} / {interval}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    cols = ["Open","High","Low","Close","Volume"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise DataError(f"Missing columns: {missing}")
    return df[cols].dropna()
