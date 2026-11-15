# AgroAdapt Ebéjico — Fichas agronómicas, bloques 1 y 2
**Cultivos:** fríjol, maíz, tomate, yuca, aguacate, cacao, café, caña, lima, limón, maracuyá y plátano  
**Versión:** 2026-11-15  
**Estado:** referencias técnicas documentadas; no equivale a validación parcelaria en Ebéjico.

## Alcance y precauciones
Esta entrega completa el bloque 2 en los tres CSV existentes, conservando el esquema del bloque 1. No modifica `crops_catalog.csv`, `catalogo_agronomico_ebejico.csv`, módulos Python ni las plantillas ambientales. Los valores con `reference_only` son referencias publicadas y deben contrastarse con variedad, altitud, sistema productivo y análisis de suelo/agua del lote. Los campos `pending` permanecen vacíos deliberadamente.

## Hallazgos principales
- **Fríjol común:** AGROSAVIA publica alrededor de 500 mm/ciclo, 15–27 °C, suelos franco-limosos a franco-arcillosos, profundos y bien drenados, pH 5,5–6,5 en su referencia de Cundinamarca. No asumir que describe todas las variedades ni parcelas de Ebéjico.
- **Maíz:** la fuente técnica colombiana reporta 550–650 mm por ciclo y picos de 4,8–5,4 mm/día en germinación, floración y llenado; la temperatura óptima se diferencia por ambiente (30–34 °C en tierras bajas/media altitud y alrededor de 21 °C en tierras altas). El pH de referencia es 5,6–7,5. No se fija ciclo en días sin conocer el híbrido/variedad.
- **Tomate:** el manual consultado es para producción protegida en Antioquia. Reporta 21–27 °C como óptimo, riego dependiente de la fenología y 1–1,5 L/planta/día como referencia literaria. El inicio de cosecha alrededor de 90 días tras trasplante corresponde al sistema descrito, no a todo tomate. Se registran mosca blanca y ácaros como problemas relevantes.
- **Yuca:** AGROSAVIA (2024) reporta 8–18 meses, 750–2.000 mm de precipitación, 25–32 °C, pH 5,5–7,5, textura franca a franco-arcillosa y profundidad de suelo superior a 60 cm. Esa profundidad es del suelo requerido, no de raíz medida. El manual recomienda rotar con cultivos de otra familia y menciona maíz y fríjol; en un capítulo regional también advierte evitar lotes procedentes de maíz/gramíneas cuando exista alta población del chinche de la viruela. La regla debe condicionarse al historial fitosanitario.
- **Aguacate:** el manual AGROSAVIA de Hass indica suelos bien drenados, sensibilidad al anegamiento y un rango general de pH de 5–7. Los rangos de temperatura, precipitación y profundidad no se completan hasta verificar su contexto dentro de la fuente.
- **Cacao:** el manual AGROSAVIA del sistema agroforestal cita 18–32 °C como rango recomendado en Colombia y destaca la interacción entre luz, sombra, temperatura y agua. El cacao requiere analizarse como sistema agroforestal, no como una rotación anual de cultivos transitorios.
- **Caña panelera:** la guía de Cundinamarca describe un mínimo recomendado de 1.500 mm/año y temperaturas aproximadas de 18–30 °C para las zonas que analiza. La ficha EVA no confirma si se trata de caña panelera; estos valores no son mediciones de Ebéjico.
- **Cítricos (lima/limón):** AGROSAVIA diferencia lima Tahití (*Citrus × latifolia*), limón pajarito (*C. aurantiifolia*) y limón verdadero (*C. limon*). Los nombres “lima” y “limón” en EVA no bastan para identificar la especie; no se asignan todavía requerimientos numéricos.
- **Maracuyá:** AGROSAVIA describe zonas cálidas productoras con 22–29 °C y 700–3.000 mm/año. Son intervalos ambientales amplios de las zonas productoras citadas, no óptimos universales ni observaciones de Ebéjico.
- **Plátano:** el manual del Suroeste antioqueño diferencia Dominico Hartón (13–14 meses; temperatura media de 21 °C) y Dominico (16–18 meses; 18–19 °C). También reporta 120–150 mm/mes bien distribuidos, mayoría de raíces en 20–40 cm y profundidad efectiva de suelo superior a 0,60 m. El cultivar de los registros EVA sigue pendiente.
- **Café:** el enlace técnico previamente registrado no estuvo disponible (devolvió 404); se retiraron de la ficha los rangos que no se pudieron verificar. La búsqueda de una fuente accesible es pendiente.

Los valores de este bloque permanecen en `reference_only`, salvo atributos marcados `pending`; no representan validación local en Ebéjico. En la revisión se retiraron los intervalos numéricos no comprobados en sus fuentes. Las filas pendientes no deben convertirse en ceros ni alimentar recomendaciones.

