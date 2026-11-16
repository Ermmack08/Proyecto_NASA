"""Prepare Sentinel-2 and NASADEM layers clipped to the Ebéjico boundary."""

import argparse
import json
import tempfile
from collections import defaultdict
from contextlib import ExitStack
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import rasterio
from PIL import Image
from rasterio.crs import CRS
from rasterio.features import geometry_mask
from rasterio.mask import mask
from rasterio.merge import merge
from rasterio.warp import transform_bounds, transform_geom
from shapely.geometry import shape
from shapely.ops import unary_union

from modules.terrain import SLOPE_NODATA, compute_slope_degrees


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_FILE = PROJECT_ROOT / "data" / "geographic" / "ebejico_boundary.geojson"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

EARTH_SEARCH_URL = "https://earth-search.aws.element84.com/v1/search"
PLANETARY_COMPUTER_SEARCH_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
PLANETARY_COMPUTER_TOKEN_URL = (
    "https://planetarycomputer.microsoft.com/api/sas/v1/token/nasadem"
)
SENTINEL_COLLECTION = "sentinel-2-l2a"
SENTINEL_CRS = "EPSG:32618"
SENTINEL_RESOLUTION_M = 10
SEARCH_LOOKBACK_DAYS = 120
MAX_SCENE_CLOUD_COVER_PCT = 80
MIN_CLEAR_COVERAGE_PCT = 10
PREVIEW_MAX_SIZE = 900
NDVI_NODATA = -9999.0
SCL_CLOUD_AND_UNCERTAIN_CLASSES = (0, 1, 2, 3, 7, 8, 9, 10, 11)


def _request_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=data,
        headers={
            "User-Agent": "AgroAdapt-Ebejico/1.0",
            "Content-Type": "application/json",
        },
        method="POST" if data is not None else "GET",
    )
    try:
        with urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"No se pudo consultar la fuente geoespacial ({type(error).__name__})."
        ) from error
    if not isinstance(result, dict):
        raise ValueError("La fuente geoespacial devolvió una respuesta inválida.")
    return result


def _read_boundary() -> dict:
    try:
        data = json.loads(BOUNDARY_FILE.read_text(encoding="utf-8"))
    except OSError as error:
        raise RuntimeError(f"No se pudo leer el límite municipal: {BOUNDARY_FILE}") from error
    except json.JSONDecodeError as error:
        raise ValueError("El GeoJSON municipal no contiene JSON válido.") from error

    features = data.get("features") if isinstance(data, dict) else None
    if (
        not isinstance(features, list)
        or not features
        or not isinstance(features[0].get("geometry"), dict)
    ):
        raise ValueError(
            "El GeoJSON debe contener al menos una geometría municipal en EPSG:4326."
        )
    return features[0]["geometry"]


def _fetch_sentinel_items(boundary: dict, start_date: date, end_date: date) -> list[dict]:
    payload = {
        "collections": [SENTINEL_COLLECTION],
        "intersects": boundary,
        "datetime": (
            f"{start_date.isoformat()}T00:00:00Z/"
            f"{end_date.isoformat()}T23:59:59Z"
        ),
        "limit": 100,
        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
    }
    response = _request_json(EARTH_SEARCH_URL, payload)
    items_by_id = {}

    while True:
        for item in response.get("features", []):
            if isinstance(item, dict) and item.get("id"):
                items_by_id[item["id"]] = item

        next_link = next(
            (link for link in response.get("links", []) if link.get("rel") == "next"),
            None,
        )
        if next_link is None:
            break
        next_payload = (
            next_link.get("body")
            if next_link.get("method", "GET").upper() == "POST"
            else None
        )
        response = _request_json(next_link["href"], next_payload)

    return list(items_by_id.values())


