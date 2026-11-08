from .models import Symptom, ConditionSymptom, Condition

def match_conditions(symptom_names):
    """
    Simple weighted catalogue matching for demonstration only.
    This is not a diagnostic algorithm and must not be used for clinical decisions.
    """
    normalized = {s.strip().lower() for s in symptom_names if s.strip()}
    if not normalized:
        return []
    rows = (
        ConditionSymptom.query
        .join(Symptom, ConditionSymptom.symptom_id == Symptom.id)
        .join(Condition, ConditionSymptom.condition_id == Condition.id)
        .filter(Symptom.active.is_(True), Condition.active.is_(True))
        .all()
    )
    scores = {}
    for row in rows:
        if row.symptom.name.lower() in normalized:
            scores[row.condition_id] = scores.get(row.condition_id, 0) + max(1, min(row.weight, 5))
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:3]
    return [(Condition.query.get(cid), score) for cid, score in ranked if Condition.query.get(cid)]
