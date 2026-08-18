import streamlit as st
from app.charts import candlestick_chart
from app.components import pattern_table, probability_cards
from api.service import analyze
from constants import TIMEFRAMES

st.set_page_config(page_title="Universal Candlestick Engine", page_icon="🕯️", layout="wide")

st.title("🕯️ Universal Candlestick Engine")
st.caption("Multi-timeframe candlestick & chart-pattern intelligence — probability, not certainty.")

with st.sidebar:
    symbol=st.text_input("Symbol","RELIANCE.NS")
    timeframe=st.selectbox("Timeframe",TIMEFRAMES,index=TIMEFRAMES.index("1D"))
    period=st.selectbox("Data period",["60d","1y","2y","5y"],index=2)
    run=st.button("Analyze",type="primary",use_container_width=True)

if run or "result" not in st.session_state:
    try:
        with st.spinner("Loading market data and scanning patterns..."):
            st.session_state.result=analyze(symbol,timeframe,period)
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()

r=st.session_state.result
c1,c2,c3,c4=st.columns(4)
c1.metric("Symbol",r["symbol"])
c2.metric("Last Price",f"{r['last_price']:,.2f}")
c3.metric("Trend",r["trend"])
c4.metric("Volatility",r["volatility"])

st.subheader("Market Chart")
st.plotly_chart(candlestick_chart(r["data"].tail(300),f"{r['symbol']} — {r['timeframe']}"),use_container_width=True)

st.subheader("Probability")
probability_cards(r["probabilities"])

st.subheader("Detected Patterns")
if r["patterns"]:
    pattern_table(r["patterns"])
else:
    st.info("No qualifying patterns detected on the latest candle/structure window.")

st.subheader("Projection")
p=r["projection"]
st.write(f"**Bias:** {p['direction']}  |  **Upper zone:** {p['upper_zone']:,.2f}  |  **Lower zone:** {p['lower_zone']:,.2f}")
