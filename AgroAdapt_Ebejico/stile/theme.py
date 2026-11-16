import streamlit as st

def apply_theme():

    st.markdown("""
    <style>

    /* Fondo principal */
    .stApp {
        background-color: #F5F7F4;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #244D3B;
    }

    /* Texto general */
    p, label {
        color: #263238;
    }

    /* Contenedor principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    </style>
    """, unsafe_allow_html=True)