def _select_scene_groups(
    items: list[dict], boundary_utm, max_cloud_cover_pct: float
) -> list[dict]:
    groups = defaultdict(list)
    for item in items:
        properties = item.get("properties", {})
        acquired = properties.get("datetime")
        platform = properties.get("platform")
        if not acquired or not platform:
            continue
        groups[(acquired[:10], platform)].append(item)

    candidates = []
    for (acquired_date, platform), group in groups.items():
        footprints = [
            shape(transform_geom("EPSG:4326", SENTINEL_CRS, item["geometry"]))
            for item in group
            if item.get("geometry")
        ]
        if not footprints:
            continue

        coverage_pct = (
            boundary_utm.intersection(unary_union(footprints)).area
            / boundary_utm.area
            * 100
        )
        cloud_values = [
            float(item["properties"]["eo:cloud_cover"])
            for item in group
            if item.get("properties", {}).get("eo:cloud_cover") is not None
        ]
        mean_cloud_cover_pct = (
            sum(cloud_values) / len(cloud_values) if cloud_values else 100.0
        )
        if coverage_pct >= 99 and mean_cloud_cover_pct <= max_cloud_cover_pct:
            candidates.append(
                {
                    "date": acquired_date,
                    "platform": platform,
                    "coverage_pct": coverage_pct,
                    "mean_cloud_cover_pct": mean_cloud_cover_pct,
                    "items": group,
                }
            )

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate["date"],
            -candidate["mean_cloud_cover_pct"],
        ),
        reverse=True,
    )


def _mosaic_asset(
    items: list[dict], asset_key: str, bounds: tuple[float, float, float, float],
    resolution_m: int,
) -> tuple[np.ndarray, rasterio.Affine]:
    try:
        with ExitStack() as stack:
            sources = [
                stack.enter_context(rasterio.open(item["assets"][asset_key]["href"]))
                for item in items
            ]
            array, transform = merge(
                sources,
                bounds=bounds,
                res=(resolution_m, resolution_m),
                nodata=0,
                dtype=sources[0].dtypes[0],
            )
    except (KeyError, rasterio.errors.RasterioError, OSError) as error:
        raise RuntimeError(
            f"No se pudo preparar la banda Sentinel-2 {asset_key}."
        ) from error
    return array[0], transform


def _load_clear_sentinel_scene(
    candidates: list[dict], boundary_utm
) -> tuple[dict, dict[str, np.ndarray], rasterio.Affine, np.ndarray]:
    bounds = boundary_utm.bounds
    for candidate in candidates:
        items = candidate["items"]
        red, transform = _mosaic_asset(items, "red", bounds, SENTINEL_RESOLUTION_M)
        nir, transform = _mosaic_asset(items, "nir", bounds, SENTINEL_RESOLUTION_M)
        scl, transform = _mosaic_asset(items, "scl", bounds, SENTINEL_RESOLUTION_M)
        inside = geometry_mask(
            [boundary_utm],
            out_shape=red.shape,
            transform=transform,
            invert=True,
        )
        valid = (
            inside
            & ~np.isin(scl, SCL_CLOUD_AND_UNCERTAIN_CLASSES)
            & (red > 0)
            & (nir > 0)
        )
        valid_coverage_pct = 100 * int(valid.sum()) / max(1, int(inside.sum()))
        if valid_coverage_pct >= MIN_CLEAR_COVERAGE_PCT:
            return candidate, {"red": red, "nir": nir, "scl": scl}, transform, valid

    raise ValueError(
        "No se encontró una escena Sentinel-2 con cobertura municipal completa "
        f"y al menos {MIN_CLEAR_COVERAGE_PCT}% de píxeles válidos sin nubes "
        "en el periodo consultado."
    )


def _write_geotiff(
    path: Path,
    arrays: np.ndarray,
    transform: rasterio.Affine,
    crs: str,
    nodata: int | float,
    valid_mask: np.ndarray,
    tags: dict[str, str],
) -> None:
    if arrays.ndim == 2:
        arrays = arrays[np.newaxis, ...]
    profile = {
        "driver": "GTiff",
        "height": arrays.shape[1],
        "width": arrays.shape[2],
        "count": arrays.shape[0],
        "dtype": arrays.dtype,
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "compress": "deflate",
        "tiled": True,
        "predictor": 3 if np.issubdtype(arrays.dtype, np.floating) else 2,
    }
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(arrays)
        dataset.write_mask(valid_mask.astype(np.uint8) * 255)
        dataset.update_tags(**tags)


