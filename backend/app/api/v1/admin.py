"""Admin panel endpoints for system telemetry, user management, and AI provider status."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import check_db_health, get_db
from app.models.analysis import Analysis
from app.models.document import Document
from app.models.job import Job
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
settings = get_settings()


@router.get(
    "/stats",
    summary="Get overall system statistics and health metrics",
)
async def get_admin_stats(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Return aggregated telemetry for the admin dashboard."""
    # Count metrics
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    job_count = (await db.execute(select(func.count(Job.id)))).scalar() or 0
    analysis_count = (await db.execute(select(func.count(Analysis.id)))).scalar() or 0

    db_ok = await check_db_health()

    return {
        "metrics": {
            "total_users": user_count,
            "total_documents": doc_count,
            "total_jobs": job_count,
            "total_analyses": analysis_count,
        },
        "system": {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "database_status": "Healthy" if db_ok else "Fallback / In-Memory",
            "active_ai_provider": settings.DEFAULT_AI_PROVIDER.upper(),
            "active_ai_model": settings.OPENAI_MODEL if "openai" in settings.DEFAULT_AI_PROVIDER.lower() else settings.GEMINI_MODEL,
        },
    }


@router.get(
    "/users",
    summary="List registered users",
)
async def list_admin_users(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return recent registered taxpayers."""
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(limit))
    users = result.scalars().all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name or "Anonymous Taxpayer",
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get(
    "/documents",
    summary="List uploaded Form 16 documents and parsing state",
)
async def list_admin_documents(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return recently uploaded documents."""
    result = await db.execute(select(Document).order_by(Document.created_at.desc()).limit(limit))
    documents = result.scalars().all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_size_kb": round(d.file_size_bytes / 1024, 2),
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            "sha256_hash": d.sha256_hash[:16] + "..." if d.sha256_hash else None,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in documents
    ]


@router.get(
    "/ai-providers",
    summary="Get status of AI extraction models",
)
async def get_ai_providers_status() -> list[dict[str, Any]]:
    """Return status and configuration of all AI engines."""
    return [
        {
            "provider": "OpenAI",
            "model": settings.OPENAI_MODEL,
            "is_active": "openai" in settings.DEFAULT_AI_PROVIDER.lower(),
            "configured": bool(settings.OPENAI_API_KEY),
            "description": "Primary Extraction & JSON schema structured output engine",
            "latency": "~850ms",
        },
        {
            "provider": "Google Gemini",
            "model": settings.GEMINI_MODEL,
            "is_active": "gemini" in settings.DEFAULT_AI_PROVIDER.lower(),
            "configured": bool(settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY),
            "description": "Multimodal fallback & high-speed table extraction",
            "latency": "~920ms",
        },
        {
            "provider": "Anthropic Claude",
            "model": settings.CLAUDE_MODEL,
            "is_active": "claude" in settings.DEFAULT_AI_PROVIDER.lower(),
            "configured": bool(settings.ANTHROPIC_API_KEY),
            "description": "Dual-model cross-verification & semantic reconciliation",
            "latency": "~1450ms",
        },
    ]
