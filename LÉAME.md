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
data_loader.py Lee archivos CSV y GeoJSON para alimentar la interfaz.
map_utils.py Construye y presenta mapas interactivos con Folium.
indicators.py Calcula resúmenes e indicadores ambientales.
rotation_model.py Estandariza la recepción y comparación de resultados del modelo agrícola.
data/raw/ Almacena los datos originales descargados.
data/processed/ Contiene los datos limpios que utilizará la aplicación.
data/geographic/ Almacena límites municipales y zonas geográficas.
