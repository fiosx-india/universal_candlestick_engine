import pandas as pd
from candles.patterns import detect_candlestick_patterns

def test_hammer():
    idx=pd.date_range("2026-01-01",periods=3)
    df=pd.DataFrame({"Open":[10,10,10],"High":[11,11,10.5],"Low":[9,9,7],"Close":[10.5,9.8,10.4],"Volume":[100,100,200]},index=idx)
    names=[p.name for p in detect_candlestick_patterns(df)]
    assert "Hammer" in names
