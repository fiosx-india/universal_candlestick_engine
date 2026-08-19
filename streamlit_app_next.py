import streamlit as st

from api.service import analyze
from app.charts import candlestick_chart
from app.components import pattern_table, probability_cards
from constants import TIMEFRAMES

st.set_page_config(page_title="Universal Candlestick Engine", page_icon="🕯️", layout="wide")
st.title("🕯️ Universal Candlestick Engine")
st.caption("Multi-timeframe candlestick & market-structure intelligence. Outputs are evidence-based probabilities, not certainty.")

with st.sidebar:
    st.header("Market Input")
    symbol = st.text_input("Symbol", "RELIANCE.NS").strip().upper()
    timeframe = st.selectbox("Timeframe", TIMEFRAMES, index=TIMEFRAMES.index("1D"))
    period = st.selectbox("Historical data", ["60d", "1y", "2y", "5y"], index=2)
    analyze_now = st.button("Analyze Market", type="primary", use_container_width=True)

if analyze_now or "result" not in st.session_state:
    if not symbol:
        st.warning("Enter a valid symbol.")
        st.stop()
    try:
        with st.spinner(f"Analyzing {symbol} on {timeframe}..."):
            st.session_state.result = analyze(symbol=symbol, timeframe=timeframe, period=period)
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.stop()

result = st.session_state.result

st.subheader("Market State")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Symbol", result["symbol"])
c2.metric("Timeframe", result["timeframe"])
c3.metric("Last Price", f"{result['last_price']:,.2f}")
c4.metric("Trend", result["trend"])
c5.metric("Volatility", result["volatility"])

st.subheader("Candlestick Chart")
st.plotly_chart(candlestick_chart(result["data"].tail(300), f"{result['symbol']} — {result['timeframe']}"), use_container_width=True)

st.subheader("Direction Probability")
probability_cards(result["probabilities"])
st.caption("Probability is a model estimate from detected evidence. It is not a guaranteed future-price forecast.")

st.subheader("Confluence")
conf = float(result.get("confluence", 0.0))
st.progress(max(0.0, min(1.0, conf)), text=f"Evidence confluence: {conf:.1%}")

st.subheader("Detected Patterns")
patterns = result.get("patterns", [])
if patterns:
    pattern_table(patterns)
else:
    st.info("No qualifying candlestick or structure pattern was detected on the latest available data.")

st.subheader("Historical Evidence")
historical = result.get("historical_evidence")
if historical:
    h1, h2, h3 = st.columns(3)
    h1.metric("Historical Bullish", f"{historical['bullish']:.1%}")
    h2.metric("Historical Bearish", f"{historical['bearish']:.1%}")
    h3.metric("Historical Sideways", f"{historical['sideways']:.1%}")
else:
    st.info("Not enough matching historical occurrences were available to produce a reliable historical evidence blend.")

st.subheader("Price Projection Zone")
projection = result.get("projection", {})
if projection:
    p1, p2, p3 = st.columns(3)
    p1.metric("Bias", projection.get("direction", "UNKNOWN"))
    p2.metric("Upper Zone", f"{projection.get('upper_zone', 0):,.2f}")
    p3.metric("Lower Zone", f"{projection.get('lower_zone', 0):,.2f}")
    st.caption("Projection zones are volatility-based reference areas, not guaranteed targets.")

with st.expander("Engine Diagnostics"):
    st.write({
        "symbol": result["symbol"],
        "timeframe": result["timeframe"],
        "trend": result["trend"],
        "volatility": result["volatility"],
        "pattern_count": len(patterns),
        "confluence": result.get("confluence", 0.0),
        "historical_evidence_available": bool(historical),
    })
