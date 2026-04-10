#!/usr/bin/env bash
set -euo pipefail

# End-to-end local demo:
# synthetic data -> data cleaning/security -> train -> build image -> deploy "production"

ROWS="${ROWS:-5000}"
SEED="${SEED:-42}"

echo "[pipeline] Generating synthetic dataset..."
python3 scripts/generate_synthetic_data.py --rows "${ROWS}" --seed "${SEED}" --out data/raw.csv

echo "[pipeline] Cleaning + data security..."
python3 src/data_prep.py --input data/raw.csv --output data/clean.csv

echo "[pipeline] Training model + writing artifacts..."
rm -rf artifacts/*
python3 src/train.py --train data/clean.csv --out artifacts --seed "${SEED}"

echo "[pipeline] Building Docker image..."
  TAG="mlops-workshop-student:local-$(date +%Y%m%d-%H%M%S)"
docker build -t "${TAG}" .

echo "[pipeline] Deploying to local production container..."
chmod +x scripts/deploy.sh
./scripts/deploy.sh "${TAG}"

echo "[pipeline] Done."

