pipeline {
    agent any

    environment {
        PYTHON     = 'python3'
        VENV_DIR   = 'venv'
        APP_MODULE = 'src.app'
    }

    stages {

        // ── Stage 1: Checkout ─────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                echo "✅ Branch: ${env.GIT_BRANCH ?: 'local'} | Commit: ${env.GIT_COMMIT?.take(7) ?: 'N/A'}"
            }
        }

        // ── Stage 2: Setup Environment ────────────────────────────────────
        stage('Setup Environment') {
            steps {
                echo '🐍 Setting up Python virtual environment...'
                sh '''
                    ${PYTHON} -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip --quiet
                    pip install -r requirements.txt --quiet
                    echo "✅ Dependencies installed successfully"
                    pip list | grep -E "customtkinter|pandas|pytest|flake8|coverage"
                '''
            }
        }

        // ── Stage 3: Code Quality (flake8) ───────────────────────────────
        stage('Code Quality') {
            steps {
                echo '🔍 Running flake8 code quality check...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 src/ tests/ \
                        --max-line-length=100 \
                        --exclude=__pycache__,.git,${VENV_DIR} \
                        --per-file-ignores="src/app.py:E402" \
                        --statistics \
                        --format="%(path)s:%(row)d:%(col)d: %(code)s %(text)s"
                    echo "✅ Code quality check passed — no violations found"
                '''
            }
        }

        // ── Stage 4: Run Tests + Coverage ─────────────────────────────────
        stage('Tests') {
            steps {
                echo '🧪 Running unit tests with coverage...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest tests/ \
                        -v \
                        --tb=short \
                        --cov=src \
                        --cov-config=.coveragerc \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov \
                        --cov-fail-under=80
                    echo "✅ All tests passed!"
                '''
            }
            post {
                always {
                    // Publish coverage report if plugin installed
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        // ── Stage 5: Headless Run ─────────────────────────────────────────
        stage('Headless Validation') {
            steps {
                echo '⚡ Running headless validation (no GUI)...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    mkdir -p test_data
                    # create sample files for headless test
                    touch test_data/photo.jpg test_data/script.py test_data/doc.pdf
                    touch test_data/music.mp3 test_data/archive.zip test_data/unknown.xyz

                    python3 -c "
import sys
sys.path.insert(0, '.')
from src.organizer import organize_files, get_folder_stats

stats = get_folder_stats('test_data')
print('📊 Stats before:', stats)

summary = organize_files('test_data', dry_run=True)
print(f'✅ Dry run: {summary[\"moved\"]} files simulated | {summary[\"errors\"]} errors')
assert summary['errors'] == 0, 'Headless validation failed: errors detected'
print('✅ Headless validation passed!')
"
                '''
            }
        }

        // ── Stage 6: Archive Artifacts ────────────────────────────────────
        stage('Archive Artifacts') {
            steps {
                echo '📦 Archiving logs and reports...'
                sh '''
                    mkdir -p logs
                    echo "Build: ${BUILD_NUMBER}" > logs/build_info.txt
                    echo "Date:  $(date)"          >> logs/build_info.txt
                    echo "Job:   ${JOB_NAME}"      >> logs/build_info.txt
                    cat logs/build_info.txt
                '''
                archiveArtifacts artifacts: 'logs/**,coverage.xml,htmlcov/**', allowEmptyArchive: true
                echo '✅ Artifacts archived successfully!'
            }
        }
    }

    // ── Post Actions ──────────────────────────────────────────────────────────
    post {
        success {
            echo '''
╔════════════════════════════════════════╗
║   ✅  PIPELINE PASSED SUCCESSFULLY     ║
╚════════════════════════════════════════╝
            '''
        }
        failure {
            echo '''
╔════════════════════════════════════════╗
║   ❌  PIPELINE FAILED                  ║
╚════════════════════════════════════════╝
            '''
        }
        always {
            echo "🏁 Pipeline finished — Build #${BUILD_NUMBER}"
            cleanWs()
        }
    }
}
