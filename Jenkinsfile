pipeline {
  agent any

  environment {
    // The workshop repo is mounted into the Jenkins container at /workspace.
    WORKDIR = "/workspace"
    PATH = "/var/jenkins_home/.local/bin:/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    BUILD_TAG = "mlops-workshop-student:jenkins-${env.BUILD_NUMBER}"
    // Set SKIP_DOCKER=true in the Jenkins job (e.g. Parameters / Environment) to pass the
    // pipeline without image build/deploy when Docker-in-Jenkins is not available.
  }

  stages {
    stage('Checkout') {
      steps {
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

    stage('Docker preflight') {
      when {
        expression { return env.SKIP_DOCKER != 'true' }
      }
      steps {
        sh '''
          cd "${WORKDIR}"
          if ! command -v docker >/dev/null 2>&1; then
            echo "[preflight] docker CLI not found. Options:"
            echo "  1) Rebuild Jenkins image from jenkins/Dockerfile.jenkins (static docker CLI is installed there)."
            echo "  2) Set job env SKIP_DOCKER=true to finish pipeline after tests (no image build/deploy)."
            exit 127
          fi
          docker --version
        '''
      }
    }

    stage('Build Docker image') {
      when {
        expression { return env.SKIP_DOCKER != 'true' }
      }
      steps {
        sh '''
          cd "${WORKDIR}"
          docker build -t "${BUILD_TAG}" .
        '''
      }
    }

    stage('Deploy to local production') {
      when {
        expression { return env.SKIP_DOCKER != 'true' }
      }
      steps {
        sh '''
          cd "${WORKDIR}"
          chmod +x scripts/deploy.sh
          ./scripts/deploy.sh "${BUILD_TAG}"
        '''
      }
    }

    stage('Docker skipped (manual deploy)') {
      when {
        expression { return env.SKIP_DOCKER == 'true' }
      }
      steps {
        echo 'SKIP_DOCKER=true: ML stages completed. On the host run: ./scripts/pipeline_local_deploy.sh or docker build + ./scripts/deploy.sh <tag>'
      }
    }
  }
}
