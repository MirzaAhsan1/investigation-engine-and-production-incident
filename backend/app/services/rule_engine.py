from app.models.incident import Incident
from app.rules.investigation_rules import (
    SEVERITY_SCORES,
    TYPE_SCORES,
    SOURCE_SCORES,
)


def analyze_incident(incident: Incident) -> dict:

    risk_score = 0
    triggered_rules = []

    # Severity
    severity_score = SEVERITY_SCORES[incident.severity]
    risk_score += severity_score
    triggered_rules.append(f"SEVERITY_{incident.severity.value}")

    # Type
    type_score = TYPE_SCORES[incident.incident_type]
    risk_score += type_score
    triggered_rules.append(f"TYPE_{incident.incident_type.value}")

    # Source
    source_score = SOURCE_SCORES[incident.source]
    risk_score += source_score
    triggered_rules.append(f"SOURCE_{incident.source.value}")

    # Risk score should never exceed 100
    risk_score = min(risk_score, 100)

    # Confidence
    confidence = min(60 + len(triggered_rules) * 10, 100)

    # Category
    predicted_category = incident.incident_type.value

    return {
        "risk_score": risk_score,
        "confidence": confidence,
        "predicted_category": predicted_category,
        "triggered_rules": triggered_rules,
    }