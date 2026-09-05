"""Job status tracking schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class JobData(BaseModel):
    """Job status and progress tracking payload."""
    job_id: str = Field(..., description="Unique job ID")
    document_id: str | None = Field(default=None, description="Associated document ID")
    job_type: str = Field(default="form16_extraction", description="Type of background job")
    status: str = Field(..., description="Job status (queued, extracting, calculating, processing, completed, failed)")
    progress_percentage: int = Field(default=0, description="Completion percentage 0-100")
    step_description: str | None = Field(default=None, description="Current processing step")
    result_id: str | None = Field(default=None, description="ID of generated analysis or calculation result")
    result_data: dict[str, Any] | None = Field(default=None, description="Output payload if processing succeeded")
    error_message: str | None = Field(default=None, description="Error explanation if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
