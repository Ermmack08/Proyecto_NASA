"""
Prepara la evaluación agrícola por cultivo cuando lleguen los datos ambientales.
En esta etapa reporta cobertura y brechas; no genera aptitudes ficticias.
"""
from modules.environmental_data import load_environmental_indicators, validate_environmental_indicators

EXPECTED_VARIABLES = {
    "temperature": ["temperatura_media", "temperatura_minima", "temperatura_maxima"],
    "water": ["precipitacion", "humedad_suelo", "evapotranspiracion"],
    "terrain": ["elevacion", "pendiente"],
    "soil": ["ph_suelo", "textura_suelo", "materia_organica", "profundidad_suelo"],
    "vegetation": ["ndvi", "cobertura_vegetal"],
}

def environmental_gaps(df):
    present = set(df["variable_name"].dropna().astype(str).str.lower()) if not df.empty else set()
    return {
        group: [v for v in expected if v not in present]
        for group, expected in EXPECTED_VARIABLES.items()
    }

def build_readiness_report(environmental_csv, output_csv):
    df = load_environmental_indicators(environmental_csv)
    errors = validate_environmental_indicators(df)
    if errors:
        raise ValueError("Datos ambientales no válidos: " + " | ".join(errors))
    gaps = environmental_gaps(df)
    import pandas as pd
    rows = []
    for group, missing in gaps.items():
        rows.append({
            "componente":group,
            "estado":"pendiente_integrante_1" if missing else "datos_recibidos_revisar_calidad",
            "variables_faltantes":";".join(missing),
            "observacion":"No se calcula aptitud hasta disponer de datos compatibles y perfiles agronómicos validados."
        })
    result = pd.DataFrame(rows)
    result.to_csv(output_csv,index=False,encoding="utf-8-sig")
    return result
