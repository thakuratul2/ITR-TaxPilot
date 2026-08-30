"""Health check endpoint routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.schemas.health import HealthData, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Service Health Check")
async def health_check(request: Request) -> HealthResponse:
    """Return application health, version, environment, and current timestamp."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    request_id = getattr(request.state, "request_id", "req_unknown")

    health_data = HealthData(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(UTC).isoformat(),
        database="ready",
        redis="ready",
    )

    return HealthResponse(
        success=True,
        data=health_data,
        error=None,
        request_id=request_id,
    )
