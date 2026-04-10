import argparse
import os

import pandas as pd


PII_COLS = {"customer_id", "email", "phone"}


def drop_pii(df: pd.DataFrame) -> pd.DataFrame:
    # Data security: remove PII fields prior to training.
    cols_to_drop = [c for c in PII_COLS if c in df.columns]
    return df.drop(columns=cols_to_drop) if cols_to_drop else df


def validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.input)

    # Required ML schema
    required = ["fraud", "age", "country", "device_type", "transaction_amount", "hour_of_day", "num_prev_txns", "is_international"]
    validate_columns(df, required)

    # Basic security: drop PII
    df = drop_pii(df)

    # Fill missing numeric and categorical values.
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c != "fraud"]

    for c in numeric_cols:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())

    for c in categorical_cols:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].mode(dropna=True).iloc[0])

    if df["fraud"].isna().any():
        raise ValueError("Target column 'fraud' has nulls after cleaning")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Clean dataset written: {args.output} shape={df.shape}")


if __name__ == "__main__":
    main()

