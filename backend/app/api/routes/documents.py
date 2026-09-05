"""Document ingestion and upload routes."""

from typing import Any

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.documents.form16_parser import parse_form16_text_deterministically
from app.models.document import Document, DocumentStatus
from app.schemas.base import APIResponse
from app.services.document_service import DocumentService
from app.services.job_service import JobService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/form16",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Form 16 PDF and extract tax parameters",
)
async def upload_form16(
    request: Request,
    file: UploadFile = File(..., description="Form 16 PDF file"),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[dict[str, Any]]:
    """Accept, validate, extract, and persist real Form 16 PDF data."""
    request_id = getattr(request.state, "request_id", "req_unknown")

    # Read uploaded bytes
    file_bytes = await file.read()

    # Execute document validation, security check, and text extraction
    normalized_doc, _ = DocumentService.process_form16_upload(
        filename=file.filename or "form16.pdf",
        content_type=file.content_type or "application/pdf",
        file_bytes=file_bytes,
    )

    # Deterministic parameter extraction
    extracted = parse_form16_text_deterministically(normalized_doc.full_text)

    # If AI provider is configured, run AI extraction
    try:
        from app.ai.providers.factory import get_ai_provider
        from app.core.config import get_settings
        settings = get_settings()
        if settings.OPENAI_API_KEY and extracted.get("gross_salary", 0) == 0:
            ai_provider = get_ai_provider("openai")
            ai_data = await ai_provider.extract_form16(normalized_doc)
            if ai_data.gross_salary > 0:
                extracted["gross_salary"] = ai_data.gross_salary
                extracted["total_tds_deducted"] = ai_data.total_tds_deducted
                if ai_data.deductions_chapter_vi_a:
                    extracted["deductions_chapter_vi_a"] = [
                        {"section": d.section, "amount": d.amount}
                        for d in ai_data.deductions_chapter_vi_a
                    ]
                    extracted["total_deductions_chapter_vi_a"] = sum(d["amount"] for d in extracted["deductions_chapter_vi_a"])
    except Exception:
        pass

    # Persist document record in PostgreSQL DB for Admin telemetry
    try:
        import hashlib
        file_sha256 = hashlib.sha256(file_bytes).hexdigest()
        doc_record = Document(
            id=normalized_doc.document_id,
            filename=normalized_doc.filename,
            original_filename=file.filename or "form16.pdf",
            content_type=file.content_type or "application/pdf",
            file_size_bytes=len(file_bytes),
            storage_path=f"ephemeral://{normalized_doc.document_id}",
            status=DocumentStatus.PARSED,
            sha256_hash=file_sha256,
        )
        db.add(doc_record)
        await db.commit()
    except Exception:
        await db.rollback()

    job = await JobService.create_job(document_id=normalized_doc.document_id)
    job_id = job.job_id

    detected_ay = normalized_doc.classification.detected_ay or extracted.get("assessment_year") or "2026-27"
    payload = {
        "document_id": normalized_doc.document_id,
        "job_id": job_id,
        "status": "pending",
        "message": f"Form 16 '{normalized_doc.filename}' processed. Detected AY: {detected_ay}.",
        "extracted": extracted,
        "classification": {
            "detected_ay": detected_ay,
            "has_part_a": normalized_doc.classification.has_part_a,
            "has_part_b": normalized_doc.classification.has_part_b,
            "confidence": normalized_doc.classification.confidence,
        },
    }

    # Update job to completed with result data and cache
    from app.models.job import JobStatus
    await JobService.update_job(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        progress_percentage=100,
        step_description="Form 16 extracted and processed successfully",
        result_id=normalized_doc.document_id,
        result_data=payload,
    )

    return APIResponse(
        success=True,
        data=payload,
        error=None,
        request_id=request_id,
    )
