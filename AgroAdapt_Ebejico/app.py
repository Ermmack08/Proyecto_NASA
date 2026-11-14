# Punto de entrada de AgroAdapt Ebéjico.
# Ejecutar desde la raíz del proyecto: streamlit run app.py

import streamlit as st
from modules.data_loader import load_environment
from modules.indicators import summarize_environment

st.set_page_config(
    page_title="AgroAdapt Ebéjico",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos sencillos. Mantenerlos aquí evita dispersar CSS por las páginas.
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {
        background: #f4f7f2; border: 1px solid #dce6d8;
        padding: 12px 14px; border-radius: 10px;
    }
    .project-note {
        padding: 14px; border-left: 4px solid #4d7c0f;
        background: #f5f8f2; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("AgroAdapt Ebéjico")
st.caption("Sistema de apoyo a decisiones para explorar alternativas de rotación de cultivos.")

st.markdown(
    '<div class="project-note"><b>Propósito del prototipo</b><br>'
    'Integrar información territorial, ambiental y agrícola para comparar escenarios '
    'de rotación. Las recomendaciones deben validarse con información local y criterio agronómico.</div>',
    unsafe_allow_html=True,
)

environment = load_environment()
summary = summarize_environment(environment)

st.subheader("Vista general")
c1, c2, c3 = st.columns(3)
c1.metric("Registros ambientales", summary["records"])
c2.metric("Variables disponibles", summary["variables"])
c3.metric("Estado de datos", "Demostración" if summary["is_demo"] else "Datos cargados")

st.subheader("Navegación")
st.write(
    "Utiliza el menú lateral para explorar el territorio, revisar indicadores ambientales, "
    "consultar cultivos y comparar escenarios de rotación."
)

st.info(
    "Importante: los archivos incluidos en esta plantilla son una estructura inicial. "
    "Los registros marcados como demostración no representan mediciones reales de Ebéjico."
)

st.markdown("### Módulos")
col1, col2 = st.columns(2)
with col1:
    st.markdown("- **Territorio:** límites, zonas y capas geográficas.")
    st.markdown("- **Ambiente:** series temporales e indicadores.")
with col2:
    st.markdown("- **Cultivos:** catálogo y requerimientos.")
    st.markdown("- **Rotaciones:** comparación explicable de alternativas.")
