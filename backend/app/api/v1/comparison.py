"""FastAPI endpoints for Tax Regime Comparison and Breakeven Analysis."""

from fastapi import APIRouter, Query, status

from app.calculator.models import (
    SalaryInput,
    SeniorCitizenCategory,
    TaxpayerProfileInput,
)
from app.comparison.breakeven_solver import BreakevenSolver
from app.comparison.comparison_engine import ComparisonEngine
from app.comparison.models import (
    BreakevenAnalysis,
    ComprehensiveComparisonResponse,
)

router = APIRouter(prefix="/comparison", tags=["Regime Comparison & Breakeven"])


@router.post(
    "/compare",
    response_model=ComprehensiveComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute comprehensive side-by-side tax regime comparison",
)
async def compare_regimes(profile: TaxpayerProfileInput) -> ComprehensiveComparisonResponse:
    """
    Execute parallel regime calculation, take-home salary differential,
    deduction breakeven threshold analysis, and transparent line-by-line delta.
    """
    return ComparisonEngine.compare_comprehensive(profile)


@router.get(
    "/breakeven",
    response_model=BreakevenAnalysis,
    status_code=status.HTTP_200_OK,
    summary="Calculate exact deduction breakeven threshold for a given gross income",
)
async def get_breakeven_threshold(
    gross_income: float = Query(..., ge=0.0, description="Gross annual income"),
    assessment_year: str = Query(default="2026-27", description="Assessment Year"),
    category: SeniorCitizenCategory = Query(default=SeniorCitizenCategory.INDIVIDUAL, description="Taxpayer age category"),
) -> BreakevenAnalysis:
    """
    Solve the mathematical breakeven deduction threshold where Old Regime tax equals New Regime tax.
    """
    profile = TaxpayerProfileInput(
        assessment_year=assessment_year,
        taxpayer_category=category,
        salary=SalaryInput(gross_salary_sec_17_1=gross_income),
    )
    return BreakevenSolver.analyze_breakeven(profile)
