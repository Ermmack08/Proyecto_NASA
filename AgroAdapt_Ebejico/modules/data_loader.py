"""Load processed data and sample values from geographic raster layers."""

import json

import pandas as pd
import streamlit as st

from config import (
    BOUNDARY_FILE,
    CROPS_FILE,
    CROP_HISTORY_FILE,
    ENVIRONMENT_FILE,
    SATELLITE_METADATA_FILE,
    SATELLITE_RASTER_FILES,
    ZONES_FILE,
)

CROP_HISTORY_COLUMNS = {
    "year",
    "crop",
    "crop_group",
    "crop_subgroup",
    "crop_detail",
    "scientific_name",
    "crop_cycle",
    "area_planted_ha",
    "area_harvested_ha",
    "production_t",
    "yield_t_ha",
}
CROP_HISTORY_TEXT_COLUMNS = (
    "crop",
    "crop_group",
    "crop_subgroup",
    "crop_detail",
    "scientific_name",
    "crop_cycle",
)
CROP_HISTORY_MEASURE_COLUMNS = (
    "area_planted_ha",
    "area_harvested_ha",
    "production_t",
    "yield_t_ha",
)


def _modified_time(path):
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return None


@st.cache_data(show_spinner=False)
def _read_environment(path, modified_ns):
    if modified_ns is None:
        return pd.DataFrame()

    data = pd.read_csv(path)
    required = {"date", "source", "is_demo"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            "El CSV ambiental no cumple el contrato del README. "
            f"Faltan columnas: {', '.join(sorted(missing))}."
        )

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    if data["date"].isna().any():
        raise ValueError("El CSV ambiental contiene fechas vacías o inválidas.")

    demo_values = data["is_demo"].astype("string").str.strip().str.lower()
    valid_demo_values = {"true", "false", "1", "0"}
    if data["is_demo"].isna().any() or not demo_values.isin(valid_demo_values).all():
        raise ValueError("La columna is_demo solo puede contener True, False, 1 o 0.")
    data["is_demo"] = demo_values.isin({"true", "1"})

    if not data.select_dtypes(include="number").columns.tolist():
        raise ValueError("El CSV ambiental debe incluir al menos una variable numérica.")

    return data


def load_environment():
    """Load the environmental CSV, returning an empty table if it is absent."""
    return _read_environment(str(ENVIRONMENT_FILE), _modified_time(ENVIRONMENT_FILE))


@st.cache_data(show_spinner=False)
def _read_crops(path, modified_ns):
    if modified_ns is None:
        return pd.DataFrame()

    data = pd.read_csv(path)
    if "crop" not in data.columns:
        raise ValueError("El catálogo de cultivos debe incluir la columna 'crop'.")
    return data


def load_crops():
    """Load the crop catalog, returning an empty table if it is absent."""
    return _read_crops(str(CROPS_FILE), _modified_time(CROPS_FILE))


@st.cache_data(show_spinner=False)
def _read_crop_history(path, modified_ns):
    if modified_ns is None:
        return pd.DataFrame()

    data = pd.read_csv(path)
    missing = CROP_HISTORY_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(
            "El histórico EVA no cumple el contrato esperado. "
            f"Faltan columnas: {', '.join(sorted(missing))}."
        )
    if data.empty:
        return data

    year = pd.to_numeric(data["year"], errors="coerce")
    if year.isna().any() or (year % 1 != 0).any():
        raise ValueError("El histórico EVA contiene años vacíos o inválidos.")
    data["year"] = year.astype(int)

    for column in CROP_HISTORY_TEXT_COLUMNS:
        data[column] = data[column].astype("string").str.strip()
        if data[column].isna().any() or data[column].eq("").any():
            raise ValueError(
                f"El histórico EVA contiene valores vacíos en '{column}'."
            )

    for column in CROP_HISTORY_MEASURE_COLUMNS:
        original = data[column]
        numeric = pd.to_numeric(original, errors="coerce")
        if (original.notna() & numeric.isna()).any():
            raise ValueError(
                f"El histórico EVA contiene valores no numéricos en '{column}'."
            )
        if numeric.dropna().lt(0).any():
            raise ValueError(
                f"El histórico EVA contiene valores negativos en '{column}'."
            )
        data[column] = numeric

    return data.sort_values(
        ["year", "crop", "crop_detail"], kind="stable"
    ).reset_index(drop=True)


