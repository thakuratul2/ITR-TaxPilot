"""Tax analysis and recommendation endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.schemas.analysis import AnalysisData, TaxCalculationSummary
from app.schemas.base import APIResponse

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get(
    "/{analysis_id}",
    response_model=APIResponse[AnalysisData],
    summary="Get Tax Analysis Result",
)
async def get_analysis_result(analysis_id: str, request: Request) -> APIResponse[AnalysisData]:
    """Retrieve full tax calculation breakdown and ITR recommendation for an analysis."""
    request_id = getattr(request.state, "request_id", "req_unknown")

    now = datetime.now(UTC)
    old_regime = TaxCalculationSummary(
        regime="OLD",
        gross_income=1200000.0,
        total_deductions=200000.0,
        taxable_income=1000000.0,
        total_tax_liability=117000.0,
        tds_credit=120000.0,
        tax_payable=0.0,
        refund_due=3000.0,
    )
    new_regime = TaxCalculationSummary(
        regime="NEW",
        gross_income=1200000.0,
        total_deductions=75000.0,
        taxable_income=1125000.0,
        total_tax_liability=67600.0,
        tds_credit=120000.0,
        tax_payable=0.0,
        refund_due=52400.0,
    )

    data = AnalysisData(
        analysis_id=analysis_id,
        document_id="doc_sample_123",
        assessment_year="2026-27",
        financial_year="2025-26",
        status="calculated",
        recommended_itr="ITR-1 (Sahaj)",
        explanation="Under the New Tax Regime (AY 2026-27), your total tax liability is ₹67,600 compared to ₹1,17,000 under the Old Regime, saving you ₹49,400.",
        calculations=[old_regime, new_regime],
        created_at=now,
    )

    return APIResponse(
        success=True,
        data=data,
        error=None,
        request_id=request_id,
    )
