# -*- coding: utf-8 -*-
"""
AgroAdapt Ebéjico — Integrante 1 (Datos geoespaciales GIS / NASA)
Pasos 2, 3 y 4: PROBLEMA, RIESGO y RESULTADO FINAL

Versión sencilla: casi todo sale de APIs abiertas SIN cuenta ni llave.

  A. Clima diario (NASA POWER): temperatura, lluvia, humedad del aire,
     humedad del suelo (superficial y de raíces) y radiación solar.
     -> reemplaza a SMAP/GLDAS (humedad del suelo) e IMERG (lluvia), que piden login de Earthdata.
  B. Riesgo climático por año: lluvias extremas, rachas secas y días de calor.
  C. Pronóstico de 7 días (Open-Meteo; no es de la NASA, pero es gratis y sin llave).
  D. Relieve (NASADEM = SRTM reprocesado por la NASA): elevación y pendiente.
  E. Aptitud de cultivos por píxel (temperatura según altura + lluvia + pendiente)
     y comparación de rotaciones. Rangos de cultivo aproximados tipo FAO ECOCROP/GAEZ.

Requisito: correr antes 01_diagnostico_satelital.py (crea limite_ebejico.geojson).
Ejecución:  python 02_clima_relieve_aptitud.py
"""

# %% 0. Configuración ---------------------------------------------------------
from datetime import date, timedelta
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import planetary_computer
import pystac_client
import rasterio
import requests
from rasterio.features import geometry_mask
from rasterio.merge import merge

AÑOS_HISTORIA = 5
try:
    BASE = Path(__file__).resolve().parent   # al correr el archivo completo
except NameError:
    BASE = Path.cwd()                        # al correr celda por celda (Run Cell) en VS Code
SALIDA = BASE / "data" / "processed"
pd.set_option("display.width", 160)

limite = gpd.read_file(SALIDA / "limite_ebejico.geojson")
centro = limite.to_crs("EPSG:32618").centroid.to_crs("EPSG:4326").iloc[0]
LAT, LON = round(centro.y, 4), round(centro.x, 4)
print(f"Centro de Ebéjico: lat {LAT}, lon {LON}")

# %% A. Clima diario NASA POWER -----------------------------------------------
fin = date.today() - timedelta(days=10)          # POWER publica con unos días de retraso
inicio = date(fin.year - AÑOS_HISTORIA, 1, 1)
VARIABLES = {
    "T2M": "temp_media_C",
    "T2M_MAX": "temp_max_C",
    "T2M_MIN": "temp_min_C",
    "PRECTOTCORR": "lluvia_mm",
    "RH2M": "humedad_aire_%",
    "GWETTOP": "humedad_suelo_sup_0a1",     # 0 = seco, 1 = saturado (0–5 cm)
    "GWETROOT": "humedad_suelo_raiz_0a1",   # zona de raíces (0–100 cm)
    "ALLSKY_SFC_SW_DWN": "radiacion_MJ_m2_dia",
}
resp = requests.get(
    "https://power.larc.nasa.gov/api/temporal/daily/point",
    params={
        "parameters": ",".join(VARIABLES),
        "community": "AG",
        "latitude": LAT,
        "longitude": LON,
        "start": inicio.strftime("%Y%m%d"),
        "end": fin.strftime("%Y%m%d"),
        "format": "JSON",
    },
    timeout=180,
).json()
ALTURA_POWER = resp["geometry"]["coordinates"][2]   # altura media de la celda de POWER (m)

clima = (pd.DataFrame(resp["properties"]["parameter"])
         .rename(columns=VARIABLES)
         .replace(-999, np.nan))
clima.index = pd.to_datetime(clima.index, format="%Y%m%d")
clima.index.name = "fecha"
clima.to_csv(SALIDA / "clima_diario_power.csv")

clima_mensual = clima.resample("MS").agg({
    "temp_media_C": "mean", "temp_max_C": "mean", "temp_min_C": "mean",
    "lluvia_mm": "sum", "humedad_aire_%": "mean",
    "humedad_suelo_sup_0a1": "mean", "humedad_suelo_raiz_0a1": "mean",
    "radiacion_MJ_m2_dia": "mean",
}).round(2)
clima_mensual.to_csv(SALIDA / "clima_mensual_power.csv")

# Año "típico": promedio de cada mes calendario (sirve para calendarios de siembra)
normal = clima_mensual.groupby(clima_mensual.index.month).mean().round(1)
normal.index.name = "mes"
normal.to_csv(SALIDA / "clima_normal_por_mes.csv")

