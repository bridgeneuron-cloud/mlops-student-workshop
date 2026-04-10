pipeline {
  agent any

  environment {
    // The workshop repo is mounted into the Jenkins container at /workspace.
    WORKDIR = "/workspace"
    VENV_DIR = "/workspace/.venv"
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
          python3 -m venv "${VENV_DIR}"
          . "${VENV_DIR}/bin/activate"
          pip install -U pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Generate synthetic data') {
      steps {
        sh '''
          cd "${WORKDIR}"
          . "${VENV_DIR}/bin/activate"
          python3 scripts/generate_synthetic_data.py --rows 5000 --seed 42 --out data/raw.csv
        '''
      }
    }

    stage('Data prep (security + cleaning)') {
      steps {
        sh '''
          cd "${WORKDIR}"
          . "${VENV_DIR}/bin/activate"
          python3 src/data_prep.py --input data/raw.csv --output data/clean.csv
        '''
      }
    }

    stage('Train') {
      steps {
        sh '''
          cd "${WORKDIR}"
          . "${VENV_DIR}/bin/activate"
          rm -rf artifacts/*
          python3 src/train.py --train data/clean.csv --out artifacts --seed 42
        '''
      }
    }

    stage('Unit tests') {
      steps {
        sh '''
          cd "${WORKDIR}"
          . "${VENV_DIR}/bin/activate"
          pytest -q
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

