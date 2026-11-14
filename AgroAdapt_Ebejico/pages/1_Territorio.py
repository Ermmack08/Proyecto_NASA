# Página 1: mapa territorial.
# El integrante GIS debe entregar el límite municipal y, si existen, las zonas de análisis
# en formato GeoJSON (coordenadas en WGS84 / EPSG:4326).

import streamlit as st
from modules.data_loader import load_boundary, load_zones
from modules.map_utils import build_base_map, render_map

st.set_page_config(page_title="Territorio | AgroAdapt", layout="wide")
st.title("Diagnóstico territorial")
st.caption("Exploración geográfica del municipio y de las unidades espaciales disponibles.")

boundary = load_boundary()
zones = load_zones()

if boundary is None:
    st.warning("Aún no se ha incorporado el GeoJSON oficial del límite municipal.")
if zones is None:
    st.info("Las zonas agroambientales todavía no están disponibles. Se mostrará el mapa base.")

map_object = build_base_map(boundary=boundary, zones=zones)
interaction = render_map(map_object)

with st.expander("Información para integrar capas"):
    st.markdown("""
    - Límite municipal: `data/geographic/ebejico_boundary.geojson`.
    - Zonas de análisis: `data/geographic/agricultural_zones.geojson`.
    - Usar geometrías oficiales y registrar fuente, fecha, escala y sistema de coordenadas.
    - No interpretar el mapa base como evidencia de límites o aptitud agrícola.
    """)
