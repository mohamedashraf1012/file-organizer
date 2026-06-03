# 🗂 File Organizer — CI/CD Pipeline Project

> A Python desktop application that automatically organizes files into categorized folders,
> wired into a full Jenkins CI/CD pipeline — built as part of the CI/CD course at ITI.

---

## 🖥 GUI Preview

<!-- Add your GUI screenshot here -->
![File Organizer GUI](image.png)

---

## ✨ Features

- 🖥 **Modern Dark GUI** built with CustomTkinter
- 📁 Organizes files into: `Images`, `Videos`, `Audio`, `Documents`, `Code`, `Archives`, `Others`
- 🔍 **Folder Preview** — shows category breakdown before organizing
- ⚡ **Dry Run mode** — simulate without moving any files
- 📝 Structured logging to `logs/organizer.log`
- 🧪 **32 unit tests** with pytest + coverage reporting (94% coverage)

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| CustomTkinter | Modern dark-themed GUI |
| pytest + pytest-cov | Unit testing & coverage |
| flake8 | Code quality linting |
| Jenkins | CI/CD pipeline automation |
| Docker | Jenkins runtime environment |
| Git / GitHub | Version control & SCM trigger |

---

## 🔧 Jenkins Pipeline — 6 Stages

```
Stage 1 → Checkout            Pull source code from GitHub
Stage 2 → Setup Environment   Install dependencies into venv
Stage 3 → Code Quality        flake8 linting (zero violations)
Stage 4 → Tests               pytest + coverage report (≥80%)
Stage 5 → Headless Validation Validate core logic without GUI
Stage 6 → Archive Artifacts   Save logs & coverage reports
```

---

## 📁 Project Structure

```
file-organizer/
├── src/
│   ├── __init__.py
│   ├── organizer.py          # Core business logic (pure functions)
│   ├── app.py                # CustomTkinter GUI
│   └── headless_check.py     # Headless validation script for Jenkins
├── tests/
│   ├── __init__.py
│   └── test_organizer.py     # 32 unit tests
├── logs/                     # Auto-generated logs
├── .coveragerc               # Coverage config (excludes GUI)
├── Jenkinsfile               # Pipeline definition
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/mohamedashraf1012/file-organizer.git
cd file-organizer

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/app.py

# Run tests locally
pytest tests/ -v --cov=src --cov-config=.coveragerc --cov-report=term-missing
```

---

## ⚙️ Jenkins Setup

1. Build custom Jenkins image with Python:
```dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv
USER jenkins
```

2. Run the container:
```bash
docker build -t jenkins-python .
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins-python \
  jenkins-python
```

3. Create a **Pipeline** job in Jenkins
4. Set SCM → Git → this repo URL
5. Set Script Path → `Jenkinsfile`
6. Click **Build Now**

---

## 📊 Test Results

```
32 tests — all passing ✅
src/organizer.py → 94% coverage
flake8 → zero violations ✅
```

---

## 👤 Author

**Mohamed Ashraf** — Data Engineering Track @ ITI

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/mohamedashraf1012)