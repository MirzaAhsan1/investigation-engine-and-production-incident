from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET = (
    BASE_DIR
    / "datasets"
    / "production_incidents_v6.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "app"
    / "ml"
    / "models"
)

ARTIFACT_DIR = (
    BASE_DIR
    / "app"
    / "ml"
    / "artifacts"
)


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [

    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "disk_io_wait",

    "api_latency",
    "http_5xx_count",
    "http_4xx_count",
    "request_per_second",

    "error_rate",
    "db_connections",

    "failed_login_attempts",
    "packet_loss",
    "network_latency",

    "restart_count",
    "active_containers",
    "deployment_changed",

    "ssl_certificate_days_left",
]


# ============================================================
# TARGETS
# ============================================================

TARGET_COLUMNS = [

    "incident_category",
    "incident_cause",

]


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("=" * 70)
print("LOADING DATASET")
print("=" * 70)

print(
    f"Dataset: {DATASET}"
)

df = pd.read_csv(DATASET)

print(
    f"Rows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = (
    FEATURE_COLUMNS
    + TARGET_COLUMNS
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(missing_columns)
    )


# ============================================================
# CHECK MISSING VALUES
# ============================================================

print()
print("=" * 70)
print("CHECKING DATA")
print("=" * 70)

missing_values = (
    df[required_columns]
    .isnull()
    .sum()
)

print(
    missing_values[
        missing_values > 0
    ]
)


# ============================================================
# PREPARE FEATURES / TARGETS
# ============================================================

X = df[
    FEATURE_COLUMNS
]

y = df[
    TARGET_COLUMNS
]


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("INCIDENT CATEGORY DISTRIBUTION")
print("=" * 70)

print(
    y["incident_category"]
    .value_counts()
)


print()
print("=" * 70)
print("INCIDENT CAUSE DISTRIBUTION")
print("=" * 70)

print(
    y["incident_cause"]
    .value_counts()
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,

)


print()
print("=" * 70)
print("DATA SPLIT")
print("=" * 70)

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples: {len(X_test)}"
)


# ============================================================
# RANDOM FOREST
# ============================================================

base_model = RandomForestClassifier(

    n_estimators=500,

    max_depth=18,

    min_samples_leaf=2,

    class_weight="balanced",

    random_state=42,

    n_jobs=-1,

)


# ============================================================
# MULTI OUTPUT MODEL
# ============================================================

model = MultiOutputClassifier(

    base_model,

    n_jobs=-1,

)


# ============================================================
# TRAIN
# ============================================================

print()
print("=" * 70)
print("TRAINING MODEL")
print("=" * 70)

model.fit(

    X_train,

    y_train,

)

print(
    "Training completed."
)


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(

    X_test,

)


# ============================================================
# CATEGORY EVALUATION
# ============================================================

category_actual = (
    y_test[
        "incident_category"
    ]
)

category_predicted = (
    predictions[:, 0]
)

category_accuracy = (
    accuracy_score(
        category_actual,
        category_predicted,
    )
)


print()
print("=" * 70)
print("INCIDENT CATEGORY RESULTS")
print("=" * 70)

print(
    f"Accuracy: "
    f"{category_accuracy:.4f}"
)

print()

print(
    classification_report(
        category_actual,
        category_predicted,
        zero_division=0,
    )
)

print(
    "Confusion Matrix:"
)

print(
    confusion_matrix(
        category_actual,
        category_predicted,
    )
)


# ============================================================
# CAUSE EVALUATION
# ============================================================

cause_actual = (
    y_test[
        "incident_cause"
    ]
)

cause_predicted = (
    predictions[:, 1]
)

cause_accuracy = (
    accuracy_score(
        cause_actual,
        cause_predicted,
    )
)


print()
print("=" * 70)
print("INCIDENT CAUSE RESULTS")
print("=" * 70)

print(
    f"Accuracy: "
    f"{cause_accuracy:.4f}"
)

print()

print(
    classification_report(
        cause_actual,
        cause_predicted,
        zero_division=0,
    )
)

print(
    "Confusion Matrix:"
)

print(
    confusion_matrix(
        cause_actual,
        cause_predicted,
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

MODEL_PATH = (
    MODEL_DIR
    / "incident_classifier.pkl"
)

joblib.dump(

    model,

    MODEL_PATH,

)


# ============================================================
# SAVE FEATURE COLUMNS
# ============================================================

FEATURE_PATH = (
    ARTIFACT_DIR
    / "feature_columns.pkl"
)

joblib.dump(

    FEATURE_COLUMNS,

    FEATURE_PATH,

)


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 70)
print("MODEL SAVED SUCCESSFULLY")
print("=" * 70)

print(
    f"Model: {MODEL_PATH}"
)

print(
    f"Features: {FEATURE_PATH}"
)

print()
print(
    "Training pipeline completed."
)