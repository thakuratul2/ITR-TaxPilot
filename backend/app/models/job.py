"""Job processing state model."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class JobStatus(str, enum.Enum):
    """Job processing lifecycle state."""
    QUEUED = "queued"
    EXTRACTING = "extracting"
    CALCULATING = "calculating"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, enum.Enum):
    """Job operation type."""
    FORM16_EXTRACTION = "form16_extraction"
    TAX_COMPUTATION = "tax_computation"
    REPORT_GENERATION = "report_generation"


class Job(Base, TimestampMixin):
    """Asynchronous background job tracking entity."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
    )
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType),
        default=JobType.FORM16_EXTRACTION,
        nullable=False,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.QUEUED,
        nullable=False,
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    step_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    result_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    document = relationship("Document", back_populates="jobs")
