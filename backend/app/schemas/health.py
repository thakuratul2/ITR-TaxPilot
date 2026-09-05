"""Health check schemas."""


from pydantic import BaseModel, Field

from app.schemas.base import APIResponse


class HealthData(BaseModel):
    """Health check payload."""

    status: str = Field(default="healthy", description="Application status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Running environment")
    timestamp: str = Field(..., description="UTC timestamp of the check")
    database: str | None = Field(default="not_checked", description="Database health status")
    redis: str | None = Field(default="not_checked", description="Redis health status")
    storage: str | None = Field(default="ready", description="Ephemeral storage status")
    ai_providers: dict[str, str] | None = Field(default=None, description="Configured AI provider statuses")


class HealthResponse(APIResponse[HealthData]):
    """Standard health check response."""
    pass
