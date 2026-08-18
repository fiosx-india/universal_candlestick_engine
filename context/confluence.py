def confluence_score(patterns, trend):
    if not patterns: return 0.0
    score=sum(p.confidence for p in patterns)/len(patterns)
    aligned=[p for p in patterns if p.direction==trend]
    if aligned: score=min(1.0, score+0.10)
    return round(score,4)
