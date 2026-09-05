"""Operational metrics endpoint for telemetry inspection."""

from typing import Any
from fastapi import APIRouter, Request

from app.core.telemetry import metrics_collector
from app.schemas.base import APIResponse

router = APIRouter(prefix="/metrics", tags=["Observability"])


@router.get(
    "",
    summary="Get System and API Performance Metrics",
    response_model=APIResponse[dict[str, Any]],
)
async def get_system_metrics(request: Request) -> APIResponse[dict[str, Any]]:
    """Retrieve operational metrics including latency, error rates, and request throughput."""
    request_id = getattr(request.state, "request_id", "req_unknown")
    summary = metrics_collector.get_metrics_summary()

    return APIResponse(
        success=True,
        data=summary,
        error=None,
        request_id=request_id,
    )
