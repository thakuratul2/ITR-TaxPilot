"""Job status tracking schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class JobData(BaseModel):
    """Job status and progress tracking payload."""
    job_id: str = Field(..., description="Unique job ID")
    document_id: str | None = Field(default=None, description="Associated document ID")
    job_type: str = Field(..., description="Type of background job")
    status: str = Field(..., description="Job status (pending, processing, completed, failed)")
    progress_percentage: int = Field(default=0, description="Completion percentage 0-100")
    step_description: str | None = Field(default=None, description="Current processing step")
    result_id: str | None = Field(default=None, description="ID of generated analysis or calculation result")
    error_message: str | None = Field(default=None, description="Error explanation if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
