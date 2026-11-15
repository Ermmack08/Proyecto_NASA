# Contrato de integración — Integrantes 1, 2 y 3

## Responsabilidades
- Integrante 1: entrega capas GIS y estadísticas derivadas (no modifica el catálogo ni el modelo agrícola).
- Integrante 2: mantiene EVA, perfiles agronómicos, criterios y motor multicriterio; consume los indicadores GIS.
- Integrante 3: consume las salidas del Integrante 2 y construye interfaz, mapas y dashboard.

## Entrada ambiental del Integrante 1
Archivo acordado: `data/processed/environmental_indicators.csv`.
Plantilla: `data/processed/environmental_indicators_template.csv`.
`data/processed/environment_demo.csv` es exclusivamente una entrada de demostración para la interfaz y no sustituye la entrega del Integrante 1.

Cada fila representa una variable para una unidad espacial y periodo. Campos obligatorios:
`variable_id, variable_name, value, unit, source, product_id, period_start, period_end, temporal_resolution, spatial_resolution, spatial_unit_id, spatial_unit_type, geometry_reference, quality_flag, processing_method, source_url, retrieved_at, evidence_status, limitations`.

Nombres controlados sugeridos:
- `temperatura_media`, `temperatura_minima`, `temperatura_maxima` (°C)
- `precipitacion` (mm; indicar acumulación y periodo)
- `humedad_suelo` (unidad según producto, por ejemplo m³/m³ o %)
- `evapotranspiracion` (mm/día o mm/periodo)
- `elevacion` (m), `pendiente` (% o grados; declarar cuál)
- `ph_suelo` (unidad pH), `textura_suelo` (clase textural), `materia_organica` (%), `profundidad_suelo` (cm)
- `ndvi` (adimensional), `cobertura_vegetal` (clase o %)

No mezclar productos/resoluciones sin conservar metadatos. Los valores modelados, estimados o de referencia deben indicarse en `evidence_status`. Las estadísticas agregadas municipales no deben presentarse como mediciones por finca.

## Salidas del Integrante 2
- `data/processed/crops_catalog.csv`: 12 cultivos EVA y campos agronómicos pendientes/validados.
- `data/processed/agronomic_reference_records.csv`: fichas normalizadas enlazadas por `crop_id` y `source_id`; sus estados distinguen referencias de datos pendientes.
- `data/processed/fuentes_tecnicas_bloque1.csv`: resolución de `source_id` a documento, URL, alcance y limitaciones.
- `data/processed/eva_ebejico_records.csv`, `eva_ebejico_trends.csv`: evidencia productiva EVA.
- `data/processed/environmental_readiness.csv`: cobertura de datos recibidos y brechas.
- `data/outputs/crop_assessment.csv`: evaluación por cultivo, solo cuando los datos necesarios estén disponibles.
- `data/outputs/rotation_alternatives.csv`: alternativas y criterios con trazabilidad.

## Contrato para el Integrante 3
No depender de rutas internas de módulos. Consumir CSV/JSON de `data/outputs` y conservar:
`name, description, scores, total_score, evidence_status, limitations, sources`.
No mostrar un puntaje como recomendación validada cuando `evidence_status` no sea `verified` o `modelled` con metodología documentada.

El contrato de salida incluye `sources` para conservar la trazabilidad. Además de los estados de evidencia, el motor puede informar `insufficient_evidence` cuando faltan criterios y `blocked_by_constraint` cuando existe una restricción bloqueante; estos estados no significan validación local.

Las plantillas `data/outputs/crop_assessment_template.csv` y `data/outputs/rotation_alternatives_template.csv` describen los esquemas para el Integrante 3; no contienen evaluaciones. No se deben renombrar como salidas reales mientras falten datos de entrada o criterios validados.

## Estado inicial
El archivo ambiental plantilla está vacío intencionalmente. El sistema debe funcionar y mostrar `awaiting_integrante_1` hasta recibir los datos geoespaciales.
