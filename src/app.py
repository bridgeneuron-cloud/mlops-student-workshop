import argparse
import json
import os
from typing import Any

import joblib
import pandas as pd
from flask import Flask, jsonify, request


def safe_payload_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    # Data security: never log raw payload values; log only shape/type metadata.
    # (You can expand this to include request_id, user_role, etc.)
    return {
        "num_fields": len(payload.keys()),
        "fields": sorted(list(payload.keys())),
    }


def load_bundle(artifacts_dir: str) -> dict[str, Any]:
    model_path = os.path.join(artifacts_dir, "model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Missing artifact: {model_path}")
    return joblib.load(model_path)


def create_app(artifacts_dir: str) -> Flask:
    bundle = load_bundle(artifacts_dir)
    clf = bundle["model"]
    version = bundle["version"]
    feature_cols = bundle["feature_cols"]

    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/version")
    def version_endpoint():
        return jsonify({"model_version": version})

    @app.post("/predict")
    def predict():
        payload = request.get_json(force=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Payload must be a JSON object"}), 400

        # Validate input keys (protects from accidental schema mismatch)
        missing = [c for c in feature_cols if c not in payload]
        if missing:
            return jsonify({"error": f"Missing feature fields: {missing}"}), 400

        # Build input dataframe in the same feature order
        row = {c: payload[c] for c in feature_cols}
        X = pd.DataFrame([row])

        # Data security: do not persist/log raw payload values
        _ = safe_payload_metadata(payload)

        proba = float(clf.predict_proba(X)[:, 1][0])
        pred = int(proba >= 0.5)

        return jsonify(
            {
                "model_version": version,
                "prediction": pred,
                "probability": proba,
            }
        )

    return app


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", default="artifacts")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    app = create_app(args.artifacts)
    app.run(host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

