# -*- coding: utf-8 -*-
"""
Funciones de apoyo para el notebook `ebejico_datos_nasa.ipynb`.

Todo se pide a servicios en línea que YA tienen los datos procesados:
  - geoBoundaries ............ límite del municipio
  - Planetary Computer (STAC + Data API) ... Sentinel-2, Landsat y NASADEM (SRTM)
        El servidor recorta la imagen al municipio y calcula las estadísticas;
        aquí no se descargan imágenes completas.
  - NASA POWER ............... clima (temperatura, lluvia, humedad del aire y del suelo)

No hay valores escritos a mano: todos los números salen de las respuestas de las APIs.
"""
import io
import json
import unicodedata
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pystac_client
import requests
from PIL import Image

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
DATA = "https://planetarycomputer.microsoft.com/api/data/v1"
POWER = "https://power.larc.nasa.gov/api/temporal"
CARPETA = Path.cwd() / "data" / "processed"
CARPETA.mkdir(parents=True, exist_ok=True)
CACHE = Path.cwd() / "data" / "cache"     # respuestas ya descargadas (se puede borrar para refrescar)
CACHE.mkdir(parents=True, exist_ok=True)

_catalogo = pystac_client.Client.open(STAC)

# Si la conexión se cae o el servidor está ocupado, se reintenta solo (hasta 6 veces)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
_http = requests.Session()
_http.mount("https://", HTTPAdapter(max_retries=Retry(
    total=8, backoff_factor=2, status_forcelist=[429, 502, 503, 504], allowed_methods=None)))


# ---------------------------------------------------------------- límite
def limite_municipio(nombre="Ebéjico"):
    """Polígono del municipio desde geoBoundaries (se guarda para no volver a pedirlo)."""
    archivo = CARPETA / "limite_ebejico.geojson"
    if archivo.exists():
        return gpd.read_file(archivo)
    sin_tilde = lambda s: "".join(c for c in unicodedata.normalize("NFD", s)
                                  if unicodedata.category(c) != "Mn").lower()
    meta = _http.get("https://www.geoboundaries.org/api/current/gbOpen/COL/ADM2/", timeout=60).json()
    todos = gpd.read_file(meta["simplifiedGeometryGeoJSON"])
    gdf = todos[todos["shapeName"].map(sin_tilde) == sin_tilde(nombre)][["shapeName", "geometry"]]
    gdf.to_file(archivo, driver="GeoJSON")
    return gdf


def _feature(gdf):
    return json.loads(gdf.to_crs("EPSG:4326").to_json())["features"][0]


# ---------------------------------------------------------------- catálogo de escenas
def buscar_escenas(gdf, coleccion, inicio, fin, max_nubes=None):
    """Tabla con las escenas disponibles (una fila por fecha)."""
    query = {"eo:cloud_cover": {"lt": max_nubes}} if max_nubes else {}
    if coleccion == "landsat-c2-l2":
        query["platform"] = {"in": ["landsat-8", "landsat-9"]}
    items = _catalogo.search(collections=[coleccion], intersects=_feature(gdf)["geometry"],
                             datetime=f"{inicio}/{fin}", query=query).item_collection()
    filas = [{"fecha": it.datetime.date(), "satelite": it.properties.get("platform"),
              "nubes_escena_%": it.properties.get("eo:cloud_cover"), "id": it.id} for it in items]
    df = pd.DataFrame(filas)
    # Un municipio puede caer en 2 "teselas" el mismo día: se agrupan por fecha
    return (df.groupby("fecha")
              .agg(satelite=("satelite", "first"), nubes_escena_pct=("nubes_escena_%", "mean"),
                   ids=("id", list))
              .reset_index().sort_values("fecha"))


# ---------------------------------------------------------------- llamadas al servidor
def _post(ruta, coleccion, item_id, gdf, **params):
    # nodata=0: fuera del área de cada tesela el satélite guarda 0; así no se cuenta como dato
    params.setdefault("nodata", 0)
    # Para promedios del municipio basta una versión reducida (~512 px de lado): el servidor responde en segundos
    if ruta.endswith("statistics"):
        params.setdefault("max_size", 512)
    params = {"collection": coleccion, "item": item_id, **params}

    # Copia local de cada respuesta: si ya se pidió antes, no se vuelve a consultar el servidor
    import hashlib
    clave = hashlib.sha1(json.dumps([ruta, params, gdf.total_bounds.round(5).tolist()],
                                    sort_keys=True, default=str).encode()).hexdigest()
    copia = CACHE / clave
    if not copia.exists():
        r = _http.post(f"{DATA}/{ruta}", params=params, json=_feature(gdf), timeout=300)
        r.raise_for_status()
        copia.write_bytes(r.content)
    return _Respuesta(copia.read_bytes())


class _Respuesta:
    """Imita la respuesta de requests (.content y .json()) para lo guardado en disco."""
    def __init__(self, contenido):
        self.content = contenido

    def json(self):
        return json.loads(self.content)


