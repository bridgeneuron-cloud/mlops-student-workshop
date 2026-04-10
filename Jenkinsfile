pipeline {
  agent any

  environment {
    // The workshop repo is mounted into the Jenkins container at /workspace.
    WORKDIR = "/workspace"
    PATH = "/var/jenkins_home/.local/bin:/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    BUILD_TAG = "mlops-workshop-student:jenkins-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        // Default Jenkins SCM checkout is handled by the job configuration.
        echo "Checked out by Jenkins SCM."
      }
    }

    stage('Setup Python + Dependencies') {
      steps {
        sh '''
          cd "${WORKDIR}"
          python3 --version
          python3 -m pip install -U pip --break-system-packages
          python3 -m pip install -r requirements.txt --break-system-packages
        '''
      }
    }

    stage('Docker preflight') {
      steps {
        sh '''
          cd "${WORKDIR}"
          if ! command -v docker >/dev/null 2>&1; then
            echo "[preflight] docker CLI not found in Jenkins container PATH=${PATH}"
            echo "[preflight] Rebuild Jenkins container from jenkins/ directory:"
            echo "  docker compose -p mlops-student-workshop -f docker-compose.yml down"
            echo "  docker compose -p mlops-student-workshop -f docker-compose.yml build --no-cache"
            echo "  docker compose -p mlops-student-workshop -f docker-compose.yml up -d --force-recreate"
            exit 127
          fi
          docker --version
        '''
      }
    }

    stage('Generate synthetic data') {
      steps {
        sh '''
          cd "${WORKDIR}"
          python3 scripts/generate_synthetic_data.py --rows 5000 --seed 42 --out data/raw.csv
        '''
      }
    }

    stage('Data prep (security + cleaning)') {
      steps {
        sh '''
          cd "${WORKDIR}"
          python3 src/data_prep.py --input data/raw.csv --output data/clean.csv
        '''
      }
    }

    stage('Train') {
      steps {
        sh '''
          cd "${WORKDIR}"
          rm -rf artifacts/*
          python3 src/train.py --train data/clean.csv --out artifacts --seed 42
        '''
      }
    }

    stage('Unit tests') {
      steps {
        sh '''
          cd "${WORKDIR}"
          python3 -m pytest -q
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh '''
          cd "${WORKDIR}"
          docker build -t "${BUILD_TAG}" .
        '''
      }
    }

    stage('Deploy to local production') {
      steps {
        sh '''
          cd "${WORKDIR}"
          chmod +x scripts/deploy.sh
          ./scripts/deploy.sh "${BUILD_TAG}"
        '''
      }
    }
  }
}