anios_completos = clima[clima.index.year < fin.year]
LLUVIA_ANUAL = anios_completos["lluvia_mm"].resample("YE").sum().mean()
TEMP_MEDIA = anios_completos["temp_media_C"].mean()
print(f"\nPOWER (celda a {ALTURA_POWER:.0f} m): temp media {TEMP_MEDIA:.1f} °C | lluvia anual {LLUVIA_ANUAL:.0f} mm")
print("\n=== Año típico (promedio por mes) ===")
print(normal[["temp_media_C", "lluvia_mm", "humedad_suelo_raiz_0a1"]].T.to_string())

# %% B. Riesgo climático por año ----------------------------------------------
seco = clima["lluvia_mm"] < 1
id_racha = (~seco).cumsum()
rachas = seco.groupby(id_racha).cumsum()      # días secos seguidos hasta cada fecha

riesgo = pd.DataFrame({
    "lluvia_total_mm": clima["lluvia_mm"].resample("YE").sum(),
    "dias_lluvia_mayor_50mm": (clima["lluvia_mm"] > 50).resample("YE").sum(),   # erosión / deslizamientos
    "racha_seca_max_dias": rachas.resample("YE").max(),                          # estrés hídrico
    # Ebéjico casi nunca tiene el suelo "seco"; se cuentan los días por debajo de lo normal (percentil 10)
    "dias_suelo_mas_seco_que_normal": (clima["humedad_suelo_raiz_0a1"]
                                       < clima["humedad_suelo_raiz_0a1"].quantile(0.10)).resample("YE").sum(),
    "dias_sin_dato": clima["lluvia_mm"].isna().resample("YE").sum(),
    "dias_calor_tmax_mayor_30C": (clima["temp_max_C"] > 30).resample("YE").sum(),
})
riesgo.index = riesgo.index.year
riesgo.index.name = "año"
riesgo.to_csv(SALIDA / "riesgo_climatico_anual.csv")
print("\n=== Riesgo climático por año (el último año va incompleto) ===")
print(riesgo.round(0).to_string())

# %% C. Pronóstico 7 días (Open-Meteo) ----------------------------------------
pron = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": LAT, "longitude": LON, "timezone": "America/Bogota", "forecast_days": 7,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
    },
    timeout=60,
).json()["daily"]
pronostico = pd.DataFrame(pron).rename(columns={
    "time": "fecha", "temperature_2m_max": "temp_max_C", "temperature_2m_min": "temp_min_C",
    "precipitation_sum": "lluvia_mm", "precipitation_probability_max": "prob_lluvia_%",
})
pronostico.to_csv(SALIDA / "pronostico_7dias.csv", index=False)
print("\n=== Pronóstico 7 días ===")
print(pronostico.to_string(index=False))

# %% D. Relieve: elevación y pendiente (NASADEM) ------------------------------
stac = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                 modifier=planetary_computer.sign_inplace)
items = stac.search(collections=["nasadem"], intersects=limite.geometry.iloc[0].__geo_interface__).item_collection()
fuentes = [rasterio.open(it.assets["elevation"].href) for it in items]
dem, transform = merge(fuentes, bounds=tuple(limite.total_bounds))
dem = dem[0].astype("float32")
perfil = fuentes[0].profile | {"height": dem.shape[0], "width": dem.shape[1], "transform": transform,
                               "count": 1, "dtype": "float32", "nodata": np.nan, "driver": "GTiff"}

dentro = ~geometry_mask(limite.geometry, out_shape=dem.shape, transform=transform)
dem[~dentro] = np.nan

# Pendiente en %: tamaño del píxel (grados) convertido a metros
px_x = transform.a * 111_320 * np.cos(np.radians(LAT))
px_y = -transform.e * 110_574
dz_dy, dz_dx = np.gradient(dem, px_y, px_x)
pendiente = np.hypot(dz_dx, dz_dy) * 100

for nombre, arr in [("elevacion_nasadem.tif", dem), ("pendiente_pct.tif", pendiente)]:
    with rasterio.open(SALIDA / nombre, "w", **perfil) as dst:
        dst.write(arr.astype("float32"), 1)

AREA_PX_KM2 = px_x * px_y / 1e6
validos = np.isfinite(dem)
relieve = pd.DataFrame({"elevacion_m": dem[validos], "pendiente_%": pendiente[validos]})
relieve["piso_termico"] = pd.cut(relieve["elevacion_m"], [0, 1000, 2000, 3000, 5000],
                                 labels=["cálido (<1000 m)", "templado (1000–2000 m)",
                                         "frío (2000–3000 m)", "páramo (>3000 m)"])
relieve["clase_pendiente"] = pd.cut(relieve["pendiente_%"], [-1, 12, 25, 50, 75, 1e4],
                                    labels=["plana-suave (<12%)", "moderada (12–25%)", "fuerte (25–50%)",
                                            "muy fuerte (50–75%)", "escarpada (>75%)"])
