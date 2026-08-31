"""API routes aggregator."""

from fastapi import APIRouter

from app.api.routes import analysis, documents, health, jobs
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.calculator import router as calculator_router
from app.api.v1.comparison import router as comparison_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(calculator_router)
api_router.include_router(comparison_router)
api_router.include_router(documents.router)
api_router.include_router(jobs.router)
api_router.include_router(analysis.router)
