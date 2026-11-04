from app.models.evidence import Evidence
from app.ml.feature_extractor import (
    extract_features,
    FEATURE_COLUMNS,
)
from app.ml.model_loader import load_model

import pandas as pd


def create_test_evidence():
    """
    Create realistic database incident evidence.
    """

    evidence = Evidence(
        log_count=150,
        error_count=15,
        warning_count=35,
        error_rate=10.0,
        database_timeout_count=5,
        cpu_usage=45.0,
        memory_usage=62.0,
        disk_usage=55.0,
    )

    return evidence


def main():

    print("=" * 70)
    print("INCIDENT MODEL INFERENCE TEST")
    print("=" * 70)

    # =========================================================
    # 1. Load model
    # =========================================================

    model = load_model()

    print()
    print("Model loaded successfully.")

    # =========================================================
    # 2. Create test evidence
    # =========================================================

    evidence = create_test_evidence()

    # =========================================================
    # 3. Extract features
    # =========================================================

    features = extract_features(
        evidence,
    )

    print()
    print("Extracted features:")
    print(features)

    # =========================================================
    # 4. Create DataFrame
    #
    # IMPORTANT:
    # Model was trained with feature names.
    # Therefore inference must also use feature names.
    # =========================================================

    feature_df = pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS,
    )

    print()
    print("Feature DataFrame:")
    print(feature_df)

    # =========================================================
    # 5. Prediction
    # =========================================================

    prediction = model.predict(
        feature_df,
    )[0]

    predicted_category = prediction[0]

    predicted_cause = prediction[1]

    # =========================================================
    # 6. Category probabilities
    # =========================================================

    category_probabilities = (
        model.estimators_[0]
        .predict_proba(
            feature_df,
        )[0]
    )

    # =========================================================
    # 7. Cause probabilities
    # =========================================================

    cause_probabilities = (
        model.estimators_[1]
        .predict_proba(
            feature_df,
        )[0]
    )

    # =========================================================
    # 8. Confidence
    # =========================================================

    category_confidence = (
        max(category_probabilities) * 100
    )

    cause_confidence = (
        max(cause_probabilities) * 100
    )

    overall_confidence = (
        category_confidence
        + cause_confidence
    ) / 2

    # =========================================================
    # 9. Results
    # =========================================================

    print()
    print("=" * 70)
    print("PREDICTION RESULT")
    print("=" * 70)

    print()

    print(
        f"Predicted Category: "
        f"{predicted_category}"
    )

    print(
        f"Predicted Cause: "
        f"{predicted_cause}"
    )

    print(
        f"Category Confidence: "
        f"{category_confidence:.2f}%"
    )

    print(
        f"Cause Confidence: "
        f"{cause_confidence:.2f}%"
    )

    print(
        f"Overall Confidence: "
        f"{overall_confidence:.2f}%"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()