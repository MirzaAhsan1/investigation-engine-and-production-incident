from sqlalchemy.orm import Session

from app.ml.inference import predict

from app.services.evidence_service import (
    aggregate_incident_evidence,
)


def predict_incident(
    db: Session,
    incident_id,
):
    """
    Run ML prediction for an incident.

    Caller only provides incident_id — the incident-level
    aggregated Evidence (combining ALL correlation groups that
    fed into this incident, not just the latest one) is built
    internally via aggregate_incident_evidence().

    Flow:

        incident_id
            ↓
        Aggregated Evidence (all correlation groups combined)
            ↓
        ML Inference
            ↓
        Prediction Result
    """

    if incident_id is None:
        raise ValueError(
            "incident_id is required for ML prediction"
        )

    evidence = aggregate_incident_evidence(
        db=db,
        incident_id=incident_id,
    )

    if evidence is None:
        raise ValueError(
            f"No evidence found for incident {incident_id}"
        )

    return predict(
        incident_id=incident_id,
        evidence=evidence,
    )