# Actualización incremental — Integrante 2

Esta actualización se aplica sobre la carpeta existente `AgroAdapt_Ebejico`.
No reemplaza datos EVA, catálogos, plantillas ambientales, páginas Streamlit ni archivos del Integrante 1/3.

## Archivos incluidos
- `scripts/validate_agronomic_data.py` (nuevo): valida estructura del catálogo principal, los 12 IDs esperados y la plantilla de referencias. Genera `data/processed/agronomic_validation_report.csv`.
- `modules/rotation_model.py` (reemplaza): evita generar puntaje total si faltan criterios o existen restricciones bloqueantes. Añade `score` como alias de compatibilidad con la página Streamlit existente, manteniendo `total_score` como campo oficial.

## Aplicación
Extraer el ZIP desde la raíz del proyecto, permitiendo reemplazar `modules/rotation_model.py` y agregando el script nuevo. No borrar archivos.

## Ejecución
```bash
cd "/mnt/c/Users/Emmag/OneDrive/Escritorio/Proyecto_NASA/AgroAdapt_Ebejico"
source .venv/bin/activate
.venv/bin/python -m scripts.validate_agronomic_data
.venv/bin/python -m compileall modules scripts
```

El validador puede informar campos agronómicos pendientes. Eso es esperado: no inventa datos ni impide conservar el catálogo. Solo los errores estructurales hacen que termine con código distinto de cero.

## Prueba aislada del motor
```bash
.venv/bin/python - <<'PY'
from modules.rotation_model import compare_rotations

tests = [
    {
        "name": "Alternativa completa de prueba",
        "scores": {"climate": 80, "soil": 75, "soil_health": 90,
                   "production": 70, "farmer_priority": 85},
        "limitations": ["Puntajes sintéticos para probar el código."],
        "evidence_status": "reference_only"
    },
    {
        "name": "Alternativa incompleta de prueba",
        "scores": {"climate": 80, "soil": None, "soil_health": 90,
                   "production": 70, "farmer_priority": 85}
    },
    {
        "name": "Alternativa bloqueada de prueba",
        "scores": {"climate": 80, "soil": 75, "soil_health": 90,
                   "production": 70, "farmer_priority": 85},
        "blocking_constraints": ["Restricción de ejemplo; no es un diagnóstico real."]
    }
]
for result in compare_rotations(tests):
    print(result["name"], result["total_score"], result["evidence_status"])
PY
```

Los puntajes del primer escenario son exclusivamente sintéticos para comprobar el cálculo, no son recomendaciones agrícolas.
