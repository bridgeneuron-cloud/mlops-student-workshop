## Local Jenkins (Docker) for this workshop

### Prerequisites
- Docker installed and running

### Start Jenkins
From this directory:
`mlops-student-workshop/jenkins`
```bash
docker compose -f docker-compose.yml up --build -d
```

Open Jenkins:
- http://localhost:8080

### Create the Pipeline job (recommended setup)
1. Click **New Item**
2. Name it: `mlops-workshop-student`
3. Select **Pipeline**
4. Configure:
   - **Definition**: `Pipeline script from SCM`
   - **SCM**: `Git`
   - **Repository URL**: `https://github.com/bridgeneuron-cloud/mlops-student-workshop.git`
   - **Branch Specifier**: `*/main`
   - **Script Path**: `Jenkinsfile`
   - **Credentials**:
     - Jenkins -> Manage Jenkins -> Credentials -> Add Credentials
     - **Kind**: `Username with password`
     - **Username**: your GitHub username
     - **Password**: your GitHub PAT token
     - Select this credential in the job SCM section
5. Save

Why this is recommended:
- Jenkins always executes the latest committed `Jenkinsfile`.
- Avoids stale pasted scripts (for example old `pip3 install` commands that fail with PEP 668).
- Avoids SSH host key verification failures on fresh Jenkins containers.

### Run the job
- Click **Build Now**

Expected behavior:
- The pipeline runs data generation -> data security cleaning -> training -> tests -> docker build -> deploys to local container named `ml-prod`.
- After deployment, your instructor can verify with:
  - `curl http://localhost:8000/version`
  - `curl http://localhost:8000/health`

### Notes for smoother classroom demo
- If Jenkins asks for initial admin password, follow the logs printed in the terminal where you started compose.
- First run may take longer because Jenkins container needs to download base layers.

### If "Pipeline" is not visible in New Item
- Cause: Jenkins started without Pipeline plugins.
- Fix from `jenkins/` directory:
```bash
docker compose -f docker-compose.yml down -v
docker compose -f docker-compose.yml up --build -d
```
- Then refresh `http://localhost:8080` and create a new item again. You should see **Pipeline**.

### If console still shows old commands
- Symptom: You still see outdated lines (for example `pip3 install -U pip`) even after repo updates.
- Cause: Job is configured as **Pipeline script** with old pasted content.
- Fix: Edit job -> Configure -> set **Definition** to **Pipeline script from SCM** with `Jenkinsfile` path, then Save and Build again.

