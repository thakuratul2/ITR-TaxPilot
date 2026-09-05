"""Asynchronous job execution and lifecycle management service."""

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.cache.cache_service import CacheService
from app.calculator.models import (
    AdvanceTaxScheduleInput,
    ChapterVIAInput,
    SalaryInput,
    TaxpayerProfileInput,
)
from app.comparison.comparison_engine import ComparisonEngine
from app.db.session import AsyncSessionLocal
from app.documents.form16_parser import parse_form16_text_deterministically
from app.models.document import Document, DocumentStatus
from app.models.job import Job, JobStatus, JobType
from app.schemas.job import JobData
from app.services.document_service import DocumentService

logger = logging.getLogger("app.services.job_service")


class JobService:
    """Manages asynchronous background job lifecycle, Redis caching, and pipeline orchestration."""

    @classmethod
    async def create_job(
        cls,
        document_id: str | None = None,
        job_type: JobType = JobType.FORM16_EXTRACTION,
    ) -> JobData:
        """Create and initialize a new background job in database and Redis cache."""
        job_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        job_data = JobData(
            job_id=job_id,
            document_id=document_id,
            job_type=job_type.value if isinstance(job_type, JobType) else str(job_type),
            status=JobStatus.QUEUED.value,
            progress_percentage=0,
            step_description="Job queued for processing",
            result_id=None,
            result_data=None,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

        # Cache initial state
        await CacheService.cache_job_state(job_id, job_data.model_dump())

        # Persist to database if available
        try:
            async with AsyncSessionLocal() as session:
                db_job = Job(
                    id=job_id,
                    document_id=document_id,
                    job_type=job_type,
                    status=JobStatus.QUEUED,
                    progress_percentage=0,
                    step_description="Job queued for processing",
                )
                session.add(db_job)
                await session.commit()
        except Exception as exc:
            logger.warning("Failed to persist initial job %s to database (using cache fallback): %s", job_id, exc)

        return job_data

    @classmethod
    async def update_job(
        cls,
        job_id: str,
        status: JobStatus,
        progress_percentage: int,
        step_description: str | None = None,
        result_id: str | None = None,
        result_data: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> JobData | None:
        """Update job lifecycle state across cache and database."""
        now = datetime.now(UTC)
        current = await cls.get_job(job_id)

        document_id = current.document_id if current else None
        job_type = current.job_type if current else "form16_extraction"
        created_at = current.created_at if current else now

        job_data = JobData(
            job_id=job_id,
            document_id=document_id,
            job_type=job_type,
            status=status.value if isinstance(status, JobStatus) else str(status),
            progress_percentage=progress_percentage,
            step_description=step_description,
            result_id=result_id,
            result_data=result_data,
            error_message=error_message,
            created_at=created_at,
            updated_at=now,
        )

        # Update Redis Cache
        await CacheService.cache_job_state(job_id, job_data.model_dump())

        # Update Database
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(Job).where(Job.id == job_id)
                res = await session.execute(stmt)
                db_job = res.scalars().first()
                if db_job:
                    db_job.status = status
                    db_job.progress_percentage = progress_percentage
                    db_job.step_description = step_description
                    if result_id:
                        db_job.result_id = result_id
                    if error_message:
                        db_job.error_message = error_message
                    await session.commit()
        except Exception as exc:
            logger.warning("Failed to update job %s in database: %s", job_id, exc)

        return job_data

    @classmethod
    async def get_job(cls, job_id: str) -> JobData | None:
        """Retrieve current job state from cache, falling back to database."""
        # 1. Check Redis Cache
        cached = await CacheService.get_cached_job_state(job_id)
        if cached:
            try:
                return JobData(**cached)
            except Exception:
                pass

        # 2. Check Database
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(Job).where(Job.id == job_id)
                res = await session.execute(stmt)
                db_job = res.scalars().first()
                if db_job:
                    job_data = JobData(
                        job_id=db_job.id,
                        document_id=db_job.document_id,
                        job_type=db_job.job_type.value if hasattr(db_job.job_type, "value") else str(db_job.job_type),
                        status=db_job.status.value if hasattr(db_job.status, "value") else str(db_job.status),
                        progress_percentage=db_job.progress_percentage,
                        step_description=db_job.step_description,
                        result_id=db_job.result_id,
                        result_data=db_job.result_data,
                        error_message=db_job.error_message,
                        created_at=db_job.created_at,
                        updated_at=db_job.updated_at,
                    )
                    # Re-hydrate cache
                    await CacheService.cache_job_state(job_id, job_data.model_dump())
                    return job_data
        except Exception as exc:
            logger.warning("Database query failed for job %s: %s", job_id, exc)

        return None

    @classmethod
    def start_background_processing(
        cls,
        job_id: str,
        filename: str,
        content_type: str,
        file_bytes: bytes,
    ) -> asyncio.Task:
        """Launch non-blocking background task worker to process document."""
        return asyncio.create_task(
            cls._execute_document_pipeline(
                job_id=job_id,
                filename=filename,
                content_type=content_type,
                file_bytes=file_bytes,
            )
        )

    @classmethod
    async def _execute_document_pipeline(
        cls,
        job_id: str,
        filename: str,
        content_type: str,
        file_bytes: bytes,
    ) -> None:
        """Worker pipeline executing document validation, extraction, and tax computation."""
        try:
            # 1. State: EXTRACTING (20%)
            await cls.update_job(
                job_id=job_id,
                status=JobStatus.EXTRACTING,
                progress_percentage=20,
                step_description="Validating PDF security and extracting text...",
            )

            # Ingest and normalize document
            normalized_doc, _ = DocumentService.process_form16_upload(
                filename=filename,
                content_type=content_type,
                file_bytes=file_bytes,
            )

            # 2. State: EXTRACTING (40%)
            await cls.update_job(
                job_id=job_id,
                status=JobStatus.EXTRACTING,
                progress_percentage=40,
                step_description="Extracting salary, allowances, and TDS deductions...",
            )

            # Deterministic parameter extraction
            extracted = parse_form16_text_deterministically(normalized_doc.full_text)

            # Persist document record to DB
            try:
                import hashlib
                file_sha256 = hashlib.sha256(file_bytes).hexdigest()
                async with AsyncSessionLocal() as session:
                    doc_record = Document(
                        id=normalized_doc.document_id,
                        filename=normalized_doc.filename,
                        original_filename=filename,
                        content_type=content_type,
                        file_size_bytes=len(file_bytes),
                        storage_path=f"ephemeral://{normalized_doc.document_id}",
                        status=DocumentStatus.PARSED,
                        sha256_hash=file_sha256,
                    )
                    session.add(doc_record)
                    await session.commit()
            except Exception as exc:
                logger.warning("Could not persist document model in background job: %s", exc)

            # 3. State: CALCULATING (60%)
            await cls.update_job(
                job_id=job_id,
                status=JobStatus.CALCULATING,
                progress_percentage=60,
                step_description="Computing tax under Old and New Regimes...",
            )

            detected_ay = normalized_doc.classification.detected_ay or extracted.get("assessment_year") or "2026-27"
            if not detected_ay.startswith("20"):
                detected_ay = "2026-27"
            gross_salary = float(extracted.get("gross_salary", 0.0) or 0.0)
            tds_deducted = float(extracted.get("total_tds_deducted", 0.0) or 0.0)
            sec_80c = float(extracted.get("section_80c", 0.0) or 0.0)
            sec_80d = float(extracted.get("section_80d", 0.0) or 0.0)

            # Construct profile input
            profile = TaxpayerProfileInput(
                assessment_year=detected_ay,
                salary=SalaryInput(
                    gross_salary_sec_17_1=gross_salary,
                    basic_salary=gross_salary,
                ),
                chapter_vi_a=ChapterVIAInput(
                    section_80c=sec_80c,
                    section_80d_self_family=sec_80d,
                ),
                advance_tax=AdvanceTaxScheduleInput(
                    total_tds_tcs_deducted=tds_deducted,
                ),
            )

            # 4. State: CALCULATING (80%)
            await cls.update_job(
                job_id=job_id,
                status=JobStatus.CALCULATING,
                progress_percentage=80,
                step_description="Comparing regimes and determining ITR form...",
            )

            comparison_result = ComparisonEngine.compare_comprehensive(profile)

            # 5. Finalize Result Payload & Cache (100%)
            result_payload = {
                "document_id": normalized_doc.document_id,
                "job_id": job_id,
                "status": "completed",
                "extracted": extracted,
                "classification": {
                    "detected_ay": detected_ay,
                    "has_part_a": normalized_doc.classification.has_part_a,
                    "has_part_b": normalized_doc.classification.has_part_b,
                    "confidence": normalized_doc.classification.confidence,
                },
                "comparison": comparison_result.model_dump() if hasattr(comparison_result, "model_dump") else comparison_result,
            }

            # Cache final result
            await CacheService.cache_result(normalized_doc.document_id, result_payload)

            # Complete Job
            await cls.update_job(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress_percentage=100,
                step_description="Document processing and tax computation complete",
                result_id=normalized_doc.document_id,
                result_data=result_payload,
            )
            logger.info("Job %s completed successfully for document %s", job_id, normalized_doc.document_id)

        except Exception as exc:
            logger.error("Job %s failed: %s", job_id, str(exc))
            await cls.update_job(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress_percentage=0,
                step_description="Processing failed",
                error_message=f"Processing failed: {str(exc)}",
            )
