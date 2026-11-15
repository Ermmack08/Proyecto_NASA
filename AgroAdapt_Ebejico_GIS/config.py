"""Configuración compartida. Mantiene rutas compatibles con AgroAdapt_Ebejico."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
GEOGRAPHIC_DIR = DATA_DIR / "geographic"
OUTPUTS_DIR = BASE_DIR / "outputs"

BOUNDARY_FILE = GEOGRAPHIC_DIR / "ebejico_boundary.geojson"
ZONES_FILE = GEOGRAPHIC_DIR / "agricultural_zones.geojson"

# Ebéjico: EPSG:32618 es una proyección métrica UTM apropiada para cálculos locales.
# Se conserva EPSG:4326 para intercambio GeoJSON y visualización web.
ANALYSIS_CRS = "EPSG:32618"
WEB_CRS = "EPSG:4326"
DANE_CODE = "05240"
IGAC_LAYER_QUERY_URL = (
    "https://sigi.igac.gov.co/dip/rest/services/Limites/MapServer/0/query"
)
