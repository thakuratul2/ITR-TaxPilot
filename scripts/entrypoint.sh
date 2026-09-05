#!/bin/sh
set -e

echo "[+] Starting ITR-TaxPilot Production Entrypoint..."

# Run database migrations
echo "[*] Checking and running database migrations (Alembic)..."
alembic upgrade head || echo "[!] Database migrations failed or skipped (fallback enabled)."

# Start FastAPI application
echo "[*] Launching Uvicorn ASGI production server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips="*"
