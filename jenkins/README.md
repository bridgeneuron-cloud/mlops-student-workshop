## Local Jenkins (Docker) for this workshop

### Prerequisites
- Docker installed and running

### Start Jenkins
From this directory:
`mlops-workshop/jenkins`
```bash
docker compose -f docker-compose.yml up --build -d
```

Open Jenkins:
- http://localhost:8080

### Create the Pipeline job (quick manual setup)
1. Click **New Item**
 2. Name it: `mlops-workshop-student`
3. Select **Pipeline**
4. Configure:
   - **Definition**: `Pipeline script`
   - Paste the contents of the workshop `Jenkinsfile` (from `../Jenkinsfile`) into the script box
5. Save

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

