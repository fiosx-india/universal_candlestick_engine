from ..constants import TIMEFRAMES
NATIVE_INTERVALS={"1m","5m","15m","30m","45m","1h","1d","1wk","1mo"}
def normalize_timeframe(tf:str)->str:
    x=tf.strip().upper()
    if x in {"60M","60MIN","1HR"}: return "1H"
    return x
def is_supported(tf:str)->bool:
    return normalize_timeframe(tf) in TIMEFRAMES
