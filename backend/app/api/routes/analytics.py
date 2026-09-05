"""Analytics and Product Hunt launch tracking endpoints."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.analytics import AnalyticsStatsResponse, GitHubRepoStats, TrackVisitRequest, TrackVisitResponse
from app.schemas.base import APIResponse
from app.services.analytics_service import fetch_github_stars, get_analytics_stats, record_visit

router = APIRouter(prefix="/analytics", tags=["Analytics & Launch Tracking"])


@router.post(
    "/track",
    response_model=APIResponse[TrackVisitResponse],
    summary="Track visitor pageview and traffic source",
)
async def track_page_visit(
    payload: TrackVisitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TrackVisitResponse]:
    """Record anonymous traffic origin, UTM params, and Product Hunt referrals."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    header_referrer = request.headers.get("referer")

    result = await record_visit(
        req=payload,
        db=db,
        client_ip=client_ip,
        user_agent=user_agent,
        header_referrer=header_referrer,
    )
    request_id = getattr(request.state, "request_id", "req_analytics")
    return APIResponse(success=True, data=result, request_id=request_id)


@router.get(
    "/stats",
    response_model=APIResponse[AnalyticsStatsResponse],
    summary="Get aggregated launch analytics, traffic sources, and GitHub stars",
)
async def get_launch_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[AnalyticsStatsResponse]:
    """Retrieve live metrics including Product Hunt referrals and GitHub stargazers."""
    stats = await get_analytics_stats(db=db)
    request_id = getattr(request.state, "request_id", "req_analytics")
    return APIResponse(success=True, data=stats, request_id=request_id)


@router.get(
    "/github-stars",
    response_model=APIResponse[GitHubRepoStats],
    summary="Get live GitHub stars for the repository",
)
async def get_github_stars(
    request: Request,
    force_refresh: bool = Query(default=False, description="Force refresh cache"),
) -> APIResponse[GitHubRepoStats]:
    """Get live star count and fork stats from GitHub for thakuratul2/ITR-TaxPilot."""
    stats = await fetch_github_stars(force_refresh=force_refresh)
    request_id = getattr(request.state, "request_id", "req_analytics")
    return APIResponse(success=True, data=stats, request_id=request_id)
