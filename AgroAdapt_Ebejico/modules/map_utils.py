# Funciones para construir mapas interactivos con Folium.
# El mapa puede mostrar GeoJSON municipal, zonas y capas vectoriales procesadas.
# Para rásteres (NDVI, temperatura superficial, etc.) se recomienda preparar mosaicos
# o tiles previamente; no cargar imágenes satelitales pesadas en cada interacción.

import folium
import streamlit as st
from streamlit_folium import st_folium
from config import MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM

def build_base_map(boundary=None, zones=None):
    """Crea mapa base y añade las geometrías disponibles."""
    map_object = folium.Map(
        location=MAP_DEFAULT_CENTER,
        zoom_start=MAP_DEFAULT_ZOOM,
        tiles="CartoDB positron",
        control_scale=True,
    )

    if boundary:
        folium.GeoJson(
            boundary,
            name="Límite municipal",
            style_function=lambda feature: {
                "color": "#245c35", "weight": 3, "fillOpacity": 0.05
            },
            tooltip="Límite municipal (verificar fuente y fecha)",
        ).add_to(map_object)

    if zones:
        folium.GeoJson(
            zones,
            name="Zonas de análisis",
            style_function=lambda feature: {
                "color": "#b45309", "weight": 2, "fillOpacity": 0.18
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name"] if zones.get("features") and
                "name" in zones["features"][0].get("properties", {}) else [],
                aliases=["Zona:"],
            ) if zones.get("features") and
                 "name" in zones["features"][0].get("properties", {}) else None,
        ).add_to(map_object)

    folium.LayerControl(collapsed=False).add_to(map_object)
    return map_object

def render_map(map_object, height=580, key="agroadapt_map"):
    """Renderiza Folium en Streamlit y devuelve la interacción del usuario."""
    return st_folium(map_object, height=height, width=None, key=key)
