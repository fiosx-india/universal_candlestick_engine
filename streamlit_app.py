import streamlit as st

from app.charts import candlestick_chart
from app.components import (
    pattern_table,
    probability_cards,
)

from api.service import analyze
from constants import TIMEFRAMES


st.set_page_config(
    page_title="Universal Candlestick Engine",
    page_icon="🕯️",
    layout="wide",
)


st.title(
    "🕯️ Universal Candlestick Engine"
)

st.caption(
    "Multi-timeframe candlestick & "
    "chart-pattern intelligence — "
    "probability, not certainty."
)

# ============================================================
# RESET INSTRUMENT STATE WHEN EXCHANGE CHANGES
# ============================================================

def _reset_instrument_selection():
    """
    Exchange மாற்றப்பட்டவுடன் பழைய search result,
    selected instrument மற்றும் previous analysis-ஐ clear செய்கிறது.
    """

    st.session_state.pop(
        "instrument_results",
        None,
    )

    st.session_state.pop(
        "selected_instrument",
        None,
    )

    st.session_state.pop(
        "result",
        None,
    )

# ============================================================
# MARKET INPUT
# ============================================================

with st.sidebar:

    st.header(
        "Market Input"
    )

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
        placeholder=(
            "RELIANCE / TCS / "
            "GOLD / CRUDEOIL"
        ),
    ).strip().upper()

    search_button = st.button(
        "Search Instrument",
        type="secondary",
        use_container_width=True,
    )


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search_button:

        if not search_query:

            st.warning(
                "Enter an instrument name."
            )

        else:

            try:

                from data.angel_one import (
                    AngelOneDataClient
                )
                
                import os


                def get_secret(name):
                    """
                    Read credentials from Streamlit Secrets first,
                    then fall back to environment variables.
                    """

                    try:
                        value = st.secrets.get(name)

                        if value:
                            return str(value).strip()

                    except Exception:
                        pass

                    value = os.getenv(name)

                    if value:
                        return str(value).strip()

                    return ""


                client = (
                    AngelOneDataClient(
                        api_key=get_secret(
                            "ANGEL_API_KEY"
                        ),
                        client_code=get_secret(
                            "ANGEL_CLIENT_CODE"
                        ),
                        mpin=get_secret(
                            "ANGEL_MPIN"
                        ),
                        totp_secret=get_secret(
                            "ANGEL_TOTP_SECRET"
                        ),
                    )
                )

                results = (
                    client.search_instruments(
                        exchange=exchange,
                        query=search_query,
                        limit=50,
                    )
                )

                st.session_state[
                    "instrument_results"
                ] = results

            except Exception as exc:

                st.error(
                    f"Instrument search failed: {exc}"
                )

                st.session_state[
                    "instrument_results"
                ] = []


    results = st.session_state.get(
        "instrument_results",
        [],
    )


    # --------------------------------------------------------
    # SELECT RESULT
    # --------------------------------------------------------

    if results:

        labels = [
            (
                f"{item['tradingsymbol']} "
                f"• {item['exchange']} "
                f"• Token "
                f"{item['symboltoken']}"
            )
            for item in results
        ]

        selected_index = st.selectbox(
            "Select Instrument",
            range(
                len(results)
            ),
            format_func=lambda i: labels[i],
        )

        selected = results[
            selected_index
        ]

        st.session_state[
            "selected_instrument"
        ] = selected

        st.success(
            "Selected: "
            f"{selected['tradingsymbol']}"
        )


    # --------------------------------------------------------
    # TIMEFRAME
    # --------------------------------------------------------

    timeframe = st.selectbox(
        "Timeframe",
        TIMEFRAMES,
        index=TIMEFRAMES.index(
            "1D"
        ),
    )


    # --------------------------------------------------------
    # HISTORICAL PERIOD
    # --------------------------------------------------------

    period = st.selectbox(
        "Historical data",
        [
            "60d",
            "1y",
            "2y",
            "5y",
        ],
        index=2,
    )


    analyze_now = st.button(
        "Analyze Market",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# SELECTED INSTRUMENT
# ============================================================

selected_instrument = (
    st.session_state.get(
        "selected_instrument"
    )
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_now:

    if not selected_instrument:

        st.warning(
            "Search and select an instrument first."
        )

        st.stop()


    # Angel One trading symbol is the
    # canonical symbol used by analysis.

    symbol = selected_instrument[
        "tradingsymbol"
    ]


    try:

        with st.spinner(
            "Loading market data and "
            "scanning patterns..."
        ):

            result = analyze(
                selected_instrument,
                timeframe,
                period,
            )

            st.session_state[
                "result"
            ] = result

    except Exception as exc:

        st.error(
            f"Analysis failed: {exc}"
        )

        st.stop()


# ============================================================
# RESULT
# ============================================================

if "result" not in st.session_state:

    st.info(
        "Search an instrument and "
        "click Analyze Market."
    )

    st.stop()


r = st.session_state[
    "result"
]


# ============================================================
# SUMMARY
# ============================================================

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Symbol",
    r["symbol"],
)

c2.metric(
    "Last Price",
    f"{r['last_price']:,.2f}",
)

c3.metric(
    "Trend",
    r["trend"],
)

c4.metric(
    "Volatility",
    r["volatility"],
)


# ============================================================
# CHART
# ============================================================

st.subheader(
    "Market Chart"
)

st.plotly_chart(
    candlestick_chart(
        r["data"].tail(300),
        (
            f"{r['symbol']} "
            f"— {r['timeframe']}"
        ),
    ),
    use_container_width=True,
)


# ============================================================
# PROBABILITY
# ============================================================

st.subheader(
    "Probability"
)

probability_cards(
    r["probabilities"]
)


# ============================================================
# PATTERNS
# ============================================================

st.subheader(
    "Detected Patterns"
)

if r["patterns"]:

    pattern_table(
        r["patterns"]
    )

else:

    st.info(
        "No qualifying patterns detected "
        "on the latest candle/structure window."
    )


# ============================================================
# PROJECTION
# ============================================================

st.subheader(
    "Projection"
)

p = r["projection"]

st.write(
    f"**Bias:** {p['direction']}  |  "
    f"**Upper zone:** "
    f"{p['upper_zone']:,.2f}  |  "
    f"**Lower zone:** "
    f"{p['lower_zone']:,.2f}"
)
