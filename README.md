## 2-hour MLOps + DevOps + Data Security Workshop

### What you will do (real hands-on loop)
1. Generate a **synthetic fraud dataset** (includes PII to demonstrate data security).
2. Perform **data cleaning + data security steps** (drop PII, validate schema).
3. Train an ML model and produce a **versioned model artifact**.
4. Deploy the model behind a **real-time HTTP API** (`/predict`).
5. Run CI/CD in two ways:
   - **Jenkins pipeline** (local Jenkins in Docker)
   - **GitHub Actions workflow** (local “GitHub copy” via the included simulator or `act`)
6. Deploy into a local “production” container and verify with `curl`.

### Repo contents
- `scripts/generate_synthetic_data.py` - creates `data/raw.csv`
- `src/data_prep.py` - creates `data/clean.csv` (drops PII, validates)
- `src/train.py` - trains and writes model + metrics to `artifacts/`
- `src/app.py` - Flask real-time inference API
- `Dockerfile` - production image (build includes trained artifacts)
- `scripts/deploy.sh` - deploys a new image tag to local production container
- `Jenkinsfile` - Jenkins pipeline for the same ML lifecycle
- `.github/workflows/mlops-ci.yml` - GitHub Actions workflow (same stages)

### Student HTML files (open in a browser)
- `STUDENT_HANDOUT.html` (lab steps)

Instructor-only rehearsal script is not included in this student repo.

### Fast start (host machine)
1. Create venv
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   pip install -r requirements.txt
   ```
2. Generate + clean + train
   ```bash
   python3 scripts/generate_synthetic_data.py --rows 5000 --out data/raw.csv
   python3 src/data_prep.py --input data/raw.csv --output data/clean.csv
   python3 src/train.py --train data/clean.csv --out artifacts
   ```
3. Start “production” API locally
   ```bash
   python3 src/app.py --artifacts artifacts --port 8000
   ```
4. Test prediction
   ```bash
   curl -s -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"age":42,"country":"US","device_type":"mobile","transaction_amount":250.5,"hour_of_day":13,"num_prev_txns":3,"is_international":0}'
   ```

### Local “production” via Docker (recommended for demos)
Use these steps so students can see CI/CD deployment clearly:
1. Build and deploy:
   ```bash
   ./scripts/pipeline_local_deploy.sh
   ```
2. Verify:
   ```bash
   curl -s http://localhost:8000/health
   curl -s http://localhost:8000/version
   ```

Rollback demo:
```bash
chmod +x scripts/rollback.sh
./scripts/rollback.sh
curl -s http://localhost:8000/version
```

### Jenkins (local) - what to show in class
This workshop includes:
- `jenkins/Dockerfile.jenkins` (Jenkins + Python + build tools + **static Docker CLI** for reliable `docker build` against the mounted socket)
- `Jenkinsfile` with the same ML lifecycle as the lab, optional **`SKIP_DOCKER=true`** to pass CI when only the ML stages are needed (deploy on the host instead)

**Setup, HTTPS + PAT, branch `main`, compose container name, and troubleshooting** are documented in `jenkins/README.md`. Student-facing steps are also summarized in `STUDENT_HANDOUT.md` section 7.

### Data Security points (talk track)
Use the following “checkpoint” moments during the demo:
1. **PII minimization**: `src/data_prep.py` drops PII columns before training.
2. **No secret leakage**: no API keys are stored in code; pipelines would use secrets.
3. **Safe logging**: API does not log raw request payloads.
4. **Versioned artifacts**: model and metadata include a `version` for traceability.

### Time plan
This student repo contains the lab + CI/CD automation you will run.


