import argparse
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Config:
    rows: int
    seed: int


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True, help="Path to output CSV (e.g., data/raw.csv)")
    args = ap.parse_args()

    cfg = Config(rows=args.rows, seed=args.seed)
    rng = np.random.default_rng(cfg.seed)

    # Synthetic “fraud” label is correlated with amount, age, country risk, and device risk.
    age = rng.integers(18, 86, size=cfg.rows)
    transaction_amount = rng.gamma(shape=2.0, scale=120.0, size=cfg.rows)  # positive skew
    country = rng.choice(["US", "CA", "GB", "IN", "NG", "BR", "DE", "FR"], size=cfg.rows, p=[0.25, 0.08, 0.08, 0.12, 0.08, 0.12, 0.17, 0.10])
    device_type = rng.choice(["mobile", "desktop", "tablet"], size=cfg.rows, p=[0.62, 0.30, 0.08])
    hour_of_day = rng.integers(0, 24, size=cfg.rows)
    num_prev_txns = rng.poisson(lam=3.0, size=cfg.rows).clip(0, 50)
    is_international = rng.binomial(1, p=0.18, size=cfg.rows)

    country_risk_map = {
        "US": 0.0,
        "CA": 0.1,
        "GB": 0.05,
        "DE": 0.05,
        "FR": 0.05,
        "IN": 0.25,
        "NG": 0.35,
        "BR": 0.22,
    }
    device_risk_map = {"mobile": 0.18, "desktop": 0.02, "tablet": 0.10}

    country_risk = np.vectorize(country_risk_map.get)(country)
    device_risk = np.vectorize(device_risk_map.get)(device_type)

    # Some time-of-day effect: fraud slightly more likely late night.
    late_night = ((hour_of_day >= 0) & (hour_of_day <= 5)).astype(float)

    # Score -> probability -> label
    # Note: This is synthetic; the workshop goal is MLOps lifecycle, not “perfect fraud modelling”.
    score = (
        -4.0
        + 0.004 * transaction_amount
        + (-0.01) * (age - 40)  # younger users have slightly higher risk
        + 1.8 * country_risk
        + 2.0 * device_risk
        + 0.9 * is_international
        + 0.6 * late_night
        + 0.07 * num_prev_txns
    )
    fraud_prob = sigmoid(score)
    fraud = rng.binomial(1, fraud_prob, size=cfg.rows)

    # Add PII columns (to demonstrate data security: we will drop them before training)
    customer_id = rng.integers(100000, 999999, size=cfg.rows)
    email = [f"user{cid}@example.com" for cid in customer_id]
    phone = [f"+1-555-{rng.integers(100,999)}-{rng.integers(1000,9999)}" for _ in range(cfg.rows)]

    # Other non-PII identifiers
    transaction_id = [f"tx_{i:06d}" for i in range(cfg.rows)]

    df = pd.DataFrame(
        {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "email": email,
            "phone": phone,
            "age": age,
            "country": country,
            "device_type": device_type,
            "transaction_amount": transaction_amount.round(2),
            "hour_of_day": hour_of_day,
            "num_prev_txns": num_prev_txns,
            "is_international": is_international,
            "fraud": fraud,
        }
    )

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote synthetic dataset: {args.out} rows={len(df)} fraud_rate={df['fraud'].mean():.4f}")


if __name__ == "__main__":
    main()

