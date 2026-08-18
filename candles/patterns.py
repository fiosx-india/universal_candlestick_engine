import pandas as pd
from .features import add_candle_features
from ..models import PatternResult

def detect_candlestick_patterns(df: pd.DataFrame, timeframe: str = "") -> list[PatternResult]:
    x = add_candle_features(df)
    if len(x) < 3: return []
    r = x.iloc[-1]
    p = x.iloc[-2]
    body = max(float(r.Body), 1e-12)
    patterns = []

    def add(name, direction, confidence, **details):
        patterns.append(PatternResult(name, direction, "CONFIRMED", confidence, confidence, timeframe, details))

    if r.BodyRatio <= 0.10:
        add("Doji","SIDEWAYS",0.65, body_ratio=float(r.BodyRatio))
    if r.LowerWick >= 2*body and r.UpperWick <= 0.5*body:
        add("Hammer","BULLISH",0.72, lower_wick=float(r.LowerWick), upper_wick=float(r.UpperWick))
    if r.UpperWick >= 2*body and r.LowerWick <= 0.5*body:
        add("Shooting Star","BEARISH",0.72, lower_wick=float(r.LowerWick), upper_wick=float(r.UpperWick))
    if r.Bullish and p.Bearish and r.Close >= p.Open and r.Open <= p.Close:
        add("Bullish Engulfing","BULLISH",0.80)
    if r.Bearish and p.Bullish and r.Close <= p.Open and r.Open >= p.Close:
        add("Bearish Engulfing","BEARISH",0.80)
    if r.Bullish and r.BodyRatio >= 0.95:
        add("Bullish Marubozu","BULLISH",0.76)
    if r.Bearish and r.BodyRatio >= 0.95:
        add("Bearish Marubozu","BEARISH",0.76)
    if r.High < p.High and r.Low > p.Low:
        add("Inside Bar","SIDEWAYS",0.64)
    if len(x) >= 4:
        a,b,c = x.iloc[-3], x.iloc[-2], x.iloc[-1]
        if a.Bearish and b.BodyRatio < 0.5 and c.Bullish and c.Close > (a.Open+a.Close)/2:
            add("Morning Star","BULLISH",0.74)
        if a.Bullish and b.BodyRatio < 0.5 and c.Bearish and c.Close < (a.Open+a.Close)/2:
            add("Evening Star","BEARISH",0.74)
    if len(x) >= 4 and all(x.iloc[-i].Bullish for i in (3,2,1)) and r.Bearish and r.Close < x.iloc[-2].Open:
        add("Three Line Strike","BEARISH",0.62)
    return patterns
