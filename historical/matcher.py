import pandas as pd

from candles.patterns import detect_candlestick_patterns


def find_occurrences(
    df: pd.DataFrame,
    pattern_name: str,
    max_bars: int = 1000,
) -> pd.Index:
    """
    Find historical occurrences of a candlestick pattern.

    The scan is bounded so intraday analysis cannot accidentally become an
    unbounded O(n^2) operation on very large datasets.
    """
    if len(df) < 3:
        return pd.Index([])

    start = max(2, len(df) - int(max_bars))
    hits = []

    for i in range(start, len(df)):
        found = detect_candlestick_patterns(df.iloc[: i + 1])
        if any(p.name == pattern_name for p in found):
            hits.append(df.index[i])

    return pd.Index(hits)