def _preview_bounds(
    transform: rasterio.Affine, width: int, height: int, crs: str
) -> list[list[float]]:
    left, bottom, right, top = rasterio.transform.array_bounds(
        height, width, transform
    )
    left, bottom, right, top = transform_bounds(
        crs, "EPSG:4326", left, bottom, right, top, densify_pts=21
    )
    return [[bottom, left], [top, right]]


def _resize_preview(image: Image.Image, destination: Path) -> None:
    image.thumbnail((PREVIEW_MAX_SIZE, PREVIEW_MAX_SIZE), Image.Resampling.LANCZOS)
    image.save(destination, format="PNG", optimize=True)


def _ndvi_rgba(ndvi: np.ndarray, valid: np.ndarray) -> Image.Image:
    stops = np.array([-0.2, 0.0, 0.2, 0.4, 0.6, 0.8])
    colors = np.array(
        [
            [145, 75, 35],
            [205, 145, 65],
            [232, 210, 105],
            [155, 190, 90],
            [80, 145, 65],
            [25, 100, 50],
        ],
        dtype=np.uint8,
    )
    clipped = np.clip(ndvi, stops[0], stops[-1])
    rgba = np.zeros((*ndvi.shape, 4), dtype=np.uint8)
    for channel in range(3):
        rgba[..., channel] = np.interp(
            clipped, stops, colors[:, channel]
        ).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 220, 0).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def _rgb_rgba(
    red: np.ndarray,
    green: np.ndarray,
    blue: np.ndarray,
    valid: np.ndarray,
) -> Image.Image:
    channels = []
    for band in (red, green, blue):
        samples = band[valid].astype(np.float32)
        low, high = np.percentile(samples, [2, 98])
        stretched = np.clip((band.astype(np.float32) - low) / max(high - low, 1), 0, 1)
        channels.append(np.power(stretched, 1 / 1.8))

    rgba = np.zeros((*red.shape, 4), dtype=np.uint8)
    rgba[..., :3] = (
        np.stack(channels, axis=-1).clip(0, 1) * 255
    ).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 220, 0).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def _elevation_rgba(elevation: np.ndarray, valid: np.ndarray) -> Image.Image:
    values = elevation[valid].astype(np.float32)
    low, high = np.percentile(values, [2, 98])
    scale = np.clip((elevation.astype(np.float32) - low) / max(high - low, 1), 0, 1)
    stops = np.array([0, 0.25, 0.5, 0.75, 1])
    colors = np.array(
        [
            [40, 100, 65],
            [125, 150, 75],
            [205, 185, 110],
            [145, 105, 75],
            [240, 240, 230],
        ],
        dtype=np.uint8,
    )
    rgba = np.zeros((*elevation.shape, 4), dtype=np.uint8)
    for channel in range(3):
        rgba[..., channel] = np.interp(
            scale, stops, colors[:, channel]
        ).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 220, 0).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def _slope_rgba(slope: np.ndarray, valid: np.ndarray) -> Image.Image:
    scale = np.clip(slope.astype(np.float32) / 45, 0, 1)
    stops = np.array([0, 0.25, 0.5, 0.75, 1])
    colors = np.array(
        [
            [35, 132, 67],
            [166, 189, 91],
            [250, 208, 86],
            [224, 112, 55],
            [150, 45, 45],
        ],
        dtype=np.uint8,
    )
    rgba = np.zeros((*slope.shape, 4), dtype=np.uint8)
    for channel in range(3):
        rgba[..., channel] = np.interp(
            scale, stops, colors[:, channel]
        ).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 220, 0).astype(np.uint8)
    return Image.fromarray(rgba, mode="RGBA")


