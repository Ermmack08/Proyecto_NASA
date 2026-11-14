# Página 4: comparador de escenarios de rotación.
# La interfaz utiliza datos demostrativos. En la integración, reemplazar DEMO_ROTATIONS
# por la salida del motor del integrante agrícola, manteniendo el mismo contrato de datos.

import streamlit as st
import pandas as pd
import plotly.express as px
from modules.rotation_model import compare_rotations

st.set_page_config(page_title="Rotaciones | AgroAdapt", layout="wide")
st.title("Comparador de rotaciones")
st.caption("Comparación multicriterio de escenarios; los puntajes de ejemplo son ilustrativos.")

# Datos sintéticos para probar la interfaz. NO son recomendaciones para Ebéjico.
DEMO_ROTATIONS = [
    {
        "name": "Escenario demostrativo A",
        "description": "Secuencia de ejemplo para probar la visualización.",
        "scores": {"climate": 75, "soil": 70, "soil_health": 82, "production": 68, "farmer_priority": 80},
        "limitations": "Puntajes inventados para validar la interfaz; reemplazar con evaluación técnica."
    },
    {
        "name": "Escenario demostrativo B",
        "description": "Segunda secuencia de ejemplo para comparar resultados.",
        "scores": {"climate": 68, "soil": 84, "soil_health": 72, "production": 78, "farmer_priority": 65},
        "limitations": "Puntajes inventados para validar la interfaz; reemplazar con evaluación técnica."
    },
]

# Controles de demostración: luego deben vincularse con zonas y preferencias reales.
zone = st.selectbox("Unidad territorial", ["Municipio completo", "Zona de demostración"])
priority = st.selectbox("Prioridad del agricultor", ["Equilibrio general", "Uso eficiente del agua", "Salud del suelo", "Productividad"])

results = compare_rotations(DEMO_ROTATIONS)
table = pd.DataFrame([{
    "Escenario": r["name"],
    "Puntuación ilustrativa": r["score"],
    "Descripción": r["description"],
} for r in results])

st.subheader("Resultados")
st.dataframe(table, use_container_width=True, hide_index=True)

fig = px.bar(table, x="Escenario", y="Puntuación ilustrativa",
             range_y=[0, 100], title="Comparación de escenarios (datos de demostración)")
st.plotly_chart(fig, use_container_width=True)

for result in results:
    with st.expander(f"{result['name']} — {result['score']}/100"):
        st.write(result["description"])
        st.write("**Criterios evaluados**")
        st.json(result["scores"])
        st.write("**Limitaciones**")
        st.warning(result["limitations"])

st.info(f"Selección actual: {zone}. Prioridad: {priority}. Conecta estos controles al modelo real antes de presentar recomendaciones.")
