"""Analysis and Tax Calculation schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaxCalculationSummary(BaseModel):
    """Regime calculation summary."""
    regime: str = Field(..., description="OLD or NEW regime")
    gross_income: float = Field(..., description="Gross taxable income")
    total_deductions: float = Field(..., description="Total eligible deductions")
    taxable_income: float = Field(..., description="Net taxable income after deductions")
    total_tax_liability: float = Field(..., description="Total tax including cess")
    tds_credit: float = Field(..., description="Tax deducted at source credit")
    tax_payable: float = Field(..., description="Net tax payable")
    refund_due: float = Field(..., description="Refund due to taxpayer")


class AnalysisData(BaseModel):
    """Analysis summary and regime comparisons."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    document_id: str = Field(..., description="Associated document ID")
    assessment_year: str = Field(..., description="Assessment Year (e.g. 2026-27)")
    financial_year: str | None = Field(default=None, description="Financial Year (e.g. 2025-26)")
    status: str = Field(..., description="Analysis status")
    recommended_itr: str | None = Field(default=None, description="Recommended ITR form (ITR-1, ITR-2, etc.)")
    explanation: str | None = Field(default=None, description="AI-generated plain English summary")
    calculations: list[TaxCalculationSummary] = Field(default_factory=list, description="Regime calculations")
    created_at: datetime = Field(..., description="Analysis creation timestamp")
