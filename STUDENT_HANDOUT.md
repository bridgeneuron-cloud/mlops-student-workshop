## Student Handout (Hands-on MLOps with Local CI/CD)

### Goal
Build and deploy an ML model end-to-end:
data generation -> data security cleaning -> train -> real-time API -> CI/CD -> production deploy.

### 0) Setup (host)
```bash
cd "mlops-workshop-student"
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 1) Generate synthetic data
```bash
python3 scripts/generate_synthetic_data.py --rows 5000 --seed 42 --out data/raw.csv
```
Data security note:
- `data/raw.csv` contains PII columns: `email`, `phone`, `customer_id`.

### 2) Data cleaning + data security
```bash
python3 src/data_prep.py --input data/raw.csv --output data/clean.csv
```
Expected outcome:
- `src/data_prep.py` drops PII columns before training.

### 3) Train model + create artifacts
```bash
rm -rf artifacts/*
python3 src/train.py --train data/clean.csv --out artifacts --seed 42
```
You should see:
- `artifacts/model.joblib`
- `artifacts/metrics.json`
- `artifacts/metadata.json`

### 4) Deploy to local “production” container
```bash
./scripts/pipeline_local_deploy.sh
```
Verify:
```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/version
```

### 5) Prediction (real-time demo)
```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":42,"country":"US","device_type":"mobile","transaction_amount":250.5,"hour_of_day":13,"num_prev_txns":3,"is_international":0}'
```

### 6) CI/CD practice (GitHub copy simulation)
Run the GitHub-style pipeline locally:
```bash
chmod +x scripts/github_pipeline_sim.sh
./scripts/github_pipeline_sim.sh
```
Then re-check:
```bash
curl -s http://localhost:8000/version
```
The `model_version` should change after redeploy.

### 7) Jenkins (if instructor starts local Jenkins)

**Full setup (start Jenkins, job config, troubleshooting):** follow `jenkins/README.md` in this repo.

**Create the Pipeline job:** **Pipeline script from SCM** → **Git** → Repository URL `https://github.com/bridgeneuron-cloud/mlops-student-workshop.git` → Branch `*/main` → Script Path `Jenkinsfile` → add **Credentials** (Jenkins: **Username with password** = GitHub username + personal access token).

**Expected stages (full pipeline):** Setup Python + Dependencies → Generate synthetic data → Data prep → Train → Unit tests → Docker preflight → Build Docker image → Deploy to local production.

**If Docker steps fail inside Jenkins:** set job parameter / environment **`SKIP_DOCKER=true`** so the run **stops after tests** (ML path still validated). On your host, deploy with `./scripts/pipeline_local_deploy.sh` (or `docker build` + `./scripts/deploy.sh <tag>` as in `jenkins/README.md`).

**After a successful deploy:** `curl -s http://localhost:8000/health` and `curl -s http://localhost:8000/version`.

