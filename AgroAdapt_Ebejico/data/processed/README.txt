Ubicar aquí datos limpios y derivados. Documentar unidades, resolución, cobertura temporal y método.

eva_ebejico.csv: registros municipales EVA procesados desde
data/raw/eva_ebejico.json. Contiene 132 filas descargadas, con año, cultivo,
desagregación, ciclo, área sembrada/cosechada, producción y rendimiento. Áreas
en hectáreas, producción en toneladas y rendimiento en toneladas por hectárea.
Se preservan las filas sin agregación; el rendimiento faltante en una fila queda vacío.

environment_nasa_power.csv: serie mensual preparada desde NASA POWER/MERRA-2,
2016–2025, para el punto latitude=6.325, longitude=-75.768. Incluye temperatura
(°C), precipitación corregida (mm/día, tasa media diaria mensual) y humedad
relativa (%). El producto es contexto de reanálisis/modelo, no medición local.
El script reproducible es scripts/fetch_nasa_power.py.

sentinel2_ndvi.tif y sentinel2_rgb.tif: productos Sentinel-2 L2A recortados al
límite municipal, EPSG:32618 y 10 m. El NDVI usa B08 y B04; ambos productos
enmascaran nubes/sombras con SCL. Los archivos *_preview.png son vistas ligeras
para el mapa, no sustituyen los GeoTIFF.

nasadem_elevation.tif: elevación NASADEM HGT v001, derivada principalmente de
SRTM, recortada al municipio. Resolución de 1 segundo de arco (~30 m), unidades
en metros y CRS original de la tesela. Su vista previa es una representación
cualitativa de elevación, no una capa de pendiente.

Las vistas previas son visualizaciones: NDVI usa una escala de marrón a verde
(-0,2 a 0,8) y la elevación una rampa relativa al rango municipal. Los píxeles
transparentes corresponden a áreas fuera del límite o datos enmascarados.
