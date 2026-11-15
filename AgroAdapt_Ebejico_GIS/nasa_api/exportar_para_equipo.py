# -*- coding: utf-8 -*-
"""
Copia los resultados de nasa_api/ a las rutas y formatos acordados en el README del equipo
(contrato con el integrante 3). Ejecutar desde la carpeta raíz AgroAdapt_Ebejico_GIS:

    python nasa_api/exportar_para_equipo.py
"""
from pathlib import Path
import shutil

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "nasa_api" / "data" / "processed"
DESTINO = RAIZ / "data" / "processed"
UTM = "EPSG:32618"


def a_utm(origen, destino, convertir=None):
    """Reproyecta un GeoTIFF a UTM 18N (opcionalmente transformando los valores)."""
    with rasterio.open(origen) as src:
        datos = src.read(1).astype("float32")
        if convertir is not None:
            datos = convertir(datos)
        tr, w, h = calculate_default_transform(src.crs, UTM, src.width, src.height, *src.bounds)
        perfil = src.profile | {"crs": UTM, "transform": tr, "width": w, "height": h,
                                "dtype": "float32", "nodata": np.nan, "driver": "GTiff"}
        salida = np.full((h, w), np.nan, dtype="float32")
        reproject(datos, salida, src_transform=src.transform, src_crs=src.crs, src_nodata=np.nan,
                  dst_transform=tr, dst_crs=UTM, dst_nodata=np.nan, resampling=Resampling.bilinear)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(destino, "w", **perfil) as dst:
        dst.write(salida, 1)


# 1. Límite municipal (GeoJSON EPSG:4326). Si el equipo ya tiene el del IGAC, se respeta.
limite = RAIZ / "data" / "geographic" / "ebejico_boundary.geojson"
if not limite.exists():
    limite.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ORIGEN / "limite_ebejico.geojson", limite)

# 2. NDVI Sentinel-2 (ya está en UTM 18N)
(DESTINO / "vegetation").mkdir(parents=True, exist_ok=True)
shutil.copy(ORIGEN / "ndvi_mediana_sentinel2.tif", DESTINO / "vegetation" / "sentinel2_ndvi_ebejico.tif")

# 3. Elevación en UTM 18N y pendiente en grados
a_utm(ORIGEN / "elevacion_nasadem.tif", DESTINO / "terrain" / "dem_utm18n.tif")
a_utm(ORIGEN / "pendiente_pct.tif", DESTINO / "terrain" / "slope_degrees.tif",
      convertir=lambda pct: np.degrees(np.arctan(pct / 100)))

# 4. Clima diario NASA POWER con columna source
clima = pd.read_csv(ORIGEN / "clima_diario_power.csv")
clima["source"] = "NASA POWER (power.larc.nasa.gov), comunidad AG, centroide de Ebéjico"
(DESTINO / "environmental").mkdir(parents=True, exist_ok=True)
clima.to_csv(DESTINO / "environmental" / "nasa_power_daily.csv", index=False)

for f in ["data/geographic/ebejico_boundary.geojson",
          "data/processed/vegetation/sentinel2_ndvi_ebejico.tif",
          "data/processed/terrain/dem_utm18n.tif",
          "data/processed/terrain/slope_degrees.tif",
          "data/processed/environmental/nasa_power_daily.csv"]:
    print("✔", f, f"({(RAIZ / f).stat().st_size / 1024:.0f} KB)")

# 5. Vista previa: una imagen con los 5 entregables para comprobar que quedaron bien
import geopandas as gpd
import matplotlib.pyplot as plt

def leer(ruta):
    with rasterio.open(DESTINO / ruta) as src:
        datos = src.read(1).astype("float32")
        if src.nodata is not None and not np.isnan(src.nodata):
            datos[datos == src.nodata] = np.nan
    return datos


TEXTOS = []


def explicar(a, texto):
    """Cuadro de texto debajo de cada panel (se ubica al final, todos alineados por fila)."""
    TEXTOS.append((a, texto))


def mapa(a, datos, titulo, fuente, cmap, unidad, vmin=None, vmax=None):
    im = a.imshow(datos, cmap=cmap, vmin=vmin, vmax=vmax)
    fig.colorbar(im, ax=a, orientation="horizontal", fraction=0.05, pad=0.02, label=unidad)
    a.set_title(f"{titulo}\n", fontsize=13, fontweight="bold")
    a.text(0.5, 1.01, fuente, transform=a.transAxes, ha="center", fontsize=8.5, color="gray")
    a.set_axis_off()


ndvi = leer("vegetation/sentinel2_ndvi_ebejico.tif")
dem = leer("terrain/dem_utm18n.tif")
pend = leer("terrain/slope_degrees.tif")
gdf_limite = gpd.read_file(limite)
area_km2 = gdf_limite.to_crs(UTM).area.sum() / 1e6

clima["fecha"] = pd.to_datetime(clima.iloc[:, 0])
mensual = clima.set_index("fecha").resample("MS").agg({"temp_media_C": "mean", "lluvia_mm": "sum"})
completos = mensual[mensual.index.year < mensual.index.max().year]
lluvia_anual = completos["lluvia_mm"].groupby(completos.index.year).sum().mean()
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
por_mes = completos.groupby(completos.index.month).mean()

