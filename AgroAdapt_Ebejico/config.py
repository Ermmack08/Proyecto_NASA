
# ============================================================
# CONFIGURACIÓN CENTRAL DEL PROYECTO AGROADAPT
# ============================================================
# Este archivo centraliza las rutas, los parámetros generales
# y la identidad visual de la aplicación.
#
# Las demás páginas deben importar estos valores en lugar
# de definirlos nuevamente.
# ============================================================

from pathlib import Path


# ------------------------------------------------------------
# 1. RUTAS DEL PROYECTO
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
GEOGRAPHIC_DIR = DATA_DIR / "geographic"


# ------------------------------------------------------------
# 2. ARCHIVOS DE DATOS
# ------------------------------------------------------------

BOUNDARY_FILE = GEOGRAPHIC_DIR / "ebejico_boundary.geojson"
ZONES_FILE = GEOGRAPHIC_DIR / "agricultural_zones.geojson"

ENVIRONMENT_FILE = PROCESSED_DIR / "environment_nasa_power.csv"
ENVIRONMENT_DEMO_FILE = PROCESSED_DIR / "environment_demo.csv"
CROPS_FILE = PROCESSED_DIR / "crops_catalog.csv"
CROP_HISTORY_FILE = PROCESSED_DIR / "eva_ebejico.csv"
SATELLITE_METADATA_FILE = RAW_DIR / "satellite_layers_metadata.json"
SATELLITE_RASTER_FILES = {
    "sentinel2_ndvi": PROCESSED_DIR / "sentinel2_ndvi.tif",
    "sentinel2_rgb": PROCESSED_DIR / "sentinel2_rgb.tif",
    "nasadem_elevation": PROCESSED_DIR / "nasadem_elevation.tif",
    "nasadem_slope": PROCESSED_DIR / "nasadem_slope.tif",
}


# ------------------------------------------------------------
# 3. IDENTIDAD DEL PROYECTO
# ------------------------------------------------------------

APP_NAME = "AgroAdapt Ebéjico"

APP_DESCRIPTION = (
    "Sistema de apoyo a decisiones agrícolas mediante "
    "el análisis de datos ambientales y geoespaciales."
)

# Logo opcional ubicado en la carpeta principal del proyecto.
# Si todavía no existe, la aplicación podrá funcionar sin él.
LOGO_FILE = BASE_DIR / "logoRoboticados.png"


# ------------------------------------------------------------
# 4. PALETA DE COLORES
# ------------------------------------------------------------

COLORS = {
    "primary": "#244D3B",
    "secondary": "#6D9775",
    "light_green": "#E8F0E8",
    "accent": "#D8A34A",
    "dark": "#263238",
    "background": "#F5F7F4",
    "white": "#FFFFFF",
    "muted": "#718078",
    "border": "#DCE5DD"
}


# ------------------------------------------------------------
# 5. CONFIGURACIÓN DEL MAPA
# ------------------------------------------------------------

# Centro aproximado únicamente para encuadrar el mapa cuando
# todavía no hay geometría disponible.
# No representa un límite oficial ni debe utilizarse
# para análisis espacial.

MAP_DEFAULT_CENTER = [6.325, -75.768]
MAP_DEFAULT_ZOOM = 11


# ------------------------------------------------------------
# 6. IDENTIFICACIÓN DE DATOS DE DEMOSTRACIÓN
# ------------------------------------------------------------

# Identifica explícitamente los datos creados para pruebas
# de interfaz y desarrollo.

DEMO_DATA_LABEL = "Datos sintéticos de demostración"
