import argparse
import json
import os
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True, help="Path to cleaned training CSV")
    ap.add_argument("--out", required=True, help="Output artifacts directory")
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.train)
    if "fraud" not in df.columns:
        raise ValueError("Expected target column 'fraud'")

    target_col = "fraud"
    X = df.drop(columns=[target_col])
    y = df[target_col].astype(int)

    feature_cols = X.columns.tolist()
    numeric_cols = X.select_dtypes(include="number").columns.tolist()
    categorical_cols = [c for c in feature_cols if c not in numeric_cols]

    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[("impute", SimpleImputer(strategy="median"))]), numeric_cols),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ]
    )

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    clf = Pipeline(steps=[("pre", pre), ("model", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )

    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:, 1]
    auc = float(roc_auc_score(y_test, proba))

    version = f"v{int(time.time())}"
    os.makedirs(args.out, exist_ok=True)

    bundle = {
        "model": clf,
        "version": version,
        "target_col": target_col,
        "feature_cols": feature_cols,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "metrics": {"roc_auc": auc, "test_size": args.test_size, "seed": args.seed},
    }

    artifact_path = os.path.join(args.out, "model.joblib")
    joblib.dump(bundle, artifact_path)

    metrics_path = os.path.join(args.out, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({"version": version, **bundle["metrics"]}, f, indent=2)

    meta_path = os.path.join(args.out, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(
            {
                "version": version,
                "feature_cols": feature_cols,
                "numeric_cols": numeric_cols,
                "categorical_cols": categorical_cols,
                "created_unix": int(time.time()),
                # workshop-only: label definition info
                "label_definition": "Synthetic fraud indicator (for workshop demo).",
            },
            f,
            indent=2,
        )

    print(f"Trained model version={version} roc_auc={auc:.4f}")
    print(f"Saved artifacts to: {args.out}")


if __name__ == "__main__":
    main()

