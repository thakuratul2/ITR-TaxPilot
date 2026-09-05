"""Tax report schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    """Metadata for generated tax report."""
    report_id: str = Field(..., description="Unique report identifier")
    analysis_id: str = Field(..., description="Associated analysis or calculation ID")
    document_id: str | None = Field(default=None, description="Source Form 16 document ID")
    assessment_year: str = Field(..., description="Assessment Year (e.g. 2026-27)")
    financial_year: str = Field(..., description="Financial Year (e.g. 2025-26)")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    recommended_regime: str = Field(..., description="Recommended Tax Regime (OLD / NEW)")
    tax_savings: float = Field(default=0.0, description="Annual tax savings amount")
    recommended_itr: str = Field(..., description="Recommended ITR Form")
    report_download_url: str = Field(..., description="URL endpoint to download PDF report")
    summary: dict[str, Any] = Field(default_factory=dict, description="Key calculation figures")
