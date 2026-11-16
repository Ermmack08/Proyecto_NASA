"""Download and prepare a monthly NASA POWER point time series."""

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_FILE = PROCESSED_DIR / "environment_nasa_power.csv"
METADATA_FILE = RAW_DIR / "nasa_power_metadata.json"

LATITUDE = 6.325
LONGITUDE = -75.768
COMMUNITY = "AG"
SOURCE = "NASA POWER (MERRA-2)"
API_BASE = "https://power.larc.nasa.gov/api/temporal/monthly/point"

PARAMETERS = {
    "T2M": ("temperature_c", "C"),
    "PRECTOTCORR": ("precipitation_mm_day", "mm/day"),
    "RH2M": ("relative_humidity_pct", "%"),
}
CSV_COLUMNS = [
    "date",
    *(column for column, _ in PARAMETERS.values()),
    "source",
    "is_demo",
]


def build_api_url(start_year: int, end_year: int) -> str:
    query = urlencode(
        {
            "parameters": ",".join(PARAMETERS),
            "community": COMMUNITY,
            "longitude": LONGITUDE,
            "latitude": LATITUDE,
            "start": start_year,
            "end": end_year,
            "format": "JSON",
        }
    )
    return f"{API_BASE}?{query}"


def fetch_response(url: str) -> str:
    request = Request(url, headers={"User-Agent": "AgroAdapt-Ebejico/1.0"})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"No se pudo descargar NASA POWER: {error}") from error


def parse_response(raw_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise ValueError("NASA POWER no devolvió un JSON válido.") from error

    if not isinstance(payload, dict) or payload.get("type") != "Feature":
        raise ValueError("La respuesta de NASA POWER no tiene el formato esperado.")
    if payload.get("messages"):
        raise ValueError(
            "NASA POWER informó errores o advertencias: "
            + "; ".join(map(str, payload["messages"]))
        )

    properties = payload.get("properties", {})
    parameter_data = properties.get("parameter", {})
    missing = set(PARAMETERS).difference(parameter_data)
    if missing:
        raise ValueError(
            "La respuesta de NASA POWER no incluye: "
            + ", ".join(sorted(missing))
        )
    return payload


def prepare_monthly_rows(
    payload: dict[str, Any], start_year: int, end_year: int
) -> list[dict[str, Any]]:
    properties = payload["properties"]
    parameter_data = properties["parameter"]
    fill_value = float(payload.get("header", {}).get("fill_value", -999))
    expected_periods = {
        f"{year}{month:02d}"
        for year in range(start_year, end_year + 1)
        for month in range(1, 13)
    }

    rows_by_period: dict[str, dict[str, Any]] = {
        period: {
            "date": f"{period[:4]}-{period[4:]}-01",
            "source": SOURCE,
            "is_demo": False,
        }
        for period in expected_periods
    }

    for parameter, (column, expected_unit) in PARAMETERS.items():
        parameter_metadata = payload.get("parameters", {}).get(parameter, {})
        actual_unit = parameter_metadata.get("units")
        if actual_unit != expected_unit:
            raise ValueError(
                f"Unidad inesperada para {parameter}: {actual_unit!r}; "
                f"se esperaba {expected_unit!r}."
            )

        series = parameter_data[parameter]
        missing_periods = expected_periods.difference(series)
        if missing_periods:
            raise ValueError(
                f"Faltan periodos mensuales en {parameter}: "
                f"{', '.join(sorted(missing_periods)[:5])}."
            )

        for period in expected_periods:
            raw_value = series[period]
            if raw_value is None:
                value = None
            else:
                value = float(raw_value)
                if not math.isfinite(value):
                    raise ValueError(f"Valor no finito en {parameter}, {period}.")
                if value == fill_value:
                    value = None
            rows_by_period[period][column] = value

    return [rows_by_period[period] for period in sorted(expected_periods)]


def write_outputs(
    raw_text: str,
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
    start_year: int,
    end_year: int,
    raw_file: Path,
    api_url: str,
) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(raw_text, encoding="utf-8")

    with PROCESSED_FILE.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    coordinates = payload.get("geometry", {}).get("coordinates", [])
    metadata = {
        "source": "NASA POWER Monthly and Annual API",
        "api_url": api_url,
        "requested_point": {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "response_elevation_m": coordinates[2] if len(coordinates) > 2 else None,
        },
        "period": {"start_year": start_year, "end_year": end_year},
        "time_standard": payload.get("header", {}).get("time_standard"),
        "data_sources": payload.get("header", {}).get("sources", []),
        "parameters": payload.get("parameters", {}),
        "processed_rows": len(rows),
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        "processing_notes": [
            "Solo se guardan periodos mensuales; el agregado anual YYYY13 se excluye.",
            "PRECTOTCORR conserva la unidad mm/day (tasa media diaria del mes).",
            "Los valores fill_value se guardan vacíos; no se convierten en cero.",
            "El punto representa contexto regional y no una medición de parcela.",
        ],
    }
    METADATA_FILE.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument(
        "--raw-json",
        type=Path,
        help="Procesa una respuesta JSON guardada sin consultar la API.",
    )
    args = parser.parse_args()

    if args.start_year > args.end_year:
        parser.error("--start-year debe ser menor o igual que --end-year.")

    api_url = build_api_url(args.start_year, args.end_year)
    if args.raw_json:
        raw_file = args.raw_json.resolve()
        try:
            raw_text = raw_file.read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(f"No se pudo leer {raw_file}: {error}") from error
    else:
        raw_text = fetch_response(api_url)
        raw_file = RAW_DIR / (
            f"nasa_power_{args.start_year}_{args.end_year}.json"
        )

    payload = parse_response(raw_text)
    rows = prepare_monthly_rows(payload, args.start_year, args.end_year)
    write_outputs(
        raw_text,
        payload,
        rows,
        args.start_year,
        args.end_year,
        raw_file,
        api_url,
    )
    print(f"Guardados {len(rows)} meses en {PROCESSED_FILE}")
    print(f"Respuesta original: {raw_file}")
    print(f"Metadatos: {METADATA_FILE}")


if __name__ == "__main__":
    main()
