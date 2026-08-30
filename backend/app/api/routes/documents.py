"""Document ingestion and upload routes."""

import uuid

from fastapi import APIRouter, File, Request, UploadFile, status

from app.schemas.base import APIResponse
from app.schemas.document import DocumentUploadPayload
from app.services.document_service import DocumentService

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
    """Accept, validate, and execute document pipeline on Form 16 PDF file."""
    request_id = getattr(request.state, "request_id", "req_unknown")

    # Read uploaded bytes
    file_bytes = await file.read()

    # Execute document validation, security check, and extraction
    normalized_doc, _ = DocumentService.process_form16_upload(
        filename=file.filename or "form16.pdf",
        content_type=file.content_type or "application/pdf",
        file_bytes=file_bytes,
    )

    job_id = str(uuid.uuid4())

    message = (
        f"Form 16 '{normalized_doc.filename}' ({normalized_doc.total_pages} pages) "
        f"processed. Detected AY: {normalized_doc.classification.detected_ay or 'Pending AI Extraction'}."
    )

    payload = DocumentUploadPayload(
        document_id=normalized_doc.document_id,
        job_id=job_id,
        status="pending",
        message=message,
    )

    return APIResponse(
        success=True,
        data=payload,
        error=None,
        request_id=request_id,
    )
