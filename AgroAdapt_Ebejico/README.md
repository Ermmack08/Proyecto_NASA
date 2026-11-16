# AgroAdapt Ebéjico — plantilla inicial

## 1. Requisitos

- Python 3.10 o superior.
- pip.
- Visual Studio Code u otro editor.

## 2. Instalación en Windows (PowerShell)

```powershell
# Entrar a la carpeta del proyecto
cd ruta\AgroAdapt_Ebejico

# Crear entorno virtual
py -m venv .venv

# Activarlo
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

Si PowerShell bloquea la activación, se puede ejecutar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Idioma de la interfaz

Al abrir la aplicación, el idioma se detecta a partir de la configuración
regional del equipo. En la barra lateral se puede cambiar en cualquier momento
entre **Español** e **English**, o dejar **Automático** para volver a usar el
idioma detectado. Si el idioma del sistema no es español ni inglés, se usa
español como valor predeterminado. La selección manual se conserva durante la
sesión de la aplicación.

Al ejecutar Streamlit localmente, la detección usa la configuración regional
del computador donde se ejecuta el proceso. En un despliegue alojado, el modo
automático depende de la configuración regional del servidor.

## 3. Estructura

- `app.py`: página principal y resumen.
- `pages/`: páginas de cada módulo, registradas con navegación localizada desde `app.py`.
- `modules/`: funciones compartidas de carga, mapas, indicadores y modelo.
- `modules/i18n.py`: traducciones de interfaz y detección regional del idioma.
- `data/raw/`: fuentes originales sin modificar.
- `data/processed/`: archivos limpios y derivados para la interfaz.
- `data/geographic/`: límites y zonas en GeoJSON.
- `config.py`: rutas y parámetros comunes.

## 4. Contratos de integración entre integrantes

### GIS / NASA

Entregar:

- `data/geographic/ebejico_boundary.geojson`
- `data/geographic/agricultural_zones.geojson` (si se construyen zonas)
- Capas procesadas y metadatos de cada variable.

Formato geográfico recomendado: GeoJSON en EPSG:4326 para intercambio web.
Para rásteres, acordar previamente formato, resolución, extensión y método de visualización.

El límite de Ebéjico está integrado desde el servicio municipal del IGAC
(Base de Datos Geográfica ET), filtrado por el código DANE `05240`. La respuesta
original y la fecha de consulta se conservan en `data/raw/`; la geometría
procesada está en `data/geographic/ebejico_boundary.geojson`. Para actualizar:

```powershell
python scripts/fetch_igac_boundary.py
```

La capa está en EPSG:4326 y sirve para el contexto municipal; no representa
linderos prediales ni parcelas agrícolas. El servicio consultado no publica una
licencia específica en sus metadatos, por lo que deben verificarse sus condiciones
de uso con el IGAC antes de redistribuirla.

### Datos ambientales

La aplicación carga la serie preparada en `data/processed/environment_nasa_power.csv`.
Para volver a consultar y procesar NASA POWER desde la raíz del proyecto:

```powershell
python scripts/fetch_nasa_power.py
```

La respuesta original queda en `data/raw/` y los metadatos de consulta en
`data/raw/nasa_power_metadata.json`. `data/processed/environment_demo.csv` se
conserva únicamente como ejemplo sintético.

El corte integrado consulta el punto aproximado del municipio
(`latitude=6.325`, `longitude=-75.768`) para 2016–2025. Incluye temperatura a 2 m
(`T2M`, °C), precipitación corregida (`PRECTOTCORR`, mm/día como tasa media diaria
mensual) y humedad relativa a 2 m (`RH2M`, %). El agregado anual `YYYY13` de la
respuesta se excluye; los valores de relleno se dejan vacíos, no se convierten
en cero. Los parámetros meteorológicos de POWER proceden de MERRA-2, por lo que
son contexto de reanálisis/modelo y no mediciones de una parcela ni imágenes
satelitales de alta resolución.

El punto consultado reporta una elevación aproximada de 2.074 m, diferente de la
estación IDEAM activa de Ebéjico reportada a 1.183 m. Esta diferencia debe
considerarse al interpretar la serie y validarse con mediciones locales.

Al incorporar otras fuentes, conservar al menos:

- `date`: fecha en formato ISO.
- columnas numéricas para variables.
- `source`: fuente de los datos.
- `is_demo`: False para datos reales.
  Documentar unidades y resolución en un archivo de metadatos o diccionario de datos.

### Capas satelitales y topográficas

Sentinel-2 L2A y NASADEM se preparan antes de iniciar Streamlit, usando el límite
municipal integrado. Para descargar y generar los productos:

```powershell
python scripts/fetch_satellite_layers.py
```

El script busca escenas Sentinel-2 de los últimos 120 días, exige cobertura
municipal completa y descarta escenas con menos de 10% de píxeles válidos
después de enmascarar nubes, sombras y clases inciertas con SCL. La escena
seleccionada y el porcentaje válido quedan en
`data/raw/satellite_layers_metadata.json`. La nubosidad de las teselas es un
dato de escena a nivel de tesela, no una medición exclusiva sobre Ebéjico.

Se generan un mosaico RGB y un NDVI de Sentinel-2 L2A a 10 m, y un modelo de
elevación NASADEM HGT v001 derivado principalmente de SRTM a aproximadamente
30 m. Los GeoTIFF y vistas previas PNG se guardan en `data/processed/`; las
fuentes STAC consultadas se conservan en `data/raw/satellite_stac_items.json`.
El token temporal usado para leer NASADEM no se guarda en los archivos.
Fuentes: [Copernicus Sentinel-2 L2A](https://doi.org/10.5270/S2_-742ikth) y
[NASADEM HGT v001](https://lpdaac.usgs.gov/products/nasadem_hgtv001/).

El NDVI se calcula como `(B08-B04)/(B08+B04)`. Se deriva también la pendiente
del NASADEM con una ventana Horn 3×3, expresada en grados. La conversión de
resolución geográfica a metros usa una aproximación local basada en WGS84; los
bordes y vecindarios con píxeles sin datos se enmascaran. La pendiente es un
indicador de relieve, no una evaluación de erosión o aptitud agrícola. Los
productos describen el contexto municipal, no identifican cultivos ni parcelas
y no constituyen un diagnóstico agronómico.

En **Territorio**, el filtro de capa permite consultar NDVI, reflectancia RGB,
elevación o pendiente. Al hacer clic en el mapa, debajo se muestran los valores
del píxel que contiene el punto, su centro aproximado, la fecha (si aplica) y la
resolución disponibles. Los píxeles enmascarados, sin datos o fuera del límite
no producen un valor.

### Cultivos / modelo agrícola

El catálogo se carga desde `data/processed/crops_catalog.csv`.
El histórico municipal EVA se conserva en `data/raw/eva_ebejico.json` y su tabla
limpia se carga desde `data/processed/eva_ebejico.csv`. El corte descargado para
Ebéjico contiene 132 registros de 12 cultivos, entre 2006 y 2018. La fuente es
el conjunto de [Evaluaciones Agropecuarias Municipales (EVA)](https://www.datos.gov.co/d/2pnw-mmge),
filtrado por código municipal `5240`.

La página Cultivos permite consultar los registros por cultivo, año, área,
producción y rendimiento. Se preservan las filas publicadas, incluidas las que
comparten cultivo y año; no se suman porque el conjunto puede contener varias
desagregaciones o registros repetidos. Los años sin fila no se interpretan como
cero.

**Límite importante:** EVA es información agregada municipal y no identifica
parcelas ni el orden de cultivos en ellas. Por tanto, este histórico describe
tendencias municipales; no permite inferir cada cuánto debe cambiarse el cultivo
ni calcular un intervalo ideal de rotación. Para ello se necesitan registros
por lote y recomendaciones agronómicas verificadas para cada secuencia.

El comparador espera una lista de diccionarios con:

```python
[
    {
        "name": "Nombre del escenario",
        "description": "Explicación",
        "scores": {
            "climate": 0,
            "soil": 0,
            "soil_health": 0,
            "production": 0,
            "farmer_priority": 0
        },
        "limitations": "Limitaciones y supuestos"
    }
]
```

Los valores de puntuación deben estar entre 0 y 100 y tener una justificación verificable.
La interfaz no debe inventar puntuaciones ni presentar escenarios hipotéticos como recomendaciones.

La página **Rotaciones** recibe estos escenarios como un archivo JSON (una lista con
el mismo formato). Verifica los cinco criterios y los valores entre 0 y 100 antes
de mostrar resultados. Permite ajustar pesos para explorar la comparación; los
pesos iniciales son solo valores de interfaz y deben validarse con el equipo
técnico. El índice resultante no es una recomendación agronómica.

## 5. Buenas prácticas

1. Mantener intactos los datos originales en `raw`.
2. No descargar ni procesar imágenes satelitales pesadas al abrir el dashboard.
3. Preparar capas y tablas antes de iniciar Streamlit.
4. Registrar fuente, fecha, unidad, resolución y cobertura espacial/temporal.
5. Diferenciar datos observados, estimados, modelados y sintéticos.
6. No afirmar precisión a nivel de parcela si la resolución de la fuente no lo permite.
7. Invalidar caché de Streamlit cuando se actualicen archivos (`st.cache_data`).

## 6. Siguiente integración

La serie contextual mensual de NASA POWER, el límite municipal oficial del IGAC,
Sentinel-2, NASADEM y la pendiente derivada están integrados. Aún no hay zonas de
análisis ni productos de Landsat, ECOSTRESS, SMAP, GLDAS o IMERG. El siguiente
paso es agregar otras variables climáticas e hidrológicas como contexto regional
y combinar los factores disponibles para evaluar riesgos con sus limitaciones.
Para evaluar rotaciones se requieren fichas agronómicas verificadas y datos
locales; el histórico EVA municipal no permite inferir intervalos de cambio de
cultivo por parcela.

# Nasa space apps challenge

# Propuesta de Proyecto: Sistema Inteligente para la Adaptación Agrícola en Ebéjico, Antioquia

- **Reto:** Field Shift: Adapting Farms with NASA Data
- **Nombre provisional:** AgroAdapt Ebéjico

---

## 1. Planteamiento de la Propuesta

Desarrollar una plataforma digital de apoyo a la toma de decisiones agrícolas que integre datos de observación terrestre de la NASA, información geoespacial y características agronómicas de los cultivos para analizar las condiciones ambientales y productivas de **Ebéjico, Antioquia**.

La plataforma permitirá caracterizar las condiciones del terreno, monitorear variables ambientales, identificar posibles riesgos para la producción agrícola y explorar estrategias de rotación de cultivos que contribuyan a mejorar la salud del suelo, optimizar el aprovechamiento de los recursos y fortalecer la adaptación de las actividades agrícolas frente a la variabilidad climática.

El sistema estará orientado a transformar información científica y geoespacial en indicadores y recomendaciones comprensibles para los agricultores.

---

## 2. Objetivo General

Diseñar un sistema de apoyo a decisiones agrícolas que integre información satelital, variables ambientales, características del suelo y requerimientos de los cultivos para evaluar alternativas de rotación agrícola en Ebéjico, Antioquia.

---

## 3. Objetivos Específicos

1. **Caracterizar** las condiciones del terreno mediante imágenes satelitales, modelos de elevación y datos ambientales.
2. **Analizar** variables como humedad, temperatura, precipitación y condiciones de la vegetación para identificar posibles factores limitantes de la producción agrícola.
3. **Construir** una base de información sobre los cultivos, incluyendo sus requerimientos ambientales, ciclos productivos, necesidades de recuperación del suelo y características agronómicas.
4. **Evaluar** posibles escenarios de riesgo relacionados con el comportamiento climático y las condiciones del terreno.
5. **Desarrollar** un modelo de evaluación que permita comparar diferentes estrategias de rotación de cultivos.
6. **Presentar** los resultados mediante una plataforma visual que facilite la interpretación de la información y la toma de decisiones.

---

## 4. Arquitectura de Datos y Etapas de Procesamiento

Se conservan las cuatro etapas planteadas, ajustando la función de cada fuente de datos:

### Etapa 1. Diagnóstico territorial

- **Fuentes:** Sentinel-2, Landsat y SRTM.
- **Aplicación:** Identificar cobertura vegetal, índices de vegetación, cambios temporales y características topográficas.

### Etapa 2. Identificación de condiciones limitantes

- **Objetivo:** Estudiar las condiciones ambientales que pueden afectar el desarrollo de los cultivos y la disponibilidad de agua.

| Fuente        | Variables principales                                                        | Aplicación                                                            |
| :------------ | :--------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| **ECOSTRESS** | Temperatura superficial y evapotranspiración.                                | Identificar condiciones de estrés térmico e hídrico en la vegetación. |
| **SMAP**      | Humedad superficial y de la zona radicular del suelo.                        | Evaluar disponibilidad de agua en el suelo.                           |
| **GLDAS**     | Humedad del suelo, temperatura, evapotranspiración y variables hidrológicas. | Analizar el comportamiento del sistema terrestre.                     |

> **Nota técnica:** Ebéjico tiene un territorio montañoso y condiciones locales que pueden cambiar considerablemente entre fincas. Por eso, no debemos interpretar SMAP o GLDAS como mediciones directas de cada terreno; deben funcionar como contexto ambiental regional y complementarse con imágenes de mayor resolución y, cuando sea posible, mediciones locales.

### Etapa 3. Evaluación de riesgos

- **Fuentes:** IMERG, SRTM y NASA POWER.
- **Aplicación:** Analizar precipitaciones, características del relieve y variables climáticas, construyendo indicadores de susceptibilidad ambiental.

### Etapa 4. Evaluación agrícola y estrategias de rotación

- **Objetivo:** Utilizar los resultados de las etapas anteriores para comparar cultivos y proponer estrategias de rotación que se ajusten a las condiciones del territorio.

Se integra **GAEZ** (_Global Agro-Ecological Zones_), una metodología y base de datos desarrollada conjuntamente por la FAO y el IIASA (complementaria a los datos de la NASA), que permite estudiar:

- Aptitud agroecológica del territorio.
- Características y limitaciones de los suelos.
- Condiciones climáticas para el desarrollo de cultivos.
- Rendimientos potenciales.
- Calendarios de cultivo.
- Requerimientos agroecológicos de diferentes especies.

#### Ficha técnica requerida por cultivo

Para pasar de una simple visualización de datos a un sistema que compare alternativas agrícolas, se construirá una ficha por especie con la siguiente estructura:

| Característica               | Información requerida                                            |
| :--------------------------- | :--------------------------------------------------------------- |
| **Tipo de cultivo**          | Especie y variedad.                                              |
| **Ciclo productivo**         | Duración desde la siembra hasta la cosecha.                      |
| **Necesidad hídrica**        | Requerimientos de agua.                                          |
| **Temperatura**              | Rangos óptimos y tolerancias.                                    |
| **Suelo**                    | Textura, pH, drenaje y fertilidad.                               |
| **Profundidad radicular**    | Desarrollo de las raíces.                                        |
| **Recuperación del terreno** | Periodo de descanso o manejo necesario, cuando aplique.          |
| **Familia botánica**         | Familia a la que pertenece el cultivo.                           |
| **Aporte al suelo**          | Fijación de nitrógeno, aporte de residuos orgánicos o cobertura. |

#### Definiciones clave para el desarrollo

- **Tiempo de cultivo:** Duración del ciclo productivo de una especie, desde su establecimiento hasta la cosecha.
- **Tiempo de recuperación:** Periodo de descanso, cobertura o manejo que puede requerir el suelo entre cultivos. No es un valor universal: depende de la especie anterior, la siguiente, la fertilidad, la extracción de nutrientes, las condiciones del terreno y las prácticas de manejo.
- **Compatibilidad entre cultivos:** Relación entre dos especies consecutivas teniendo en cuenta sus familias botánicas, requerimientos nutricionales, profundidad radicular, enfermedades compartidas y aportes al suelo.

---

## 5. Alcance Funcional y Módulos de la Plataforma

**Meta principal:** Desarrollar un modelo multicriterio que evalúe cada alternativa de rotación y destaque por su claridad y facilidad de interpretación.

### Módulo 1. Diagnóstico del territorio

- Mapa interactivo de Ebéjico.
- Visualización de imágenes satelitales.
- Índices de vegetación.
- Información topográfica.

### Módulo 2. Condiciones ambientales

- Humedad del suelo.
- Temperatura.
- Precipitación.
- Indicadores de estrés hídrico.
- Histórico de variables ambientales.

### Módulo 3. Caracterización agrícola

- Catálogo de cultivos.
- Requerimientos ambientales.
- Ciclos productivos.
- Necesidades nutricionales.
- Compatibilidad entre cultivos.

### Módulo 4. Recomendaciones y rotación

- Comparación de alternativas.
- Evaluación de aptitud.
- Secuencias de rotación.
- Indicadores de sostenibilidad.
- Justificación de las recomendaciones.

---

## 6. Stack Tecnológico (Prototipo Hackatón)

Para desarrollar un prototipo ágil durante el hackatón sin una arquitectura excesivamente compleja:

| Componente                 | Tecnología                           |
| :------------------------- | :----------------------------------- |
| **Procesamiento de datos** | Python                               |
| **Análisis geoespacial**   | GeoPandas, Rasterio, Xarray          |
| **Imágenes satelitales**   | Google Earth Engine o NASA Earthdata |
| **Visualización de mapas** | Folium o Leaflet                     |
| **Gráficas**               | Plotly                               |
| **Aplicación web**         | Streamlit                            |

¿Qué hace cada archivo?
Archivo Función
app.py Página principal, presentación e indicadores generales.
config.py Centraliza las rutas y parámetros del proyecto.
pages/ Contiene las cuatro páginas de navegación de Streamlit.
data_loader.py Lee CSV/GeoJSON y consulta píxeles de los rásteres para la interfaz.
modules/terrain.py Deriva pendiente local en grados a partir del NASADEM.
map_utils.py Construye y presenta mapas interactivos con Folium.
indicators.py Calcula resúmenes e indicadores ambientales.
rotation_model.py Estandariza la recepción y comparación de resultados del modelo agrícola.
data/raw/ Almacena los datos originales descargados.
data/processed/ Contiene los datos limpios que utilizará la aplicación.
data/geographic/ Almacena límites municipales y zonas geográficas.
