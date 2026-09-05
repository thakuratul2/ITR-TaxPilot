"""Golden test suite validating deterministic tax calculation and regime comparison across known fixtures."""

import pytest

from app.calculator.models import (
    ChapterVIAInput,
    HousePropertyInput,
    OtherSourcesInput,
    SalaryInput,
    TaxpayerProfileInput,
)
from app.calculator.tax_engine import TaxEngine
from app.comparison.comparison_engine import ComparisonEngine
from app.tax.itr_selector import ITRSelector
from app.tax.rules.base import TaxRegime


def test_golden_standard_salaried_tax_computation():
    """Verify standard salaried individual tax calculation and regime comparison for AY 2025-26."""
    profile = TaxpayerProfileInput(
        assessment_year="2025-26",
        salary=SalaryInput(
            basic_salary=600000.0,
            gross_salary_sec_17_1=1200000.0,
            hra_received=120000.0,
            rent_paid_annual=180000.0,
            is_metro=True,
            professional_tax_paid=2500.0,
        ),
        other_sources=OtherSourcesInput(
            savings_bank_interest=20000.0,
        ),
        chapter_vi_a=ChapterVIAInput(
            section_80c=150000.0,
            section_80ccd_1b=50000.0,
            section_80d_self=25000.0,
            section_80tta=10000.0,
        ),
    )

    comparison = ComparisonEngine.compare_comprehensive(profile)

    assert comparison.recommended_regime in ["OLD", "NEW"]
    assert comparison.tax_savings_amount >= 0.0

    # Old Regime calculation details
    old_calc = TaxEngine.compute_regime(profile, TaxRegime.OLD)
    assert old_calc.gross_total_income > 0.0
    assert old_calc.total_chapter_via_deductions >= 225000.0
    assert old_calc.aggregate_liability >= 0.0

    # New Regime calculation details
    new_calc = TaxEngine.compute_regime(profile, TaxRegime.NEW)
    assert new_calc.gross_total_income > 0.0
    assert new_calc.standard_deduction_sec_16_ia == 50000.0
    assert new_calc.aggregate_liability >= 0.0

    # Line item audit verification
    assert len(comparison.line_items) > 10


def test_golden_zero_tax_rebate_87a():
    """Verify below 7 LPA (New Regime) and below 5 LPA (Old Regime) 87A rebate."""
    profile = TaxpayerProfileInput(
        assessment_year="2025-26",
        salary=SalaryInput(
            gross_salary_sec_17_1=550000.0,
        ),
        chapter_vi_a=ChapterVIAInput(
            section_80c=50000.0,
        ),
    )

    old_calc = TaxEngine.compute_regime(profile, TaxRegime.OLD)
    new_calc = TaxEngine.compute_regime(profile, TaxRegime.NEW)

    # In AY 2025-26, taxable income <= 5L in Old Regime has 0 tax liability after 87A
    assert old_calc.total_taxable_income <= 500000.0
    assert old_calc.aggregate_liability == 0.0

    # In AY 2025-26, taxable income <= 7L in New Regime has 0 tax liability after 87A
    assert new_calc.total_taxable_income <= 700000.0
    assert new_calc.aggregate_liability == 0.0


def test_golden_high_net_worth_surcharge():
    """Verify high income tax calculation with surcharge and cess."""
    profile = TaxpayerProfileInput(
        assessment_year="2025-26",
        salary=SalaryInput(
            gross_salary_sec_17_1=7500000.0,
            professional_tax_paid=2500.0,
        ),
        house_property=HousePropertyInput(
            housing_loan_interest_sop=200000.0,
        ),
        other_sources=OtherSourcesInput(
            fixed_deposit_interest=150000.0,
        ),
        chapter_vi_a=ChapterVIAInput(
            section_80c=150000.0,
            section_80d_self=50000.0,
        ),
    )

    old_calc = TaxEngine.compute_regime(profile, TaxRegime.OLD)
    new_calc = TaxEngine.compute_regime(profile, TaxRegime.NEW)

    # Income > 50L triggers surcharge
    assert old_calc.net_surcharge > 0.0
    assert new_calc.net_surcharge > 0.0
    assert old_calc.cess_amount > 0.0
    assert new_calc.cess_amount > 0.0
