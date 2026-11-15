"""Ejecutar primero: descarga el límite municipal oficial (IGAC, Superservicios o geoBoundaries, en ese orden)."""
import sys
from pathlib import Path
# Permite ejecutar este script desde la raíz con: python scripts/NOMBRE.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modules.gis.boundary import download_ebejico_boundary

if __name__ == "__main__":
    boundary = download_ebejico_boundary()
    print(boundary[["dane_code", "municipio", "area_km2", "source"]])
    print("Límite guardado en data/geographic/ebejico_boundary.geojson")
