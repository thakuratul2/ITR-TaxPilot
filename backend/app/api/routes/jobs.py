"""Background job tracking endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.schemas.base import APIResponse
from app.schemas.job import JobData

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "/{job_id}",
    response_model=APIResponse[JobData],
    summary="Get Job Processing Status",
)
async def get_job_status(job_id: str, request: Request) -> APIResponse[JobData]:
    """Retrieve current processing status and progress for a specific background job."""
    request_id = getattr(request.state, "request_id", "req_unknown")

    # Stub status handler for job retrieval
    now = datetime.now(UTC)
    job_data = JobData(
        job_id=job_id,
        job_type="form16_extraction",
        status="processing",
        progress_percentage=45,
        step_description="Extracting salary and tax deduction fields",
        result_id=None,
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
