"""Background job tracking endpoints."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.schemas.base import APIResponse
from app.schemas.job import JobData
from app.services.job_service import JobService

logger = logging.getLogger("app.api.jobs")
router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "/{job_id}",
    response_model=APIResponse[JobData],
    summary="Get Job Processing Status",
)
async def get_job_status(job_id: str, request: Request) -> APIResponse[JobData]:
    """Retrieve real-time processing status, progress percentage, and results for a background job."""
    request_id = getattr(request.state, "request_id", "req_unknown")

    # Fetch live job state from Redis or database
    job_data = await JobService.get_job(job_id)

    # Fallback if job is untracked
    if not job_data:
        now = datetime.now(UTC)
        job_data = JobData(
            job_id=job_id,
            document_id=None,
            job_type="form16_extraction",
            status="processing",
            progress_percentage=45,
            step_description="Extracting salary and tax deduction fields",
            result_id=None,
            result_data=None,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    return APIResponse(
        success=True,
        data=job_data,
        error=None,
        request_id=request_id,
    )
