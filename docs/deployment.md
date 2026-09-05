# ITR-TaxPilot — Production Deployment Guide

This guide documents the architecture, prerequisites, environment configuration, container deployment steps, and verification procedures for **ITR-TaxPilot** in a production environment.

---

## 1. System Architecture

```text
[Client / Browser]
       │
   (HTTPS :443 / HTTP :80)
       ▼
   [Nginx Reverse Proxy]
       │
   (Internal Network)
       ▼
   [FastAPI Application (Uvicorn - 4 Workers)]
    ├── PostgreSQL (Port 5432) ── Data Persistence & Users
    ├── Redis (Port 6379) ──────── Rate Limiting & Job Queue
    └── AI Extraction Layer ───── Gemini / Claude / OpenAI
```

---

## 2. Infrastructure Requirements

- **Minimum Specs:** 2 vCPU, 4GB RAM, 20GB SSD Storage
- **Recommended Specs:** 4 vCPU, 8GB RAM, 50GB SSD Storage
- **Operating System:** Ubuntu 22.04 LTS / Debian 12 / RHEL 9
- **Docker Version:** 24.0+
- **Docker Compose:** v2.20+

---

## 3. Environment Configuration (`.env.production`)

Create a `.env.production` file on the deployment host:

```bash
# Application Mode
APP_NAME=ITR-TaxPilot
APP_ENV=production
DEBUG=False
PORT=8000
HOST=0.0.0.0

# Cryptographic Keys (Must be 32+ random hex characters)
SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_SECRET_KEY=generate_with_openssl_rand_hex_32

# Database & Redis Credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_super_secure_postgres_password
POSTGRES_DB=itrtaxpilot
DATABASE_URL=postgresql+psycopg://postgres:your_super_secure_postgres_password@postgres:5432/itrtaxpilot
REDIS_URL=redis://redis:6379/0

# AI Provider Keys
GEMINI_API_KEY=your_production_gemini_api_key
OPENAI_API_KEY=your_production_openai_api_key
DEFAULT_AI_PROVIDER=gemini

# Security & Limits
ALLOWED_ORIGINS=https://app.itrtaxpilot.com,https://itrtaxpilot.com
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_SIZE_MB=10
DOCUMENT_RETENTION_MINUTES=30
```

---

## 4. Deployment Steps

```bash
# 1. Clone repository
git clone https://github.com/thakuratul2/ITR-TaxPilot.git /opt/itrtaxpilot
cd /opt/itrtaxpilot

# 2. Configure environment
cp .env.example .env.production
nano .env.production

# 3. Build & start containers
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 4. Verify running services
docker compose -f docker-compose.prod.yml ps
```

---

## 5. Post-Deployment Smoke Verification

Run the automated smoke test suite:

```bash
python scripts/smoke_test.py --url http://localhost
```

---

## 6. Backup & Restore Procedures

### Database Backup
```bash
docker exec -t itr_taxpilot_postgres pg_dump -U postgres itrtaxpilot | gzip > /backups/itrtaxpilot_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Database Restore
```bash
gunzip < /backups/itrtaxpilot_backup.sql.gz | docker exec -i itr_taxpilot_postgres psql -U postgres -d itrtaxpilot
```
