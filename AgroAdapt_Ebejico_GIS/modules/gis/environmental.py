"""Descarga de variables diarias NASA POWER para un punto representativo.

NASA POWER es un producto de escala regional. Esta descarga puntual no representa
mediciones de cada parcela ni un promedio espacial municipal.
"""
from datetime import date, timedelta
from pathlib import Path
import requests
import pandas as pd
import geopandas as gpd
from config import BOUNDARY_FILE, PROCESSED_DIR

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def download_power_daily(start="20250101", end=None,
                         parameters="T2M,PRECTOTCORR", output_path=None):
    # POWER tiene un retraso de 2-3 días en meteorología: si no se indica fecha final,
    # se usa hoy menos 4 días para no pedir fechas futuras.
    if end is None:
        end = (date.today() - timedelta(days=4)).strftime("%Y%m%d")
    boundary = gpd.read_file(BOUNDARY_FILE).to_crs("EPSG:4326")
    centroid = boundary.geometry.union_all().centroid
    params = {
        "parameters": parameters,
        "community": "AG",
        "longitude": float(centroid.x),
        "latitude": float(centroid.y),
        "start": start,
        "end": end,
        "format": "JSON",
    }
    response = requests.get(POWER_URL, params=params, timeout=120)
    response.raise_for_status()
    payload = response.json()

    parameter_data = payload["properties"]["parameter"]
    frames = []
    for parameter, values in parameter_data.items():
        frame = pd.Series(values, name=parameter).rename_axis("date").reset_index()
        frame["date"] = pd.to_datetime(frame["date"], format="%Y%m%d")
        frames.append(frame.set_index("date"))
    result = pd.concat(frames, axis=1).reset_index()
    result["source"] = "NASA POWER Daily API"
    result["spatial_note"] = "Punto representativo en centroide municipal; no es dato de parcela."
    result["is_demo"] = False

    output_path = output_path or (PROCESSED_DIR / "environmental" / "nasa_power_daily.csv")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result
