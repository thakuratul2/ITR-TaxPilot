"""Comprehensive Unit Tests for the Deterministic Tax Engine (Milestone 7)."""

import pytest
from app.calculator.deduction_engine import DeductionEngine
from app.calculator.house_property_engine import HousePropertyEngine
from app.calculator.interest_engine import InterestEngine
from app.calculator.models import (
    AdvanceTaxScheduleInput,
    ChapterVIAInput,
    HousePropertyInput,
    OtherSourcesInput,
    PropertyType,
    SalaryInput,
    SeniorCitizenCategory,
    TaxpayerProfileInput,
)
from app.calculator.other_sources_engine import OtherSourcesEngine
from app.calculator.rebate_engine import RebateEngine
from app.calculator.regime_comparator import RegimeComparator
from app.calculator.salary_engine import SalaryEngine
from app.calculator.slab_engine import SlabEngine
from app.calculator.surcharge_engine import SurchargeEngine
from app.calculator.tax_engine import TaxEngine
from app.tax.rules.base import TaxRegime


# ==========================================
# 1. Salary Engine & HRA Exemption Tests
# ==========================================

def test_hra_exemption_calculation_metro():
    """Test HRA exemption Section 10(13A) in metro city (50%)."""
    sal_input = SalaryInput(
        basic_salary=600000.0,
        dearness_allowance=0.0,
        hra_received=240000.0,
        rent_paid_annual=240000.0,  # ₹20,000/mo
        is_metro=True,
    )
    # Limits:
    # 1. Actual HRA = 240,000
    # 2. Rent - 10% Salary = 240,000 - 60,000 = 180,000
    # 3. 50% Salary = 300,000
    # Min = 180,000
    exempt_hra = SalaryEngine.calculate_hra_exemption(sal_input)
    assert exempt_hra == 180000.0


def test_hra_exemption_calculation_non_metro():
    """Test HRA exemption Section 10(13A) in non-metro city (40%)."""
    sal_input = SalaryInput(
        basic_salary=500000.0,
        dearness_allowance=100000.0,  # Salary = 600,000
        hra_received=300000.0,
        rent_paid_annual=300000.0,
        is_metro=False,
    )
    # Limits:
    # 1. Actual = 300,000
    # 2. Rent - 10% = 300,000 - 60,000 = 240,000
    # 3. 40% Salary = 240,000
    exempt_hra = SalaryEngine.calculate_hra_exemption(sal_input)
    assert exempt_hra == 240000.0


def test_salary_standard_deduction_ay_2026_27():
    """Test Standard Deduction ₹75,000 in New vs ₹50,000 in Old for AY 2026-27."""
    sal_input = SalaryInput(gross_salary_sec_17_1=1200000.0, professional_tax_paid=2400.0)
    
    new_res = SalaryEngine.compute_salary_income(sal_input, TaxRegime.NEW, "2026-27")
    assert new_res["standard_deduction_sec_16_ia"] == 75000.0
    assert new_res["professional_tax_sec_16_iii"] == 0.0
    assert new_res["net_salary_income"] == 1125000.0

    old_res = SalaryEngine.compute_salary_income(sal_input, TaxRegime.OLD, "2026-27")
    assert old_res["standard_deduction_sec_16_ia"] == 50000.0
    assert old_res["professional_tax_sec_16_iii"] == 2400.0
    assert old_res["net_salary_income"] == 1147600.0


# ==========================================
# 2. House Property Engine Tests
# ==========================================

def test_sop_housing_loan_interest_limit():
    """Test Self-Occupied property loan interest up to ₹2,00,000 in Old Regime and ₹0 in New."""
    hp_input = HousePropertyInput(
        property_type=PropertyType.SELF_OCCUPIED,
        housing_loan_interest_sop=250000.0,
    )
    old_res = HousePropertyEngine.compute_house_property_income(hp_input, TaxRegime.OLD)
    assert old_res["housing_loan_interest_sec_24b"] == 200000.0
    assert old_res["net_house_property_income"] == -200000.0

    new_res = HousePropertyEngine.compute_house_property_income(hp_input, TaxRegime.NEW)
    assert new_res["net_house_property_income"] == 0.0


