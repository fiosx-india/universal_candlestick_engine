def trend_state(df):
    if len(df) < 50: return "UNKNOWN"
    close=df["Close"]
    fast=close.rolling(20).mean().iloc[-1]
    slow=close.rolling(50).mean().iloc[-1]
    if fast > slow*1.002: return "BULLISH"
    if fast < slow*0.998: return "BEARISH"
    return "SIDEWAYS"
