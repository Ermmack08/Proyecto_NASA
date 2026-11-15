# Contrato de integración con el integrante 3

## Archivos compartidos
- Catálogo: `data/processed/crops_catalog.csv`
- Referencias agronómicas normalizadas: `data/processed/agronomic_reference_records.csv` (relación por `crop_id`; conservar `source_id`, `source_url`, `evidence_status` y `notes`).
- Registro de fuentes: `data/processed/fuentes_tecnicas_bloque1.csv`.
- EVA procesada: `data/processed/eva_ebejico_records.csv`
- Resumen EVA: `data/processed/eva_ebejico_crop_summary.csv`
- Indicadores ambientales del Integrante 1: `data/processed/environmental_indicators.csv`, una vez entregados y validados.
- Escenarios: salida de `modules.rotation_model.to_streamlit_contract()`

Los archivos `data/outputs/*_template.csv` solo definen esquemas. No mostrarlos como resultados ni como recomendaciones.

## Forma de cada escenario
```python
{
    "name": "Nombre de la alternativa",
    "description": "Descripción técnica breve",
    "scores": {
        "climate": 0-100,
        "soil": 0-100,
        "soil_health": 0-100,
        "production": 0-100,
        "farmer_priority": 0-100
    },
    "limitations": "Supuestos, restricciones y datos faltantes",
    "total_score": 0-100,
    "evidence_status": "verified | modelled | reference_only | pending_local_validation | insufficient_evidence | blocked_by_constraint",
    "sources": ["Identificadores o referencias trazables"]
}
```

`insufficient_evidence` y `blocked_by_constraint` son estados de evaluación: indican, respectivamente, que faltan criterios para calcular un resultado o que una restricción impide evaluarlo. No equivalen a evidencia agronómica local verificada.

## Integración recomendada
La interfaz debe consumir las salidas estructuradas de `data/outputs/`; no debe importar el motor ni recalcular ponderaciones dentro de Streamlit. Cuando existan resultados, debe mostrar `total_score`, `scores`, `limitations`, `sources` y `evidence_status`.

Mientras esas salidas no se hayan generado, la interfaz puede mantener el modo demostrativo, claramente rotulado como sintético y no recomendatorio.
