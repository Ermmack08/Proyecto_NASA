# Configuración central del proyecto.
# Sustituir rutas y parámetros aquí; evitar escribir rutas absolutas en las páginas.

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
GEOGRAPHIC_DIR = DATA_DIR / "geographic"

BOUNDARY_FILE = GEOGRAPHIC_DIR / "ebejico_boundary.geojson"
ZONES_FILE = GEOGRAPHIC_DIR / "agricultural_zones.geojson"
ENVIRONMENT_FILE = PROCESSED_DIR / "environment_demo.csv"
ENVIRONMENTAL_INDICATORS_FILE = PROCESSED_DIR / "environmental_indicators.csv"
CROPS_FILE = PROCESSED_DIR / "crops_catalog.csv"
AGRONOMIC_REFERENCES_FILE = PROCESSED_DIR / "agronomic_reference_records.csv"

# Centro aproximado únicamente para encuadrar el mapa cuando todavía no hay geometría.
# No es un límite oficial ni debe utilizarse para análisis espacial.
MAP_DEFAULT_CENTER = [6.325, -75.768]
MAP_DEFAULT_ZOOM = 11

# Identifica explícitamente los datos creados para pruebas de interfaz.
DEMO_DATA_LABEL = "Datos sintéticos de demostración"
