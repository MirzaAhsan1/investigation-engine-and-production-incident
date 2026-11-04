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

from app.ml.feature_extractor import FEATURE_COLUMNS

# ============================================================
# BOOTSTRAP TRAINING
#
# Trains the SAME model architecture as train.py, but from the
# synthetic dataset (scripts/generate_dataset.py) instead of
# real database Evidence/Investigation rows.
#
# PURPOSE: give the classifier something non-degenerate to
# stand on while real incidents accumulate. This is NOT a
# substitute for real training — once enough genuine
# Evidence/Investigation rows exist, run train.py instead,
# which will overwrite the model this script produces.
#
# db_connections is intentionally dropped below even though
# the synthetic CSV has it — it isn't one of our 16 real
# FEATURE_COLUMNS yet (deferred), so training on it here would
# create a feature the live model never actually receives.
# ============================================================

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = (
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
# TARGETS
# ============================================================

TARGET_COLUMNS = [
    "incident_category",
    "incident_cause",
]

# ============================================================
# LOAD SYNTHETIC DATASET
# ============================================================

print()
print("=" * 70)
print("LOADING SYNTHETIC BOOTSTRAP DATASET")
print("=" * 70)

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Synthetic dataset not found at {DATASET_PATH}. "
        f"Run scripts/generate_dataset.py first."
    )

df = pd.read_csv(
    DATASET_PATH,
)

print(
    f"Loaded {len(df)} synthetic examples from {DATASET_PATH}"
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
# PREPARE FEATURES / TARGETS
#
# Select ONLY our 16 real FEATURE_COLUMNS — the synthetic CSV
# also has db_connections/packet_loss/network_latency/
# restart_count/ssl_certificate_days_left, which are either
# deferred or out of scope, so they're dropped here.
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
print("TRAINING MODEL (SYNTHETIC BOOTSTRAP)")
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
print("MODEL SAVED SUCCESSFULLY (BOOTSTRAP — SYNTHETIC DATA)")
print("=" * 70)

print(
    f"Model: {MODEL_PATH}"
)

print(
    f"Features: {FEATURE_PATH}"
)

print()
print(
    "IMPORTANT: this model was trained on SYNTHETIC data, not "
    "real incidents. Once real Evidence/Investigation rows "
    "accumulate, run train.py (DB-based) to replace it."
)