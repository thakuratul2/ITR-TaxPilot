"""Unit Tests for Tax Regime Comparison and Breakeven Analysis Engine (Milestone 8)."""

from app.calculator.models import (
    ChapterVIAInput,
    HousePropertyInput,
    SalaryInput,
    TaxpayerProfileInput,
)
from app.comparison.breakeven_solver import BreakevenSolver
from app.comparison.comparison_engine import ComparisonEngine

# ==========================================
# 1. Breakeven Solver Tests
# ==========================================

def test_breakeven_solver_zero_tax_threshold():
    """Test breakeven solver when New Regime tax is ₹0 (e.g. Gross ₹7,50,000 in AY 2026-27)."""
    # Gross ₹7.5L - ₹75k std ded = ₹6.75L taxable -> Tax in New Regime is ₹0 (Section 87A rebate)
    # In Old Regime, to reach ₹0 tax, taxable income must be <= ₹5,00,000.
    # Therefore, Breakeven deductions required = ₹7,50,000 - ₹5,00,000 = ₹2,50,000.
    breakeven_req, new_tax = BreakevenSolver.solve_breakeven_deductions(750000.0, "2026-27")
    assert new_tax == 0.0
    assert breakeven_req == 250000.0


def test_breakeven_solver_middle_income_10_lakhs():
    """Test breakeven solver at ₹10,00,000 gross salary."""
    # Under New Regime AY 2026-27:
    # Gross 10L - 75k = 9.25L Taxable.
    # Tax = 20,000 (3-7L @ 5%) + 22,500 (7-9.25L @ 10%) = 42,500 + 4% cess (1,700) = ₹44,200.
    # In Old Regime: Taxable income required to yield ₹44,200 tax:
    # Slabs: 0-2.5L: 0, 2.5-5L: 12.5k, 5L-X @ 20%: (42,500 - 12,500) = 30,000 / 0.20 = 1,50,000.
    # Target Old Taxable Income = 5,00,000 + 1,50,000 = 6,50,000.
    # Breakeven Deductions = 10,00,000 - 6,50,000 = ₹3,50,000.
    breakeven_req, new_tax = BreakevenSolver.solve_breakeven_deductions(1000000.0, "2026-27")
    assert new_tax == 44200.0
    assert abs(breakeven_req - 350000.0) <= 10.0


def test_breakeven_analysis_shortfall_and_recommendations():
    """Test breakeven analysis when deductions are insufficient (New Regime wins)."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=1200000.0),
        chapter_vi_a=ChapterVIAInput(section_80c=50000.0),
    )
    analysis = BreakevenSolver.analyze_breakeven(profile)
    assert not analysis.is_old_regime_beneficial
    assert analysis.deduction_shortfall_or_surplus > 0.0
    assert len(analysis.optimization_recommendations) > 0
    assert any("Section 80C" in r for r in analysis.optimization_recommendations)


def test_breakeven_analysis_surplus_old_regime():
    """Test breakeven analysis when deductions exceed threshold (Old Regime wins)."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=1500000.0, professional_tax_paid=2500.0),
        house_property=HousePropertyInput(housing_loan_interest_sop=200000.0),
        chapter_vi_a=ChapterVIAInput(
            section_80c=150000.0,
            section_80ccd_1b=50000.0,
            section_80d_self=25000.0,
            section_80d_parents=50000.0,
            parents_are_senior_citizens=True,
        ),
    )
    # Total deductions claimed = 50k std + 2.5k PT + 200k SOP + 150k 80C + 50k 80CCD(1B) + 75k 80D = 527,500
    analysis = BreakevenSolver.analyze_breakeven(profile)
    assert analysis.is_old_regime_beneficial
    assert analysis.deduction_shortfall_or_surplus < 0.0  # Negative represents surplus


# ==========================================
# 2. Comprehensive Comparison Engine Tests
# ==========================================

def test_take_home_salary_monthly_calculation():
    """Test monthly net take-home salary computation and differential."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=1200000.0),
    )
    res = ComparisonEngine.compare_comprehensive(profile)
    th = res.take_home_analysis
    assert th.annual_gross_income == 1200000.0
    assert th.new_regime_monthly_in_hand > th.old_regime_monthly_in_hand
    assert th.monthly_in_hand_difference > 0.0
    assert th.optimal_monthly_regime == "NEW"


def test_line_items_differential_completeness():
    """Test line-by-line delta generator includes all mandatory heads."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=1000000.0),
        chapter_vi_a=ChapterVIAInput(section_80c=150000.0),
    )
    res = ComparisonEngine.compare_comprehensive(profile)
    labels = [item.label for item in res.line_items]
    assert "Gross Salary" in labels
    assert "Standard Deduction u/s 16(ia)" in labels
    assert "Total Chapter VI-A Deductions" in labels
    assert "Total Taxable Income (Sec 288A)" in labels
    assert "Total Annual Tax Liability" in labels


def test_user_form16_zero_tax_comparison():
    """Test user Atul Pratap Singh's Form 16 comparison."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=348952.0),
    )
    res = ComparisonEngine.compare_comprehensive(profile)
    assert res.recommended_regime == "NEW"
    assert res.old_regime.aggregate_liability == 0.0
    assert res.new_regime.aggregate_liability == 0.0
    assert res.recommended_itr_form == "ITR-1 (Sahaj)"
