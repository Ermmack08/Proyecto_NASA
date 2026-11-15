"""
Motor multicriterio de comparación de rotaciones de AgroAdapt Ebéjico.

No convierte datos faltantes en puntuaciones. Una alternativa solo recibe
puntaje total cuando los cinco criterios tienen valores y no hay restricciones
bloqueantes declaradas por el análisis agronómico.
"""
from modules.rotation_criteria import DEFAULT_WEIGHTS, validate_weights

SCORE_KEYS = tuple(DEFAULT_WEIGHTS.keys())

def weighted_score(criteria_scores: dict, weights: dict | None = None) -> float:
    """Promedio ponderado de criterios disponibles; función matemática auxiliar."""
    weights = weights or DEFAULT_WEIGHTS
    validate_weights(weights)
    available = {
        key: float(criteria_scores[key])
        for key in weights
        if key in criteria_scores and criteria_scores[key] is not None
    }
    if not available:
        raise ValueError("No hay criterios evaluables para calcular el puntaje.")
    for key, value in available.items():
        if not 0 <= value <= 100:
            raise ValueError(f"El criterio '{key}' debe estar entre 0 y 100.")
    active_weight = sum(weights[key] for key in available)
    if active_weight <= 0:
        raise ValueError("Los criterios disponibles tienen peso total cero.")
    return sum(available[key] * weights[key] for key in available) / active_weight

def evaluate_rotation(rotation: dict, weights: dict | None = None) -> dict:
    """Evalúa una alternativa; no asigna total si faltan criterios o hay bloqueos."""
    weights = weights or DEFAULT_WEIGHTS
    validate_weights(weights)
    scores = rotation.get("scores") or {}
    normalized_scores = {key: scores.get(key) for key in SCORE_KEYS}
    missing = [key for key in SCORE_KEYS if normalized_scores.get(key) is None]

    raw_limitations = rotation.get("limitations") or []
    if isinstance(raw_limitations, str):
        limitations = [raw_limitations] if raw_limitations else []
    else:
        limitations = list(raw_limitations)

    blocking = rotation.get("blocking_constraints") or []
    if isinstance(blocking, str):
        blocking = [blocking] if blocking else []

    # Validate any supplied score even if the alternative is not yet evaluable.
    for key, value in normalized_scores.items():
        if value is not None:
            number = float(value)
            if not 0 <= number <= 100:
                raise ValueError(f"El criterio '{key}' debe estar entre 0 y 100.")
            normalized_scores[key] = number

    if missing:
        limitations.append("Criterios sin información suficiente: " + ", ".join(missing))
    if blocking:
        limitations.append("Restricciones bloqueantes: " + "; ".join(map(str, blocking)))

    evaluable = not missing and not blocking
    total = round(weighted_score(normalized_scores, weights), 1) if evaluable else None
    evidence_status = rotation.get("evidence_status", "pending_local_validation")
    if not evaluable:
        evidence_status = "insufficient_evidence" if missing else "blocked_by_constraint"

    result = {
        "name": rotation["name"],
        "description": rotation.get("description", ""),
        "scores": normalized_scores,
        "total_score": total,
        # Alias temporal para compatibilidad con pages/4_Rotaciones.py existente.
        "score": total,
        "limitations": "; ".join(limitations) if limitations else "No reportadas.",
        "evidence_status": evidence_status,
        "sequence": rotation.get("sequence", []),
        "sources": rotation.get("sources", []),
        "evaluable": evaluable,
        "blocking_constraints": list(blocking),
    }
    return result

def compare_rotations(rotations: list[dict], weights: dict | None = None) -> list[dict]:
    """Ordena alternativas evaluables primero; las no evaluables quedan al final."""
    results = [evaluate_rotation(item, weights) for item in rotations]
    return sorted(
        results,
        key=lambda item: (
            item["evaluable"],
            item["total_score"] if item["total_score"] is not None else -1
        ),
        reverse=True
    )

def to_streamlit_contract(results: list[dict]) -> list[dict]:
    """Entrega el contrato de salida sin ocultar faltantes ni restricciones."""
    return [
        {
            "name": item["name"],
            "description": item["description"],
            "scores": item["scores"],
            "limitations": item["limitations"],
            "total_score": item["total_score"],
            "evidence_status": item["evidence_status"],
            "evaluable": item["evaluable"],
            "blocking_constraints": item["blocking_constraints"],
            "sources": item["sources"],
        }
        for item in results
    ]
