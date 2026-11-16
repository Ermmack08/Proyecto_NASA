Ubicar aquí los datos originales descargados. Conservar fuente, fecha de descarga y licencia.

eva_ebejico.json: respuesta original de la API de Datos Abiertos Colombia para
Evaluaciones Agropecuarias Municipales (EVA), filtrada por c_d_mun=5240.
Descargada el 2026-11-15. Fuente y licencia: https://www.datos.gov.co/d/2pnw-mmge
Licencia indicada por el conjunto: CC BY-SA 4.0.
No editar el archivo original; para la aplicación usar la tabla procesada.

nasa_power_2016_2025.json: respuesta mensual original de NASA POWER para
latitude=6.325, longitude=-75.768, parámetros T2M, PRECTOTCORR y RH2M.
nasa_power_metadata.json documenta la consulta, unidades y transformaciones.
Actualizar desde la raíz del proyecto con: python scripts/fetch_nasa_power.py

igac_boundary_05240.json: respuesta original de la capa municipal del IGAC,
filtrada por el código DANE 05240 y consultada en EPSG:4326.
igac_boundary_metadata.json documenta la fuente, fecha de consulta y tratamiento.
El servicio consultado no declara una licencia específica en sus metadatos.
Actualizar desde la raíz del proyecto con: python scripts/fetch_igac_boundary.py

satellite_stac_items.json: registros STAC de las teselas Sentinel-2 L2A elegidas
y del elemento NASADEM usado para generar las capas procesadas.
satellite_layers_metadata.json: fecha de escena, teselas, nubosidad, cobertura
válida, estadísticas NDVI/elevación, resoluciones, método y limitaciones.
Actualizar desde la raíz del proyecto con: python scripts/fetch_satellite_layers.py
El token SAS temporal de NASADEM no se conserva en estos archivos.
