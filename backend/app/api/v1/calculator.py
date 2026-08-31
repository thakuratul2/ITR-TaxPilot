"""FastAPI routes for the Deterministic Tax Calculation Engine."""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.calculator.models import (
    RegimeComparisonResult,
    RegimeComputation,
    SalaryInput,
    TaxpayerProfileInput,
)
from app.calculator.salary_engine import SalaryEngine
from app.calculator.tax_engine import TaxEngine
from app.tax.rules.base import TaxRegime

router = APIRouter(prefix="/calculator", tags=["Tax Calculator"])


class QuickCompareRequest(BaseModel):
    """Lightweight salary and deduction input for instant comparison."""
    gross_salary: float = Field(..., ge=0.0, description="Annual gross salary")
    total_deductions_80c: float = Field(default=0.0, ge=0.0, description="Section 80C deductions")
    health_insurance_80d: float = Field(default=0.0, ge=0.0, description="Section 80D health insurance")
    housing_loan_interest_sop: float = Field(default=0.0, ge=0.0, description="Self-occupied home loan interest")
    nps_80ccd_1b: float = Field(default=0.0, ge=0.0, description="Additional NPS Tier-1 contribution")
    assessment_year: str = Field(default="2026-27", description="Assessment Year (2026-27 or 2025-26)")


@router.post(
    "/calculate",
    response_model=RegimeComparisonResult,
    status_code=status.HTTP_200_OK,
    summary="Compute comprehensive dual-regime tax comparison",
)
async def calculate_tax(profile: TaxpayerProfileInput) -> RegimeComparisonResult:
    """
    Execute deterministic tax calculation across both Old and New Tax Regimes,
    returning winning regime recommendation, exact savings, and itemized breakdown.
    """
    return TaxEngine.calculate_all(profile)


@router.post(
    "/regime/{regime}",
    response_model=RegimeComputation,
    status_code=status.HTTP_200_OK,
    summary="Compute tax for a single specific regime",
)
async def calculate_single_regime(
    regime: str,
    profile: TaxpayerProfileInput,
) -> RegimeComputation:
    """
    Compute full tax breakdown for either 'OLD' or 'NEW' regime.
    """
    regime_enum = TaxRegime.OLD if regime.upper() == "OLD" else TaxRegime.NEW
    return TaxEngine.compute_regime(profile, regime_enum)


@router.post(
    "/salary/breakdown",
    status_code=status.HTTP_200_OK,
    summary="Compute salary components & HRA exemption",
)
async def compute_salary_breakdown(
    salary: SalaryInput,
    regime: str = "NEW",
    assessment_year: str = "2026-27",
) -> dict:
    """
    Compute Section 17 salary, Section 10(13A) HRA exemption, and Section 16 deductions.
    """
    regime_enum = TaxRegime.OLD if regime.upper() == "OLD" else TaxRegime.NEW
    return SalaryEngine.compute_salary_income(salary, regime_enum, assessment_year)


@router.post(
    "/quick-compare",
    response_model=RegimeComparisonResult,
    status_code=status.HTTP_200_OK,
    summary="Quick comparison from gross salary and basic deductions",
)
async def quick_compare(payload: QuickCompareRequest) -> RegimeComparisonResult:
    """
    Convenient quick comparison endpoint for instant UI sliders and calculators.
    """
    profile = TaxpayerProfileInput(
        assessment_year=payload.assessment_year,
        salary=SalaryInput(gross_salary_sec_17_1=payload.gross_salary),
        house_property={"housing_loan_interest_sop": payload.housing_loan_interest_sop},
        chapter_vi_a={
            "section_80c": payload.total_deductions_80c,
            "section_80d_self": payload.health_insurance_80d,
            "section_80ccd_1b": payload.nps_80ccd_1b,
        },
    )
    return TaxEngine.calculate_all(profile)
