from timeframe.engine import load_timeframe
from candles.patterns import detect_candlestick_patterns
from structures.patterns import detect_structure_patterns
from candles.features import add_candle_features
from context.trend import trend_state
from context.volatility import volatility_state
from context.confluence import confluence_score
from historical.matcher import find_occurrences
from historical.outcomes import forward_outcomes
from prediction.probability import probability_from_patterns
from prediction.projection import build_projection


def _historical_summary(df, patterns):
    """Return conservative aggregated historical evidence for current patterns."""
    if not patterns:
        return None

    bull = bear = side = weight = 0.0
    # Daily horizons are the least surprising common denominator across
    # intraday/daily datasets. Detailed outcomes are returned separately.
    for pattern in patterns[:5]:
        try:
            occurrences = find_occurrences(df, pattern.name, max_bars=800)
            outcome = forward_outcomes(df, occurrences, "1D")
        except Exception:
            outcome = None

        if not outcome or outcome["samples"] < 5:
            continue

        w = min(1.0, outcome["samples"] / 30.0)
        bull += outcome["bullish_probability"] * w
        bear += outcome["bearish_probability"] * w
        side += outcome["sideways_probability"] * w
        weight += w

    if weight == 0:
        return None

    return {
        "bullish": bull / weight,
        "bearish": bear / weight,
        "sideways": side / weight,
    }


def analyze(symbol, timeframe="1D", period="2y"):
    df = load_timeframe(symbol, timeframe, period)
    features = add_candle_features(df)

    candle = detect_candlestick_patterns(features, timeframe)
    structure = detect_structure_patterns(features, timeframe)
    patterns = candle + structure

    trend = trend_state(features)
    volatility = volatility_state(features)

    latest_rvol = features["RVOL"].iloc[-1] if "RVOL" in features else None
    confluence = confluence_score(patterns, trend, volatility, latest_rvol)
    historical = _historical_summary(features, patterns)

    probs = probability_from_patterns(
        patterns,
        trend=trend,
        volatility=volatility,
        historical=historical,
        confluence=confluence,
    )

    atr = float(features["ATR"].iloc[-1]) if "ATR" in features and features["ATR"].notna().any() else None
    last_price = float(features["Close"].iloc[-1])
    projection = build_projection(last_price, probs, atr)

    return {
        "data": features,
        "symbol": symbol,
        "timeframe": timeframe,
        "last_price": last_price,
        "trend": trend,
        "volatility": volatility,
        "patterns": patterns,
        "probabilities": probs,
        "projection": projection,
        "confluence": confluence,
        "historical_evidence": historical,
    }
