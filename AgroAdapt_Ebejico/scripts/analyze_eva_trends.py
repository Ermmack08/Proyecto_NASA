#!/usr/bin/env python3
"""Indicadores temporales EVA para Ebéjico (DANE 05240)."""
from pathlib import Path
import argparse
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/processed/eva_ebejico_records.csv"
NUMERIC = ["area_sembrada_ha", "area_cosechada_ha", "produccion_t"]

def pct(first, last):
    if pd.isna(first) or pd.isna(last) or first == 0:
        return None
    return round((last - first) / abs(first) * 100, 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default=str(DEFAULT_INPUT))
    args = parser.parse_args()
    path = Path(args.input)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")

    df = pd.read_csv(path, dtype={"anio": "string"})
    required = {"cultivo", "anio", *NUMERIC}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Faltan columnas: " + ", ".join(sorted(missing)))
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["cultivo", "anio"]).copy()
    df["anio"] = df["anio"].astype(int)

    # Agregados anuales municipales. Rendimiento ponderado = producción / área cosechada.
    annual = (df.groupby(["cultivo", "anio"], as_index=False)
        .agg(area_sembrada_ha=("area_sembrada_ha", "sum"),
             area_cosechada_ha=("area_cosechada_ha", "sum"),
             produccion_t=("produccion_t", "sum"),
             registros=("cultivo", "size")))
    annual["rendimiento_calculado_t_ha"] = (
        annual["produccion_t"] / annual["area_cosechada_ha"].where(annual["area_cosechada_ha"] > 0)
    ).round(4)
    annual["porcentaje_area_cosechada"] = (
        annual["area_cosechada_ha"] / annual["area_sembrada_ha"].where(annual["area_sembrada_ha"] > 0) * 100
    ).round(2)

    rows = []
    for crop, g in annual.groupby("cultivo"):
        g = g.sort_values("anio")
        a, b = g.iloc[0], g.iloc[-1]
        rows.append({
            "cultivo": crop, "anios_con_registro": len(g),
            "anio_inicial": int(a.anio), "anio_final": int(b.anio),
            "area_sembrada_inicial_ha": a.area_sembrada_ha,
            "area_sembrada_final_ha": b.area_sembrada_ha,
            "variacion_area_sembrada_pct": pct(a.area_sembrada_ha, b.area_sembrada_ha),
            "area_cosechada_inicial_ha": a.area_cosechada_ha,
            "area_cosechada_final_ha": b.area_cosechada_ha,
            "variacion_area_cosechada_pct": pct(a.area_cosechada_ha, b.area_cosechada_ha),
            "produccion_inicial_t": a.produccion_t, "produccion_final_t": b.produccion_t,
            "variacion_produccion_pct": pct(a.produccion_t, b.produccion_t),
            "rendimiento_inicial_t_ha": a.rendimiento_calculado_t_ha,
            "rendimiento_final_t_ha": b.rendimiento_calculado_t_ha,
            "variacion_rendimiento_pct": pct(a.rendimiento_calculado_t_ha, b.rendimiento_calculado_t_ha),
            "advertencia": "Comparar primer y último año disponible; revisar años faltantes y cambios metodológicos."
        })
    trends = pd.DataFrame(rows).sort_values("cultivo")

    out = ROOT / "data/processed"
    docs = ROOT / "docs"
    out.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    annual.to_csv(out / "eva_ebejico_annual_indicators.csv", index=False, encoding="utf-8-sig")
    trends.to_csv(out / "eva_ebejico_trends.csv", index=False, encoding="utf-8-sig")

    latest = annual.sort_values("anio").groupby("cultivo").tail(1).sort_values("area_sembrada_ha", ascending=False)
    lines = [
        "# Análisis temporal EVA — Ebéjico", "",
        f"- Registros: {len(df)}", f"- Cultivos: {df.cultivo.nunique()}",
        f"- Periodo: {int(df.anio.min())}–{int(df.anio.max())}", "",
        "## Interpretación y límites", "",
        "Los datos son agregados municipales, no ubican parcelas ni describen lotes individuales.",
        "El rendimiento se calcula como producción total / área cosechada total, no como promedio simple de rendimientos.",
        "Las variaciones comparan el primer y último año disponible por cultivo; pueden existir años faltantes.",
        "Los cambios también pueden reflejar cobertura estadística, clasificación o metodología EVA.", "",
        "## Último año disponible por cultivo", ""
    ]
    for _, r in latest.iterrows():
        y = r.rendimiento_calculado_t_ha
        lines.append(f"- {r.cultivo}: {r.area_sembrada_ha:.2f} ha sembradas en {int(r.anio)}; producción {r.produccion_t:.2f} t; rendimiento calculado {y if pd.notna(y) else 'no calculable'} t/ha.")
    lines += ["", "## Precauciones para AgroAdapt", "",
        "1. No sumar hectáreas de distintos años para presentarlas como área actual.",
        "2. No convertir presencia EVA en recomendación agronómica.",
        "3. No forzar rotaciones anuales sobre cultivos permanentes o semipermanentes.",
        "4. Completar ciclo, familia, agua, clima, suelo, raíces, plagas y manejo con fuentes técnicas y validación local.",
        "5. Mostrar años faltantes y estado de evidencia en la interfaz."]
    (docs / "analisis_tendencias_eva.md").write_text("\n".join(lines), encoding="utf-8")

    print("ANÁLISIS EVA COMPLETADO")
    print(f"Registros: {len(df)} | Cultivos: {df.cultivo.nunique()} | Años: {int(df.anio.min())}-{int(df.anio.max())}")
    print(f"Generado: {out / 'eva_ebejico_annual_indicators.csv'}")
    print(f"Generado: {out / 'eva_ebejico_trends.csv'}")
    print(f"Generado: {docs / 'analisis_tendencias_eva.md'}")

if __name__ == "__main__":
    main()
