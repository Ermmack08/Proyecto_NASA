# AgroAdapt Ebéjico — Integrante 1 (GIS / NASA)

Paso 1 del flujo: **Diagnóstico** con Sentinel-2 y Landsat 8/9.

## Fuentes (APIs abiertas, sin llave)
| Dato | API | Uso |
|---|---|---|
| Límite municipal | geoBoundaries (`gbOpen/COL/ADM2`) | recorte del área de estudio |
| Sentinel-2 L2A (10–20 m, cada ~5 días) | STAC Microsoft Planetary Computer | NDVI, NDMI, NDWI |
| Landsat 8/9 C2 L2 (30 m, cada ~8 días) | STAC Microsoft Planetary Computer | NDVI, NDMI, NDWI + temperatura superficial (LST) |

## Correr
```bash
pip install -r requirements.txt
python 01_diagnostico_satelital.py
```
Parámetros al inicio del script: fechas, % máximo de nubes, número de escenas, resolución.

## Salidas (`data/processed/`) — para los integrantes 2 y 3
| Archivo | Contenido |
|---|---|
| `limite_ebejico.geojson` | polígono del municipio (capa base del mapa web) |
| `catalogo_escenas.csv` | todas las escenas disponibles: fecha, sensor, % nubes |
| `indices_por_escena.csv` | media, p10 y p90 de NDVI/NDMI/NDWI/LST por fecha y % de píxeles sin nube |
| `indices_mensuales.csv` | promedio mensual por sensor (serie para el dashboard) |
| `cobertura_ndvi.csv` | % y km² por clase de vegetación |
| `ndvi_mediana_sentinel2.tif` | raster NDVI (COG, EPSG:32618) para el mapa |
| `mapa_y_serie_ndvi.png` | mapa + serie temporal para la presentación |

## Pasos 2, 3 y 4 — `02_clima_relieve_aptitud.py`
Corre después del 01 (usa `limite_ebejico.geojson`). Solo usa APIs sin cuenta:

| Paso del plan | Dataset original | Qué se usa aquí (sin login) |
|---|---|---|
| 2. Problema | SMAP / GLDAS (humedad del suelo) | NASA POWER `GWETTOP`, `GWETROOT` |
| 2. Problema | ECOSTRESS (temperatura) | NASA POWER temperatura + LST de Landsat (script 01) |
| 3. Riesgo | IMERG (lluvia) | NASA POWER `PRECTOTCORR` |
| 3. Riesgo | SRTM | NASADEM (SRTM reprocesado) vía Planetary Computer |
| 3. Riesgo | NASA POWER | NASA POWER (diario, últimos 5 años) |
| Pronóstico | — | Open-Meteo, 7 días (no es de la NASA) |
| 4. Final | GAEZ | Rangos de cultivo tipo FAO ECOCROP/GAEZ + temperatura corregida por altura |

| Archivo | Contenido |
|---|---|
| `clima_diario_power.csv` / `clima_mensual_power.csv` | temperatura, lluvia, humedad aire/suelo, radiación |
| `clima_normal_por_mes.csv` | año típico (para calendario de siembra) |
| `riesgo_climatico_anual.csv` | lluvias > 50 mm, rachas secas, suelo más seco que lo normal, calor |
| `pronostico_7dias.csv` | pronóstico diario |
| `elevacion_nasadem.tif`, `pendiente_pct.tif` | rasters EPSG:4326 (~30 m) |
| `relieve_area_km2.csv` | km² por piso térmico × clase de pendiente |
| `aptitud_cultivos.csv` | aptitud media, km² aptos, rango de altura óptimo y prioridad |
| `rotaciones_comparadas.csv` | rotaciones y asocios con área apta |
| `cultivo_mas_apto.tif` + `_leyenda.csv` | mapa del cultivo más apto por píxel |
| `resumen_clima_relieve_aptitud.png` | figura resumen |

Los rangos de cultivos están en la tabla `CULTIVOS` dentro del script: ajústenlos con información local.

## Cómo leer los índices
- **NDVI** > 0.6 vegetación densa (bosque, café con sombrío); 0.4–0.6 cultivos/pastos; < 0.2 suelo desnudo o urbano.
- **NDMI** (humedad de la vegetación): valores bajos o en descenso = estrés hídrico.
- **LST**: temperatura de la superficie (no del aire); para aire usar NASA POWER (paso 3).

Nota: Ebéjico es muy nublado; por eso se filtran escenas con < 20 % de píxeles válidos y el mapa usa la mediana de varias fechas.
