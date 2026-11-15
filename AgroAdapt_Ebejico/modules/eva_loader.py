"""
Carga y normalización de archivos EVA de UPRA/SIPRA o Datos Abiertos Colombia.
Admite encabezados con tildes y decimales escritos con coma o punto.
"""
import re
import unicodedata
from pathlib import Path
import pandas as pd

DANE_EBEJICO = "05240"

COLUMN_ALIASES = {
    "codigo_municipio": [
        "codigo_dane_municipio", "codigo_dane_del_municipio",
        "c_digo_dane_municipio", "c_d_mun", "codigo_municipio",
        "cod_municipio"
    ],
    "municipio": ["municipio"],
    "departamento": ["departamento"],
    "cultivo": ["cultivo"],
    "grupo_cultivo": ["grupo_cultivo", "grupo_de_cultivo"],
    "subgrupo": ["subgrupo", "subgrupo_de_cultivo"],
    "anio": ["ano", "anio", "a_o"],
    "periodo": ["periodo"],
    "area_sembrada_ha": ["area_sembrada", "area_sembrada_ha", "rea_sembrada"],
    "area_cosechada_ha": ["area_cosechada", "area_cosechada_ha", "rea_cosechada"],
    "produccion_t": ["produccion", "produccion_t", "producci_n_t"],
    "rendimiento_t_ha": ["rendimiento", "rendimiento_t_ha"],
    "ciclo_cultivo": ["ciclo_del_cultivo", "ciclo_de_cultivo", "ciclo_cultivo"],
    "nombre_cientifico": ["nombre_cientifico", "nombre_cientifico_del_cultivo"],
}

NUMERIC_COLUMNS = [
    "area_sembrada_ha", "area_cosechada_ha",
    "produccion_t", "rendimiento_t_ha"
]

def normalize_name(value):
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")

def normalize_columns(df):
    lookup = {normalize_name(col): col for col in df.columns}
    rename = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            key = normalize_name(alias)
            if key in lookup:
                rename[lookup[key]] = canonical
                break
    return df.rename(columns=rename)

def to_number(series):
    """Convierte '1.234,56', '1234,56' o '1234.56' a número."""
    values = series.astype("string").str.strip()
    values = values.str.replace(r"(?<=\d)\.(?=\d{3}(?:\D|$))", "", regex=True)
    values = values.str.replace(",", ".", regex=False)
    return pd.to_numeric(values, errors="coerce")

def load_eva_csv(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo EVA: {path}")
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            # Mantener columnas como texto evita perder códigos DANE y
            # permite normalizar decimales mezclados (coma/punto).
            df = pd.read_csv(path, encoding=encoding, dtype="string", low_memory=False)
            break
        except UnicodeDecodeError as exc:
            last_error = exc
    else:
        raise last_error
    df = normalize_columns(df)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = to_number(df[col])
    return df

def filter_ebejico(df):
    data = df.copy()
    if "codigo_municipio" in data.columns:
        codes = (data["codigo_municipio"].astype("string")
                 .str.replace(r"\.0$", "", regex=True)
                 .str.replace(r"\D", "", regex=True)
                 .str.zfill(5))
        data = data.loc[codes == DANE_EBEJICO]
    elif {"municipio", "departamento"}.issubset(data.columns):
        municipio = data["municipio"].astype("string").str.strip().str.casefold()
        departamento = data["departamento"].astype("string").str.strip().str.casefold()
        data = data.loc[
            municipio.isin(["ebejico", "ebéjico"])
            & departamento.isin(["antioquia", "05", "5"])
        ]
    else:
        raise ValueError(
            "No se reconocen columnas de municipio. Columnas: "
            + ", ".join(map(str, data.columns))
        )
    if data.empty:
        raise ValueError(
            "No se encontraron registros de Ebéjico (DANE 05240). "
            "Verifica que el archivo corresponda a EVA y contenga ese municipio."
        )
    return data

def summarize_eva(df):
    if "cultivo" not in df.columns:
        raise ValueError("La tabla EVA no contiene la columna 'cultivo'.")
    aggregations = {}
    for col in ("area_sembrada_ha", "area_cosechada_ha", "produccion_t"):
        if col in df.columns:
            aggregations[col] = "sum"
    if "rendimiento_t_ha" in df.columns:
        aggregations["rendimiento_t_ha"] = "mean"
    group_cols = ["cultivo"]
    if "anio" in df.columns:
        group_cols.append("anio")
    if not aggregations:
        return df[group_cols].drop_duplicates().sort_values(group_cols)
    return (df.groupby(group_cols, dropna=False)
              .agg(aggregations).reset_index()
              .sort_values(group_cols))

def summarize_crop_presence(df):
    """Resumen municipal por cultivo, sin convertir presencia en recomendación."""
    aggregations = {}
    for col in ("area_sembrada_ha", "area_cosechada_ha", "produccion_t"):
        if col in df.columns:
            aggregations[col] = "sum"
    if "anio" in df.columns:
        aggregations["anio"] = lambda s: ", ".join(sorted(set(s.dropna().astype(str))))
    if not aggregations:
        return df[["cultivo"]].drop_duplicates()
    out = df.groupby("cultivo", dropna=False).agg(aggregations).reset_index()
    if "anio" in out.columns:
        out = out.rename(columns={"anio": "anios_reportados"})
    return out.sort_values("cultivo")