def estadisticas(gdf, coleccion, ids, **params):
    """Estadísticas calculadas por el servidor dentro del municipio.
    Si hay varias teselas el mismo día, se combinan ponderando por número de píxeles."""
    partes = []
    for item_id in ids:
        st = _post("item/statistics", coleccion, item_id, gdf, **params).json()["properties"]["statistics"]
        partes.append(next(iter(st.values())))
    n = sum(p["count"] for p in partes)
    if n == 0:
        return {"media": np.nan, "minimo": np.nan, "maximo": np.nan, "pixeles": 0, "histograma": ([], [])}
    hist_c, hist_v = {}, {}
    for p in partes:
        for c, v in zip(*p["histogram"]):
            hist_c[v] = hist_c.get(v, 0) + c
    return {
        "media": sum(p["mean"] * p["count"] for p in partes) / n,
        "minimo": min(p["min"] for p in partes),
        "maximo": max(p["max"] for p in partes),
        "pixeles": n,
        "histograma": (list(hist_c.values()), list(hist_c.keys())),
    }


def imagen(gdf, coleccion, ids, **params):
    """Imagen PNG recortada al municipio, generada por el servidor (une teselas del mismo día)."""
    capas = [Image.open(io.BytesIO(_post("item/crop.png", coleccion, i, gdf, max_size=900, **params).content))
             .convert("RGBA") for i in ids]
    base = capas[0]
    for capa in capas[1:]:
        base = Image.alpha_composite(base, capa.resize(base.size))
    return base


def mostrar(img, titulo, ax=None, leyenda=None):
    ax = ax or plt.subplots(figsize=(7, 7))[1]
    ax.imshow(img)
    ax.set_title(titulo, fontsize=12)
    ax.set_axis_off()
    if leyenda:
        ax.text(0.5, -0.04, leyenda, transform=ax.transAxes, ha="center", va="top", fontsize=9)
    return ax


# ---------------------------------------------------------------- nubes según el propio satélite
def calidad_escena(gdf, coleccion, ids):
    """Devuelve (% de Ebéjico que cubre la toma, % de lo cubierto que está bajo nubes/sombras).
    Usa la capa de calidad que trae el propio producto:
      Sentinel-2 -> SCL (0 = sin dato; 3 sombra, 8-9 nubes, 10 cirros)
      Landsat    -> QA_PIXEL (bit 0 relleno; bits 1, 3, 4 = nube dilatada, nube, sombra)"""
    if coleccion == "sentinel-2-l2a":
        banda, vacio, nube = "SCL", (lambda v: v == 0), (lambda v: v in (3, 8, 9, 10))
    else:
        banda, vacio, nube = "qa_pixel", (lambda v: int(v) & 1), (lambda v: int(v) & 0b11010)
    # Fracción del rectángulo de recorte que ocupa el municipio (el servidor recorta un rectángulo)
    utm = gdf.to_crs("EPSG:32618")
    fraccion = utm.area.sum() / utm.envelope.area.sum()
    total, cubiertos, nublados = 0, 0, 0
    for item_id in ids:
        st = _post("item/statistics", coleccion, item_id, gdf, assets=banda,
                   categorical="true", nodata=None).json()["properties"]["statistics"]
        p = next(iter(st.values()))
        conteos, valores = p["histogram"]
        # píxeles que tendría el municipio completo en esta grilla
        total = max(total, (p["valid_pixels"] + p["masked_pixels"]) * fraccion)
        for c, v in zip(conteos, valores):
            if not vacio(v):
                cubiertos += c
                nublados += c if nube(v) else 0
    cobertura = min(100.0, 100 * cubiertos / total) if total else 0.0
    return cobertura, (100 * nublados / cubiertos if cubiertos else np.nan)


# ---------------------------------------------------------------- relieve (NASADEM = SRTM)
def relieve(gdf):
    """Elevación (m) y pendiente (%) de NASADEM recortadas al municipio."""
    import planetary_computer
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.merge import merge

    items = _catalogo.search(collections=["nasadem"], intersects=_feature(gdf)["geometry"]).item_collection()
    fuentes = [rasterio.open(planetary_computer.sign(it.assets["elevation"].href)) for it in items]
    dem, tr = merge(fuentes, bounds=tuple(gdf.total_bounds))
    dem = dem[0].astype("float32")
    dem[geometry_mask(gdf.geometry, out_shape=dem.shape, transform=tr)] = np.nan
    lat = gdf.total_bounds[[1, 3]].mean()
    px_x, px_y = tr.a * 111_320 * np.cos(np.radians(lat)), -tr.e * 110_574   # grados -> metros
    dy, dx = np.gradient(dem, px_y, px_x)
    pendiente = np.hypot(dx, dy) * 100
    b = gdf.total_bounds
    return dem, pendiente, [b[0], b[2], b[1], b[3]], px_x * px_y / 1e6


# ---------------------------------------------------------------- NASA POWER
def clima_power(lat, lon, parametros, tipo="climatology", inicio=None, fin=None):
    """Datos de NASA POWER. Devuelve (tabla, descripción de cada variable según la API)."""
    params = {"parameters": ",".join(parametros), "community": "AG",
              "latitude": lat, "longitude": lon, "format": "JSON"}
    if inicio:
        params |= {"start": inicio, "end": fin}
    r = _http.get(f"{POWER}/{tipo}/point", params=params, timeout=180).json()
    tabla = pd.DataFrame(r["properties"]["parameter"]).replace(-999, np.nan)
    info = pd.DataFrame(r["parameters"]).T.rename(columns={"longname": "descripcion_nasa", "units": "unidades"})
    info["altura_celda_m"] = r["geometry"]["coordinates"][2]
    return tabla, info

