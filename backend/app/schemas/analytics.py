"""Pydantic schemas for analytics tracking and Product Hunt launch statistics."""

from datetime import datetime
from pydantic import BaseModel, Field


class TrackVisitRequest(BaseModel):
    """Payload sent by client when visiting a page."""

    visitor_id: str | None = Field(default=None, description="Anonymous visitor token stored in localStorage")
    source: str | None = Field(default=None, description="Inferred or specified source, e.g. producthunt, github")
    ref: str | None = Field(default=None, description="URL ref query param (e.g. ?ref=producthunt)")
    utm_source: str | None = Field(default=None, description="UTM Source parameter")
    utm_medium: str | None = Field(default=None, description="UTM Medium parameter")
    utm_campaign: str | None = Field(default=None, description="UTM Campaign parameter")
    referrer: str | None = Field(default=None, description="Document referrer URL")
    path: str = Field(default="/", description="Current page path")


class TrackVisitResponse(BaseModel):
    """Response payload acknowledging tracked event."""

    recorded: bool = True
    source: str
    visitor_id: str | None = None
    message: str = "Visit recorded successfully"


class GitHubRepoStats(BaseModel):
    """Live metrics for repository."""

    repo: str = "thakuratul2/ITR-TaxPilot"
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    cached_at: datetime | None = None


class AnalyticsStatsResponse(BaseModel):
    """Aggregated launch and traffic telemetry."""

    total_visits: int = 0
    unique_visitors: int = 0
    product_hunt_visits: int = 0
    github_visits: int = 0
    direct_visits: int = 0
    other_visits: int = 0
    product_hunt_percentage: float = 0.0
    sources_breakdown: dict[str, int] = Field(default_factory=dict)
    github_stats: GitHubRepoStats
    recent_referrers: list[dict] = Field(default_factory=list)
