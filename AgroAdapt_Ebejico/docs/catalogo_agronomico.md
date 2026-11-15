# Protocolo para construir el catálogo agronómico

## A. Evidencia productiva local
Para cada cultivo:
- Confirmar presencia en EVA para Ebéjico (código 05240).
- Registrar años y periodos disponibles.
- Registrar área sembrada, cosechada, producción y rendimiento.
- Revisar vacíos, cambios de clasificación y posibles valores atípicos.
- Contrastar con UMATA/Secretaría de Agricultura, asociaciones y productores.

EVA caracteriza la producción a escala municipal; no identifica por sí sola la ubicación
de cada cultivo ni describe las propiedades de cada parcela.

## B. Evidencia agronómica
Registrar para cada especie:
- Nombre común y científico.
- Familia botánica.
- Ciclo y duración (indicando variedad/sistema cuando aplique).
- Requerimientos de temperatura y agua.
- Requerimientos de suelo: textura, drenaje, pH y profundidad efectiva.
- Extracción/aporte de nutrientes, con fuente técnica.
- Arquitectura radicular y cobertura del suelo.
- Susceptibilidad a plagas/enfermedades relevantes para secuencias.
- Compatibilidad con otros cultivos y prácticas de manejo.

## C. Estado de evidencia
- `verified`: respaldado por fuente y/o validación local identificable.
- `reference_only`: dato de referencia general, aún no validado en Ebéjico.
- `pending_local_validation`: dato faltante o pendiente de confirmar.

No convertir campos vacíos en cero. No inferir presencia local solo porque el cultivo
sea común en Antioquia o Colombia.

## D. Cultivos permanentes
Café, plátano y caña pueden requerir análisis de asociación, renovación, cobertura,
rotación en etapas de establecimiento o manejo de entrecalles. No forzar secuencias
anuales de cultivos transitorios sobre sistemas permanentes.