def _prepare_sentinel_products(
    scene: dict,
    bands: dict[str, np.ndarray],
    transform: rasterio.Affine,
    valid: np.ndarray,
    boundary_utm,
    output_dir: Path,
) -> dict:
    green, _ = _mosaic_asset(
        scene["items"], "green", boundary_utm.bounds, SENTINEL_RESOLUTION_M
    )
    blue, _ = _mosaic_asset(
        scene["items"], "blue", boundary_utm.bounds, SENTINEL_RESOLUTION_M
    )
    red = bands["red"]
    nir = bands["nir"]
    denominator = nir.astype(np.float32) + red.astype(np.float32)
    ndvi = np.full(red.shape, NDVI_NODATA, dtype=np.float32)
    valid &= denominator > 0
    ndvi[valid] = (
        nir[valid].astype(np.float32) - red[valid].astype(np.float32)
    ) / denominator[valid]
    rgb = np.stack([red, green, blue])
    rgb[:, ~valid] = 0

    _write_geotiff(
        output_dir / "sentinel2_ndvi.tif",
        ndvi,
        transform,
        SENTINEL_CRS,
        NDVI_NODATA,
        valid,
        {
            "source": "Copernicus Sentinel-2 L2A",
            "acquisition_date": scene["date"],
            "index": "(B08-B04)/(B08+B04)",
            "pixel_size_m": str(SENTINEL_RESOLUTION_M),
            "cloud_mask": "SCL classes 0,1,2,3,7,8,9,10,11; non-zero B04 and B08",
        },
    )
    _write_geotiff(
        output_dir / "sentinel2_rgb.tif",
        rgb,
        transform,
        SENTINEL_CRS,
        0,
        valid,
        {
            "source": "Copernicus Sentinel-2 L2A",
            "acquisition_date": scene["date"],
            "bands": "B04 red, B03 green, B02 blue",
            "pixel_size_m": str(SENTINEL_RESOLUTION_M),
        },
    )
    _resize_preview(
        _ndvi_rgba(ndvi, valid), output_dir / "sentinel2_ndvi_preview.png"
    )
    _resize_preview(
        _rgb_rgba(red, green, blue, valid),
        output_dir / "sentinel2_rgb_preview.png",
    )

    values = ndvi[valid]
    inside = geometry_mask(
        [boundary_utm],
        out_shape=valid.shape,
        transform=transform,
        invert=True,
    )
    valid_coverage_pct = 100 * int(valid.sum()) / max(1, int(inside.sum()))
    metadata = {
        "acquisition_date": scene["date"],
        "platform": scene["platform"],
        "scene_ids": [item["id"] for item in scene["items"]],
        "mean_scene_cloud_cover_percent": round(
            scene["mean_cloud_cover_pct"], 2
        ),
        "valid_coverage_percent": round(valid_coverage_pct, 2),
        "mean_ndvi": round(float(np.mean(values)), 4),
        "median_ndvi": round(float(np.median(values)), 4),
        "minimum_ndvi": round(float(np.min(values)), 4),
        "maximum_ndvi": round(float(np.max(values)), 4),
        "resolution_m": SENTINEL_RESOLUTION_M,
        "crs": SENTINEL_CRS,
        "bounds": _preview_bounds(transform, red.shape[1], red.shape[0], SENTINEL_CRS),
        "source": (
            "Copernicus Sentinel-2 Level-2A via Element 84 Earth Search "
            "(AWS Open Data)"
        ),
        "preview_file": "sentinel2_ndvi_preview.png",
        "rgb_preview_file": "sentinel2_rgb_preview.png",
        "ndvi_file": "sentinel2_ndvi.tif",
        "rgb_file": "sentinel2_rgb.tif",
        "processing": (
            "NDVI=(B08-B04)/(B08+B04); SCL classes 0,1,2,3,7,8,9,10,11 "
            "and zero-valued reflectance are masked. RGB preview uses "
            "a 2nd-98th percentile visual stretch."
        ),
    }
    return metadata


