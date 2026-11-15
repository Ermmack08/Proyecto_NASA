# -*- coding: utf-8 -*-
"""
AgroAdapt Ebéjico — Integrante 1 (Datos geoespaciales GIS / NASA)
Paso 1: DIAGNÓSTICO con Sentinel-2 y Landsat

Qué hace este script (se puede correr completo o celda por celda en VS Code / Jupyter,
cada bloque "# %%" es una celda):

  1. Descarga el límite municipal de Ebéjico (API geoBoundaries, sin llave).
  2. Busca escenas Sentinel-2 L2A y Landsat 8/9 Collection 2 L2 sobre el municipio
     (API STAC de Microsoft Planetary Computer, sin llave ni cuenta).
  3. Descarga SOLO el recorte del municipio, enmascara nubes y calcula índices:
        NDVI  -> vigor / cobertura vegetal (cultivos, pastos, bosque)
        NDMI  -> humedad de la vegetación
        NDWI  -> agua superficial
        LST   -> temperatura de la superficie en °C (solo Landsat, banda térmica)
  4. Arma tablas pandas (catálogo de escenas, estadísticas por escena, resumen mensual)
     y las guarda en CSV para el resto del equipo.
  5. Genera un mapa de NDVI mediano (PNG + GeoTIFF) para la app web.

Instalación (una sola vez):
    pip install -r requirements.txt
Ejecución:
    python 01_diagnostico_satelital.py
"""

# %% 0. Configuración ---------------------------------------------------------
from pathlib import Path
import unicodedata

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import planetary_computer
import pystac_client
import requests
from odc.stac import load as stac_load
from rasterio.features import geometry_mask

FECHA_INICIO = "2025-11-01"
FECHA_FIN = "2026-11-14"
MAX_NUBES = 60            # % de nubes de la escena completa (Ebéjico es muy nublado)
MAX_ESCENAS = 15          # por sensor, las menos nubladas (sube si quieres más serie)
RESOLUCION_M = 30         # metros; 10 da más detalle en Sentinel-2 pero tarda más
CRS_UTM = "EPSG:32618"    # UTM zona 18N, la que corresponde a Antioquia

try:
    BASE = Path(__file__).resolve().parent   # al correr el archivo completo
except NameError:
    BASE = Path.cwd()                        # al correr celda por celda (Run Cell) en VS Code
SALIDA = BASE / "data" / "processed"
SALIDA.mkdir(parents=True, exist_ok=True)

# Reintentos de red para leer los GeoTIFF remotos (los cortes de conexión son comunes)
import os
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)  # divisiones 0/0 en píxeles enmascarados
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "5")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")
os.environ.setdefault("GDAL_HTTP_TIMEOUT", "60")

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)


