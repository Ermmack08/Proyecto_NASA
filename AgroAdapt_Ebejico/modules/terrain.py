"""Terrain indicators derived from geographic elevation rasters."""

import numpy as np
from affine import Affine
from rasterio.crs import CRS

SLOPE_NODATA = -9999.0


def compute_slope_degrees(
    elevation: np.ndarray,
    valid_mask: np.ndarray,
    transform: Affine,
    crs: CRS,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate slope with the Horn 3x3 method for a geographic DEM."""
    if elevation.ndim != 2 or valid_mask.shape != elevation.shape:
        raise ValueError("La elevación y la máscara deben ser arreglos 2D del mismo tamaño.")
    if elevation.shape[0] < 3 or elevation.shape[1] < 3:
        raise ValueError("El ráster necesita al menos 3 filas y 3 columnas.")
    if not crs.is_geographic:
        raise ValueError("La pendiente espera un ráster con coordenadas geográficas.")
    if transform.b != 0 or transform.d != 0 or transform.a == 0 or transform.e == 0:
        raise ValueError("La transformación del ráster debe ser una grilla norte-arriba.")

    center_latitude = transform.f + transform.e * (elevation.shape[0] / 2)
    latitude_radians = np.deg2rad(center_latitude)
    meters_per_degree_longitude = (
        111412.84 * np.cos(latitude_radians)
        - 93.5 * np.cos(3 * latitude_radians)
    )
    meters_per_degree_latitude = (
        111132.92
        - 559.82 * np.cos(2 * latitude_radians)
        + 1.175 * np.cos(4 * latitude_radians)
    )
    pixel_width_m = abs(transform.a) * meters_per_degree_longitude
    pixel_height_m = abs(transform.e) * meters_per_degree_latitude
    if pixel_width_m <= 0 or pixel_height_m <= 0:
        raise ValueError("La resolución del ráster no permite calcular la pendiente.")

    elevations = np.asarray(elevation, dtype=np.float32)
    valid = np.asarray(valid_mask, dtype=bool) & np.isfinite(elevations)
    valid_neighborhood = (
        valid[:-2, :-2]
        & valid[:-2, 1:-1]
        & valid[:-2, 2:]
        & valid[1:-1, :-2]
        & valid[1:-1, 1:-1]
        & valid[1:-1, 2:]
        & valid[2:, :-2]
        & valid[2:, 1:-1]
        & valid[2:, 2:]
    )

    upper_left = elevations[:-2, :-2]
    upper = elevations[:-2, 1:-1]
    upper_right = elevations[:-2, 2:]
    left = elevations[1:-1, :-2]
    right = elevations[1:-1, 2:]
    lower_left = elevations[2:, :-2]
    lower = elevations[2:, 1:-1]
    lower_right = elevations[2:, 2:]

    derivative_x = (
        upper_right + 2 * right + lower_right
        - upper_left - 2 * left - lower_left
    ) / (8 * pixel_width_m)
    derivative_y = (
        lower_left + 2 * lower + lower_right
        - upper_left - 2 * upper - upper_right
    ) / (8 * pixel_height_m)
    slope_values = np.rad2deg(np.arctan(np.hypot(derivative_x, derivative_y)))

    slope = np.full(elevations.shape, SLOPE_NODATA, dtype=np.float32)
    slope_valid = np.zeros(elevations.shape, dtype=bool)
    inner_slope = slope[1:-1, 1:-1]
    inner_slope[valid_neighborhood] = slope_values[valid_neighborhood]
    slope_valid[1:-1, 1:-1] = valid_neighborhood
    if not slope_valid.any():
        raise ValueError("No hay vecindarios completos para calcular la pendiente.")
    return slope, slope_valid
