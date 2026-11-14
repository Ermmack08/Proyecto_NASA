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
    weights = weights or DEFAULT_WEIGHTS
    if not criteria_scores:
        raise ValueError("No se recibieron puntuaciones para evaluar.")

    active = {key: weight for key, weight in weights.items() if key in criteria_scores}
    if not active:
        raise ValueError("No hay criterios compatibles entre pesos y puntuaciones.")

    total_weight = sum(active.values())
    if total_weight <= 0:
        raise ValueError("La suma de los pesos debe ser mayor que cero.")

    for key in active:
        value = float(criteria_scores[key])
        if not 0 <= value <= 100:
            raise ValueError(f"La puntuación de {key} debe estar entre 0 y 100.")

    return sum(float(criteria_scores[k]) * active[k] for k in active) / total_weight

def compare_rotations(rotation_records):
    """
    Recibe una lista de escenarios:
    [{"name": "...", "scores": {...}, "description": "..."}]
    Devuelve escenarios con puntuación. En la integración real, scores vendrán
    del motor del integrante 2; esta función solo estandariza la presentación.
    """
    results = []
    for item in rotation_records:
        score = weighted_score(item["scores"])
        results.append({
            "name": item["name"],
            "score": round(score, 1),
            "description": item.get("description", ""),
            "scores": item["scores"],
            "limitations": item.get("limitations", "Pendiente de documentar."),
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
