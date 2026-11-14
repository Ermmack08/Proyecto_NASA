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

## 3. Estructura
- `app.py`: página principal y resumen.
- `pages/`: páginas que Streamlit detecta automáticamente.
- `modules/`: funciones compartidas de carga, mapas, indicadores y modelo.
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

### Datos ambientales
El archivo de entrada inicial es `data/processed/environment_demo.csv`.
Para reemplazarlo, conservar al menos:
- `date`: fecha en formato ISO.
- columnas numéricas para variables.
- `source`: fuente de los datos.
- `is_demo`: False para datos reales.
Documentar unidades y resolución en un archivo de metadatos o diccionario de datos.

### Cultivos / modelo agrícola
El catálogo se carga desde `data/processed/crops_catalog.csv`.
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

## 5. Buenas prácticas
1. Mantener intactos los datos originales en `raw`.
2. No descargar ni procesar imágenes satelitales pesadas al abrir el dashboard.
3. Preparar capas y tablas antes de iniciar Streamlit.
4. Registrar fuente, fecha, unidad, resolución y cobertura espacial/temporal.
5. Diferenciar datos observados, estimados, modelados y sintéticos.
6. No afirmar precisión a nivel de parcela si la resolución de la fuente no lo permite.
7. Invalidar caché de Streamlit cuando se actualicen archivos (`st.cache_data`).

## 6. Siguiente integración
Primero sustituir los GeoJSON vacíos por el límite municipal oficial y cargar una capa sencilla.
Después conectar la tabla ambiental real y, finalmente, consumir la salida del modelo de rotaciones.
