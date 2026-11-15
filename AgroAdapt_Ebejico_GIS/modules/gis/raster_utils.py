"""Operaciones comunes para ráster: recorte, reproyección y exportación."""
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling

def clip_raster_to_boundary(input_raster: Path, boundary_file: Path, output_raster: Path):
    """Recorta un GeoTIFF al límite municipal. Conserva CRS y metadatos del ráster."""
    boundary = gpd.read_file(boundary_file)
    with rasterio.open(input_raster) as src:
        boundary = boundary.to_crs(src.crs)
        geometries = [geom.__geo_interface__ for geom in boundary.geometry if geom is not None]
        clipped, transform = mask(src, geometries, crop=True, filled=True)
        meta = src.meta.copy()
        meta.update(
            height=clipped.shape[1],
            width=clipped.shape[2],
            transform=transform,
        )
    output_raster.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(output_raster, "w", **meta) as dst:
        dst.write(clipped)
    return output_raster

def reproject_raster(input_raster: Path, output_raster: Path, target_crs="EPSG:32618"):
    """Reproyecta un ráster a CRS métrico para análisis de terreno."""
    with rasterio.open(input_raster) as src:
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )
        meta = src.meta.copy()
        meta.update(crs=target_crs, transform=transform, width=width, height=height)
        output_raster.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_raster, "w", **meta) as dst:
            for band in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band),
                    destination=rasterio.band(dst, band),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    src_nodata=src.nodata,
                    dst_nodata=src.nodata,
                    resampling=Resampling.bilinear,
                )
    return output_raster
