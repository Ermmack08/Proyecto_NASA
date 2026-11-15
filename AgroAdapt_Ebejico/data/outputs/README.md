# Salidas para integración

Estos archivos definen los contratos de entrega del Integrante 2 al Integrante 3:

- `crop_assessment_template.csv`: una fila por cultivo evaluado, con estado, puntaje (si es evaluable), brechas, evidencia, fuentes y limitaciones.
- `rotation_alternatives_template.csv`: alternativas de rotación con criterios, puntaje, evidencia, fuentes y restricciones.

Son plantillas sin resultados. No representan recomendaciones y no deben renombrarse como salidas reales.

Las salidas `crop_assessment.csv` y `rotation_alternatives.csv` solo se generarán cuando existan datos ambientales compatibles, perfiles agronómicos suficientes y criterios de evaluación aprobados. Si faltan entradas críticas, el sistema debe informar la brecha y dejar los puntajes vacíos.
