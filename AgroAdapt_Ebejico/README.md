# AgroAdapt Ebéjico — paquete EVA e Integrante 2

Este paquete contiene el módulo del Integrante 2 y la base EVA 2019–2025 que se va a procesar para Ebéjico, Antioquia.

## Qué incluye

- `modules/`: cargador EVA, catálogo de cultivos y modelo multicriterio de rotaciones.
- `scripts/process_eva.py`: procesa la base EVA y genera archivos de salida.
- `data/raw/eva/eva_2019_2025_base_agricola.csv`: CSV original suministrado. No editarlo.
- `data/processed/`: catálogo agronómico inicial y resultados procesados.
- `docs/`: criterios y contrato de integración con el Integrante 3.

## Ejecutar en WSL (Ubuntu)

Abre la terminal integrada de VS Code y ejecuta los comandos desde la carpeta raíz `AgroAdapt_Ebejico`.

Si descargaste/descomprimiste este paquete dentro de `Proyecto_NASA`, la ruta de la captura es:

```bash
cd "/mnt/c/Users/Emmag/OneDrive/Escritorio/Proyecto_NASA/AgroAdapt_Ebejico"
```

Comprueba que estás en la carpeta correcta:

```bash
pwd
ls
```

Deben aparecer `modules`, `scripts`, `data`, `docs` y `README.md`.

Crea y activa un entorno virtual (solo la primera vez):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install pandas
```

En las siguientes sesiones, solo necesitas:

```bash
cd "/mnt/c/Users/Emmag/OneDrive/Escritorio/Proyecto_NASA/AgroAdapt_Ebejico"
source .venv/bin/activate
```

Ejecuta el procesamiento:

```bash
.venv/bin/python scripts/process_eva.py data/raw/eva/eva_2019_2025_base_agricola.csv
```

Usa `.venv/bin/python` para ejecutar los comandos del proyecto: en algunos entornos WSL, `python3` puede resolver al intérprete global y no cargar los paquetes instalados en `.venv`.

## Archivos que debe producir

Después de ejecutar el script, revisa:

- `data/processed/eva_ebejico_records.csv`: registros originales filtrados para Ebéjico.
- `data/processed/eva_ebejico_crop_summary.csv`: resumen por cultivo y año.
- `data/processed/eva_ebejico_crop_presence.csv`: presencia productiva municipal y contraste con el catálogo agronómico.

## Validaciones incorporadas

- Filtra por código DANE/DIVIPOLA `05240`.
- Reconoce encabezados con tildes de la base EVA compartida.
- Convierte decimales escritos con coma o punto a números.
- Comprueba que se hayan encontrado registros de Ebéjico.
- Informa cuántos valores numéricos quedaron válidos.

## Importante para el proyecto

EVA aporta evidencia de producción a escala municipal. No indica en qué vereda o parcela está cada cultivo, ni demuestra por sí sola que una especie sea apta para una zona específica. Los cultivos reportados deben contrastarse con UMATA/Secretaría de Agricultura, productores y fuentes técnicas antes de usarlos como recomendación o como rotación definitiva.

El catálogo agronómico inicial conserva estados `pending_local_validation`. No se rellenan requerimientos de suelo, clima o agua sin fuente verificable.


## Segunda etapa: análisis temporal EVA

Después de procesar la base municipal, ejecuta:

```bash
.venv/bin/python scripts/analyze_eva_trends.py
```

Genera:
- `data/processed/eva_ebejico_annual_indicators.csv`
- `data/processed/eva_ebejico_trends.csv`
- `docs/analisis_tendencias_eva.md`

Las tendencias comparan primer y último año disponible por cultivo. Son indicadores municipales y no equivalen a aptitud de parcela ni recomendación de rotación.


## Tercera etapa: catálogo agronómico preliminar

Archivo: `data/processed/catalogo_agronomico_ebejico.csv`. Los atributos técnicos permanecen pendientes de validación; no usar aún como motor de recomendaciones.


## Integración preparada (Integrante 2)
Activa el entorno virtual y sincroniza las fichas técnicas con el catálogo canónico:

```bash
.venv/bin/python -m scripts.sync_agronomic_catalog
.venv/bin/python -m scripts.validate_agronomic_data
.venv/bin/python -m scripts.check_integration_readiness
```

La sincronización actualiza `data/processed/agronomic_reference_records.csv` y agrega los identificadores de fuente a `technical_source` en `crops_catalog.csv`. Conserva vacíos los atributos pendientes y el estado `pending_local_validation`.

El chequeo ambiental lee `data/processed/environmental_indicators.csv` y genera `data/processed/environmental_readiness.csv`. La plantilla `environmental_indicators_template.csv` define el formato que debe entregar el Integrante 1. `environment_demo.csv` sigue siendo exclusivamente para la demostración de la interfaz. No se inventan temperaturas, humedad, suelos ni pendientes.

Las plantillas de `data/outputs/` documentan el contrato para el Integrante 3; no son evaluaciones ni recomendaciones. Las salidas reales solo deben generarse después de validar los datos y aplicar el modelo.
Consulta `docs/contrato_integracion_integrantes.md`.
