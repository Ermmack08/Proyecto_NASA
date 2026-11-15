AGROADAPT EBEJICO — INTEGRACION AGRONOMICA

Archivos de datos:
- agronomic_sources_register.csv: registro bibliográfico inicial por cultivo.
- crop_identity_review.csv: identidades que requieren confirmación local.
- fichas_agronomicas_bloque1.csv y fuentes_tecnicas_bloque1.csv: referencias y atributos con su alcance y estado de evidencia.
- agronomic_reference_records.csv: registros normalizados generados desde las fichas, relacionados por crop_id y source_id.
- crops_catalog.csv: catálogo canónico; conserva `pending_local_validation` mientras falte validación local.

Sincronización desde la raíz AgroAdapt_Ebejico:
```bash
.venv/bin/python -m scripts.sync_agronomic_catalog
.venv/bin/python -m scripts.validate_agronomic_data
```

IMPORTANTE
Los registros `reference_only` son referencias publicadas fuera de una validación de lote en Ebéjico. Los campos `pending_local_validation` deben permanecer vacíos hasta contar con fuentes o datos locales verificables. El estado de la ficha no cambia a `verified` por ejecutar el script.
