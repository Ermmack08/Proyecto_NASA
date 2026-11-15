"""Procesamiento de índices de vegetación desde bandas ya descargadas y preparadas.

No descarga imágenes. El usuario debe colocar los GeoTIFF de bandas en data/raw.
Para Sentinel-2 usar reflectancia de superficie (p. ej. L2A) y máscara de nubes.
Para Landsat Collection 2 aplicar primero escala y offset a la reflectancia.
"""
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from config import PROCESSED_DIR

def _read_band(path):
    with rasterio.open(path) as src:
        return src.read(1).astype("float32"), src.profile.copy(), src.nodata

def calculate_ndvi(nir_path: Path, red_path: Path, output_path: Path):
    """Calcula NDVI alineando la banda roja a la grilla NIR si es necesario."""
    nir, profile, nir_nodata = _read_band(nir_path)
    with rasterio.open(red_path) as red_src:
        red = red_src.read(1).astype("float32")
        if (red_src.crs != profile["crs"] or red_src.transform != profile["transform"]
                or red_src.width != profile["width"] or red_src.height != profile["height"]):
            aligned = np.empty((profile["height"], profile["width"]), dtype="float32")
            reproject(
                source=red,
                destination=aligned,
                src_transform=red_src.transform,
                src_crs=red_src.crs,
                dst_transform=profile["transform"],
                dst_crs=profile["crs"],
                resampling=Resampling.bilinear,
            )
            red = aligned
        red_nodata = red_src.nodata

    denominator = nir + red
    ndvi = np.divide(
        nir - red, denominator,
        out=np.full_like(nir, -9999.0),
        where=np.abs(denominator) > 1e-6,
    )
    invalid = ~np.isfinite(ndvi) | (np.abs(denominator) <= 1e-6)
    if nir_nodata is not None:
        invalid |= nir == nir_nodata
    if red_nodata is not None:
        invalid |= red == red_nodata
    # Recortar primero y marcar nodata después: así -9999 no se convierte en -1.
    ndvi = np.clip(ndvi, -1, 1)
    ndvi[invalid] = -9999.0

    profile.update(count=1, dtype="float32", nodata=-9999.0, compress="lzw")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(ndvi.astype("float32"), 1)
        dst.set_band_description(1, "NDVI")
    return output_path

def landsat_collection2_surface_reflectance(digital_number):
    """Escala SR Landsat Collection 2: reflectancia = DN * 0.0000275 - 0.2."""
    return digital_number.astype("float32") * 0.0000275 - 0.2
