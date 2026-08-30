"""Health check endpoint routes with DB and Redis connectivity indicators."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.cache.redis import check_redis_health
from app.core.config import get_settings
from app.db.session import check_db_health
from app.schemas.health import HealthData, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Service Health Check")
async def health_check(request: Request) -> HealthResponse:
    """Return application health, version, environment, and subsystem status."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    request_id = getattr(request.state, "request_id", "req_unknown")

    # Probe subsystems (with graceful degradation for standalone development)
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()

    health_data = HealthData(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(UTC).isoformat(),
        database="ready" if db_ok else "unreachable",
        redis="ready" if redis_ok else "unreachable",
    )

    return HealthResponse(
        success=True,
        data=health_data,
        error=None,
        request_id=request_id,
    )
