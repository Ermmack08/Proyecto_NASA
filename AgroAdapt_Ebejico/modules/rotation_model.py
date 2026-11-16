import math

# Motor inicial de comparación multicriterio.
# Este módulo es un ESQUELETO: las puntuaciones y reglas deben acordarse con el
# integrante responsable del modelo agrícola y validarse con asesoría agronómica.
# No presentar el resultado como recomendación agronómica definitiva.

DEFAULT_WEIGHTS = {
    "climate": 0.25,
    "soil": 0.25,
    "soil_health": 0.20,
    "production": 0.20,
    "farmer_priority": 0.10,
}

def weighted_score(criteria_scores, weights=None):
    """
    Calcula un puntaje ponderado entre 0 y 100.
    criteria_scores: diccionario con claves iguales a DEFAULT_WEIGHTS y valores 0-100.
    """
    if not isinstance(criteria_scores, dict) or not criteria_scores:
        raise ValueError("No se recibieron puntuaciones para evaluar.")

    weights = DEFAULT_WEIGHTS if weights is None else weights
    if not isinstance(weights, dict):
        raise ValueError("Los pesos deben ser un diccionario de criterios.")
    missing = set(DEFAULT_WEIGHTS).difference(criteria_scores)
    if missing:
        raise ValueError(
            "Faltan puntuaciones para los criterios: "
            f"{', '.join(sorted(missing))}."
        )
    unknown = set(criteria_scores).difference(DEFAULT_WEIGHTS)
    if unknown:
        raise ValueError(
            f"Criterios no reconocidos: {', '.join(sorted(unknown))}."
        )
    if set(weights) != set(DEFAULT_WEIGHTS):
        raise ValueError("Los pesos deben incluir los cinco criterios definidos.")

    scores = {}
    numeric_weights = {}
    for key in DEFAULT_WEIGHTS:
        try:
            scores[key] = float(criteria_scores[key])
            numeric_weights[key] = float(weights[key])
        except (TypeError, ValueError) as error:
            raise ValueError(f"El criterio {key} debe tener un valor numérico.") from error
        if not math.isfinite(scores[key]) or not 0 <= scores[key] <= 100:
            raise ValueError(f"La puntuación de {key} debe estar entre 0 y 100.")
        if not math.isfinite(numeric_weights[key]) or numeric_weights[key] < 0:
            raise ValueError(f"El peso de {key} debe ser un número no negativo.")

    total_weight = sum(numeric_weights.values())
    if total_weight <= 0:
        raise ValueError("La suma de los pesos debe ser mayor que cero.")

    return sum(scores[key] * numeric_weights[key] for key in scores) / total_weight

def compare_rotations(rotation_records, weights=None):
    """
    Recibe una lista de escenarios:
    [{"name": "...", "scores": {...}, "description": "..."}]
    Devuelve escenarios con puntuación. En la integración real, scores vendrán
    del motor del integrante 2; esta función solo estandariza la presentación.
    """
    if not isinstance(rotation_records, list) or not rotation_records:
        raise ValueError("Se requiere una lista no vacía de escenarios.")

    results = []
    for index, item in enumerate(rotation_records, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El escenario {index} debe ser un objeto JSON.")
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError(f"El escenario {index} debe tener un nombre.")
        if not isinstance(item.get("description"), str) or not item["description"].strip():
            raise ValueError(f"El escenario {item['name']} debe incluir una descripción.")
        if not isinstance(item.get("scores"), dict):
            raise ValueError(f"El escenario {item['name']} debe incluir scores.")
        if not isinstance(item.get("limitations"), str) or not item["limitations"].strip():
            raise ValueError(f"El escenario {item['name']} debe documentar sus limitaciones.")
        score = weighted_score(item["scores"], weights=weights)
        results.append({
            "name": item["name"],
            "score": round(score, 1),
            "description": item["description"],
            "scores": item["scores"],
            "limitations": item["limitations"],
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
