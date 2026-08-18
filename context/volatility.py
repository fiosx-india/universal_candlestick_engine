def volatility_state(df):
    if len(df) < 30: return "UNKNOWN"
    r=df["High"]-df["Low"]
    cur=r.rolling(14).mean().iloc[-1]
    base=r.rolling(30).mean().iloc[-1]
    if cur > base*1.5: return "EXPANDING"
    if cur < base*.7: return "CONTRACTING"
    return "NORMAL"
