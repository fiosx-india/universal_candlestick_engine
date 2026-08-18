def build_projection(last_price, probabilities, atr=None):
    p=probabilities
    edge=p["bullish"]-p["bearish"]
    width=(atr or last_price*0.02)
    return {
        "direction":"BULLISH" if edge>.10 else "BEARISH" if edge<-.10 else "SIDEWAYS",
        "upper_zone":last_price+width,
        "lower_zone":max(0,last_price-width),
        "edge":edge
    }
