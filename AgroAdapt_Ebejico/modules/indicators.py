# Cálculo de indicadores ambientales simples.
# No confundir estos indicadores descriptivos con pronósticos meteorológicos.

import pandas as pd

def summarize_environment(df):
    """Resumen para la página de inicio."""
    if df is None or df.empty:
        return {"records": 0, "variables": 0, "is_demo": False}
    metadata = {"date", "source", "is_demo"}
    variables = [
        column for column in df.select_dtypes(include="number").columns
        if column not in metadata
    ]
    is_demo = bool(df["is_demo"].any()) if "is_demo" in df else False
    return {"records": len(df), "variables": len(variables), "is_demo": is_demo}

def monthly_summary(df):
    """Agrupa por mes para visualizar tendencias, si existe columna date."""
    if df is None or df.empty or "date" not in df:
        return pd.DataFrame()
    numeric = [
        column for column in df.select_dtypes(include="number").columns
        if column != "is_demo"
    ]
    if not numeric:
        return pd.DataFrame()
    data = df.copy()
    data["month"] = pd.to_datetime(data["date"]).dt.to_period("M").astype(str)
    return data.groupby("month", as_index=False)[numeric].mean()
