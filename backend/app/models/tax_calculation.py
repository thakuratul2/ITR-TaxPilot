"""TaxCalculation model for storing deterministic calculation breakdown per regime."""

import enum
import uuid

from sqlalchemy import JSON, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TaxRegime(str, enum.Enum):
    """Tax regime identifier."""
    OLD = "OLD"
    NEW = "NEW"


class TaxCalculation(Base, TimestampMixin):
    """Tax calculation result for an analysis under a specific regime."""

    __tablename__ = "tax_calculations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    assessment_year: Mapped[str] = mapped_column(String(10), nullable=False)
    regime: Mapped[TaxRegime] = mapped_column(Enum(TaxRegime), nullable=False)

    gross_income: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    total_deductions: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    taxable_income: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    tax_before_rebate: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    rebate_87a: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    cess: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    total_tax_liability: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    tds_credit: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    tax_payable: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    refund_due: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)

    # Detailed audit trail & slab breakdown JSON
    calculation_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationship
    analysis = relationship("Analysis", back_populates="calculations")
