# Development Guide

## 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Git

## 2. Local Environment Setup

### 1. Clone & Environment Configuration
```bash
cp .env.example .env
```

### 2. Python Virtual Environment
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Running with Docker Compose
```bash
docker compose up --build -d
```

### 4. Running Backend Locally
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Health Check
Open `http://localhost:8000/health` or `http://localhost:8000/api/v1/health` in your browser or run:
```bash
curl http://localhost:8000/health
```

## 3. Running Tests & Quality Checks
```bash
# Run pytest test suite
pytest -v

# Run linting
ruff check .

# Run code formatting check
black --check .
```