def test_let_out_property_standard_deduction_24a():
    """Test Let-Out property NAV and 30% statutory standard deduction."""
    hp_input = HousePropertyInput(
        property_type=PropertyType.LET_OUT,
        annual_lettable_value_or_rent=360000.0,
        municipal_taxes_paid=20000.0,  # NAV = 340,000
        housing_loan_interest_lop=100000.0,
    )
    # 30% of 340,000 = 102,000
    # Net income = 340,000 - 102,000 - 100,000 = 138,000
    res = HousePropertyEngine.compute_house_property_income(hp_input, TaxRegime.OLD)
    assert res["net_annual_value"] == 340000.0
    assert res["standard_deduction_sec_24a"] == 102000.0
    assert res["net_house_property_income"] == 138000.0


# ==========================================
# 3. Other Sources Engine Tests
# ==========================================

def test_family_pension_deduction():
    """Test Section 57(iia) family pension deduction (1/3rd or ₹25k in New / ₹15k in Old)."""
    os_input = OtherSourcesInput(
        family_pension=90000.0,  # 1/3rd = 30,000
        savings_bank_interest=15000.0,
    )
    new_res = OtherSourcesEngine.compute_other_sources_income(os_input, TaxRegime.NEW, "2026-27")
    assert new_res["family_pension_deduction_sec_57_iia"] == 25000.0
    assert new_res["net_family_pension"] == 65000.0
    assert new_res["total_other_sources_income"] == 80000.0

    old_res = OtherSourcesEngine.compute_other_sources_income(os_input, TaxRegime.OLD, "2026-27")
    assert old_res["family_pension_deduction_sec_57_iia"] == 15000.0
    assert old_res["net_family_pension"] == 75000.0
    assert old_res["total_other_sources_income"] == 90000.0


# ==========================================
# 4. Chapter VI-A Deduction Engine Tests
# ==========================================

def test_chapter_via_80cce_cap_and_nps_1b():
    """Test 80CCE ₹1.5L cap and exclusive 80CCD(1B) ₹50k deduction."""
    ch_input = ChapterVIAInput(
        section_80c=120000.0,
        section_80ccc=30000.0,
        section_80ccd_1=40000.0,  # Total 190,000 -> capped at 150,000
        section_80ccd_1b=60000.0,  # Capped at 50,000
    )
    os_input = OtherSourcesInput()
    res = DeductionEngine.compute_chapter_via_deductions(
        ch_input, os_input, 1000000.0, TaxRegime.OLD
    )
    assert res["total_deductions"] == 200000.0
    assert res["itemized"]["80CCE (80C/80CCC/80CCD(1))"] == 150000.0
    assert res["itemized"]["80CCD(1B)"] == 50000.0


def test_chapter_via_80d_senior_parents():
    """Test 80D health insurance for self + senior parents + preventive checkup."""
    ch_input = ChapterVIAInput(
        section_80d_self=22000.0,
        section_80d_parents=48000.0,
        section_80d_preventive=5000.0,
        parents_are_senior_citizens=True,
    )
    # Self limit = 25,000 (22,000 + 3,000 preventive = 25,000)
    # Parents limit = 50,000 (48,000 + 2,000 preventive = 50,000)
    # Total = 75,000
    ded_80d = DeductionEngine.calculate_section_80d(ch_input, SeniorCitizenCategory.INDIVIDUAL)
    assert ded_80d == 75000.0


# ==========================================
# 5. Progressive Slab Engine Tests
# ==========================================

def test_ay_2026_27_new_regime_slabs():
    """Test AY 2026-27 Section 115BAC progressive slabs."""
    # Income ₹16,00,000
    # Slabs:
    # 0 - 3L: 0
    # 3 - 7L (4L @ 5%): 20,000
    # 7 - 10L (3L @ 10%): 30,000
    # 10 - 12L (2L @ 15%): 30,000
    # 12 - 15L (3L @ 20%): 60,000
    # >15L (1L @ 30%): 30,000
    # Total Base Tax = 170,000
    tax, details = SlabEngine.compute_slab_tax(1600000.0, TaxRegime.NEW, "2026-27")
    assert tax == 170000.0
    assert len(details) == 6


# ==========================================
# 6. Section 87A Rebate & Marginal Relief
# ==========================================

def test_section_87a_full_rebate_at_7_lakhs():
    """Test full Section 87A rebate for income <= ₹7,00,000 in New Regime."""
    # Base tax on 700,000 = (4,00,000 * 5%) = 20,000
    reb_res = RebateEngine.compute_rebate_and_marginal_relief(
        700000.0, 20000.0, TaxRegime.NEW, "2026-27"
    )
    assert reb_res["rebate_87a_claimed"] == 20000.0
    assert reb_res["marginal_relief_87a"] == 0.0
    assert reb_res["tax_after_87a"] == 0.0


