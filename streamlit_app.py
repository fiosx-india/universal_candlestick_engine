import streamlit as st
from app.charts import candlestick_chart
from app.components import pattern_table, probability_cards
from api.service import analyze
from constants import TIMEFRAMES

st.set_page_config(page_title="Universal Candlestick Engine", page_icon="🕯️", layout="wide")

st.title("🕯️ Universal Candlestick Engine")
st.caption("Multi-timeframe candlestick & chart-pattern intelligence — probability, not certainty.")

with st.sidebar:

    st.header("Market Input")

    exchange = st.selectbox(
        "Exchange",
        [
            "NSE",
            "BSE",
            "MCX",
            "NFO",
            "BFO",
            "CDS",
        ],
        index=0,
    )

    search_query = st.text_input(
        "Search Instrument",
        placeholder="RELIANCE / TCS / GOLD / CRUDEOIL",
    ).strip().upper()

    search_button = st.button(
        "Search Instrument",
        type="secondary",
        width="stretch",
    )

    # --------------------------------------------------------
    # Angel One instrument search
    # --------------------------------------------------------

    if search_button:

        if not search_query:
            st.warning("Enter an instrument name.")
            st.stop()

        try:

            # Uses the existing Angel One authentication.
            registry_client = AngelOneDataClient(
                symbol="NIFTY",
                exchange=exchange,
            )

            search_results = registry_client.search_instruments(
                exchange=exchange,
                query=search_query,
                limit=50,
            )

            st.session_state["instrument_results"] = search_results
            st.session_state["instrument_exchange"] = exchange

        except Exception as exc:

            st.error(
                f"Instrument search failed: {exc}"
            )

            st.session_state["instrument_results"] = []


    results = st.session_state.get(
        "instrument_results",
        [],
    )

    if results:

        labels = []

        for item in results:

            labels.append(
                f"{item['tradingsymbol']} "
                f"• {item['exchange']} "
                f"• Token {item['symboltoken']}"
            )

        selected_index = st.selectbox(
            "Select Instrument",
            range(len(results)),
            format_func=lambda i: labels[i],
        )

        selected_instrument = results[selected_index]

        st.session_state["selected_instrument"] = (
            selected_instrument
        )

        st.success(
            f"Selected: "
            f"{selected_instrument['tradingsymbol']}"
        )


    timeframe = st.selectbox(
        "Timeframe",
        TIMEFRAMES,
        index=TIMEFRAMES.index("1D"),
    )

    period = st.selectbox(
        "Historical data",
        ["60d", "1y", "2y", "5y"],
        index=2,
    )

    analyze_now = st.button(
        "Analyze Market",
        type="primary",
        width="stretch",
    )

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
