from app.models.incident import Incident
from app.rules.investigation_rules import (
    SEVERITY_SCORES,
    TYPE_SCORES,
    SOURCE_SCORES,
    SAFE_THRESHOLD,
    MEDIUM_THRESHOLD,
    HIGH_THRESHOLD,
    MAX_SCORE,
)


def evaluate_incident(incident: Incident) -> dict:

    risk_score = 0
    triggered_rules = []

    # -------------------------
    # Severity Score
    # -------------------------

    severity_score = SEVERITY_SCORES.get(
        incident.severity,
        0,
    )

    risk_score += severity_score

    if severity_score:
        triggered_rules.append(
            f"Severity: {incident.severity.value}"
        )

    # -------------------------
    # Incident Type Score
    # -------------------------

    type_score = TYPE_SCORES.get(
        incident.incident_type,
        0,
    )

    risk_score += type_score

    if type_score:
        triggered_rules.append(
            f"Type: {incident.incident_type.value}"
        )

    # -------------------------
    # Source Score
    # -------------------------

    source_score = SOURCE_SCORES.get(
        incident.source,
        0,
    )

    risk_score += source_score

    if source_score:
        triggered_rules.append(
            f"Source: {incident.source.value}"
        )

    # -------------------------
    # Normalize
    # -------------------------

    risk_score = min(
        risk_score,
        MAX_SCORE,
    )

    # -------------------------
    # Rule Result
    # -------------------------

    if risk_score >= HIGH_THRESHOLD:
        rule_result = "CRITICAL"

    elif risk_score >= MEDIUM_THRESHOLD:
        rule_result = "HIGH"

    elif risk_score >= SAFE_THRESHOLD:
        rule_result = "MEDIUM"

    else:
        rule_result = "LOW"

    # -------------------------
    # Confidence
    # -------------------------

    confidence_score = min(
        70 + len(triggered_rules) * 10,
        100,
    )

    return {
        "risk_score": risk_score,
        "rule_result": rule_result,
        "confidence_score": confidence_score,
        "triggered_rules": triggered_rules,
    }