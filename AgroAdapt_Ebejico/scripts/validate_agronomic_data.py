#!/usr/bin/env python3
"""Valida estructura y cobertura del catálogo agronómico de AgroAdapt.

No completa datos faltantes ni convierte referencias preliminares en evidencia local.
Los faltantes técnicos se reportan como advertencias, no como errores estructurales.
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.crop_catalog import load_crop_catalog, validate_crop_catalog, REQUIRED_FIELDS

CATALOG = ROOT / "data/processed/crops_catalog.csv"
LEGACY_CATALOG = ROOT / "data/processed/catalogo_agronomico_ebejico.csv"
REFERENCES = ROOT / "data/processed/agronomic_references_template.csv"
REFERENCE_RECORDS = ROOT / "data/processed/agronomic_reference_records.csv"
TECHNICAL_SOURCES = ROOT / "data/processed/fuentes_tecnicas_bloque1.csv"
REPORT = ROOT / "data/processed/agronomic_validation_report.csv"

EXPECTED_CROP_IDS = {
    "AGU", "CAC", "CAF", "CAN", "FRI", "LIM",
    "LIMON", "MAR", "MAI", "PLA", "TOM", "YUC"
}
TECHNICAL_FIELDS = [
    "cycle_days_min", "cycle_days_max", "water_requirement",
    "temperature_min_c", "temperature_opt_min_c",
    "temperature_opt_max_c", "temperature_max_c",
    "soil_texture", "soil_ph_min", "soil_ph_max",
    "root_depth_cm", "nutrient_notes", "soil_cover_notes",
    "rotation_notes", "technical_source"
]
REFERENCE_COLUMNS = [
    "crop_id", "source_id", "crop", "attribute", "value", "unit",
    "source_organization", "document_title", "publication_year",
    "geographic_scope", "source_url", "evidence_status", "notes"
]
REFERENCE_STATUSES = {"verified", "reference_only", "pending_local_validation"}

def add(rows, level, component, detail, count=""):
    rows.append({
        "nivel": level,
        "componente": component,
        "detalle": detail,
        "cantidad": count
    })

def main():
    rows = []
    errors = 0
    warnings = 0

    if not CATALOG.exists():
        add(rows, "ERROR", "catalogo_principal", f"No existe {CATALOG.relative_to(ROOT)}")
        errors += 1
        df = pd.DataFrame()
    else:
        df = load_crop_catalog(CATALOG)
        structural = validate_crop_catalog(df)
        for message in structural:
            add(rows, "ERROR", "catalogo_principal", message)
            errors += 1

        if not structural:
            add(rows, "OK", "estructura", "Columnas obligatorias y estructura reconocidas.")
        if "crop_id" in df.columns:
            ids = set(df["crop_id"].dropna().astype(str))
            missing_ids = sorted(EXPECTED_CROP_IDS - ids)
            unexpected = sorted(ids - EXPECTED_CROP_IDS)
            if missing_ids:
                add(rows, "ERROR", "identificacion_cultivos",
                    "Faltan identificadores esperados: " + ", ".join(missing_ids))
                errors += 1
            if unexpected:
                add(rows, "ADVERTENCIA", "identificacion_cultivos",
                    "Identificadores adicionales: " + ", ".join(unexpected))
                warnings += 1
            if not missing_ids:
                add(rows, "OK", "identificacion_cultivos",
                    "Los 12 identificadores esperados están presentes.", len(ids))

        for field in TECHNICAL_FIELDS:
            if field not in df.columns:
                continue
            missing = int(df[field].isna().sum())
            if df[field].dtype == "object":
                missing += int(df[field].astype("string").str.strip().eq("").sum())
            if missing:
                add(rows, "PENDIENTE", field,
                    "Requiere fuente técnica y/o validación local; no rellenar por suposición.",
                    f"{missing}/{len(df)}")
                warnings += 1
            else:
                add(rows, "OK", field, "Campo diligenciado en todos los registros.")

        if "evidence_status" in df.columns:
            counts = df["evidence_status"].fillna("sin_estado").value_counts()
            for status, count in counts.items():
                add(rows, "INFO", "estado_evidencia", str(status), int(count))

    if REFERENCES.exists():
        refs = pd.read_csv(REFERENCES, nrows=0).columns.tolist()
        missing_cols = [c for c in REFERENCE_COLUMNS if c not in refs]
        if missing_cols:
            add(rows, "ERROR", "plantilla_referencias",
                "Faltan columnas: " + ", ".join(missing_cols))
            errors += 1
        else:
            add(rows, "OK", "plantilla_referencias",
                "Plantilla de referencias trazables reconocida.")
    else:
        add(rows, "ERROR", "plantilla_referencias",
            f"No existe {REFERENCES.relative_to(ROOT)}")
        errors += 1

    if REFERENCE_RECORDS.exists():
        records = pd.read_csv(REFERENCE_RECORDS, dtype=str, keep_default_na=False)
        missing_cols = [c for c in REFERENCE_COLUMNS if c not in records.columns]
        if missing_cols:
            add(rows, "ERROR", "registros_referencias",
                "Faltan columnas: " + ", ".join(missing_cols))
            errors += 1
        else:
            catalog_ids = set(df["crop_id"].dropna().astype(str)) if "crop_id" in df else set()
            invalid_crops = sorted(set(records["crop_id"]) - catalog_ids)
            if invalid_crops:
                add(rows, "ERROR", "registros_referencias",
                    "Cultivos sin catálogo: " + ", ".join(invalid_crops))
                errors += 1

            statuses = set(records["evidence_status"]) - REFERENCE_STATUSES
            if statuses:
                add(rows, "ERROR", "registros_referencias",
                    "Estados de evidencia no reconocidos: " + ", ".join(sorted(statuses)))
                errors += 1

            pending_values = records[
                records["evidence_status"].eq("pending_local_validation")
                & records["value"].str.strip().ne("")
            ]
            if not pending_values.empty:
                add(rows, "ERROR", "registros_referencias",
                    "Los registros pendientes deben conservar value vacío.",
                    len(pending_values))
                errors += 1

            unsupported = records[
                records["evidence_status"].eq("reference_only")
                & (records["source_id"].str.strip().eq("") | records["source_url"].str.strip().eq(""))
            ]
            if not unsupported.empty:
                add(rows, "ERROR", "registros_referencias",
                    "Las referencias deben tener source_id y source_url.",
                    len(unsupported))
                errors += 1

            if TECHNICAL_SOURCES.exists():
                source_ids = set(pd.read_csv(
                    TECHNICAL_SOURCES, dtype=str, keep_default_na=False
                )["source_id"])
                unknown_sources = sorted(
                    set(records["source_id"].str.strip()) - {""} - source_ids
                )
                if unknown_sources:
                    add(rows, "ERROR", "registros_referencias",
                        "Fuentes sin registro: " + ", ".join(unknown_sources))
                    errors += 1
                else:
                    add(rows, "OK", "registros_referencias",
                        "Referencias normalizadas, con cultivos y fuentes trazables.",
                        len(records))
            else:
                add(rows, "ERROR", "registros_referencias",
                    f"No existe {TECHNICAL_SOURCES.relative_to(ROOT)}")
                errors += 1
    else:
        add(rows, "ADVERTENCIA", "registros_referencias",
            "Aún no se generó el archivo normalizado de referencias.")
        warnings += 1

    if LEGACY_CATALOG.exists():
        legacy = pd.read_csv(LEGACY_CATALOG)
        legacy_count = int(legacy.iloc[:, 0].nunique()) if not legacy.empty else 0
        add(rows, "INFO", "catalogo_secundario",
            "Catálogo descriptivo anterior conservado; no sustituye al catálogo principal.",
            legacy_count)
    else:
        add(rows, "ADVERTENCIA", "catalogo_secundario",
            "No se encontró el catálogo descriptivo secundario.")
        warnings += 1

    report = pd.DataFrame(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT, index=False, encoding="utf-8-sig")

    print("VALIDACIÓN AGRONÓMICA")
    print(f"Catálogo principal: {len(df)} registros" if not df.empty else "Catálogo principal: no disponible")
    print(f"Errores estructurales: {errors}")
    print(f"Campos o verificaciones pendientes: {warnings}")
    print(f"Informe: {REPORT}")
    if not report.empty:
        print(report.to_string(index=False))
    print()
    if errors:
        print("RESULTADO: REVISAR ERRORES ESTRUCTURALES.")
        raise SystemExit(1)
    print("RESULTADO: ESTRUCTURA VÁLIDA; LOS PENDIENTES AGRONÓMICOS SIGUEN SIN VALIDAR.")
    print("No se generaron aptitudes ni recomendaciones.")

if __name__ == "__main__":
    main()
