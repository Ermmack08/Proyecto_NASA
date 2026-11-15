"""Descarga serie diaria NASA POWER para el centroide del municipio."""
import sys
from pathlib import Path
# Permite ejecutar este script desde la raíz con: python scripts/NOMBRE.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modules.gis.environmental import download_power_daily

if __name__ == "__main__":
    data = download_power_daily(start="20250101")
    print(data.head())
    print("Serie guardada en data/processed/environmental/")
