def probability_from_patterns(
    patterns,
    trend="SIDEWAYS",
    volatility="NORMAL",
    historical=None,
    confluence=0.0,
):
    """
    Produce a calibrated *evidence distribution*.

    The result remains a probability-like distribution, but it is explicitly
    conservative: candle confidence is blended with trend, volatility and
    historical evidence instead of treating a pattern confidence as truth.
    """
    prior = {"bullish": 1.0 / 3.0, "bearish": 1.0 / 3.0, "sideways": 1.0 / 3.0}

    if not patterns:
        return {k: round(v, 4) for k, v in prior.items()}

    scores = {"bullish": 0.0, "bearish": 0.0, "sideways": 0.0}
    for p in patterns:
        key = p.direction.lower()
        if key in scores:
            scores[key] += max(0.0, min(1.0, float(p.confidence)))

    # Blend, rather than replace, the neutral prior.
    raw = {k: 0.35 * prior[k] + 0.65 * scores[k] for k in scores}

    # Trend is context, not a guaranteed direction.
    if trend == "BULLISH":
        raw["bullish"] += 0.10
        raw["bearish"] -= 0.04
    elif trend == "BEARISH":
        raw["bearish"] += 0.10
        raw["bullish"] -= 0.04

    # Volatility affects uncertainty more than direction.
    if volatility == "EXPANDING":
        raw["sideways"] -= 0.03
    elif volatility == "CONTRACTING":
        raw["sideways"] += 0.05

    # Historical evidence is expected as a dict with the same keys.
    if historical:
        for key in ("bullish", "bearish", "sideways"):
            if key in historical:
                raw[key] = 0.75 * raw[key] + 0.25 * float(historical[key])

    # Confluence is an evidence-strength adjustment.
    raw["bullish"] += 0.05 * float(confluence)
    raw["bearish"] += 0.05 * float(confluence)

    raw = {k: max(0.0, float(v)) for k, v in raw.items()}
    total = sum(raw.values()) or 1.0
    return {k: round(raw[k] / total, 4) for k in raw}
