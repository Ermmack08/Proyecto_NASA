# AgroAdapt Ebéjico — módulo GIS / NASA

> **Datos ya obtenidos de las APIs de la NASA → carpeta [`nasa_api/`](nasa_api/)**
> - `nasa_api/ebejico_datos_nasa.ipynb`: notebook explicado paso a paso (límite, Sentinel-2, Landsat,
>   NASADEM/SRTM y NASA POWER). Abrir en VS Code o Jupyter y usar **Run All**.
> - `nasa_api/data/processed/`: tablas CSV, mapas GeoTIFF y figuras PNG ya generadas, listas para el dashboard.
> - Instalar dependencias: `pip install -r nasa_api/requirements.txt`

Este módulo conserva la misma raíz y convenciones de la aplicación AgroAdapt.
Su objetivo es producir archivos que consumen el dashboard y el modelo agrícola.

## Requisitos
Python 3.10+ recomendado. En Windows, crear un entorno virtual desde la raíz:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-gis.txt
```

## Orden de ejecución
1. Descargar límite municipal:
```powershell
python scripts/01_download_boundary.py
```
2. Colocar bandas Sentinel-2 L2A B08 y B04 en `data/raw/sentinel/`, luego:
```powershell
python scripts/02_process_satellite.py
```
3. Colocar DEM en `data/raw/srtm/ebejico_dem.tif`, luego:
```powershell
python scripts/03_process_terrain.py
```
4. Descargar NASA POWER:
```powershell
python scripts/04_process_environment.py
```
5. Crear inventario:
```powershell
python scripts/05_generate_metadata.py
```

## Fuentes y precauciones
- Límite municipal: servicio de límites IGAC; código DANE 05240.
- Sentinel-2: preferir producto L2A / reflectancia de superficie; aplicar máscara de nubes
  con SCL o QA antes de calcular NDVI.
- Landsat Collection 2 Level-2: aplicar escala SR (DN * 0.0000275 - 0.2) y usar QA_PIXEL.
- DEM: reproyectar a CRS métrico antes de calcular pendiente.
- NASA POWER: la descarga incluida utiliza el centroide municipal como punto representativo.
  No equivale a una media espacial ni a medición de parcela.
- SMAP y ECOSTRESS: integrar solo tras confirmar producto, resolución, fecha, unidades,
  cobertura y método de reproyección. No interpolar para aparentar mayor resolución.

## Contrato con el integrante 3
Entregar estos productos cuando estén disponibles:
- `data/geographic/ebejico_boundary.geojson`
- `data/processed/vegetation/sentinel2_ndvi_ebejico.tif`
- `data/processed/terrain/dem_utm18n.tif`
- `data/processed/terrain/slope_degrees.tif`
- `data/processed/environmental/nasa_power_daily.csv`

Formato web: GeoJSON EPSG:4326.
Análisis de terreno: EPSG:32618 (UTM 18N).
Ráster: GeoTIFF con CRS, transformación y nodata definidos.
CSV: fechas ISO, unidades documentadas y columna `source`.

## Límites de esta plantilla
- No descarga automáticamente Sentinel-2, Landsat, SRTM, SMAP ni ECOSTRESS.
- El procesamiento NDVI espera bandas ya descargadas y preprocesadas.
- La función de NDVI no aplica por sí misma máscara de nubes ni escala radiométrica.
- La salida es una base técnica; la interpretación agrícola requiere validación local.
