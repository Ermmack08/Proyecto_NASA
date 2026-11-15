# Verificación de la base EVA compartida

Archivo procesado: `data/raw/eva/eva_2019_2025_base_agricola.csv`

Resultado reproducido con el procesador actualizado:
- Filas leídas en la base completa: 166.732
- Registros filtrados para Ebéjico (DANE 05240): 115
- Años presentes: 2019–2025
- Cultivos distintos reportados: 12
- Valores numéricos válidos en área sembrada, área cosechada, producción y rendimiento: 115 de 115 en cada campo.

Cultivos que aparecen en los registros EVA de Ebéjico:
Aguacate, Cacao, Café, Caña, Frijol, Lima, Limón, Maracuyá, Maíz, Plátano, Tomate y Yuca.

El catálogo agronómico inicial incluye seis fichas pendientes de validación: maíz, fríjol, yuca, café, plátano y caña. El contraste se entrega en `eva_ebejico_crop_presence.csv`. La diferencia de escritura entre “Frijol” y “Fríjol” se debe normalizar al consolidar el catálogo.

**Interpretación:** los valores agregados de presencia suman observaciones de los años/periodos disponibles; no deben presentarse como área actualmente sembrada ni como pronóstico. EVA es evidencia productiva municipal, no un mapa de ubicación de cultivos ni un diagnóstico parcelario.