def _find_nasadem_item(boundary: dict) -> dict:
    response = _request_json(
        PLANETARY_COMPUTER_SEARCH_URL,
        {
            "collections": ["nasadem"],
            "intersects": boundary,
            "limit": 10,
        },
    )
    items = response.get("features", [])
    if not items or "elevation" not in items[0].get("assets", {}):
        raise ValueError("Planetary Computer no encontró la tesela NASADEM de Ebéjico.")
    return items[0]


def _prepare_nasadem_product(
    boundary: dict, item: dict, output_dir: Path
) -> tuple[dict, dict]:
    token_response = _request_json(PLANETARY_COMPUTER_TOKEN_URL)
    token = token_response.get("token")
    if not isinstance(token, str) or not token:
        raise ValueError("Planetary Computer no devolvió un token temporal NASADEM.")

    unsigned_href = item["assets"]["elevation"]["href"]
    signed_href = unsigned_href + token if token.startswith("?") else unsigned_href + "?" + token
    try:
        with rasterio.open(signed_href) as source:
            nodata = source.nodata if source.nodata is not None else -32768
            elevation, transform = mask(
                source,
                [boundary],
                crop=True,
                filled=True,
                nodata=nodata,
            )
            crs = source.crs
            resolution_degrees = max(abs(value) for value in source.res)
    except (rasterio.errors.RasterioError, OSError, KeyError) as error:
        raise RuntimeError(
            f"No se pudo leer la tesela NASADEM ({type(error).__name__})."
        ) from None

    if crs is None:
        raise ValueError("La tesela NASADEM no tiene un sistema de coordenadas definido.")
    elevation = elevation[0]
    valid = np.isfinite(elevation) & (elevation != nodata)
    if not valid.any():
        raise ValueError("La tesela NASADEM no contiene elevaciones válidas en Ebéjico.")

    _write_geotiff(
        output_dir / "nasadem_elevation.tif",
        elevation.astype(np.int16),
        transform,
        crs,
        int(nodata),
        valid,
        {
            "source": "NASADEM HGT v001 (SRTM-derived)",
            "vertical_units": "meters",
            "horizontal_resolution": "1 arc-second, approximately 30 m",
        },
    )
    _resize_preview(
        _elevation_rgba(elevation, valid),
        output_dir / "nasadem_elevation_preview.png",
    )
    values = elevation[valid].astype(np.float64)
    elevation_metadata = {
        "item_id": item["id"],
        "source": "NASA/JPL/USGS NASADEM HGT v001 via Microsoft Planetary Computer",
        "resolution_m_approx": 30,
        "resolution_degrees": resolution_degrees,
        "crs": crs.to_string() if crs else None,
        "elevation_min_m": round(float(np.min(values)), 1),
        "elevation_mean_m": round(float(np.mean(values)), 1),
        "elevation_max_m": round(float(np.max(values)), 1),
        "bounds": _preview_bounds(
            transform, elevation.shape[1], elevation.shape[0], crs
        ),
        "preview_file": "nasadem_elevation_preview.png",
        "elevation_file": "nasadem_elevation.tif",
        "processing": (
            "NASADEM elevation clipped to the municipal boundary; "
            "the preview colors indicate relative elevation."
        ),
    }
    slope_metadata = _prepare_nasadem_slope_product(
        elevation,
        valid,
        transform,
        crs,
        output_dir,
        elevation_metadata,
    )
    return elevation_metadata, slope_metadata


