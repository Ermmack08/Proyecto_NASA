import streamlit as st

def render_metric(label, value, help_text=None):

    st.metric(
        label=label,
        value=value,
        help=help_text
    )