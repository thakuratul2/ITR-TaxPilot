"""Analysis model storing extracted and validated taxpayer data."""

import enum
import uuid

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AnalysisStatus(str, enum.Enum):
    """Analysis computation state."""
    IN_PROGRESS = "in_progress"
    EXTRACTED = "extracted"
    CALCULATED = "calculated"
    FAILED = "failed"


class Analysis(Base, TimestampMixin):
    """Analysis entity linking extracted document data to tax calculations."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    assessment_year: Mapped[str] = mapped_column(String(10), nullable=False)
    financial_year: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus),
        default=AnalysisStatus.IN_PROGRESS,
        nullable=False,
    )

    # Extracted JSON data (stored without sensitive plaintext PII like PAN/Aadhaar)
    extracted_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommended_itr: Mapped[str | None] = mapped_column(String(20), nullable=True)
    explanation: Mapped[str | None] = mapped_column(String(5000), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="analyses")
    calculations = relationship("TaxCalculation", back_populates="analysis", cascade="all, delete-orphan")
