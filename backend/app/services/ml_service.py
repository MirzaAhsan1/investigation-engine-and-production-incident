from app.ml.inference import predict


def predict_incident(
    incident,
    evidence,
):
    """
    Run ML prediction for an incident.

    Flow:

        Incident
            +
        Evidence
            ↓
        ML Inference
            ↓
        Prediction Result
    """

    if incident is None:
        raise ValueError(
            "Incident is required for ML prediction"
        )

    if evidence is None:
        raise ValueError(
            "Evidence is required for ML prediction"
        )

    return predict(
        incident=incident,
        evidence=evidence,
    )