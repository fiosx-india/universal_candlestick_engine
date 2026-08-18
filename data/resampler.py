import pandas as pd
from ..exceptions import TimeframeError

RULES = {
    "1H":"1h","2H":"2h","3H":"3h","4H":"4h","5H":"5h","6H":"6h","7H":"7h","8H":"8h",
    "1D":"1D","2D":"2D","3D":"3D","4D":"4D","5D":"5D","6D":"6D","7D":"7D","10D":"10D","15D":"15D",
    "1W":"1W","2W":"2W","3W":"3W","4W":"4W",
    "1M":"1ME","2M":"2ME","3M":"3ME","4M":"4ME","5M":"5ME","6M":"6ME",
    "7M":"7ME","8M":"8ME","9M":"9ME","10M":"10ME","11M":"11ME","12M":"12ME",
}

def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if timeframe not in RULES:
        raise TimeframeError(f"Cannot resample timeframe: {timeframe}")
    rule = RULES[timeframe]
    out = df.resample(rule).agg({
        "Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"
    }).dropna(subset=["Open","High","Low","Close"])
    return out
