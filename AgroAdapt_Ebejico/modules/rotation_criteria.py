"""
Definición de criterios, pesos y reglas agronómicas iniciales.

Los pesos son parámetros configurables para el prototipo, no constantes científicas.
El equipo debe justificarlos y validarlos con asesoría agronómica y prioridades locales.
"""

DEFAULT_WEIGHTS = {
    "climate": 0.25,          # Compatibilidad con temperatura/lluvia/estacionalidad
    "soil": 0.25,             # Compatibilidad con propiedades de suelo disponibles
    "soil_health": 0.20,      # Diversidad, cobertura y efectos esperados sobre el suelo
    "production": 0.20,       # Evidencia productiva y viabilidad del sistema
    "farmer_priority": 0.10,  # Preferencias y restricciones del productor
}

CRITERIA_DESCRIPTIONS = {
    "climate": "Compatibilidad climática de los cultivos con el escenario analizado.",
    "soil": "Compatibilidad entre los requerimientos del cultivo y los datos de suelo.",
    "soil_health": "Diversificación de familias, cobertura y manejo de residuos.",
    "production": "Evidencia de producción y viabilidad productiva local.",
    "farmer_priority": "Ajuste a las prioridades declaradas por el agricultor.",
}

# Penalizaciones configurables. Aplicar únicamente si la información agronómica
# de la especie y el contexto confirma la condición.
DEFAULT_RULES = {
    "same_family_consecutive_penalty": 15,
    "missing_evidence_penalty": 0,  # No penalizar automáticamente: marcar como no evaluable.
    "minimum_score": 0,
    "maximum_score": 100,
}

def validate_weights(weights: dict) -> None:
    if not weights:
        raise ValueError("Debe definirse al menos un peso.")
    if any(value < 0 for value in weights.values()):
        raise ValueError("Los pesos no pueden ser negativos.")
    if sum(weights.values()) <= 0:
        raise ValueError("La suma de los pesos debe ser mayor que cero.")
