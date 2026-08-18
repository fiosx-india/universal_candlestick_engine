import pandas as pd

def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).title() for c in out.columns]
    required = ["Open","High","Low","Close","Volume"]
    for c in required:
        if c not in out:
            raise ValueError(f"Missing OHLCV column: {c}")
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=required)
    out.index = pd.to_datetime(out.index)
    return out.sort_index()
