def direction_for_pattern(name: str) -> str:
    if any(k in name for k in ["Bearish","Shooting","Evening"]): return "BEARISH"
    if any(k in name for k in ["Bullish","Hammer","Morning"]): return "BULLISH"
    return "SIDEWAYS"