def load_crop_history():
    """Load verified municipal EVA records, or an empty table if absent."""
    return _read_crop_history(
        str(CROP_HISTORY_FILE), _modified_time(CROP_HISTORY_FILE)
    )


@st.cache_data(show_spinner=False)
def _read_geojson(path, modified_ns):
    if modified_ns is None:
        return None

    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"El archivo geográfico {path} no contiene JSON válido.") from error

    if (
        not isinstance(data, dict)
        or data.get("type") != "FeatureCollection"
        or not isinstance(data.get("features"), list)
    ):
        raise ValueError(
            f"El archivo geográfico {path} debe ser un GeoJSON FeatureCollection."
        )
    if any(
        not isinstance(feature, dict) or feature.get("type") != "Feature"
        for feature in data["features"]
    ):
        raise ValueError(f"El archivo geográfico {path} contiene entidades inválidas.")
    return data


def load_geojson(path):
    """Load a GeoJSON FeatureCollection; return None if its file is absent."""
    return _read_geojson(str(path), _modified_time(path))


def load_boundary():
    """Load the municipal boundary layer when it has been provided."""
    return load_geojson(BOUNDARY_FILE)


def load_zones():
    """Load analysis zones without assuming they represent veredas."""
    return load_geojson(ZONES_FILE)


@st.cache_data(show_spinner=False)
def _read_satellite_metadata(path, modified_ns):
    if modified_ns is None:
        return None

    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError("Los metadatos satelitales no contienen JSON válido.") from error

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("products"), dict)
    ):
        raise ValueError("Los metadatos satelitales no cumplen el formato esperado.")
    return data


def load_satellite_metadata():
    """Load prepared satellite product metadata, or None before processing."""
    return _read_satellite_metadata(
        str(SATELLITE_METADATA_FILE),
        _modified_time(SATELLITE_METADATA_FILE),
    )


@st.cache_data(show_spinner=False)
def _sample_raster_point(path, modified_ns, latitude, longitude):
    if modified_ns is None:
        return None

    import numpy as np
    import rasterio
    from rasterio.warp import transform
    from rasterio.windows import Window

    try:
        with rasterio.open(path) as dataset:
            if dataset.crs is None:
                raise ValueError(f"El ráster no tiene CRS definido: {path}")

            x, y = transform(
                "EPSG:4326",
                dataset.crs,
                [longitude],
                [latitude],
            )
            row, column = dataset.index(x[0], y[0])
            if not (0 <= row < dataset.height and 0 <= column < dataset.width):
                return None

            window = Window(column, row, 1, 1)
            if dataset.dataset_mask(window=window)[0, 0] == 0:
                return None

            values = dataset.read(window=window)[:, 0, 0]
            if not np.all(np.isfinite(values)):
                return None

            center_x, center_y = dataset.xy(row, column)
            center_lon, center_lat = transform(
                dataset.crs,
                "EPSG:4326",
                [center_x],
                [center_y],
            )
    except rasterio.errors.RasterioError as error:
        raise RuntimeError(f"No se pudo consultar el ráster: {path}") from error

    return {
        "values": [float(value) for value in values],
        "pixel_center": {
            "latitude": float(center_lat[0]),
            "longitude": float(center_lon[0]),
        },
    }


def sample_satellite_point(product_key, latitude, longitude):
    """Return the valid raster pixel containing a WGS84 map click, if any."""
    try:
        path = SATELLITE_RASTER_FILES[product_key]
    except KeyError as error:
        raise ValueError(f"Producto satelital desconocido: {product_key}") from error

    return _sample_raster_point(
        str(path),
        _modified_time(path),
        float(latitude),
        float(longitude),
    )
