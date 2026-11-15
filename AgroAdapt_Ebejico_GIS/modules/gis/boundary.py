"""Descarga y validación del límite municipal de Ebéjico (DANE 05240).

Prueba varias fuentes en orden y usa la primera que devuelva el municipio:
1. IGAC (servicio original del proyecto).
2. Superservicios - Divipola (capa de municipios con código DANE).
3. geoBoundaries (CC BY 4.0), buscando el municipio por nombre.

Siempre valida el resultado (área plausible) y registra la fuente usada.
"""
import json
import unicodedata
from pathlib import Path

import requests
import geopandas as gpd

from config import (
    IGAC_LAYER_QUERY_URL,
    DANE_CODE,
    BOUNDARY_FILE,
    WEB_CRS,
    ANALYSIS_CRS,
)

SUPERSERVICIOS_QUERY_URL = (
    "https://geoportal.superservicios.gov.co/server/rest/services/"
    "Divipola/Division_politico_administrativa/FeatureServer/0/query"
)
GEOBOUNDARIES_API_URL = "https://www.geoboundaries.org/api/current/gbOpen/COL/ADM2/"
MUNICIPIO_NOMBRE = "ebejico"
AREA_MIN_KM2, AREA_MAX_KM2 = 150.0, 350.0  # Ebéjico ronda ~235 km²


def _normalizar(texto) -> str:
    sin_tildes = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return sin_tildes.lower().strip()


def _desde_arcgis(url: str, where: str, nombre: str):
    """Consulta una capa ArcGIS REST y devuelve un GeoDataFrame o None."""
    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    try:
        response = requests.get(url, params=params, timeout=90)
        response.raise_for_status()
        payload = response.json()
    except Exception as error:  # red, JSON inválido, HTTP != 200
        print(f"[{nombre}] no disponible: {error}")
        return None
    features = payload.get("features") or []
    if not features:
        print(f"[{nombre}] respondió, pero sin geometría para {DANE_CODE}")
        return None
    return gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")


def _desde_igac():
    return _desde_arcgis(IGAC_LAYER_QUERY_URL, f"mpcodigo='{DANE_CODE}'", "IGAC")


def _desde_superservicios():
    return _desde_arcgis(
        SUPERSERVICIOS_QUERY_URL, f"MPIO_CCNCT='{DANE_CODE}'", "Superservicios"
    )


def _desde_geoboundaries():
    try:
        meta = requests.get(GEOBOUNDARIES_API_URL, timeout=60)
        meta.raise_for_status()
        url = meta.json()["gjDownloadURL"]
        data = requests.get(url, timeout=300)
        data.raise_for_status()
        todos = gpd.GeoDataFrame.from_features(data.json()["features"], crs="EPSG:4326")
    except Exception as error:
        print(f"[geoBoundaries] no disponible: {error}")
        return None
    columna = "shapeName" if "shapeName" in todos.columns else None
    if columna is None:
        print("[geoBoundaries] el archivo no tiene la columna shapeName")
        return None
    coincide = todos[todos[columna].map(_normalizar) == MUNICIPIO_NOMBRE]
    if coincide.empty:
        print("[geoBoundaries] no se encontró el municipio Ebéjico")
        return None
    return coincide


FUENTES = [
    ("IGAC - Servicio de límites municipales", _desde_igac),
    ("Superservicios - Divipola (DANE)", _desde_superservicios),
    ("geoBoundaries gbOpen COL ADM2 (CC BY 4.0)", _desde_geoboundaries),
]


def download_ebejico_boundary(output_path: Path = BOUNDARY_FILE) -> gpd.GeoDataFrame:
    """Obtiene el polígono de Ebéjico, lo valida y lo guarda como GeoJSON (EPSG:4326)."""
    gdf, fuente = None, None
    for nombre, funcion in FUENTES:
        gdf = funcion()
        if gdf is not None and not gdf.empty:
            fuente = nombre
            break
    if gdf is None or gdf.empty:
        raise ValueError(
            f"Ninguna fuente devolvió geometría para el código {DANE_CODE} (Ebéjico). "
            "Revisa la conexión o descarga el límite desde el DANE (MGN) manualmente."
        )

    gdf = gdf.to_crs(WEB_CRS)
    geometria = gdf.geometry.union_all()
    area_km2 = gpd.GeoSeries([geometria], crs=WEB_CRS).to_crs(ANALYSIS_CRS).area.iloc[0] / 1e6
    if not (AREA_MIN_KM2 <= area_km2 <= AREA_MAX_KM2):
        raise ValueError(
            f"El área obtenida ({area_km2:.1f} km²) no es plausible para Ebéjico "
            f"({AREA_MIN_KM2:.0f}-{AREA_MAX_KM2:.0f} km²). Fuente: {fuente}."
        )

    resultado = gpd.GeoDataFrame(
        {
            "dane_code": [DANE_CODE],
            "municipio": ["Ebéjico"],
            "area_km2": [round(float(area_km2), 2)],
            "source": [fuente],
        },
        geometry=[geometria],
        crs=WEB_CRS,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_file(output_path, driver="GeoJSON")
    print(f"Fuente usada: {fuente} | área: {area_km2:.1f} km² | guardado en {output_path}")
    return resultado