def _prepare_nasadem_slope_product(
    elevation: np.ndarray,
    valid: np.ndarray,
    transform: rasterio.Affine,
    crs: CRS,
    output_dir: Path,
    elevation_metadata: dict,
) -> dict:
    slope, slope_valid = compute_slope_degrees(elevation, valid, transform, crs)
    _write_geotiff(
        output_dir / "nasadem_slope.tif",
        slope,
        transform,
        crs,
        SLOPE_NODATA,
        slope_valid,
        {
            "source": "Derived from NASADEM HGT v001",
            "method": "Horn 3x3",
            "units": "degrees",
            "horizontal_spacing": (
                "Approximate local pixel spacing converted from EPSG:4326 "
                "at raster center using the WGS84 ellipsoid"
            ),
        },
    )
    _resize_preview(
        _slope_rgba(slope, slope_valid),
        output_dir / "nasadem_slope_preview.png",
    )
    values = slope[slope_valid].astype(np.float64)
    return {
        "item_id": elevation_metadata["item_id"],
        "source": elevation_metadata["source"],
        "resolution_m_approx": elevation_metadata["resolution_m_approx"],
        "resolution_degrees": elevation_metadata["resolution_degrees"],
        "crs": crs.to_string(),
        "slope_min_degrees": round(float(np.min(values)), 2),
        "slope_mean_degrees": round(float(np.mean(values)), 2),
        "slope_max_degrees": round(float(np.max(values)), 2),
        "valid_coverage_percent": round(
            100 * int(slope_valid.sum()) / max(1, int(valid.sum())),
            2,
        ),
        "bounds": elevation_metadata["bounds"],
        "preview_file": "nasadem_slope_preview.png",
        "slope_file": "nasadem_slope.tif",
        "processing": (
            "Slope in degrees derived with a 3x3 Horn estimator; local pixel "
            "spacing is approximated at the raster center. Border cells and "
            "cells without a complete valid neighborhood are masked."
        ),
    }