## Vacíos que no se rellenaron
1. Ciclos locales en días de fríjol y maíz; identificar variedad/híbrido.
2. Profundidad radicular cuantitativa para los cuatro cultivos.
3. Requerimientos nutricionales cuantitativos por cultivo: deben derivarse de fuentes específicas y análisis de suelo, no de dosis genéricas.
4. Pautas de cobertura del suelo y compatibilidad local de rotación; la recomendación de yuca después de maíz requiere revisar historial de chinche de la viruela y otras condiciones fitosanitarias.
5. Identificación de variedades/sistemas productivos que realmente se usan en Ebéjico.
6. Validación con productores/UMATA y resultados de análisis de suelo.

## Integración
- `fichas_agronomicas_bloque1.csv`: una fila por atributo, con valor, unidad, fuente, alcance geográfico y nivel de evidencia.
- `fuentes_tecnicas_bloque1.csv`: registro bibliográfico y limitaciones.
- `agronomic_reference_records.csv`: registros normalizados generados desde la raíz del proyecto con `.venv/bin/python -m scripts.sync_agronomic_catalog`; vincula cada ficha con el catálogo mediante `crop_id` y cada referencia con `source_id`.
- La sincronización conserva `pending_local_validation` en el catálogo principal. No convierte referencias generales en datos verificados de Ebéjico.
- La última sincronización generó 58 registros trazables: 40 referencias generales y 18 atributos pendientes. La validación estructural reportó 0 errores; los campos agronómicos incompletos siguen pendientes en los 12 cultivos.
- `criterios_rotacion_bloque1.csv`: reglas preliminares, sin puntuaciones de aptitud.
- La función `get_crop_profile` en `modules/crop_catalog.py` entrega el registro canónico junto con sus referencias técnicas.
- `environmental_indicators.csv` aún no ha sido entregado por el Integrante 1: el chequeo queda en `awaiting_integrante_1` con 0 registros, por lo que no se generan evaluaciones ni recomendaciones reales. Las plantillas de `data/outputs/` son solo esquemas.

## Fuentes consultadas
1. AGROSAVIA (2022), *Aspectos generales del cultivo de fríjol en Cundinamarca*: https://repository.agrosavia.co/server/api/core/bitstreams/d3d38353-df1e-4c1d-bcac-502b6fe293f0/content
2. CORPOICA/AGROSAVIA, *Aspectos técnicos de la producción de maíz en Colombia*: https://repository.agrosavia.co/bitstream/handle/20.500.12324/19418/45021_60774.pdf
3. CORPOICA/FAO/Gobernación de Antioquia-MANA (2007), *Buenas Prácticas Agrícolas en tomate bajo condiciones protegidas*: https://repository.agrosavia.co/server/api/core/bitstreams/6d2a5bf5-733f-4bab-88fe-c8de51c8ccb1/content
4. AGROSAVIA (2024), *Manual de manejo de yuca para consumo fresco en diferentes regiones de Colombia*: https://editorial.agrosavia.co/index.php/publicaciones/catalog/download/401/461/2326-1?inline=1
5. ICA, *Protección fitosanitaria en maíz*: https://www.ica.gov.co/areas/agricola/direccion-tecnica-de-sanidad-vegetal/proteccion-fitosanitaria-en-maiz-y-sorgo
6. ICA, *Manejo Integrado de Plagas*: https://www.ica.gov.co/preguntas-frecuentes/agricola/que-es-el-manejo-integrado-de-plagas-mip
7. AGROSAVIA (2023), *Prácticas de manejo sostenible para fertilización y riego de aguacate Hass en el departamento del Cauca*: https://editorial.agrosavia.co/index.php/publicaciones/catalog/book/357
8. AGROSAVIA (2025), *Manual del sistema agroforestal de cacao*: https://editorial.agrosavia.co/index.php/publicaciones/catalog/book/469
9. AGROSAVIA (2022), *Aspectos generales del cultivo de café en Cundinamarca*: enlace registrado no disponible al momento de la revisión; no se usó para validar rangos.
10. AGROSAVIA (2022), *Aspectos generales del cultivo de caña de azúcar para la producción panelera en Cundinamarca*: https://editorial.agrosavia.co/index.php/publicaciones/catalog/book/262
11. AGROSAVIA (2020), *Generalidades del cultivo, descripción botánica, variedades y fenología de la lima ácida Tahití*: https://vivo.agrosavia.co/display/cali1374
12. AGROSAVIA (2020), *Caracterización sanitaria de los cultivos de granadilla, gulupa y maracuyá en Colombia*: https://editorial.agrosavia.co/index.php/publicaciones/catalog/book/68
13. AGROSAVIA (2022), *Tecnología para el cultivo del plátano en el Suroeste antioqueño*: https://editorial.agrosavia.co/index.php/publicaciones/catalog/book/303
