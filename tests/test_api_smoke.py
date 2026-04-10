import os
import sys

import joblib
import pandas as pd

# Ensure imports work when pytest is executed from different working directories.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from src.app import create_app


def test_predict_smoke():
    bundle = joblib.load("artifacts/model.joblib")
    feature_cols = bundle["feature_cols"]

    app = create_app("artifacts")
    client = app.test_client()

    df = pd.read_csv("data/clean.csv")

    # Build a valid payload based on the trained feature schema.
    row0 = df.iloc[0]
    payload = {}
    for c in feature_cols:
        v = row0[c]
        # Flask's JSON encoder doesn't handle numpy scalar types well.
        payload[c] = v.item() if hasattr(v, "item") else v

    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200

    body = resp.get_json()
    assert "model_version" in body
    assert "prediction" in body
    assert "probability" in body