fig, ax = plt.subplots(2, 3, figsize=(16, 12))
fig.suptitle("Ebéjico (Antioquia) — Datos geoespaciales NASA", fontsize=17, fontweight="bold")

# 1. Límite
a = ax[0, 0]
gdf_limite.plot(ax=a, color="#d9f0d3", edgecolor="darkgreen", linewidth=1.5)
a.set_title("1. Límite del municipio\n", fontsize=13, fontweight="bold")
a.text(0.5, 1.01, "Fuente: límite oficial del municipio", transform=a.transAxes, ha="center", fontsize=8.5, color="gray")
a.set_axis_off()
explicar(a, f"Área: {area_km2:.0f} km²\nEs el contorno con el que se\nrecortan todas las demás capas.")

# 2. Elevación
mapa(ax[0, 1], dem, "2. Elevación", "Fuente: NASADEM (misión SRTM, NASA)", "terrain", "metros sobre el nivel del mar")
explicar(ax[0, 1], f"Más bajo: {np.nanmin(dem):.0f} m   ·   Más alto: {np.nanmax(dem):.0f} m\n"
                   f"Altura promedio: {np.nanmean(dem):.0f} m\nAzul = zonas bajas · Blanco = zonas altas")

# 3. Pendiente
mapa(ax[0, 2], pend, "3. Pendiente del terreno", "Calculada a partir de NASADEM", "magma_r", "grados")
explicar(ax[0, 2], f"La mitad del municipio tiene más de {np.nanmedian(pend):.0f}° de inclinación\n"
                   f"Máxima: {np.nanmax(pend):.0f}°\nClaro = plano · Oscuro = muy empinado")

# 4. Vegetación
mapa(ax[1, 0], ndvi, "4. Verdor de la vegetación (NDVI)", "Fuente: Sentinel-2 (mediana del año)",
     "RdYlGn", "NDVI (0 = sin vegetación, 1 = vegetación densa)", vmin=0, vmax=1)
explicar(ax[1, 0], f"Promedio del municipio: {np.nanmean(ndvi):.2f}\n"
                   f"El 80% del territorio está entre {np.nanpercentile(ndvi, 10):.2f} y {np.nanpercentile(ndvi, 90):.2f}\n"
                   "Rojo = suelo/vías · Verde = vegetación")

# 5. Temperatura
a = ax[1, 1]
a.plot(mensual.index, mensual["temp_media_C"], color="firebrick", lw=1.8)
a.set_title("5. Temperatura del aire\n", fontsize=13, fontweight="bold")
a.text(0.5, 1.01, "Fuente: NASA POWER (promedio de cada mes)", transform=a.transAxes, ha="center", fontsize=8.5, color="gray")
a.set_ylabel("°C"); a.grid(alpha=0.3)
explicar(a, f"Promedio: {clima['temp_media_C'].mean():.1f} °C\n"
            f"Día más frío: {clima['temp_media_C'].min():.1f} °C   ·   Día más cálido: {clima['temp_media_C'].max():.1f} °C\n"
            f"Datos de {clima['fecha'].min():%Y} a {clima['fecha'].max():%Y}")

# 6. Lluvia
a = ax[1, 2]
a.bar(MESES, por_mes["lluvia_mm"], color="steelblue")
a.set_title("6. Lluvia en un año típico\n", fontsize=13, fontweight="bold")
a.text(0.5, 1.01, "Fuente: NASA POWER (promedio por mes)", transform=a.transAxes, ha="center", fontsize=8.5, color="gray")
a.set_ylabel("mm de lluvia al mes"); a.grid(alpha=0.3, axis="y")
explicar(a, f"Lluvia al año: unos {lluvia_anual:.0f} mm\n"
            f"Mes más lluvioso: {MESES[por_mes['lluvia_mm'].idxmax() - 1]}   ·   Más seco: {MESES[por_mes['lluvia_mm'].idxmin() - 1]}")

fig.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.17, hspace=0.80, wspace=0.25)
fig.canvas.draw()
for fila in range(2):
    # debajo de todo lo que ocupa la fila (mapas, barras de color y ejes)
    caja = min(e.get_window_extent().transformed(fig.transFigure.inverted()).y0
               for a in ax[fila] for e in [a] + [c for c in fig.axes if c not in ax.ravel() and
                                                  abs(c.get_position().x0 - a.get_position().x0) < 0.15
                                                  and abs(c.get_position().y1 - a.get_position().y0) < 0.15])
    for a, texto in TEXTOS:
        if a in ax[fila]:
            p = a.get_position()
            fig.text((p.x0 + p.x1) / 2, caja - 0.045, texto, ha="center", va="top", fontsize=9.5,
                     linespacing=1.5, bbox=dict(boxstyle="round,pad=0.6", fc="#f6f6f6", ec="#cccccc"))
vista = DESTINO / "vista_previa_entregables.png"
try:
    fig.savefig(vista, dpi=110)
    print("\nVista previa guardada en:", vista)
except OSError:
    print("\n(No se pudo guardar la vista previa: la imagen está abierta en otro programa.)")
print("Se abrió una ventana con los mapas; ciérrala para terminar.")
plt.show()   # abre una ventana con la figura
