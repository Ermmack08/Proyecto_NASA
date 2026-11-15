"""Calcula NDVI a partir de bandas GeoTIFF previamente descargadas.

Ejemplo Sentinel-2 L2A:
- data/raw/sentinel/B08.tif (NIR)
- data/raw/sentinel/B04.tif (rojo)
Asegúrate de que ambas bandas correspondan a la misma escena/fecha y estén
en reflectancia de superficie, con píxeles nublados/nodata enmascarados.
"""
import sys
from pathlib import Path
# Permite ejecutar este script desde la raíz con: python scripts/NOMBRE.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modules.gis.satellite import calculate_ndvi
from modules.gis.raster_utils import clip_raster_to_boundary
from config import RAW_DIR, PROCESSED_DIR, BOUNDARY_FILE

if __name__ == "__main__":
    nir = RAW_DIR / "sentinel" / "B08.tif"
    red = RAW_DIR / "sentinel" / "B04.tif"
    ndvi = PROCESSED_DIR / "vegetation" / "sentinel2_ndvi.tif"
    calculate_ndvi(nir, red, ndvi)
    clip_raster_to_boundary(ndvi, BOUNDARY_FILE,
                            PROCESSED_DIR / "vegetation" / "sentinel2_ndvi_ebejico.tif")
    print("NDVI Sentinel-2 procesado.")
