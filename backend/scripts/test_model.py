import pandas as pd

from app.ml.model_loader import load_model


model = load_model()

sample = pd.DataFrame([
    {
        "cpu_usage":35,
        "memory_usage":40,
        "disk_usage":55,
        "api_latency":6500,
        "error_rate":10,
        "db_connections":480,
        "active_containers":8,
    }
])

prediction = model.predict(sample)

probability = model.predict_proba(sample)

print(prediction[0])

print(max(probability[0])*100)