"""
Contrato de entrada ambiental para el Integrante 1 -> Integrante 2 -> Integrante 3.
No calcula ni inventa datos. Valida los productos entregados por GIS.
"""
from pathlib import Path
import pandas as pd

ENVIRONMENTAL_FIELDS = [
    "variable_id","variable_name","value","unit","source","product_id",
    "period_start","period_end","temporal_resolution","spatial_resolution",
    "spatial_unit_id","spatial_unit_type","geometry_reference","quality_flag",
    "processing_method","source_url","retrieved_at","evidence_status","limitations"
]
ALLOWED_STATUS = {"verified","modelled","estimated","reference_only","pending"}
CATEGORICAL_VARIABLES = {"textura_suelo", "cobertura_vegetal"}

def load_environmental_indicators(path):
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=ENVIRONMENTAL_FIELDS)
    return pd.read_csv(path)

def validate_environmental_indicators(df):
    errors = []
    missing = [c for c in ENVIRONMENTAL_FIELDS if c not in df.columns]
    if missing:
        errors.append("Faltan columnas: " + ", ".join(missing))
        return errors
    if df["variable_id"].duplicated().any() and df["spatial_unit_id"].isna().all():
        errors.append("variable_id repetido sin identificar unidad espacial; revise el identificador.")
    invalid = sorted(set(df["evidence_status"].dropna()) - ALLOWED_STATUS)
    if invalid:
        errors.append("Estados de evidencia no válidos: " + ", ".join(invalid))
    variable_names = df["variable_name"].fillna("").astype(str).str.strip().str.lower()
    numeric_rows = ~variable_names.isin(CATEGORICAL_VARIABLES)
    values = df.loc[numeric_rows, "value"]
    numeric = pd.to_numeric(values, errors="coerce")
    populated = values.notna() & values.astype(str).str.strip().ne("")
    bad = populated & numeric.isna()
    if bad.any():
        errors.append(f"Hay {int(bad.sum())} valores no numéricos en 'value'.")
    return errors

def summarize_data_readiness(df):
    """Resumen de cobertura; no confunde filas faltantes con valores cero."""
    if df.empty:
        return {"status":"awaiting_integrante_1","rows":0,"variables":[]}
    return {
        "status":"received",
        "rows":int(len(df)),
        "variables":sorted(df["variable_name"].dropna().astype(str).unique().tolist()),
        "sources":sorted(df["source"].dropna().astype(str).unique().tolist()),
        "spatial_units":int(df["spatial_unit_id"].nunique(dropna=True)),
        "missing_values":int(df["value"].isna().sum())
    }
