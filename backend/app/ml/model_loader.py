from pathlib import Path

import joblib


MODEL_PATH = (
    Path(__file__)
    .parent
    / "models"
    / "incident_classifier.pkl"
)


def load_model():

    return joblib.load(
        MODEL_PATH,
    )