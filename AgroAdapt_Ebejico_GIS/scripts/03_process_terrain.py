"""Recorta un DEM al municipio y calcula pendiente.

Coloca el DEM original en data/raw/srtm/ebejico_dem.tif.
El DEM debe tener CRS definido. Para pendiente debe estar en CRS métrico.
"""
import sys
from pathlib import Path
# Permite ejecutar este script desde la raíz con: python scripts/NOMBRE.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import RAW_DIR, PROCESSED_DIR, BOUNDARY_FILE, ANALYSIS_CRS
from modules.gis.raster_utils import clip_raster_to_boundary, reproject_raster
from modules.gis.terrain import calculate_slope

if __name__ == "__main__":
    source = RAW_DIR / "srtm" / "ebejico_dem.tif"
    clipped = PROCESSED_DIR / "terrain" / "dem_clipped.tif"
    projected = PROCESSED_DIR / "terrain" / "dem_utm18n.tif"
    slope = PROCESSED_DIR / "terrain" / "slope_degrees.tif"

    clip_raster_to_boundary(source, BOUNDARY_FILE, clipped)
    reproject_raster(clipped, projected, ANALYSIS_CRS)
    calculate_slope(projected, slope)
    print("DEM y pendiente procesados.")
