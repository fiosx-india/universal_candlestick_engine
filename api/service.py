from ..timeframe.engine import load_timeframe
from ..candles.patterns import detect_candlestick_patterns
from ..structures.patterns import detect_structure_patterns
from ..context.trend import trend_state
from ..context.volatility import volatility_state
from ..context.confluence import confluence_score
from ..prediction.probability import probability_from_patterns
from ..prediction.projection import build_projection

def analyze(symbol, timeframe="1D", period="2y"):
    df=load_timeframe(symbol,timeframe,period)
    candle=detect_candlestick_patterns(df,timeframe)
    structure=detect_structure_patterns(df,timeframe)
    patterns=candle+structure
    trend=trend_state(df)
    vol=volatility_state(df)
    probs=probability_from_patterns(patterns,trend)
    projection=build_projection(float(df.Close.iloc[-1]),probs,float(df.get("ATR", (df.High-df.Low).rolling(14).mean()).iloc[-1]))
    return {"data":df,"symbol":symbol,"timeframe":timeframe,"last_price":float(df.Close.iloc[-1]),
            "trend":trend,"volatility":vol,"patterns":patterns,"probabilities":probs,"projection":projection,
            "confluence":confluence_score(patterns,trend)}
