def test_imports():
    from api.service import analyze
    from candles.patterns import detect_candlestick_patterns
    from structures.patterns import detect_structure_patterns
    assert callable(analyze)