def test_section_87a_marginal_relief_edge_cases():
    """Test Section 87A Marginal Relief for income marginally exceeding ₹7 Lakhs."""
    # Scenario 1: Taxable Income ₹7,05,000
    # Base tax = 20,000 (up to 7L) + 500 (10% on 5,000) = 20,500
    # Income exceeding 7L = 5,000
    # Tax payable cannot exceed 5,000 -> Marginal Relief = 20,500 - 5,000 = 15,500
    res_705k = RebateEngine.compute_rebate_and_marginal_relief(
        705000.0, 20500.0, TaxRegime.NEW, "2026-27"
    )
    assert res_705k["marginal_relief_87a"] == 15500.0
    assert res_705k["tax_after_87a"] == 5000.0

    # Scenario 2: Taxable Income ₹7,15,000
    # Base tax = 20,000 + 1,500 = 21,500
    # Income exceeding 7L = 15,000
    # Marginal Relief = 21,500 - 15,000 = 6,500 -> Net Tax = 15,000
    res_715k = RebateEngine.compute_rebate_and_marginal_relief(
        715000.0, 21500.0, TaxRegime.NEW, "2026-27"
    )
    assert res_715k["marginal_relief_87a"] == 6500.0
    assert res_715k["tax_after_87a"] == 15000.0


# ==========================================
# 7. Surcharge & Surcharge Marginal Relief
# ==========================================

def test_surcharge_marginal_relief_at_50_lakhs():
    """Test Surcharge marginal relief when income marginally exceeds ₹50 Lakhs."""
    # Taxable income = ₹51,00,000
    sur_res = SurchargeEngine.compute_surcharge_and_marginal_relief(
        5100000.0, 1220000.0, TaxRegime.NEW, "2026-27"
    )
    assert sur_res["surcharge_rate_percentage"] == 10.0
    assert sur_res["gross_surcharge"] == 122000.0
    # Marginal relief ensures Tax + Surcharge does not exceed (Tax on 50L) + (1L excess)
    assert sur_res["surcharge_marginal_relief"] > 0.0


# ==========================================
# 8. Section 234A/B/C Advance Tax Interest
# ==========================================

def test_section_234abc_interest_no_shortfall():
    """Test zero interest when advance tax is fully paid on schedule."""
    adv_input = AdvanceTaxScheduleInput(
        total_tds_tcs_deducted=50000.0,
        advance_tax_paid_q1_june15=15000.0,
        advance_tax_paid_q2_sept15=45000.0,
        advance_tax_paid_q3_dec15=75000.0,
        advance_tax_paid_q4_mar15=100000.0,
    )
    int_res = InterestEngine.compute_interest_234abc(
        150000.0, 0.0, adv_input, "2026-27"
    )
    assert int_res["total_interest_234"] == 0.0


# ==========================================
# 9. End-to-End Tax Engine & Regime Comparison
# ==========================================

def test_end_to_end_user_form16_zero_tax_rebate():
    """Test user Atul Pratap Singh's Form 16 (Gross Salary ₹3,48,952) yields ₹0 tax."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=348952.0),
    )
    result = TaxEngine.calculate_all(profile)
    assert result.new_regime.aggregate_liability == 0.0
    assert result.old_regime.aggregate_liability == 0.0
    assert result.new_regime.net_payable_or_refund == 0.0


def test_end_to_end_regime_comparison_high_earner():
    """Test dual regime comparison for high earner with substantial 80C and 80D investments."""
    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(
            gross_salary_sec_17_1=2500000.0,
            professional_tax_paid=2500.0,
        ),
        house_property=HousePropertyInput(
            property_type=PropertyType.SELF_OCCUPIED,
            housing_loan_interest_sop=200000.0,
        ),
        chapter_vi_a=ChapterVIAInput(
            section_80c=150000.0,
            section_80ccd_1b=50000.0,
            section_80d_self=25000.0,
            section_80d_parents=50000.0,
            parents_are_senior_citizens=True,
        ),
    )
    result = TaxEngine.calculate_all(profile)
    # Old regime gets 50k std ded + 2.5k prof tax + 200k SOP interest + 150k 80C + 50k 80CCD(1B) + 75k 80D = 527.5k deductions
    # New regime gets 75k std ded
    assert result.recommended_regime in ["OLD", "NEW"]
    assert result.tax_savings_amount > 0.0
    assert result.old_regime.total_chapter_via_deductions == 275000.0
    assert result.new_regime.standard_deduction_sec_16_ia == 75000.0
