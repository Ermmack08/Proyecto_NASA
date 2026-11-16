#encabezados de las páginas 
import streamlit as st

def render_header(title, description):

    st.title(title)

    st.caption(description)

    st.divider()