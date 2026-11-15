"""Derivación de pendiente desde un DEM en CRS proyectado y unidades métricas."""
from pathlib import Path
import numpy as np
import rasterio

def calculate_slope(dem_path: Path, slope_path: Path):
    """Calcula pendiente en grados usando gradientes x/y del DEM."""
    with rasterio.open(dem_path) as src:
        if not src.crs or not src.crs.is_projected:
            raise ValueError("Reproyecta el DEM a un CRS métrico antes de calcular pendiente.")
        dem = src.read(1).astype("float32")
        nodata = src.nodata
        x_resolution = abs(src.transform.a)
        y_resolution = abs(src.transform.e)
        profile = src.profile.copy()

    valid = np.isfinite(dem)
    if nodata is not None:
        valid &= dem != nodata
    work = dem.copy()
    work[~valid] = np.nan
    dz_dy, dz_dx = np.gradient(work, y_resolution, x_resolution)
    slope = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))
    slope[~np.isfinite(slope)] = -9999.0

    profile.update(count=1, dtype="float32", nodata=-9999.0, compress="lzw")
    slope_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(slope_path, "w", **profile) as dst:
        dst.write(slope.astype("float32"), 1)
        dst.set_band_description(1, "Pendiente en grados")
    return slope_path
