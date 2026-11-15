"""
Catálogo agronómico de cultivos.

La ficha separa:
1) presencia/producción municipal (EVA),
2) requerimientos agronómicos (fuentes técnicas),
3) observaciones locales pendientes de validar.

No se rellenan valores desconocidos con supuestos. Las celdas vacías significan
"sin dato verificado", no cero ni ausencia del requerimiento.
"""

from pathlib import Path
import pandas as pd
from config import AGRONOMIC_REFERENCES_FILE, CROPS_FILE

REQUIRED_FIELDS = [
    "crop_id", "crop", "scientific_name", "family", "crop_cycle",
    "cycle_days_min", "cycle_days_max", "water_requirement",
    "temperature_min_c", "temperature_opt_min_c", "temperature_opt_max_c",
    "temperature_max_c", "soil_texture", "soil_ph_min", "soil_ph_max",
    "root_depth_cm", "nutrient_notes", "soil_cover_notes",
    "rotation_notes", "local_evidence", "technical_source",
    "evidence_status"
]

REFERENCE_FIELDS = [
    "crop_id", "source_id", "crop", "attribute", "value", "unit",
    "source_organization", "document_title", "publication_year",
    "geographic_scope", "source_url", "evidence_status", "notes"
]

def load_crop_catalog(path: str | Path = CROPS_FILE) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=REQUIRED_FIELDS)
    return pd.read_csv(path)

def load_crop_references(path: str | Path = AGRONOMIC_REFERENCES_FILE) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=REFERENCE_FIELDS)
    references = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [field for field in REFERENCE_FIELDS if field not in references.columns]
    if missing:
        raise ValueError(f"Faltan columnas en las referencias agronómicas: {', '.join(missing)}")
    return references

def validate_crop_catalog(df: pd.DataFrame) -> list[str]:
    """Devuelve errores de estructura sin inventar ni corregir datos."""
    errors = []
    missing = [field for field in REQUIRED_FIELDS if field not in df.columns]
    if missing:
        errors.append(f"Faltan columnas obligatorias: {', '.join(missing)}")
    if "crop_id" in df and df["crop_id"].duplicated().any():
        errors.append("Hay crop_id duplicados.")
    if "evidence_status" in df:
        allowed = {"verified", "reference_only", "pending_local_validation"}
        invalid = sorted(set(df["evidence_status"].dropna()) - allowed)
        if invalid:
            errors.append(f"Estados de evidencia no reconocidos: {invalid}")
    return errors

def get_crop(crop_id: str, df: pd.DataFrame | None = None) -> dict:
    df = df if df is not None else load_crop_catalog()
    if df.empty or "crop_id" not in df:
        raise ValueError("El catálogo de cultivos está vacío o no tiene crop_id.")
    match = df.loc[df["crop_id"].astype(str) == str(crop_id)]
    if match.empty:
        raise KeyError(f"No se encontró el cultivo: {crop_id}")
    return match.iloc[0].where(match.iloc[0].notna(), None).to_dict()

def get_crop_profile(
    crop_id: str,
    df: pd.DataFrame | None = None,
    references: pd.DataFrame | None = None
) -> dict:
    """Devuelve el registro canónico junto con sus referencias trazables."""
    profile = get_crop(crop_id, df)
    references = references if references is not None else load_crop_references()
    if not references.empty and "crop_id" not in references:
        raise ValueError("Las referencias agronómicas no tienen la columna crop_id.")
    if references.empty:
        profile["agronomic_references"] = []
        return profile

    crop_references = references.loc[
        references["crop_id"].astype(str) == str(crop_id)
    ]
    crop_references = crop_references.astype(object).where(
        pd.notna(crop_references), None
    )
    profile["agronomic_references"] = crop_references.to_dict(orient="records")
    return profile
