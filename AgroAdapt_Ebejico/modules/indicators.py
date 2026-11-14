# Cálculo de indicadores ambientales simples.
# No confundir estos indicadores descriptivos con pronósticos meteorológicos.

import pandas as pd

def summarize_environment(df):
    """Resumen para la página de inicio."""
    if df is None or df.empty:
        return {"records": 0, "variables": 0, "is_demo": False}
    variables = [c for c in df.columns if c not in ("date", "source", "is_demo")]
    is_demo = bool(df["is_demo"].astype(str).str.lower().isin(["true", "1"]).any()) if "is_demo" in df else False
    return {"records": len(df), "variables": len(variables), "is_demo": is_demo}

def monthly_summary(df):
    """Agrupa por mes para visualizar tendencias, si existe columna date."""
    if df is None or df.empty or "date" not in df:
        return pd.DataFrame()
    numeric = df.select_dtypes(include="number").columns.tolist()
    if not numeric:
        return pd.DataFrame()
    data = df.copy()
    data["month"] = pd.to_datetime(data["date"]).dt.to_period("M").astype(str)
    return data.groupby("month", as_index=False)[numeric].mean()
