import streamlit as st

def pattern_table(patterns):
    rows = []

    for p in patterns:
        if isinstance(p, dict):
            confidence = float(p.get("confidence", 0.0))

            rows.append({
                "Pattern": p.get("name", ""),
                "Direction": p.get("direction", ""),
                "State": p.get("state", ""),
                "Confidence": f"{confidence:.0%}",
            })
        else:
            rows.append({
                "Pattern": p.name,
                "Direction": p.direction,
                "State": p.state,
                "Confidence": f"{p.confidence:.0%}",
            })

    st.dataframe(
        rows,
        width="stretch",
    )

def probability_cards(p):
    """
    Display the engine's direction probability distribution.

    Expected keys:
        bullish
        bearish
        sideways

    The function also safely handles missing values so a malformed
    probability payload does not crash the entire Streamlit application.
    """

    bullish = float(p.get("bullish", 0.0))
    bearish = float(p.get("bearish", 0.0))
    sideways = float(p.get("sideways", 0.0))

    # Keep displayed values inside a valid probability range.
    bullish = max(0.0, min(1.0, bullish))
    bearish = max(0.0, min(1.0, bearish))
    sideways = max(0.0, min(1.0, sideways))

    a, b, c = st.columns(3)

    a.metric(
        "Bullish",
        f"{bullish:.0%}",
    )

    b.metric(
        "Bearish",
        f"{bearish:.0%}",
    )

    c.metric(
        "Sideways",
        f"{sideways:.0%}",
    )
