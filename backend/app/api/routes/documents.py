"""Document ingestion and upload routes."""

import uuid

from fastapi import APIRouter, File, Request, UploadFile, status

from app.core.config import get_settings
from app.core.exceptions import FileSizeExceededError, InvalidFileFormatError
from app.core.security import sanitize_filename
from app.schemas.base import APIResponse
from app.schemas.document import DocumentUploadPayload

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/form16",
    response_model=APIResponse[DocumentUploadPayload],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Form 16 PDF",
)
async def upload_form16(
    request: Request,
    file: UploadFile = File(..., description="Form 16 PDF file"),
) -> APIResponse[DocumentUploadPayload]:
    """Accept and validate a Form 16 PDF file, then initiate background extraction."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    request_id = getattr(request.state, "request_id", "req_unknown")

    # Content-type validation
    if file.content_type not in settings.allowed_mimes:
        raise InvalidFileFormatError(file.content_type or "unknown", settings.allowed_mimes)

    # Read content to verify size
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise FileSizeExceededError(file_size_mb, settings.MAX_UPLOAD_SIZE_MB)

    sanitized_name = sanitize_filename(file.filename or "form16.pdf")
    doc_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    payload = DocumentUploadPayload(
        document_id=doc_id,
        job_id=job_id,
        status="pending",
        message=f"Form 16 '{sanitized_name}' accepted and queued for processing",
    )

    return APIResponse(
        success=True,
        data=payload,
        error=None,
        request_id=request_id,
    )
