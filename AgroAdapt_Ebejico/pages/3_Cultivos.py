# Página 3: catálogo agrícola.
# Los cultivos deben confirmarse con EVA/UPRA, UMATA, productores u otras fuentes locales.
# Los campos agronómicos no deben rellenarse con valores supuestos.

import streamlit as st
from modules.data_loader import load_crops

st.set_page_config(page_title="Cultivos | AgroAdapt", layout="wide")
st.title("Catálogo de cultivos")

crops = load_crops()
if crops.empty:
    st.warning("El catálogo está vacío. Completa crops_catalog.csv con información verificada.")
    st.stop()

if "crop" not in crops:
    st.error("El CSV debe incluir una columna llamada 'crop'.")
    st.stop()

selected_crop = st.selectbox("Selecciona un cultivo", sorted(crops["crop"].dropna().unique()))
record = crops[crops["crop"] == selected_crop].iloc[0]

st.subheader(selected_crop)
left, right = st.columns(2)
with left:
    for field in ["family", "cycle", "water_requirement", "root_depth"]:
        if field in record.index:
            st.write(f"**{field}:** {record[field]}")
with right:
    for field in ["soil_requirements", "nutritional_notes", "rotation_notes", "source"]:
        if field in record.index:
            st.write(f"**{field}:** {record[field]}")

st.caption("Cada ficha debe conservar la fuente y diferenciar datos locales de referencias generales.")
st.dataframe(crops, use_container_width=True)
