import pandas as pd

from app.ml.feature_extractor import (
    FEATURE_COLUMNS,
    extract_features,
)

from app.ml.model_loader import load_model


MODEL_VERSION = "v2.0"

model = None

try:
    model = load_model()

except FileNotFoundError:
    model = None


def _model_not_available_result(
    incident,
):
    return {
        "incident_id": (
            str(incident.id)
            if incident is not None
            else None
        ),

        "predicted_category": (
            "MODEL_NOT_TRAINED"
        ),

        "predicted_cause": (
            "MODEL_NOT_TRAINED"
        ),

        "category_confidence": 0.0,

        "cause_confidence": 0.0,

        "confidence": 0.0,

        "model_version": MODEL_VERSION,
    }


def predict(
    incident,
    evidence,
):
    """
    Predict incident category and probable cause.

    Flow:

        Incident
            +
        Evidence
            ↓
        Feature Extraction
            ↓
        ML Model
            ↓
        Category + Cause + Confidence
    """

    # ======================================================
    # 1. Validate Inputs
    # ======================================================

    if incident is None:
        raise ValueError(
            "Incident is required for ML prediction"
        )

    if evidence is None:
        raise ValueError(
            "Evidence is required for ML prediction"
        )

    # ======================================================
    # 2. Model Availability
    # ======================================================

    if model is None:
        return _model_not_available_result(
            incident=incident,
        )

    # ======================================================
    # 3. Extract Features
    # ======================================================

    features = extract_features(
        evidence=evidence,
    )

    # ======================================================
    # 4. Build DataFrame
    # ======================================================

    feature_data = pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS,
    )

    # ======================================================
    # 5. Run Prediction
    # ======================================================

    prediction = model.predict(
        feature_data,
    )[0]

    predicted_category = prediction[0]

    predicted_cause = prediction[1]

    # ======================================================
    # 6. Calculate Confidence
    # ======================================================

    category_probability = 0.0
    cause_probability = 0.0

    estimators = getattr(
        model,
        "estimators_",
        None,
    )

    if (
        estimators is not None
        and len(estimators) >= 2
    ):

        category_model = estimators[0]
        cause_model = estimators[1]

        if hasattr(
            category_model,
            "predict_proba",
        ):

            category_probability = float(
                max(
                    category_model.predict_proba(
                        feature_data
                    )[0]
                )
            )

        if hasattr(
            cause_model,
            "predict_proba",
        ):

            cause_probability = float(
                max(
                    cause_model.predict_proba(
                        feature_data
                    )[0]
                )
            )

    # ======================================================
    # 7. Overall Confidence
    # ======================================================

    confidence = round(
        (
            category_probability
            + cause_probability
        )
        / 2
        * 100,
        2,
    )

    # ======================================================
    # 8. Return Prediction
    # ======================================================

    return {
        "incident_id": str(
            incident.id
        ),

        "predicted_category": (
            predicted_category
        ),

        "predicted_cause": (
            predicted_cause
        ),

        "category_confidence": round(
            category_probability * 100,
            2,
        ),

        "cause_confidence": round(
            cause_probability * 100,
            2,
        ),

        "confidence": confidence,

        "model_version": MODEL_VERSION,
    }