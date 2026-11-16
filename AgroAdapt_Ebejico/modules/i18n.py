"""Small bilingual interface dictionary with device-locale detection."""

import locale
import os


TRANSLATIONS = {
    "es": {
        "language_label": "Idioma / Language",
        "language_auto": "Automático (idioma del equipo)",
        "language_spanish": "Español",
        "language_english": "English",
        "nav_home": "Inicio",
        "nav_territory": "Territorio",
        "nav_environment": "Ambiente",
        "nav_crops": "Cultivos",
        "nav_rotations": "Rotaciones",
        "app_description": (
            "Sistema de apoyo a decisiones agrícolas mediante el análisis de "
            "datos ambientales y geoespaciales."
        ),
        "purpose_title": "Propósito del prototipo",
        "purpose_text": (
            "Integrar información territorial, ambiental y agrícola para "
            "explorar y comparar alternativas de rotación de cultivos."
        ),
        "recommendation_validation": (
            "Las recomendaciones generadas deben validarse con información "
            "local y criterio agronómico."
        ),
        "overview": "Vista general",
        "environment_records": "Registros ambientales",
        "available_variables": "Variables disponibles",
        "data_status": "Estado de los datos",
        "demo": "Demostración",
        "data_loaded": "Datos cargados",
        "explore_agroadapt": "Explora AgroAdapt",
        "home_modules_intro": (
            "La plataforma está organizada en cuatro módulos que permiten "
            "analizar el territorio, consultar las condiciones ambientales, "
            "explorar cultivos y comparar alternativas agrícolas."
        ),
        "territory_description": (
            "Consulta la ubicación geográfica de Ebéjico, sus límites "
            "municipales y las zonas de análisis."
        ),
        "environment_description": (
            "Explora variables ambientales, indicadores y comportamientos temporales."
        ),
        "crops_description": (
            "Consulta el catálogo de cultivos y sus requerimientos ambientales y agrícolas."
        ),
        "rotations_description": (
            "Compara alternativas de rotación y consulta los criterios utilizados "
            "en su evaluación."
        ),
        "demo_data_warning": (
            "Los datos ambientales actuales son sintéticos y se utilizan para "
            "demostrar el funcionamiento de la plataforma. No representan "
            "mediciones reales de Ebéjico."
        ),
        "loaded_data_info": (
            "La información ambiental se cargó desde los archivos disponibles "
            "en el proyecto. Consulta las fuentes y limitaciones de cada variable "
            "en el módulo correspondiente."
        ),
        "footer": "AgroAdapt Ebéjico | Sistema de apoyo a decisiones agrícolas",
        "environment_title": "Condiciones ambientales",
        "temperature": "Temperatura a 2 m",
        "precipitation": "Precipitación corregida, tasa diaria media del mes",
        "mm_per_day": "mm/día",
        "humidity": "Humedad relativa a 2 m",
        "no_environment": (
            "No hay datos ambientales. Incorpora el CSV procesado en "
            "`data/processed/environment_nasa_power.csv`."
        ),
        "synthetic_warning": (
            "La tabla contiene datos sintéticos para demostración; no son "
            "mediciones reales."
        ),
        "environment_caption": (
            "Consulta tendencias temporales. Confirma la unidad, resolución y "
            "fuente en los metadatos antes de interpretar los datos."
        ),
        "power_warning": (
            "NASA POWER entrega datos meteorológicos derivados de MERRA-2. Son "
            "estimaciones de una celda/modelo para el punto indicado, no mediciones "
            "de cada finca ni una imagen satelital de alta resolución. Contrástalos "
            "con observaciones locales antes de usarlos para decisiones agrícolas."
        ),
        "power_docs": "Documentación de la API mensual NASA POWER",
        "no_numeric_environment": "No se encontraron variables numéricas para graficar.",
        "environment_variable": "Variable ambiental",
        "monthly_series": "Serie mensual: {variable}",
        "month": "Mes",
        "average": "Promedio de {variable}",
        "precipitation_note": (
            "La precipitación de POWER está en mm/día como tasa media diaria "
            "mensual; no es el acumulado mensual."
        ),
        "data_provenance": "Datos y procedencia",
        "date_coverage": "Cobertura temporal disponible: {start} a {end}",
        "declared_sources": "Fuentes declaradas: {sources}",
        "no_source": "Sin fuente declarada",
        "environment_info": (
            "Documenta fuente, unidades, resolución espacial, cobertura temporal "
            "y método de procesamiento. No interpretes datos de demostración "
            "como observaciones reales."
        ),
        "crops_title": "Catálogo de cultivos",
        "crop_sheets": "Fichas de cultivos",
        "municipal_history": "Histórico municipal",
        "empty_catalog": (
            "El catálogo está vacío. Completa crops_catalog.csv con información verificada."
        ),
        "search_crop": "Buscar cultivo",
        "no_crop_matches": "No hay cultivos que coincidan con la búsqueda.",
        "select_crop": "Selecciona un cultivo",
        "unverified_crop_source": "La fuente de esta ficha está pendiente de verificación.",
        "crop_sheet_note": (
            "Cada ficha debe conservar la fuente y diferenciar datos locales "
            "de referencias generales."
        ),
        "empty_history": (
            "No hay registros del histórico EVA. Revisa data/processed/eva_ebejico.csv."
        ),
        "published_records": "Registros publicados",
        "reported_crops": "Cultivos reportados",
        "recorded_coverage": "Cobertura registrada",
        "eva_source_caption": (
            "Fuente: Evaluaciones Agropecuarias Municipales (EVA), MinAgricultura, "
            "municipio de Ebéjico. Cobertura disponible en este conjunto: 2006–2018."
        ),
        "original_dataset": "Consultar conjunto original en Datos Abiertos",
        "eva_warning": (
            "Estos son registros agregados del municipio, no secuencias de una "
            "misma parcela. La fuente tiene varias filas para algunos cultivos y "
            "años: se conservan sin sumarlas. Un año sin fila significa "
            "“sin registro en este conjunto”, no producción cero. Por eso este "
            "histórico no permite calcular cada cuánto rotar ni recomendar un "
            "intervalo ideal."
        ),
        "history_crop": "Cultivo del histórico",
        "indicator": "Indicador",
        "year": "Año",
        "crop": "Cultivo",
        "crop_group": "Grupo del cultivo",
        "crop_subgroup": "Subgrupo del cultivo",
        "scientific_name": "Nombre científico",
        "reported_detail": "Desagregación reportada",
        "eva_cycle": "Ciclo (categoría EVA)",
        "planted_area": "Área sembrada (ha)",
        "harvested_area": "Área cosechada (ha)",
        "production": "Producción (t)",
        "yield": "Rendimiento (t/ha)",
        "reported_value": "{metric} reportado: {crop}",
        "download_crop_records": "Descargar registros del cultivo seleccionado",
        "territory_title": "Diagnóstico territorial",
        "territory_caption": (
            "Exploración geográfica del municipio y de las unidades espaciales disponibles."
        ),
        "layer_to_query": "Capa para consultar",
        "query_same_layer": "La consulta del punto usa la misma capa seleccionada.",
        "layer_ndvi": "Vegetación (NDVI)",
        "layer_rgb": "Color real Sentinel-2",
        "layer_elevation": "Elevación (NASADEM/SRTM)",
        "layer_slope": "Pendiente del terreno",
        "missing_boundary": (
            "El archivo del límite municipal aún no contiene geometrías. El mapa "
            "base es solo de referencia y no representa un límite oficial."
        ),
        "municipal_boundary": (
            "Límite municipal: {municipality}, {department} · Código DANE {code} · "
            "Fuente: IGAC."
        ),
        "boundary_warning": (
            "El límite municipal sirve para orientar el análisis territorial; "
            "no representa linderos de fincas ni parcelas."
        ),
        "no_zones": "No hay zonas de análisis cargadas; se mostrará el mapa base.",
        "missing_previews": (
            "Se encontraron metadatos satelitales, pero faltan las imágenes de "
            "visualización. Vuelve a ejecutar el procesamiento de capas."
        ),
        "satellite_not_ready": (
            "Las capas Sentinel-2 y NASADEM aún no están preparadas. Ejecuta "
            "`python scripts/fetch_satellite_layers.py` desde la carpeta del proyecto."
        ),
        "slope_not_ready": (
            "La pendiente derivada aún no está preparada. Vuelve a ejecutar "
            "`python scripts/fetch_satellite_layers.py` para generar la capa."
        ),
        "sentinel_scene": "Escena Sentinel-2",
        "municipal_mean_ndvi": "NDVI medio municipal",
        "clear_area": "Área válida sin nubes",
        "elevation": "Elevación NASADEM",
        "mean_slope": "Pendiente media",
        "point_information": "Información del punto seleccionado",
        "selected_point": (
            "Punto marcado: {latitude:.5f}, {longitude:.5f} · {layer}."
        ),
        "scene_date": "Fecha de escena: {date}",
        "approx_resolution": "Resolución aproximada: {resolution:g} m",
        "pixel_center": (
            "Se consulta el píxel que contiene el clic; centro aproximado del píxel: "
            "{latitude:.5f}, {longitude:.5f}."
        ),
        "no_pixel_value": (
            "No hay un valor válido en ese píxel. Puede estar fuera del municipio, "
            "cubierto por nubes/sombras o ser un dato no disponible."
        ),
        "point_ndvi": "NDVI en el punto",
        "ndvi_note": (
            "Un NDVI mayor suele reflejar una respuesta más vigorosa de la vegetación; "
            "no identifica el cultivo ni confirma su estado agronómico."
        ),
        "red_band": "B04 · rojo",
        "green_band": "B03 · verde",
        "blue_band": "B02 · azul",
        "rgb_reflectance": "Reflectancia superficial escalada del producto Sentinel-2 L2A.",
        "point_elevation": "Elevación del punto",
        "point_slope": "Pendiente local",
        "slope_note": (
            "Ángulo calculado a partir del relieve NASADEM; no equivale a un "
            "diagnóstico de erosión ni a una medición de la parcela."
        ),
        "click_map": "Haz clic en el mapa para consultar el valor aproximado del píxel.",
        "map_reading": (
            "**Lectura de capas:** NDVI en tonos marrones (valores bajos) a verdes "
            "(valores altos; escala visual −0,2 a 0,8); las zonas transparentes "
            "son píxeles enmascarados o sin datos. La elevación usa colores relativos "
            "al municipio; la pendiente va de verde (menor) a rojo (mayor), con escala "
            "visual limitada a 45°."
        ),
        "terrain_note": (
            "El NDVI se calcula con Sentinel-2 L2A (10 m); nubes, sombras y píxeles "
            "inciertos se enmascaran. NASADEM es un modelo de elevación de "
            "aproximadamente 30 m derivado principalmente de SRTM. La pendiente se "
            "deriva con el método Horn 3x3; no mide erosión ni susceptibilidad agrícola. "
            "Los datos describen el municipio, no parcelas ni fincas."
        ),
        "integration_info": "Información para integrar capas",
        "map_base_layer": "Límite municipal",
        "map_zones_layer": "Zonas de análisis",
        "map_point": "Punto consultado",
        "municipality": "Municipio:",
        "department": "Departamento:",
        "dane_code": "Código DANE:",
        "zone": "Zona:",
        "date_column": "Fecha",
        "source_column": "Fuente",
        "demo_column": "Es demostración",
        "layer_integration_markdown": (
            "- Límite municipal: `data/geographic/ebejico_boundary.geojson`.\n"
            "- Fuente del límite integrado: IGAC, Base de Datos Geográfica ET.\n"
            "- Para actualizarlo: `python scripts/fetch_igac_boundary.py`.\n"
            "- Metadatos de la consulta: `data/raw/igac_boundary_metadata.json`.\n"
            "- Preparar capas satelitales: `python scripts/fetch_satellite_layers.py`.\n"
            "- Metadatos Sentinel-2/NASADEM: `data/raw/satellite_layers_metadata.json`.\n"
            "- Elige la capa de consulta arriba del mapa y haz clic para ver el valor del píxel.\n"
            "- Zonas de análisis: `data/geographic/agricultural_zones.geojson`.\n"
            "- Usar geometrías oficiales y registrar fuente, fecha, escala y sistema de coordenadas.\n"
            "- No interpretar el mapa base como evidencia de límites o aptitud agrícola."
        ),
        "rotations_title": "Comparador de rotaciones",
        "rotations_caption": (
            "Compara escenarios recibidos del equipo agrícola. Los resultados son "
            "exploratorios y no constituyen una recomendación agronómica."
        ),
        "rotations_upload_info": (
            "Carga un archivo JSON con la lista de escenarios definida en el README. "
            "Esta página no crea puntuaciones ni escenarios de ejemplo."
        ),
        "scenario_file": "Archivo de escenarios JSON",
        "json_read_error": "No se pudo leer el archivo JSON: {error}",
        "comparison_weights": "Pesos de comparación",
        "weights_caption": (
            "Ajusta los pesos para explorar el efecto de cada criterio. Se normalizan "
            "al calcular el índice; deben validarse con el equipo técnico."
        ),
        "climate": "Clima",
        "soil": "Suelo",
        "soil_health": "Salud del suelo",
        "production": "Producción",
        "farmer_priority": "Prioridad del agricultor",
        "invalid_scenario_file": "El archivo no cumple el contrato del README: {error}",
        "comparison": "Comparación",
        "scenario": "Escenario",
        "exploratory_index": "Índice exploratorio (0–100)",
        "description": "Descripción",
        "weighted_chart_title": "Índice ponderado según los pesos seleccionados",
        "received_scores": "Puntuaciones recibidas por criterio",
        "limitations_assumptions": "Limitaciones y supuestos",
        "rotation_warning": (
            "El índice depende de las puntuaciones de entrada y de los pesos "
            "seleccionados. No representa aptitud de parcela ni reemplaza la "
            "validación agronómica local."
        ),
        "field_family": "Familia botánica",
        "field_cycle": "Ciclo productivo",
        "field_water_requirement": "Necesidad hídrica",
        "field_root_depth": "Profundidad radicular",
        "field_soil_requirements": "Requerimientos de suelo",
        "field_nutritional_notes": "Notas nutricionales",
        "field_rotation_notes": "Notas de rotación",
        "field_source": "Fuente",
        "download": "Descargar",
    },
    "en": {
        "language_label": "Language / Idioma",
        "language_auto": "Automatic (device language)",
        "language_spanish": "Español",
        "language_english": "English",
        "nav_home": "Home",
        "nav_territory": "Territory",
        "nav_environment": "Environment",
        "nav_crops": "Crops",
        "nav_rotations": "Rotations",
        "app_description": (
            "Agricultural decision-support system using environmental and "
            "geospatial data analysis."
        ),
        "purpose_title": "Prototype purpose",
        "purpose_text": (
            "Integrate territorial, environmental, and agricultural information "
            "to explore and compare crop rotation alternatives."
        ),
        "recommendation_validation": (
            "Generated recommendations must be validated with local information "
            "and agronomic expertise."
        ),
        "overview": "Overview",
        "environment_records": "Environmental records",
        "available_variables": "Available variables",
        "data_status": "Data status",
        "demo": "Demonstration",
        "data_loaded": "Data loaded",
        "explore_agroadapt": "Explore AgroAdapt",
        "home_modules_intro": (
            "The platform is organized into four modules to analyze the territory, "
            "explore environmental conditions and crops, and compare agricultural alternatives."
        ),
        "territory_description": (
            "Explore Ebéjico's location, municipal boundaries, and analysis zones."
        ),
        "environment_description": (
            "Explore environmental variables, indicators, and temporal patterns."
        ),
        "crops_description": (
            "Browse the crop catalog and its environmental and agricultural requirements."
        ),
        "rotations_description": (
            "Compare crop rotation alternatives and review the criteria used in their evaluation."
        ),
        "demo_data_warning": (
            "Current environmental data are synthetic and are used to demonstrate "
            "the platform. They are not real measurements from Ebéjico."
        ),
        "loaded_data_info": (
            "Environmental information was loaded from the files available in the "
            "project. See each variable's sources and limitations in its module."
        ),
        "footer": "AgroAdapt Ebéjico | Agricultural decision-support system",
        "environment_title": "Environmental conditions",
        "temperature": "Temperature at 2 m",
        "precipitation": "Bias-corrected precipitation, monthly mean daily rate",
        "mm_per_day": "mm/day",
        "humidity": "Relative humidity at 2 m",
        "no_environment": (
            "No environmental data found. Add the processed CSV at "
            "`data/processed/environment_nasa_power.csv`."
        ),
        "synthetic_warning": (
            "This table contains synthetic demonstration data; these are not real measurements."
        ),
        "environment_caption": (
            "Explore temporal trends. Check units, resolution, and source in the "
            "metadata before interpreting the data."
        ),
        "power_warning": (
            "NASA POWER provides weather data derived from MERRA-2. These are "
            "grid/model estimates for the selected point, not measurements from "
            "individual farms or high-resolution satellite imagery. Compare them "
            "with local observations before making agricultural decisions."
        ),
        "power_docs": "NASA POWER monthly API documentation",
        "no_numeric_environment": "No numeric variables were found to plot.",
        "environment_variable": "Environmental variable",
        "monthly_series": "Monthly series: {variable}",
        "month": "Month",
        "average": "Average {variable}",
        "precipitation_note": (
            "POWER precipitation is in mm/day as a monthly mean daily rate; it is "
            "not a monthly accumulation."
        ),
        "data_provenance": "Data and provenance",
        "date_coverage": "Available time coverage: {start} to {end}",
        "declared_sources": "Declared sources: {sources}",
        "no_source": "No source declared",
        "environment_info": (
            "Document the source, units, spatial resolution, time coverage, and "
            "processing method. Do not interpret demonstration data as observations."
        ),
        "crops_title": "Crop catalog",
        "crop_sheets": "Crop profiles",
        "municipal_history": "Municipal history",
        "empty_catalog": (
            "The catalog is empty. Add verified information to crops_catalog.csv."
        ),
        "search_crop": "Search crops",
        "no_crop_matches": "No crops match your search.",
        "select_crop": "Select a crop",
        "unverified_crop_source": "The source for this profile has not been verified.",
        "crop_sheet_note": (
            "Keep the source for each profile and distinguish local data from general references."
        ),
        "empty_history": (
            "No EVA history records found. Check data/processed/eva_ebejico.csv."
        ),
        "published_records": "Published records",
        "reported_crops": "Reported crops",
        "recorded_coverage": "Recorded coverage",
        "eva_source_caption": (
            "Source: Municipal Agricultural Evaluations (EVA), Ministry of Agriculture, "
            "municipality of Ebéjico. Coverage in this dataset: 2006–2018."
        ),
        "original_dataset": "Open the original dataset",
        "eva_warning": (
            "These are municipal aggregate records, not crop sequences from the same "
            "field. The source has multiple rows for some crops and years; they are "
            "kept separate. A year without a row means “no record in this dataset,” "
            "not zero production. This history cannot determine rotation frequency "
            "or recommend an ideal interval."
        ),
        "history_crop": "Crop in history",
        "indicator": "Indicator",
        "year": "Year",
        "crop": "Crop",
        "crop_group": "Crop group",
        "crop_subgroup": "Crop subgroup",
        "scientific_name": "Scientific name",
        "reported_detail": "Reported breakdown",
        "eva_cycle": "Cycle (EVA category)",
        "planted_area": "Planted area (ha)",
        "harvested_area": "Harvested area (ha)",
        "production": "Production (t)",
        "yield": "Yield (t/ha)",
        "reported_value": "Reported {metric}: {crop}",
        "download_crop_records": "Download selected crop records",
        "territory_title": "Territorial diagnosis",
        "territory_caption": (
            "Explore the municipality and available spatial units."
        ),
        "layer_to_query": "Layer to query",
        "query_same_layer": "The point query uses the selected layer.",
        "layer_ndvi": "Vegetation (NDVI)",
        "layer_rgb": "Sentinel-2 true color",
        "layer_elevation": "Elevation (NASADEM/SRTM)",
        "layer_slope": "Terrain slope",
        "missing_boundary": (
            "The municipal boundary file has no geometries yet. The base map is "
            "for reference only and does not show an official boundary."
        ),
        "municipal_boundary": (
            "Municipal boundary: {municipality}, {department} · DANE code {code} · "
            "Source: IGAC."
        ),
        "boundary_warning": (
            "The municipal boundary provides territorial context; it does not "
            "represent farm or field boundaries."
        ),
        "no_zones": "No analysis zones are loaded; the base map will be shown.",
        "missing_previews": (
            "Satellite metadata was found, but preview images are missing. Run the "
            "layer processing script again."
        ),
        "satellite_not_ready": (
            "Sentinel-2 and NASADEM layers are not prepared yet. Run "
            "`python scripts/fetch_satellite_layers.py` from the project folder."
        ),
        "slope_not_ready": (
            "The derived slope layer is not ready. Run "
            "`python scripts/fetch_satellite_layers.py` again to create it."
        ),
        "sentinel_scene": "Sentinel-2 scene",
        "municipal_mean_ndvi": "Municipal mean NDVI",
        "clear_area": "Valid cloud-free area",
        "elevation": "NASADEM elevation",
        "mean_slope": "Mean slope",
        "point_information": "Selected point information",
        "selected_point": "Selected point: {latitude:.5f}, {longitude:.5f} · {layer}.",
        "scene_date": "Scene date: {date}",
        "approx_resolution": "Approximate resolution: {resolution:g} m",
        "pixel_center": (
            "Querying the pixel containing the click; approximate pixel center: "
            "{latitude:.5f}, {longitude:.5f}."
        ),
        "no_pixel_value": (
            "No valid value is available for this pixel. It may be outside the "
            "municipality, covered by clouds/shadows, or contain missing data."
        ),
        "point_ndvi": "NDVI at point",
        "ndvi_note": (
            "Higher NDVI often reflects a stronger vegetation response; it does "
            "not identify the crop or confirm its agronomic condition."
        ),
        "red_band": "B04 · red",
        "green_band": "B03 · green",
        "blue_band": "B02 · blue",
        "rgb_reflectance": "Scaled surface reflectance from Sentinel-2 L2A.",
        "point_elevation": "Elevation at point",
        "point_slope": "Local slope",
        "slope_note": (
            "Angle derived from NASADEM terrain; it is not an erosion diagnosis "
            "or a field-level measurement."
        ),
        "click_map": "Click the map to query the approximate pixel value.",
        "map_reading": (
            "**Layer guide:** NDVI ranges from brown (lower values) to green "
            "(higher values; visual scale −0.2 to 0.8); transparent areas are "
            "masked pixels or no-data. Elevation colors are relative to the "
            "municipality; slope ranges from green (lower) to red (higher), with "
            "a visual scale capped at 45°."
        ),
        "terrain_note": (
            "NDVI is calculated from Sentinel-2 L2A (10 m); clouds, shadows, and "
            "uncertain pixels are masked. NASADEM is an approximately 30 m "
            "elevation model derived mainly from SRTM. Slope uses the Horn 3x3 "
            "method; it does not measure erosion or agricultural susceptibility. "
            "Data describe the municipality, not individual farms or fields."
        ),
        "integration_info": "Layer integration information",
        "map_base_layer": "Municipal boundary",
        "map_zones_layer": "Analysis zones",
        "map_point": "Queried point",
        "municipality": "Municipality:",
        "department": "Department:",
        "dane_code": "DANE code:",
        "zone": "Zone:",
        "date_column": "Date",
        "source_column": "Source",
        "demo_column": "Is demo",
        "layer_integration_markdown": (
            "- Municipal boundary: `data/geographic/ebejico_boundary.geojson`.\n"
            "- Integrated boundary source: IGAC, ET Geographic Database.\n"
            "- To update it: `python scripts/fetch_igac_boundary.py`.\n"
            "- Query metadata: `data/raw/igac_boundary_metadata.json`.\n"
            "- Prepare satellite layers: `python scripts/fetch_satellite_layers.py`.\n"
            "- Sentinel-2/NASADEM metadata: `data/raw/satellite_layers_metadata.json`.\n"
            "- Choose a query layer above the map and click to see the pixel value.\n"
            "- Analysis zones: `data/geographic/agricultural_zones.geojson`.\n"
            "- Use official geometries and record source, date, scale, and coordinate system.\n"
            "- Do not treat the base map as evidence of boundaries or agricultural suitability."
        ),
        "rotations_title": "Crop rotation comparator",
        "rotations_caption": (
            "Compare scenarios provided by the agricultural team. Results are "
            "exploratory and are not an agronomic recommendation."
        ),
        "rotations_upload_info": (
            "Upload a JSON file containing the scenario list defined in the README. "
            "This page does not create scores or example scenarios."
        ),
        "scenario_file": "JSON scenario file",
        "json_read_error": "Could not read the JSON file: {error}",
        "comparison_weights": "Comparison weights",
        "weights_caption": (
            "Adjust weights to explore each criterion's effect. They are normalized "
            "when the index is calculated and should be validated by the technical team."
        ),
        "climate": "Climate",
        "soil": "Soil",
        "soil_health": "Soil health",
        "production": "Production",
        "farmer_priority": "Farmer priority",
        "invalid_scenario_file": "The file does not match the README contract: {error}",
        "comparison": "Comparison",
        "scenario": "Scenario",
        "exploratory_index": "Exploratory index (0–100)",
        "description": "Description",
        "weighted_chart_title": "Weighted index using the selected weights",
        "received_scores": "Scores received for each criterion",
        "limitations_assumptions": "Limitations and assumptions",
        "rotation_warning": (
            "The index depends on input scores and selected weights. It does not "
            "represent field suitability or replace local agronomic validation."
        ),
        "field_family": "Botanical family",
        "field_cycle": "Growing cycle",
        "field_water_requirement": "Water requirement",
        "field_root_depth": "Root depth",
        "field_soil_requirements": "Soil requirements",
        "field_nutritional_notes": "Nutritional notes",
        "field_rotation_notes": "Rotation notes",
        "field_source": "Source",
        "download": "Download",
    },
}


def detect_system_language() -> str:
    """Return Spanish or English based on the operating-system locale."""
    candidates = [
        os.environ.get("LC_ALL"),
        os.environ.get("LC_MESSAGES"),
        os.environ.get("LANG"),
        os.environ.get("LANGUAGE"),
    ]
    try:
        candidates.append(locale.getlocale()[0])
    except locale.Error:
        pass

    for candidate in candidates:
        if not candidate:
            continue
        normalized = candidate.lower().replace("-", "_").split(".", maxsplit=1)[0]
        if normalized.startswith(("es", "spanish")):
            return "es"
        if normalized.startswith(("en", "english")):
            return "en"
    return "es"


def translate(key: str, language: str | None = None, **values: object) -> str:
    """Translate a UI string and format its named placeholders."""
    if language is None:
        import streamlit as st

        language = st.session_state.get("agroadapt_language", "es")
    if language not in TRANSLATIONS:
        raise ValueError(f"Unsupported language: {language}")
    try:
        text = TRANSLATIONS[language][key]
    except KeyError as error:
        raise KeyError(f"Missing translation key: {key}") from error
    return text.format(**values) if values else text