resumen_relieve = (relieve.groupby(["piso_termico", "clase_pendiente"], observed=True).size()
                   .mul(AREA_PX_KM2).round(1).unstack(fill_value=0))
resumen_relieve.to_csv(SALIDA / "relieve_area_km2.csv")
print(f"\nElevación: {np.nanmin(dem):.0f}–{np.nanmax(dem):.0f} m | pendiente mediana {np.nanmedian(pendiente):.0f}%")
print("\n=== Área (km²) por piso térmico y pendiente ===")
print(resumen_relieve.to_string())

# %% E. Aptitud de cultivos y rotaciones --------------------------------------
# Temperatura por píxel: la de POWER corregida por altura (-6.5 °C por cada 1000 m)
temp_pixel = TEMP_MEDIA - 0.0065 * (dem - ALTURA_POWER)

# Rangos aproximados (FAO ECOCROP / guías Agrosavia). Ajustar con datos locales y GAEZ.
# t_min_abs, t_min_opt, t_max_opt, t_max_abs (°C) | lluvia anual mm | pendiente máx. recomendada %
CULTIVOS = pd.DataFrame([
    ("Café",            "perenne",  14, 18, 22, 27, 1500, 2800, 75),
    ("Plátano",         "perenne",  17, 24, 30, 35, 1500, 3500, 50),
    ("Caña panelera",   "perenne",  16, 22, 30, 36, 1200, 3000, 50),
    ("Aguacate",        "perenne",  11, 16, 22, 28, 1200, 2500, 60),
    ("Tomate de árbol", "perenne",  10, 14, 20, 24, 1500, 3000, 50),
    ("Cítricos",        "perenne",  13, 20, 30, 36, 1000, 2500, 50),
    ("Maíz",            "anual",    10, 18, 30, 35,  600, 2500, 25),
    ("Frijol",          "anual",    10, 16, 24, 30,  600, 2200, 25),
    ("Yuca",            "anual",    16, 22, 30, 35, 1000, 2500, 30),
], columns=["cultivo", "tipo", "t_min_abs", "t_min_opt", "t_max_opt", "t_max_abs",
            "lluvia_min", "lluvia_max", "pendiente_max_%"]).set_index("cultivo")


def aptitud(c):
    """0 = no apto, 1 = óptimo. Multiplica temperatura x pendiente x lluvia."""
    f_temp = np.interp(temp_pixel, [c.t_min_abs, c.t_min_opt, c.t_max_opt, c.t_max_abs], [0, 1, 1, 0])
    f_pend = np.where(pendiente <= c["pendiente_max_%"], 1.0, 0.4)   # 0.4: posible con terrazas/barreras
    f_lluvia = 1.0 if c.lluvia_min <= LLUVIA_ANUAL <= c.lluvia_max else 0.6
    return np.where(validos, f_temp * f_pend * f_lluvia, np.nan)


capas_apt = {nombre: aptitud(c) for nombre, c in CULTIVOS.iterrows()}

tabla_apt = pd.DataFrame({
    nombre: {
        "aptitud_media": np.nanmean(a),
        "area_alta_km2 (>=0.7)": np.sum(a >= 0.7) * AREA_PX_KM2,
        "area_media_km2 (0.4-0.7)": np.sum((a >= 0.4) & (a < 0.7)) * AREA_PX_KM2,
        "altura_optima_m": f"{np.nanpercentile(dem[a >= 0.7], 10):.0f}–{np.nanpercentile(dem[a >= 0.7], 90):.0f}"
                           if np.any(a >= 0.7) else "—",
    }
    for nombre, a in capas_apt.items()
}).T
tabla_apt.insert(0, "tipo", CULTIVOS["tipo"])
tabla_apt = tabla_apt.sort_values("area_alta_km2 (>=0.7)", ascending=False)
tabla_apt["prioridad"] = range(1, len(tabla_apt) + 1)
tabla_apt.round(2).to_csv(SALIDA / "aptitud_cultivos.csv")
print("\n=== Aptitud de cultivos (prioridad por área altamente apta) ===")
print(tabla_apt.round(2).to_string())

