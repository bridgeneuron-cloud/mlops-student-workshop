#!/usr/bin/env bash
set -euo pipefail

HIST="artifacts/deploy_history.txt"
if [[ ! -f "${HIST}" ]]; then
  echo "[rollback] Missing history file: ${HIST}"
  exit 1
fi

PREV_TAG="$(awk 'NF{t=$2; tags[NR]=t} END{ if (length(tags) && NR>=2) print tags[NR-1]; else exit 1 }' "${HIST}")"

if [[ -z "${PREV_TAG}" ]]; then
  echo "[rollback] No previous tag found."
  exit 1
fi

chmod +x scripts/deploy.sh
./scripts/deploy.sh "${PREV_TAG}"

echo "[rollback] Rolled back to: ${PREV_TAG}"

