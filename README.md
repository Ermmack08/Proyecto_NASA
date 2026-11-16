# AgroAdapt Ebéjico

**NASA Space Apps Challenge 2026**

**Una plataforma inteligente para la adaptación agrícola basada en datos.**

AgroAdapt Ebéjico integra tecnologías de observación de la Tierra, información geoespacial y datos agrícolas para apoyar la comprensión del territorio y la planificación agrícola frente a la variabilidad ambiental y climática.

[Español](#español) | [English](#english)

---

# Español

## 1. Descripción general

La agricultura enfrenta desafíos cada vez mayores debido a la variabilidad ambiental y climática. El acceso a información ambiental confiable permite a las comunidades comprender mejor las condiciones de sus territorios y explorar prácticas agrícolas más sostenibles.

AgroAdapt Ebéjico es una plataforma interactiva que transforma datos satelitales y ambientales en información visual y accesible. Ofrece herramientas para explorar las condiciones geográficas locales, consultar indicadores ambientales, conocer las características de diferentes cultivos y analizar posibles alternativas de rotación agrícola.

El proyecto fue desarrollado en el marco del **NASA Space Apps Challenge 2026**, demostrando cómo las tecnologías de observación de la Tierra pueden contribuir a la toma de decisiones agrícolas en contextos locales.

## 2. El desafío

El proyecto busca facilitar el acceso y aprovechamiento de información científica y geoespacial para apoyar los procesos de adaptación agrícola.

Mediante la integración de observaciones satelitales con información geográfica y agrícola local, AgroAdapt busca reducir la brecha entre los datos de observación de la Tierra y sus aplicaciones prácticas en las comunidades rurales.

## 3. Funcionalidades principales

- **Exploración territorial:** Visualización interactiva de los límites geográficos de Ebéjico, información de elevación e imágenes satelitales.
- **Análisis ambiental:** Exploración de indicadores ambientales y variables relacionadas con las condiciones climáticas.
- **Información de cultivos:** Consulta y visualización de las características de diferentes cultivos agrícolas.
- **Rotación de cultivos:** Exploración de posibles alternativas de rotación agrícola para apoyar la planificación de los cultivos.

## 4. Fuentes de información

La plataforma integra información procedente de diferentes fuentes de datos:

- **NASA POWER:** Datos ambientales y meteorológicos. [Consultar NASA POWER](https://power.larc.nasa.gov/)
- **Sentinel-2:** Imágenes satelitales e información relacionada con la vegetación. [Consultar Copernicus Data Space](https://dataspace.copernicus.eu/)
- **NASADEM:** Datos de elevación del terreno y modelos digitales de elevación. [Consultar NASA Earthdata](https://earthdata.nasa.gov/)
- **IGAC:** Información geográfica y límites territoriales. [Consultar IGAC](https://www.igac.gov.co/)
- **Conjuntos de datos agrícolas:** Información agrícola utilizada para contextualizar los análisis del territorio.

## 5. Tecnologías utilizadas

El proyecto utiliza las siguientes tecnologías y herramientas:

- **Python:** Lenguaje de programación principal.
- **Streamlit:** Desarrollo de la interfaz interactiva.
- **Pandas:** Manipulación y análisis de datos.
- **Herramientas geoespaciales:** Procesamiento y visualización de información territorial.
- **Datos satelitales y ambientales:** Información para el análisis de las condiciones del territorio.

Para consultar las dependencias específicas del proyecto, revisa el archivo `requirements.txt`.

## 6. Estructura del proyecto

La organización general del repositorio es la siguiente:

- `app.py`: Archivo principal para ejecutar la aplicación.
- `components/`: Componentes reutilizables de la interfaz.
- `modules/`: Módulos de procesamiento de datos, indicadores, herramientas geográficas y lógica de análisis.
- `pages/`: Secciones principales de navegación de la aplicación.
- `data/`: Almacenamiento de datos originales, procesados y geográficos.
- `scripts/`: Scripts para la obtención y procesamiento de información.
- `tests/`: Pruebas automatizadas del proyecto.

## 7. Instalación y ejecución

### Requisitos previos

- Python instalado.
- Git instalado.
- Acceso a internet para obtener las dependencias necesarias.

### Paso 1. Clonar el repositorio

```bash
git clone https://github.com/USUARIO/AgroAdapt_Ebejico.git
cd AgroAdapt_Ebejico
```

### Paso 2. Crear un entorno virtual

```bash
python -m venv .venv
```

Activar el entorno virtual:

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### Paso 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### Paso 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

Una vez ejecutada, Streamlit proporcionará una dirección local para acceder a la aplicación. Generalmente:

```text
http://localhost:8501
```

## 8. Limitaciones

AgroAdapt Ebéjico es una herramienta de exploración y apoyo a la toma de decisiones. Sus visualizaciones y resultados analíticos deben interpretarse como recursos informativos y no como recomendaciones agrícolas definitivas ni predicciones garantizadas.

La calidad y disponibilidad de los resultados dependen de las fuentes de información utilizadas, su resolución espacial y temporal, y la disponibilidad de datos actualizados.

## 9. Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para conocer los términos y condiciones de uso, modificación y distribución del software.

La licencia del código fuente no implica que los datos, imágenes o recursos de terceros incluidos o utilizados por la aplicación estén sujetos a las mismas condiciones.

## 10. Equipo de desarrollo

**Desarrollado por:**

- Daniel Jimenez Estrada
- Emmanuel García Correa
- James Arley Díaz del Castillo

**NASA Space Apps Challenge 2026**

## 11. Agradecimientos

Agradecemos a la NASA y a las demás organizaciones proveedoras de datos por poner a disposición recursos de observación de la Tierra, información ambiental y herramientas geográficas que hacen posible este proyecto.

---

**AgroAdapt Ebéjico — Conectando los datos de observación de la Tierra con la adaptación agrícola local.**

---

# English

## 1. Overview

Agriculture faces increasing challenges due to environmental and climate variability. Access to reliable environmental information can help local communities better understand their territories and explore more sustainable agricultural practices.

AgroAdapt Ebéjico is an interactive platform that transforms satellite and environmental data into accessible visual information. It provides tools to explore local geographic conditions, consult environmental indicators, examine crop characteristics, and analyze potential crop rotation alternatives.

The project was developed as part of the **NASA Space Apps Challenge 2026**, demonstrating how Earth observation technologies can support agricultural decision-making in local contexts.

## 2. The Challenge

The project aims to make scientific and geospatial information more accessible and useful for agricultural adaptation.

By integrating satellite observations with local geographic and agricultural information, AgroAdapt seeks to bridge the gap between Earth observation data and its practical applications in rural communities.

## 3. Main Features

- **Territory Exploration:** Interactive visualization of Ebéjico's geographic boundaries, elevation information, and satellite imagery.
- **Environmental Analysis:** Exploration of environmental indicators and climate-related variables.
- **Crop Information:** Consultation and visualization of agricultural crop characteristics.
- **Crop Rotation:** Exploration of potential crop rotation alternatives to support agricultural planning.

## 4. Data Sources

The platform integrates information from different data sources:

- **NASA POWER:** Environmental and meteorological data. [Visit NASA POWER](https://power.larc.nasa.gov/)
- **Sentinel-2:** Satellite imagery and vegetation-related information. [Visit Copernicus Data Space](https://dataspace.copernicus.eu/)
- **NASADEM:** Terrain elevation data and digital elevation models. [Visit NASA Earthdata](https://earthdata.nasa.gov/)
- **IGAC:** Geographic information and territorial boundaries. [Visit IGAC](https://www.igac.gov.co/)
- **Agricultural Datasets:** Agricultural information used to contextualize territorial analysis.

## 5. Technologies

The project uses the following technologies and tools:

- **Python:** Main programming language.
- **Streamlit:** Interactive application interface.
- **Pandas:** Data manipulation and analysis.
- **Geospatial Tools:** Processing and visualization of territorial information.
- **Satellite and Environmental Data:** Information used to analyze local conditions.

See `requirements.txt` for the project's specific dependencies.

## 6. Project Structure

The repository is organized as follows:

- `app.py`: Main application entry point.
- `components/`: Reusable interface components.
- `modules/`: Data processing, indicators, geographic utilities, and analytical logic.
- `pages/`: Main application sections.
- `data/`: Raw, processed, and geographic datasets.
- `scripts/`: Data acquisition and processing scripts.
- `tests/`: Automated tests.

## 7. Installation and Usage

### Requirements

- Python installed.
- Git installed.
- Internet access to install the required dependencies.

### Step 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/AgroAdapt_Ebejico.git
cd AgroAdapt_Ebejico
```

### Step 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### Step 3. Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4. Run the application

```bash
streamlit run app.py
```

Once running, Streamlit will provide a local address to access the application, usually:

```text
http://localhost:8501
```

## 8. Limitations

AgroAdapt Ebéjico is an exploratory analysis and decision-support tool. Its visualizations and analytical outputs should be interpreted as informational resources, not as definitive agricultural recommendations or guaranteed predictions.

The quality and availability of results depend on the underlying data sources, their spatial and temporal resolution, and the availability of updated information.

## 9. License

This project is distributed under the MIT License. See the `LICENSE` file for details regarding the use, modification, and distribution of the software.

The software license does not automatically apply to third-party datasets, images, or other external resources used by the application.

## 10. Development Team

**Developed by:**

- Daniel Jimenez Estrada
- Emmanuel García Correa
- James Arley Díaz del Castillo

**NASA Space Apps Challenge 2026**

## 11. Acknowledgments

We acknowledge NASA and the other data providers whose Earth observation, environmental, and geographic resources make this project possible.

---

**AgroAdapt Ebéjico — Connecting Earth observation data with local agricultural adaptation.**
