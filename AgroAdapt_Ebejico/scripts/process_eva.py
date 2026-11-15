"""
Procesa la base EVA y genera salidas verificables para Ebéjico.

Uso:
python3 scripts/process_eva.py data/raw/eva/eva_2019_2025_base_agricola.csv
"""
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.eva_loader import (
    load_eva_csv, filter_ebejico, summarize_eva, summarize_crop_presence
)

def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Uso: python3 scripts/process_eva.py "
            "data/raw/eva/eva_2019_2025_base_agricola.csv"
        )

    source = Path(sys.argv[1])
    if not source.is_absolute():
        source = ROOT / source

    print(f"Leyendo base EVA: {source}")
    data = load_eva_csv(source)
    print(f"Filas totales leídas: {len(data):,}")
    print(f"Columnas reconocidas: {', '.join(data.columns)}")

    municipality = filter_ebejico(data)
    summary = summarize_eva(municipality)
    crop_presence = summarize_crop_presence(municipality)

    catalog_path = ROOT / "data" / "processed" / "crops_catalog.csv"
    catalog = pd.read_csv(catalog_path) if catalog_path.exists() else None
    if catalog is not None and "crop" in catalog.columns:
        catalog_names = set(catalog["crop"].dropna().astype(str).str.casefold())
        crop_presence["en_catalogo_agronomico"] = crop_presence["cultivo"].astype(str).str.casefold().isin(catalog_names)
        crop_presence["observacion"] = crop_presence["en_catalogo_agronomico"].map(
            {True: "Existe en el catálogo; completar/validar ficha agronómica",
             False: "Reportado por EVA; agregar ficha solo después de validación técnica"}
        )

    output_dir = ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    records_path = output_dir / "eva_ebejico_records.csv"
    summary_path = output_dir / "eva_ebejico_crop_summary.csv"
    presence_path = output_dir / "eva_ebejico_crop_presence.csv"

    municipality.to_csv(records_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    crop_presence.to_csv(presence_path, index=False, encoding="utf-8-sig")

    numeric = [
        c for c in ("area_sembrada_ha", "area_cosechada_ha",
                    "produccion_t", "rendimiento_t_ha")
        if c in municipality.columns
    ]
    print("\n========== RESULTADO EVA: EBEJICO ==========")
    print(f"Registros municipales: {len(municipality):,}")
    print(f"Cultivos distintos: {municipality['cultivo'].nunique()}")
    if "anio" in municipality.columns:
        years = sorted(municipality["anio"].dropna().astype(str).unique())
        print(f"Años encontrados: {', '.join(years)}")
    for col in numeric:
        valid = int(municipality[col].notna().sum())
        print(f"{col}: {valid}/{len(municipality)} valores numéricos válidos")
    print("\nCultivos reportados:")
    for crop in sorted(municipality["cultivo"].dropna().astype(str).unique()):
        print(f" - {crop}")
    print("\nArchivos generados:")
    print(f" - {records_path}")
    print(f" - {summary_path}")
    print(f" - {presence_path}")
    print("\nIMPORTANTE: EVA confirma reportes productivos municipales; no indica "
          "ubicación de parcelas ni demuestra por sí sola aptitud agronómica.")

if __name__ == "__main__":
    main()
