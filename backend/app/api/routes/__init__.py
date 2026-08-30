"""API routes aggregator."""

from fastapi import APIRouter

from app.api.routes import analysis, documents, health, jobs

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(documents.router)
api_router.include_router(jobs.router)
api_router.include_router(analysis.router)
