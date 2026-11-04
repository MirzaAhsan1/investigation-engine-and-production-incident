import pandas as pd

from app.ml.model_loader import load_model
from app.ml.feature_extractor import FEATURE_COLUMNS

model = load_model()

sample = pd.DataFrame([
    {
        "log_count": 150,
        "error_count": 15,
        "warning_count": 35,
        "error_rate": 10.0,
        "database_timeout_count": 5,
        "cpu_usage": 35,
        "memory_usage": 40,
        "disk_usage": 55,
    }
])

# Ensure correct order of columns
sample = sample[FEATURE_COLUMNS]

prediction = model.predict(sample)

probability = model.predict_proba(sample)

print(prediction[0])

print(max(probability[0])*100)