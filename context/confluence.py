def confluence_score(patterns, trend, volatility="NORMAL", rvol=None):
    """
    Combine independent evidence without allowing one candle pattern to
    dominate the whole score.

    Returns a 0..1 evidence score. It is not a probability.
    """
    if not patterns:
        return 0.0

    base = sum(float(p.confidence) for p in patterns) / len(patterns)

    aligned = [p for p in patterns if p.direction == trend]
    opposed = [p for p in patterns if p.direction in {"BULLISH", "BEARISH"} and p.direction != trend]

    score = base
    if aligned:
        score += 0.10
    if opposed:
        score -= 0.06

    if volatility == "EXPANDING":
        # Expanding volatility increases movement risk, not direction certainty.
        score += 0.02 if aligned else 0.0
    elif volatility == "CONTRACTING":
        score -= 0.02

    if rvol is not None:
        try:
            rv = float(rvol)
            if rv >= 1.5 and aligned:
                score += 0.04
            elif rv < 0.7:
                score -= 0.02
        except (TypeError, ValueError):
            pass

    return round(max(0.0, min(1.0, score)), 4)
