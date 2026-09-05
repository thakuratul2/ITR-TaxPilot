"""Pydantic schemas for the Tax Regime Comparison & Breakeven Analysis Engine."""

from pydantic import BaseModel, Field

from app.calculator.models import RegimeComputation


class ComparisonLineItem(BaseModel):
    """Line-by-line itemized differential between Old and New regimes."""
    category: str
    label: str
    old_value: float
    new_value: float
    difference: float  # old_value - new_value
    notes: str = ""


class TakeHomeAnalysis(BaseModel):
    """Monthly in-hand net salary analysis."""
    annual_gross_income: float
    old_regime_annual_tax: float
    new_regime_annual_tax: float
    old_regime_monthly_in_hand: float
    new_regime_monthly_in_hand: float
    monthly_in_hand_difference: float
    optimal_monthly_regime: str


class BreakevenAnalysis(BaseModel):
    """Deduction Breakeven Threshold analysis."""
    assessment_year: str
    gross_income: float
    new_regime_tax_payable: float
    breakeven_deduction_required: float
    current_claimed_deductions: float
    deduction_shortfall_or_surplus: float  # Positive = Shortfall to reach breakeven, Negative = Surplus
    is_old_regime_beneficial: bool
    breakeven_summary: str
    optimization_recommendations: list[str] = Field(default_factory=list)


from app.tax.itr_models import ITRRecommendation


class ComprehensiveComparisonResponse(BaseModel):
    """Complete response payload for side-by-side regime comparison and breakeven intelligence."""
    assessment_year: str
    recommended_regime: str  # "NEW" or "OLD"
    tax_savings_amount: float
    percentage_savings: float
    effective_tax_rate_old: float
    effective_tax_rate_new: float

    take_home_analysis: TakeHomeAnalysis
    breakeven_analysis: BreakevenAnalysis
    line_items: list[ComparisonLineItem] = Field(default_factory=list)

    old_regime: RegimeComputation
    new_regime: RegimeComputation

    recommended_itr_form: str
    itr_recommendation: ITRRecommendation | None = Field(default=None, description="Detailed statutory ITR recommendation")
    narrative_summary: str

