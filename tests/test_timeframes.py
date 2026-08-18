from timeframe.registry import is_supported
def test_timeframes():
    assert is_supported("4H")
    assert is_supported("12M")
