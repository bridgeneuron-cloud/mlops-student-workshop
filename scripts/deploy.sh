#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${1:-}"
if [[ -z "${IMAGE_TAG}" ]]; then
  echo "Usage: $0 <image_tag> (example: mlops-workshop-student:local-20260330-120000)"
  exit 1
fi

CONTAINER_NAME="ml-prod"
PORT="8000"

echo "[deploy] Deploying image: ${IMAGE_TAG}"

if docker ps -a --format '{{.Names}}' | rg -q "^${CONTAINER_NAME}$"; then
  echo "[deploy] Stopping existing container: ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null
fi

docker run -d --name "${CONTAINER_NAME}" -p "${PORT}:8000" "${IMAGE_TAG}" >/dev/null

echo "[deploy] Waiting for /health..."
for i in {1..30}; do
  if curl -s "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    echo "[deploy] Container is healthy."
    break
  fi
  sleep 1
done

echo "[deploy] Model version:"
curl -s "http://localhost:${PORT}/version" || true

mkdir -p artifacts
echo "${IMAGE_TAG}" > artifacts/last_deployed_tag.txt
echo "$(date -Iseconds) ${IMAGE_TAG}" >> artifacts/deploy_history.txt