# Rotaciones (anuales) y asocios (perennes): área donde TODOS sus cultivos son aptos (>=0.5)
ROTACIONES = [
    ("Maíz → Frijol → Yuca", "rotación", ["Maíz", "Frijol", "Yuca"],
     "gramínea + leguminosa (fija N) + raíz; rompe ciclos de plagas"),
    ("Maíz → Frijol", "rotación", ["Maíz", "Frijol"],
     "dos semestres; el frijol devuelve nitrógeno al suelo"),
    ("Frijol → Yuca", "rotación", ["Frijol", "Yuca"], "zonas más cálidas; yuca tolera suelos pobres"),
    ("Café + Plátano", "asocio", ["Café", "Plátano"], "plátano como sombrío del café"),
    ("Café + Aguacate", "asocio", ["Café", "Aguacate"], "sombrío productivo en zona alta"),
    ("Aguacate + Frijol", "asocio", ["Aguacate", "Frijol"], "frijol entre calles en los primeros años"),
]
filas = []
for nombre, tipo, cultivos, nota in ROTACIONES:
    todos = np.logical_and.reduce([capas_apt[c] >= 0.5 for c in cultivos])
    filas.append({"estrategia": nombre, "tipo": tipo,
                  "area_apta_km2": round(np.sum(todos) * AREA_PX_KM2, 1),
                  "aptitud_media": round(np.nanmean(np.mean([capas_apt[c] for c in cultivos], axis=0)), 2),
                  "beneficio": nota})
rotaciones = pd.DataFrame(filas).sort_values("area_apta_km2", ascending=False)
rotaciones.to_csv(SALIDA / "rotaciones_comparadas.csv", index=False)
print("\n=== Comparación de rotaciones y asocios ===")
print(rotaciones.to_string(index=False))

# Mapa del cultivo más apto por píxel
nombres = list(capas_apt)
pila = np.stack([np.nan_to_num(capas_apt[n], nan=-1) for n in nombres])
mejor = np.argmax(pila, axis=0).astype(float)
mejor[(pila.max(axis=0) < 0.5) | ~validos] = np.nan
with rasterio.open(SALIDA / "cultivo_mas_apto.tif", "w", **perfil) as dst:
    dst.write(mejor.astype("float32"), 1)
pd.Series(nombres, name="cultivo").rename_axis("codigo").to_csv(SALIDA / "cultivo_mas_apto_leyenda.csv")

# %% F. Figura resumen ----------------------------------------------------------
b = limite.total_bounds
extent = [b[0], b[2], b[1], b[3]]
fig, ax = plt.subplots(2, 3, figsize=(18, 11))

im = ax[0, 0].imshow(dem, cmap="terrain", extent=extent)
fig.colorbar(im, ax=ax[0, 0], label="m"); ax[0, 0].set_title("Elevación (NASADEM)")
im = ax[0, 1].imshow(pendiente, cmap="magma_r", vmin=0, vmax=100, extent=extent)
fig.colorbar(im, ax=ax[0, 1], label="%"); ax[0, 1].set_title("Pendiente")
cmap = plt.get_cmap("tab10", len(nombres))
ax[0, 2].imshow(mejor, cmap=cmap, vmin=-0.5, vmax=len(nombres) - 0.5, extent=extent, interpolation="nearest")
ax[0, 2].legend(handles=[plt.Rectangle((0, 0), 1, 1, color=cmap(i)) for i in range(len(nombres))],
                labels=nombres, fontsize=8, loc="lower left")
ax[0, 2].set_title("Cultivo más apto (aptitud ≥ 0.5)")
for a in ax[0]:
    limite.boundary.plot(ax=a, color="black", linewidth=0.8)
    a.set_axis_off()

ax[1, 0].bar(normal.index, normal["lluvia_mm"], color="tab:blue", label="lluvia (mm)")
ax2 = ax[1, 0].twinx()
ax2.plot(normal.index, normal["temp_media_C"], "o-", color="tab:red", label="temp (°C)")
ax[1, 0].set_title(f"Año típico NASA POWER ({inicio.year}–{fin.year})")
ax[1, 0].set_xticks(range(1, 13)); ax[1, 0].set_ylabel("lluvia mm/mes"); ax2.set_ylabel("°C")

ultimos = clima[clima.index > clima.index.max() - pd.Timedelta(days=365)]
ax[1, 1].plot(ultimos.index, ultimos["humedad_suelo_raiz_0a1"], label="raíces")
ax[1, 1].plot(ultimos.index, ultimos["humedad_suelo_sup_0a1"], alpha=0.6, label="superficial")
ax[1, 1].axhline(clima["humedad_suelo_raiz_0a1"].quantile(0.10), ls="--", color="gray", label="p10 histórico")
ax[1, 1].legend()
ax[1, 1].set_title("Humedad del suelo, último año (0 seco – 1 saturado)")

tabla_apt["area_alta_km2 (>=0.7)"].astype(float).sort_values().plot.barh(ax=ax[1, 2], color="tab:green")
ax[1, 2].set_title("Área altamente apta por cultivo (km²)")
fig.tight_layout()
fig.savefig(SALIDA / "resumen_clima_relieve_aptitud.png", dpi=130)
print(f"\nArchivos guardados en: {SALIDA}")
