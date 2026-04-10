#!/usr/bin/env bash
set -euo pipefail

# Local simulator for the included GitHub Actions workflow.
# This gives students “GitHub-style CI/CD logs” without needing to contact GitHub runners.

ROWS="${ROWS:-5000}"
SEED="${SEED:-42}"

echo "[github-ci] Simulating GitHub Actions stages locally"
echo "[github-ci] Stage: prepare"
python3 scripts/generate_synthetic_data.py --rows "${ROWS}" --seed "${SEED}" --out data/raw.csv

echo "[github-ci] Stage: data_prep"
python3 src/data_prep.py --input data/raw.csv --output data/clean.csv

echo "[github-ci] Stage: train"
rm -rf artifacts/*
python3 src/train.py --train data/clean.csv --out artifacts --seed "${SEED}"

echo "[github-ci] Stage: tests"
pytest -q

echo "[github-ci] Stage: docker build + deploy"
 TAG="mlops-workshop-student:github-$(date +%Y%m%d-%H%M%S)"
docker build -t "${TAG}" .
chmod +x scripts/deploy.sh
./scripts/deploy.sh "${TAG}"

echo "[github-ci] Completed."

