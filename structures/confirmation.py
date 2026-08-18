def confirm_pattern(pattern, df):
    if len(df) < 2:
        return pattern
    close=float(df["Close"].iloc[-1])
    prev=float(df["Close"].iloc[-2])
    if pattern.direction=="BULLISH" and close >= prev:
        pattern.state="CONFIRMED"
    elif pattern.direction=="BEARISH" and close <= prev:
        pattern.state="CONFIRMED"
    return pattern
