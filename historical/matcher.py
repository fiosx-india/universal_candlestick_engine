import pandas as pd
from ..candles.patterns import detect_candlestick_patterns

def find_occurrences(df: pd.DataFrame, pattern_name: str) -> pd.Index:
    hits=[]
    for i in range(2,len(df)):
        sub=df.iloc[:i+1]
        found=detect_candlestick_patterns(sub)
        if any(p.name==pattern_name for p in found):
            hits.append(df.index[i])
    return pd.Index(hits)