def sin_tildes(txt: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn").lower()


# %% 1. Límite geográfico de Ebéjico ------------------------------------------
def obtener_limite_ebejico() -> gpd.GeoDataFrame:
    destino = SALIDA / "limite_ebejico.geojson"
    if destino.exists():
        return gpd.read_file(destino)

    meta = requests.get("https://www.geoboundaries.org/api/current/gbOpen/COL/ADM2/", timeout=60).json()
    municipios = gpd.read_file(meta["simplifiedGeometryGeoJSON"])
    gdf = municipios[municipios["shapeName"].map(sin_tildes).str.contains("ebejico")]
    if gdf.empty:
        raise RuntimeError("No se encontró Ebéjico en geoBoundaries")
    gdf = gdf[["shapeName", "shapeID", "geometry"]].to_crs("EPSG:4326")
    gdf.to_file(destino, driver="GeoJSON")
    return gdf


limite = obtener_limite_ebejico()
poligono = limite.geometry.iloc[0]
area_km2 = limite.to_crs(CRS_UTM).area.iloc[0] / 1e6
print(f"Municipio: {limite['shapeName'].iloc[0]} | área ≈ {area_km2:.1f} km² | bbox = {limite.total_bounds.round(4)}")

# %% 2. Búsqueda de escenas (catálogo) ----------------------------------------
# Las URLs se firman justo antes de descargar (ver cargar): la firma dura ~45 min
# y con internet lento podría vencerse si se firma al buscar.
catalogo_stac = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")


def buscar(coleccion: str, extra_query: dict | None = None):
    query = {"eo:cloud_cover": {"lt": MAX_NUBES}}
    query.update(extra_query or {})
    items = catalogo_stac.search(
        collections=[coleccion],
        intersects=poligono.__geo_interface__,
        datetime=f"{FECHA_INICIO}/{FECHA_FIN}",
        query=query,
    ).item_collection()
    return list(items)


items_s2 = buscar("sentinel-2-l2a")
items_ls = buscar("landsat-c2-l2", {"platform": {"in": ["landsat-8", "landsat-9"]}})

df_catalogo = pd.DataFrame(
    [
        {
            "fecha": pd.to_datetime(it.datetime).tz_localize(None).normalize(),
            "sensor": "Sentinel-2" if it.collection_id == "sentinel-2-l2a" else "Landsat",
            "plataforma": it.properties.get("platform"),
            "nubes_escena_%": round(it.properties.get("eo:cloud_cover", np.nan), 1),
            "id": it.id,
        }
        for it in items_s2 + items_ls
    ]
).sort_values("fecha")

print("\nEscenas encontradas por sensor:")
print(df_catalogo.groupby("sensor").agg(escenas=("id", "count"), nubes_prom=("nubes_escena_%", "mean")).round(1))
df_catalogo.to_csv(SALIDA / "catalogo_escenas.csv", index=False)


def menos_nubladas(items, n):
    return sorted(items, key=lambda it: it.properties.get("eo:cloud_cover", 100))[:n]


# %% 3. Descarga del recorte + máscara de nubes + índices ---------------------
def mascara_municipio(ds):
    """True dentro del polígono de Ebéjico, en la grilla del dataset."""
    gb = ds.odc.geobox
    geom = limite.to_crs(CRS_UTM).geometry
    return xr_bool(~geometry_mask(geom, out_shape=gb.shape, transform=gb.affine), ds)


def xr_bool(arr, ds):
    import xarray as xr
    return xr.DataArray(arr, dims=("y", "x"), coords={"y": ds.y, "x": ds.x})


def cargar(items, bandas):
    print(f"  descargando {len(items)} escenas x {len(bandas)} bandas (recorte del municipio)...", flush=True)
    items = [planetary_computer.sign(it) for it in items]   # firma fresca para este sensor
    ds = stac_load(
        items,
        bands=bandas,
        geopolygon=poligono,
        crs=CRS_UTM,
        resolution=RESOLUCION_M,
        groupby="solar_day",   # une teselas del mismo día
        chunks={},             # carga perezosa (dask); se descarga al calcular
        fail_on_error=False,   # si un archivo falla en la red, deja hueco en vez de abortar
    )
    # Se descarga UNA sola vez a memoria (el recorte es pequeño) y luego todo se calcula local
    return ds.compute()


def indices_sentinel2(items):
    ds = cargar(items, ["B03", "B04", "B08", "B11", "SCL"])
    # Desde 2022 (baseline 04.00) los valores traen un offset de +1000
    refl = lambda b: ((ds[b].where(ds[b] > 0) - 1000) / 10000).clip(0, 1)
    g, r, nir, swir = refl("B03"), refl("B04"), refl("B08"), refl("B11")
    # SCL: 4 vegetación, 5 suelo desnudo, 6 agua, 7 sin clasificar -> válidos
    valido = ds["SCL"].isin([4, 5, 6, 7])
    return ds, valido, g, r, nir, swir, None


def indices_landsat(items):
    ds = cargar(items, ["green", "red", "nir08", "swir16", "lwir11", "qa_pixel"])
    refl = lambda b: (ds[b].where(ds[b] > 0) * 0.0000275 - 0.2).clip(0, 1)
    g, r, nir, swir = refl("green"), refl("red"), refl("nir08"), refl("swir16")
    lst_c = ds["lwir11"].where(ds["lwir11"] > 0) * 0.00341802 + 149.0 - 273.15
    qa = ds["qa_pixel"]
    # bits QA_PIXEL: 0 relleno, 1 nube dilatada, 2 cirros, 3 nube, 4 sombra de nube
    nubes = (qa & 0b11111) != 0
    valido = ~nubes
    return ds, valido, g, r, nir, swir, lst_c


def procesar(items, sensor, func):
    print(f"\n{sensor}:", flush=True)
    ds, valido, g, r, nir, swir, lst = func(items)
    dentro = mascara_municipio(ds)
    ok = valido & dentro

    capas = {
        "NDVI": ((nir - r) / (nir + r)).where(ok),
        "NDMI": ((nir - swir) / (nir + swir)).where(ok),
        "NDWI": ((g - nir) / (g + nir)).where(ok),
    }
    if lst is not None:
        capas["LST_C"] = lst.where(ok)

    pix_municipio = int(dentro.sum())
    filas = []
    print(f"  calculando índices para {ds.sizes['time']} fechas", flush=True)
    for i, t in enumerate(ds.time.values):
        pct_ok = float(ok.isel(time=i).sum()) / pix_municipio * 100
        fila = {"fecha": pd.Timestamp(t).normalize(), "sensor": sensor, "pixeles_validos_%": round(pct_ok, 1)}
        for nombre, capa in capas.items():
            v = capa.isel(time=i).values
            v = v[np.isfinite(v)]
            fila[f"{nombre}_media"] = float(v.mean()) if v.size else np.nan
            fila[f"{nombre}_p10"] = float(np.percentile(v, 10)) if v.size else np.nan
            fila[f"{nombre}_p90"] = float(np.percentile(v, 90)) if v.size else np.nan
        filas.append(fila)
        print(f"  {fila['fecha'].date()}  válidos={pct_ok:5.1f}%  NDVI={fila['NDVI_media']:.3f}")
    if all(f["pixeles_validos_%"] == 0 for f in filas):
        print(f"  ⚠ ATENCIÓN: {sensor} no trajo ningún dato. Falló la descarga (red); vuelve a correr el script.")
    return pd.DataFrame(filas), capas


df_s2, capas_s2 = procesar(menos_nubladas(items_s2, MAX_ESCENAS), "Sentinel-2", indices_sentinel2)
df_ls, capas_ls = procesar(menos_nubladas(items_ls, MAX_ESCENAS), "Landsat", indices_landsat)

# %% 4. Tablas pandas para el equipo ------------------------------------------
df_escenas = pd.concat([df_s2, df_ls], ignore_index=True).sort_values("fecha")
# Escenas casi totalmente cubiertas de nubes no son representativas
# y se descartan lecturas corruptas (archivo remoto mal descargado): un promedio municipal
# de NDVI < 0.2 o una temperatura < -10 °C no es físicamente posible en Ebéjico
df_escenas["usable"] = (
    (df_escenas["pixeles_validos_%"] >= 20)
    & (df_escenas["NDVI_media"] > 0.2)
    & ~(df_escenas.get("LST_C_media", pd.Series(np.nan, index=df_escenas.index)) < -10)
)
df_escenas.round(4).to_csv(SALIDA / "indices_por_escena.csv", index=False)

cols = [c for c in df_escenas.columns if c.endswith("_media")]
df_mensual = (
    df_escenas[df_escenas["usable"]]
    .assign(mes=lambda d: d["fecha"].dt.to_period("M").astype(str))
    .groupby(["mes", "sensor"])[cols]
    .mean()
    .round(3)
    .reset_index()
)
df_mensual.to_csv(SALIDA / "indices_mensuales.csv", index=False)

print("\n=== Índices por escena (usables) ===")
print(df_escenas[df_escenas["usable"]][["fecha", "sensor", "pixeles_validos_%"] + cols].round(3).to_string(index=False))
print("\n=== Resumen mensual ===")
print(df_mensual.to_string(index=False))

# %% 5. Mapa de NDVI mediano (para la app web y la presentación) --------------
# Se combinan las escenas de Sentinel-2: la mediana rellena huecos de nubes.
ndvi_med = capas_s2["NDVI"].median("time", skipna=True).compute()
ndvi_med.odc.write_cog(SALIDA / "ndvi_mediana_sentinel2.tif", overwrite=True)

cobertura = pd.cut(
    pd.Series(ndvi_med.values.ravel()).dropna(),
    bins=[-1, 0.0, 0.2, 0.4, 0.6, 1],
    labels=["agua/sombra", "suelo/urbano", "veg. escasa (cultivo joven, pasto degradado)",
            "veg. moderada (cultivos, pastos)", "veg. densa (bosque, café/plátano)"],
)
df_cobertura = (cobertura.value_counts(normalize=True).mul(100).round(1)
                .rename("porcentaje_%").rename_axis("clase_NDVI").reset_index())
df_cobertura["area_km2"] = (df_cobertura["porcentaje_%"] / 100 * area_km2).round(1)
df_cobertura.to_csv(SALIDA / "cobertura_ndvi.csv", index=False)
print("\n=== Cobertura según NDVI mediano (Sentinel-2) ===")
print(df_cobertura.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
ndvi_med.plot(ax=axes[0], cmap="RdYlGn", vmin=0, vmax=0.9, cbar_kwargs={"label": "NDVI"})
limite.to_crs(CRS_UTM).boundary.plot(ax=axes[0], color="black", linewidth=1)
axes[0].set_title(f"Ebéjico — NDVI mediano Sentinel-2\n{FECHA_INICIO} a {FECHA_FIN}")
axes[0].set_axis_off()

usable = df_escenas[df_escenas["usable"]]
for sensor, d in usable.groupby("sensor"):
    axes[1].plot(d["fecha"], d["NDVI_media"], "o-", label=f"NDVI {sensor}")
    axes[1].plot(d["fecha"], d["NDMI_media"], "s--", label=f"NDMI (humedad) {sensor}")
axes[1].set_title("Serie temporal de índices (promedio municipal)")
axes[1].legend()
axes[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(SALIDA / "mapa_y_serie_ndvi.png", dpi=150)

lst = usable.dropna(subset=["LST_C_media"])
if not lst.empty:
    print(f"\nTemperatura superficial Landsat: media {lst['LST_C_media'].mean():.1f} °C "
          f"(rango p10–p90 promedio {lst['LST_C_p10'].mean():.1f}–{lst['LST_C_p90'].mean():.1f} °C)")

print(f"\nArchivos guardados en: {SALIDA}")
