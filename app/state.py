import streamlit as st

def get_symbol(default="RELIANCE.NS"):
    return st.session_state.get("symbol",default)
