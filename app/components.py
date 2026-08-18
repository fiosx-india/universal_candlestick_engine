import streamlit as st

def pattern_table(patterns):
    rows=[{"Pattern":p.name,"Direction":p.direction,"State":p.state,"Confidence":f"{p.confidence:.0%}"} for p in patterns]
    st.dataframe(rows, use_container_width=True)

def probability_cards(p):
    a,b,c=st.columns(3)
    a.metric("Bullish",f"{p['bullish']:.0%}")
    b.metric("Bearish",f"{p['bearish']:.0%}")
    c.metric("Sideways",f"{p['sideways']:.0%}")
