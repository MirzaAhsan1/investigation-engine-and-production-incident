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

from app.db.session import SessionLocal
from app.models.investigation import Investigation
from app.models.evidence import Evidence
from app.ml.feature_extractor import FEATURE_COLUMNS, safe_value

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

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
# ROOT CAUSE NORMALIZATION
# ============================================================

def normalize_root_cause(root_cause: str) -> tuple[str, str] | None:
    if not root_cause:
        return None
    rc = root_cause.lower()
    
    # Deterministic keyword mapping to fixed categories/causes taxonomy
    if "cpu" in rc or "processor" in rc:
        return "INFRASTRUCTURE", "HIGH_CPU_USAGE"
    elif "memory" in rc or "leak" in rc or "ram" in rc or "oom" in rc:
        return "INFRASTRUCTURE", "HIGH_MEMORY_USAGE"
    elif "disk io" in rc or "i/o wait" in rc or "io wait" in rc:
        return "INFRASTRUCTURE", "HIGH_DISK_IO_WAIT"
    elif "disk" in rc or "storage" in rc or "space" in rc:
        return "INFRASTRUCTURE", "HIGH_DISK_USAGE"
    elif "connection" in rc or "pool" in rc or "exhaust" in rc:
        return "DATABASE", "DATABASE_CONNECTION_EXHAUSTION"
    elif "database" in rc or "db error" in rc or "sql" in rc or "query" in rc or "timeout" in rc:
        return "DATABASE", "HIGH_DATABASE_ERROR_RATE"
    elif "login" in rc or "brute" in rc or "auth" in rc or "credential" in rc:
        return "SECURITY", "BRUTE_FORCE_LOGIN_ATTEMPTS"
    elif "latency" in rc or "network" in rc or "packet" in rc or "ping" in rc or "slow" in rc:
        return "SECURITY", "HIGH_NETWORK_LATENCY"
    elif "ssl" in rc or "cert" in rc or "certificate" in rc:
        return "SECURITY", "SSL_CERTIFICATE_EXPIRING"
    elif "deploy" in rc or "release" in rc or "rollout" in rc or "version" in rc:
        return "DEPLOYMENT", "RECENT_DEPLOYMENT"
    elif "no incident" in rc or "normal" in rc or "no issue" in rc:
        return "NORMAL", "NO_INCIDENT"
    
    return None

# ============================================================
# LOAD DATASET FROM DATABASE
# ============================================================

print()
print("=" * 70)
print("LOADING DATASET FROM DATABASE")
print("=" * 70)

db = SessionLocal()
try:
    # Query all investigations, order by updated_at desc to find latest first
    investigations = db.query(Investigation).order_by(Investigation.updated_at.desc()).all()
    
    # De-duplicate investigations: only keep the latest one per incident_id
    latest_investigations = {}
    for inv in investigations:
        if inv.incident_id not in latest_investigations:
            latest_investigations[inv.incident_id] = inv
            
    # Fetch evidence associated with these incidents
    evidence_records = db.query(Evidence).filter(
        Evidence.incident_id.in_(list(latest_investigations.keys()))
    ).all()
    
    records = []
    for ev in evidence_records:
        inv = latest_investigations.get(ev.incident_id)
        if not inv or not inv.root_cause:
            continue
            
        normalized = normalize_root_cause(inv.root_cause)
        if normalized is None:
            # Exclude from training rather than guess
            continue
            
        category, cause = normalized
        
        row = {
            "log_count": safe_value(ev.log_count),
            "error_count": safe_value(ev.error_count),
            "warning_count": safe_value(ev.warning_count),
            "error_rate": safe_value(ev.error_rate),
            "database_timeout_count": safe_value(ev.database_timeout_count),
            "cpu_usage": safe_value(ev.cpu_usage),
            "memory_usage": safe_value(ev.memory_usage),
            "disk_usage": safe_value(ev.disk_usage),
            "disk_io_wait": safe_value(ev.disk_io_wait),
            "api_latency": safe_value(ev.api_latency),
            "http_4xx_count": safe_value(ev.http_4xx_count),
            "http_5xx_count": safe_value(ev.http_5xx_count),
            "request_per_second": safe_value(ev.request_per_second),
            "active_containers": safe_value(ev.active_containers),
            "deployment_changed": safe_value(ev.deployment_changed),
            "failed_login_attempts": safe_value(ev.failed_login_attempts),
            "incident_category": category,
            "incident_cause": cause
        }
        records.append(row)
        
    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} training examples from real database traffic.")
    
finally:
    db.close()

# ============================================================
# DATASET INSPECTION — which features actually have real data?
# ============================================================

print()
print("=" * 70)
print("FEATURE COVERAGE (how many rows have REAL data vs missing)")
print("=" * 70)

for column in FEATURE_COLUMNS:

    total = len(df)

    missing_or_sentinel = (
        (df[column] == -1.0) | df[column].isnull()
    ).sum()

    real_values = total - missing_or_sentinel

    print(
        f"{column:30s} "
        f"real={real_values:3d} / {total:3d}   "
        f"({real_values / total * 100:.0f}%)"
    )

# Save full dataset to CSV for manual inspection
DATASET_EXPORT_PATH = ARTIFACT_DIR / "training_dataset_export.csv"
df.to_csv(DATASET_EXPORT_PATH, index=False)
print()
print(f"Full dataset exported to: {DATASET_EXPORT_PATH}")

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