def probability_from_patterns(patterns, trend="SIDEWAYS"):
    if not patterns:
        return {"bullish":.33,"bearish":.33,"sideways":.34}
    bull=sum(p.confidence for p in patterns if p.direction=="BULLISH")
    bear=sum(p.confidence for p in patterns if p.direction=="BEARISH")
    side=sum(p.confidence for p in patterns if p.direction=="SIDEWAYS")
    total=bull+bear+side or 1
    return {"bullish":round(bull/total,4),"bearish":round(bear/total,4),"sideways":round(side/total,4)}
