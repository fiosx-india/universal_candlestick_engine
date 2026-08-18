import pandas as pd
from structures.patterns import detect_structure_patterns
def test_structure_runs():
    idx=pd.date_range("2026-01-01",periods=60)
    c=pd.Series(range(60),index=idx,dtype=float)
    df=pd.DataFrame({"Open":c,"High":c+1,"Low":c-1,"Close":c,"Volume":1000},index=idx)
    assert isinstance(detect_structure_patterns(df),list)
