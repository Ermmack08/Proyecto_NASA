#!/usr/bin/env python3
"""Synchronize technical fichas into the canonical catalog and reference table."""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import AGRONOMIC_REFERENCES_FILE, CROPS_FILE, PROCESSED_DIR
from modules.crop_catalog import REFERENCE_FIELDS

FICHAS_FILE = PROCESSED_DIR / "fichas_agronomicas_bloque1.csv"
SOURCES_FILE = PROCESSED_DIR / "fuentes_tecnicas_bloque1.csv"

FICHA_FIELDS = {
    "crop_id", "crop", "attribute", "value", "unit", "evidence_level",
    "region_scope", "cultivar_scope", "source_id", "source_url", "notes",
}
SOURCE_FIELDS = {
    "source_id", "institution", "document_title", "url",
    "geographic_scope", "use_and_limitations",
}


def read_csv(path: Path, required: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo requerido: {path}")
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{path.name}: faltan columnas: {', '.join(missing)}")
    return frame


def normalize_references(fichas: pd.DataFrame, sources: pd.DataFrame,
                         catalog_ids: set[str]) -> pd.DataFrame:
    source_by_id = sources.set_index("source_id").to_dict(orient="index")
    output = []

    for row in fichas.to_dict(orient="records"):
        crop_id = row["crop_id"].strip()
        if crop_id not in catalog_ids:
            raise ValueError(f"El cultivo {crop_id!r} de las fichas no existe en el catálogo.")

        source_id = row["source_id"].strip()
        source = source_by_id.get(source_id)
        if source_id and source is None:
            raise ValueError(f"Fuente no registrada: {source_id} ({row['crop']}).")

        status = row["evidence_level"].strip()
        if status == "pending":
            status = "pending_local_validation"
        elif status not in {"verified", "reference_only", "pending_local_validation"}:
            raise ValueError(f"Estado de evidencia no reconocido: {status!r}.")

        if status == "reference_only" and (not source_id or not row["source_url"].strip()):
            raise ValueError(
                f"La referencia {row['crop']} / {row['attribute']} no tiene fuente y URL."
            )
        if status == "pending_local_validation" and row["value"].strip():
            raise ValueError(
                f"El dato pendiente {row['crop']} / {row['attribute']} no debe tener valor."
            )

        institution = source["institution"] if source else ""
        title = source["document_title"] if source else ""
        year_matches = re.findall(r"\b(?:19|20)\d{2}\b", f"{institution} {title}")
        source_url = row["source_url"].strip() or (source["url"] if source else "")
        geographic_scope = row["region_scope"].strip()
        if not geographic_scope and source:
            geographic_scope = source["geographic_scope"]

        notes = []
        if row["cultivar_scope"].strip():
            notes.append(f"Alcance varietal/sistema: {row['cultivar_scope'].strip()}")
        if row["notes"].strip():
            notes.append(row["notes"].strip())
        if source and source["use_and_limitations"].strip():
            notes.append(f"Limitaciones de la fuente: {source['use_and_limitations'].strip()}")

        output.append({
            "crop_id": crop_id,
            "source_id": source_id,
            "crop": row["crop"].strip(),
            "attribute": row["attribute"].strip(),
            "value": row["value"].strip(),
            "unit": row["unit"].strip(),
            "source_organization": institution,
            "document_title": title,
            "publication_year": year_matches[0] if year_matches else "",
            "geographic_scope": geographic_scope,
            "source_url": source_url,
            "evidence_status": status,
            "notes": " ".join(notes),
        })

    return pd.DataFrame(output, columns=REFERENCE_FIELDS)


def update_catalog_sources(catalog: pd.DataFrame, fichas: pd.DataFrame) -> pd.DataFrame:
    sources_by_crop = (
        fichas.loc[fichas["source_id"].str.strip().ne("")]
        .groupby("crop_id")["source_id"]
        .apply(lambda values: sorted(set(value.strip() for value in values if value.strip())))
        .to_dict()
    )

    for index, row in catalog.iterrows():
        existing = row.get("technical_source", "").strip()
        source_ids = sources_by_crop.get(row["crop_id"], [])
        if not source_ids:
            continue
        existing_parts = [part.strip() for part in re.split(r"[;,|]", existing) if part.strip()]
        for source_id in source_ids:
            if source_id not in existing_parts:
                existing_parts.append(source_id)
        catalog.at[index, "technical_source"] = "; ".join(existing_parts)

    return catalog


def main() -> None:
    fichas = read_csv(FICHAS_FILE, FICHA_FIELDS)
    sources = read_csv(SOURCES_FILE, SOURCE_FIELDS)
    catalog = read_csv(CROPS_FILE, {"crop_id", "technical_source", "evidence_status"})

    if catalog["crop_id"].duplicated().any():
        raise ValueError("El catálogo contiene crop_id duplicados.")
    if sources["source_id"].duplicated().any():
        raise ValueError("El registro de fuentes contiene source_id duplicados.")

    catalog_ids = set(catalog["crop_id"])
    references = normalize_references(fichas, sources, catalog_ids)
    catalog = update_catalog_sources(catalog, fichas)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    references.to_csv(AGRONOMIC_REFERENCES_FILE, index=False, encoding="utf-8-sig")
    catalog.to_csv(CROPS_FILE, index=False, encoding="utf-8-sig")

    pending_count = int(references["evidence_status"].eq("pending_local_validation").sum())
    reference_count = int(references["evidence_status"].eq("reference_only").sum())
    print("Sincronización agronómica completada.")
    print(f"Registros trazables: {len(references)}")
    print(f"Referencias generales: {reference_count}")
    print(f"Atributos pendientes: {pending_count}")
    print(f"Catálogo: {CROPS_FILE}")
    print(f"Referencias: {AGRONOMIC_REFERENCES_FILE}")
    print("Los estados del catálogo se conservan; no se marca ningún dato como validado localmente.")


if __name__ == "__main__":
    main()
