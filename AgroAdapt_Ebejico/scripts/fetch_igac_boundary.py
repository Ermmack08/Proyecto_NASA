"""Download and prepare the official IGAC municipal boundary for Ebéjico."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
GEOGRAPHIC_DIR = PROJECT_ROOT / "data" / "geographic"
RAW_FILE = RAW_DIR / "igac_boundary_05240.json"
BOUNDARY_FILE = GEOGRAPHIC_DIR / "ebejico_boundary.geojson"
METADATA_FILE = RAW_DIR / "igac_boundary_metadata.json"

SOURCE = "Instituto Geográfico Agustín Codazzi (IGAC)"
SOURCE_ITEM_ID = "58dfbf63c6c54f98a5c4ff6c565969e4"
API_BASE = (
    "https://services2.arcgis.com/RVvWzU3lgJISqdke/arcgis/rest/services/"
    "Municipios_tem%C3%A1ticas/FeatureServer/0/query"
)
MUNICIPAL_CODE = "05240"


def build_api_url() -> str:
    query = urlencode(
        {
            "where": f"MpCodigo='{MUNICIPAL_CODE}'",
            "outFields": "MpCodigo,MpNombre,Depto,MpNorma,MpArea",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        }
    )
    return f"{API_BASE}?{query}"


def fetch_response(url: str) -> str:
    request = Request(url, headers={"User-Agent": "AgroAdapt-Ebejico/1.0"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"No se pudo descargar el límite del IGAC: {error}") from error


def parse_boundary(raw_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise ValueError("El IGAC no devolvió un GeoJSON válido.") from error

    if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection":
        raise ValueError("La respuesta del IGAC no es un GeoJSON FeatureCollection.")

    features = payload.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise ValueError(
            "La consulta al IGAC debe devolver una única entidad municipal."
        )

    feature = features[0]
    properties = feature.get("properties", {}) if isinstance(feature, dict) else {}
    if (
        not isinstance(properties, dict)
        or properties.get("MpCodigo") != MUNICIPAL_CODE
        or str(properties.get("MpNombre", "")).casefold() != "ebéjico"
        or str(properties.get("Depto", "")).casefold() != "antioquia"
    ):
        raise ValueError(
            "La entidad descargada no coincide con Ebéjico, Antioquia "
            f"(código {MUNICIPAL_CODE})."
        )

    geometry = feature.get("geometry")
    if (
        not isinstance(geometry, dict)
        or geometry.get("type") not in {"Polygon", "MultiPolygon"}
    ):
        raise ValueError("El límite del IGAC no contiene una geometría poligonal.")

    positions = list(_iter_positions(geometry.get("coordinates")))
    if not positions or any(
        not (-180 <= longitude <= 180 and -90 <= latitude <= 90)
        for longitude, latitude in positions
    ):
        raise ValueError("La geometría no contiene coordenadas válidas en EPSG:4326.")

    return payload


def _iter_positions(coordinates: Any) -> Iterator[tuple[float, float]]:
    if not isinstance(coordinates, list):
        return
    if (
        len(coordinates) >= 2
        and isinstance(coordinates[0], (int, float))
        and isinstance(coordinates[1], (int, float))
    ):
        yield float(coordinates[0]), float(coordinates[1])
        return
    for part in coordinates:
        yield from _iter_positions(part)


def write_outputs(raw_text: str, payload: dict[str, Any], api_url: str) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    GEOGRAPHIC_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(raw_text, encoding="utf-8")

    processed = {
        key: value for key, value in payload.items() if key not in {"crs", "bbox"}
    }
    BOUNDARY_FILE.write_text(
        json.dumps(processed, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    feature = payload["features"][0]
    metadata = {
        "source": SOURCE,
        "dataset": "Municipios temáticas / Base de Datos Geográfica ET",
        "source_item_id": SOURCE_ITEM_ID,
        "source_item_url": (
            f"https://www.arcgis.com/sharing/rest/content/items/"
            f"{SOURCE_ITEM_ID}?f=pjson"
        ),
        "api_url": api_url,
        "municipality": {
            "name": feature["properties"]["MpNombre"],
            "department": feature["properties"]["Depto"],
            "dane_code": feature["properties"]["MpCodigo"],
        },
        "geometry_type": feature["geometry"]["type"],
        "coordinate_reference_system": "EPSG:4326",
        "source_license_info": (
            "El elemento de ArcGIS consultado no declara una licencia específica; "
            "verificar las condiciones de uso con IGAC."
        ),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "processing_notes": [
            "La consulta se filtró por el código municipal DANE 05240.",
            "El servicio se consultó con outSR=4326.",
            "El archivo procesado conserva la geometría y atributos devueltos; "
            "se eliminó el miembro CRS heredado de la respuesta para GeoJSON web.",
            "El límite municipal no representa linderos prediales ni parcelas agrícolas.",
        ],
    }
    METADATA_FILE.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    api_url = build_api_url()
    raw_text = fetch_response(api_url)
    payload = parse_boundary(raw_text)
    write_outputs(raw_text, payload, api_url)
    print(f"Límite de Ebéjico guardado en {BOUNDARY_FILE}")
    print(f"Respuesta original: {RAW_FILE}")
    print(f"Metadatos: {METADATA_FILE}")


if __name__ == "__main__":
    main()
