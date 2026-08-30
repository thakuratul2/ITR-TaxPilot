"""Generic API response envelope and error schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIError(BaseModel):
    """Standardized API error structure."""

    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error explanation")
    details: dict | None = Field(default=None, description="Optional extra details")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response envelope for all endpoints."""

    success: bool = Field(..., description="True if operation succeeded, False otherwise")
    data: T | None = Field(default=None, description="Response payload")
    error: APIError | None = Field(default=None, description="Error detail if success is False")
    request_id: str = Field(..., description="Correlation request ID")