def prepare_products(
    boundary: dict,
    lookback_days: int = SEARCH_LOOKBACK_DAYS,
    max_cloud_cover_pct: float = MAX_SCENE_CLOUD_COVER_PCT,
) -> tuple[dict, list[dict], dict]:
    boundary_utm = shape(transform_geom("EPSG:4326", SENTINEL_CRS, boundary))
    today = date.today()
    start_date = today - timedelta(days=lookback_days)
    items = _fetch_sentinel_items(boundary, start_date, today)
    candidates = _select_scene_groups(items, boundary_utm, max_cloud_cover_pct)
    if not candidates:
        raise ValueError(
            "No se encontró una escena Sentinel-2 que cubra el municipio "
            "completo con la nubosidad máxima configurada."
        )

    scene, bands, transform, valid = _load_clear_sentinel_scene(
        candidates, boundary_utm
    )
    with tempfile.TemporaryDirectory(dir=PROCESSED_DIR) as temporary_dir:
        output_dir = Path(temporary_dir)
        sentinel_metadata = _prepare_sentinel_products(
            scene, bands, transform, valid.copy(), boundary_utm, output_dir
        )
        dem_item = _find_nasadem_item(boundary)
        dem_metadata, slope_metadata = _prepare_nasadem_product(
            boundary, dem_item, output_dir
        )

        raw_items = {
            "search": {
                "source": EARTH_SEARCH_URL,
                "collection": SENTINEL_COLLECTION,
                "lookback_days": lookback_days,
                "start_date": start_date.isoformat(),
                "end_date": today.isoformat(),
                "result_count": len(items),
                "selected_date": scene["date"],
                "selected_platform": scene["platform"],
                "selected_items": scene["items"],
            },
            "nasadem": {
                "source": PLANETARY_COMPUTER_SEARCH_URL,
                "collection": "nasadem",
                "selected_item": dem_item,
            },
        }
        metadata = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "boundary": "data/geographic/ebejico_boundary.geojson",
            "products": {
                "sentinel2_ndvi": sentinel_metadata,
                "sentinel2_rgb": {
                    "acquisition_date": sentinel_metadata["acquisition_date"],
                    "platform": sentinel_metadata["platform"],
                    "scene_ids": sentinel_metadata["scene_ids"],
                    "mean_scene_cloud_cover_percent": sentinel_metadata[
                        "mean_scene_cloud_cover_percent"
                    ],
                    "valid_coverage_percent": sentinel_metadata[
                        "valid_coverage_percent"
                    ],
                    "resolution_m": sentinel_metadata["resolution_m"],
                    "crs": sentinel_metadata["crs"],
                    "bounds": sentinel_metadata["bounds"],
                    "source": sentinel_metadata["source"],
                    "preview_file": sentinel_metadata["rgb_preview_file"],
                    "rgb_file": sentinel_metadata["rgb_file"],
                    "processing": "RGB natural color B04/B03/B02 with visual stretch.",
                },
                "nasadem_elevation": dem_metadata,
                "nasadem_slope": slope_metadata,
            },
            "limitations": [
                "Sentinel-2 cloud cover is reported per tile; valid coverage is calculated after SCL masking within the municipal boundary.",
                "NDVI is a vegetation index, not a crop identification or parcel-level agronomic diagnosis.",
                "NASADEM is a terrain model derived primarily from SRTM, not a field elevation survey.",
                "Slope is derived from NASADEM at approximately 30 m and is not an erosion-risk or parcel-level diagnosis.",
                "Products represent the municipality and do not resolve individual farms or parcels.",
            ],
        }
        files_to_publish = [
            "sentinel2_ndvi.tif",
            "sentinel2_rgb.tif",
            "sentinel2_ndvi_preview.png",
            "sentinel2_rgb_preview.png",
            "nasadem_elevation.tif",
            "nasadem_elevation_preview.png",
            "nasadem_slope.tif",
            "nasadem_slope_preview.png",
        ]
        for filename in files_to_publish:
            (output_dir / filename).replace(PROCESSED_DIR / filename)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "satellite_stac_items.json").write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    metadata_file = RAW_DIR / "satellite_layers_metadata.json"
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata, scene["items"], dem_item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=SEARCH_LOOKBACK_DAYS,
        help="Días hacia atrás para buscar escenas Sentinel-2.",
    )
    parser.add_argument(
        "--max-cloud-cover",
        type=float,
        default=MAX_SCENE_CLOUD_COVER_PCT,
        help="Nubosidad media máxima de las teselas, en porcentaje.",
    )
    args = parser.parse_args()
    if args.lookback_days < 1:
        parser.error("--lookback-days debe ser mayor que cero.")
    if not 0 <= args.max_cloud_cover <= 100:
        parser.error("--max-cloud-cover debe estar entre 0 y 100.")
    if not PROCESSED_DIR.exists():
        PROCESSED_DIR.mkdir(parents=True)

    boundary = _read_boundary()
    metadata, scene_items, dem_item = prepare_products(
        boundary,
        lookback_days=args.lookback_days,
        max_cloud_cover_pct=args.max_cloud_cover,
    )
    sentinel = metadata["products"]["sentinel2_ndvi"]
    dem = metadata["products"]["nasadem_elevation"]
    print(
        f"Sentinel-2 {sentinel['acquisition_date']}: "
        f"{sentinel['valid_coverage_percent']:.1f}% de área válida sin nubes."
    )
    print(
        f"NDVI municipal medio: {sentinel['mean_ndvi']:.3f}; "
        f"elevación NASADEM: {dem['elevation_min_m']:.0f}–"
        f"{dem['elevation_max_m']:.0f} m."
    )
    slope = metadata["products"]["nasadem_slope"]
    print(
        f"Pendiente NASADEM media: {slope['slope_mean_degrees']:.1f}° "
        f"({slope['valid_coverage_percent']:.1f}% de píxeles válidos)."
    )
    print(f"Teselas Sentinel-2: {len(scene_items)}; NASADEM: {dem_item['id']}.")
    print(f"Productos: {PROCESSED_DIR}")
    print(f"Metadatos: {RAW_DIR / 'satellite_layers_metadata.json'}")


if __name__ == "__main__":
    main()
