# Carga y validación básica de datos.
# Aquí se conectarán posteriormente los archivos reales entregados por el equipo GIS
# y el equipo de investigación agrícola.

import json
import pandas as pd
import streamlit as st
from config import BOUNDARY_FILE, ENVIRONMENT_FILE, CROPS_FILE, ZONES_FILE

@st.cache_data
def load_environment():
    """Carga la tabla ambiental procesada. Devuelve DataFrame vacío si no existe."""
    if not ENVIRONMENT_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(ENVIRONMENT_FILE, parse_dates=["date"])

@st.cache_data
def load_crops():
    """Carga el catálogo de cultivos. Completarlo con fuentes locales verificadas."""
    if not CROPS_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(CROPS_FILE)

@st.cache_data
def load_geojson(path):
    """Lee un GeoJSON y devuelve None si no está disponible o no es válido."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None

def load_boundary():
    """Límite municipal oficial de Ebéjico, cuando el equipo GIS lo incorpore."""
    return load_geojson(BOUNDARY_FILE)

def load_zones():
    """Zonas agroambientales o unidades de análisis; no asumir que son veredas."""
    return load_geojson(ZONES_FILE)
