# Página 2: variables ambientales y series temporales.
# El equipo de datos debe entregar una tabla procesada con fecha, variables, unidades y fuente.

import streamlit as st
import plotly.express as px
from modules.data_loader import load_environment
from modules.indicators import monthly_summary

st.set_page_config(page_title="Ambiente | AgroAdapt", layout="wide")
st.title("Condiciones ambientales")

df = load_environment()
if df.empty:
    st.warning("No hay datos ambientales. Incorpora un CSV procesado en data/processed.")
    st.stop()

if "is_demo" in df and df["is_demo"].astype(str).str.lower().isin(["true", "1"]).any():
    st.warning("La tabla contiene datos sintéticos para demostración; no son mediciones reales.")

st.caption("Consulta tendencias temporales. Revisa siempre la unidad, resolución y fuente.")
summary = monthly_summary(df)

numeric_cols = [c for c in df.select_dtypes(include="number").columns if c != "is_demo"]
if not numeric_cols:
    st.info("No se encontraron variables numéricas para graficar.")
else:
    selected = st.selectbox("Variable ambiental", numeric_cols)
    unit = st.text_input("Unidad de la variable", value="Consultar metadatos")
    if "date" in df:
        fig = px.line(df, x="date", y=selected, markers=True,
                      title=f"Evolución de {selected}")
        st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Unidad declarada: {unit}")

st.subheader("Datos y procedencia")
st.dataframe(df, use_container_width=True)
st.info("Añade metadatos de fuente, resolución espacial, cobertura temporal y método de procesamiento.")
