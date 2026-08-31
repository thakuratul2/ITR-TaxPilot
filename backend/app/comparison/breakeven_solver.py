"""Deterministic Deduction Breakeven Solver Sub-Engine."""

from app.calculator.models import (
    ChapterVIAInput,
    HousePropertyInput,
    OtherSourcesInput,
    SalaryInput,
    SeniorCitizenCategory,
    TaxpayerProfileInput,
)
from app.calculator.rebate_engine import RebateEngine
from app.calculator.slab_engine import SlabEngine
from app.calculator.tax_engine import TaxEngine
from app.comparison.models import BreakevenAnalysis
from app.tax.rules.base import TaxRegime


class BreakevenSolver:
    """Deterministic solver calculating the exact deduction amount needed for Old Regime to beat New Regime."""

    @classmethod
    def compute_old_regime_total_tax(
        cls,
        taxable_income: float,
        assessment_year: str = "2026-27",
        category: SeniorCitizenCategory = SeniorCitizenCategory.INDIVIDUAL,
    ) -> float:
        """Helper to compute Old Regime Tax + Cess for a given taxable income."""
        if taxable_income <= 0:
            return 0.0
        
        base_tax, _ = SlabEngine.compute_slab_tax(
            taxable_income, TaxRegime.OLD, assessment_year, category
        )
        reb_res = RebateEngine.compute_rebate_and_marginal_relief(
            taxable_income, base_tax, TaxRegime.OLD, assessment_year
        )
        tax_after_87a = reb_res["tax_after_87a"]
        cess = round(0.04 * tax_after_87a, 2)
        return tax_after_87a + cess

    @classmethod
    def solve_breakeven_deductions(
        cls,
        gross_income: float,
        assessment_year: str = "2026-27",
        category: SeniorCitizenCategory = SeniorCitizenCategory.INDIVIDUAL,
    ) -> tuple[float, float]:
        """
        Solve for the minimum total deductions (Section 16 + Section 10 + Chapter VI-A)
        required under Old Regime so that Tax(Old) <= Tax(New).
        Returns: (breakeven_deduction_required, new_regime_tax_payable)
        """
        if gross_income <= 0:
            return 0.0, 0.0

        # 1. Compute New Regime Tax on gross income (with Standard Deduction)
        dummy_profile = TaxpayerProfileInput(
            assessment_year=assessment_year,
            taxpayer_category=category,
            salary=SalaryInput(gross_salary_sec_17_1=gross_income),
        )
        new_comp = TaxEngine.compute_regime(dummy_profile, TaxRegime.NEW)
        new_regime_tax = new_comp.total_tax_and_cess

        # If New Regime tax is 0, to achieve 0 tax in Old Regime, taxable income must be <= 5 Lakhs
        if new_regime_tax <= 0:
            breakeven_deductions = max(0.0, gross_income - 500000.0)
            return round(breakeven_deductions, 2), 0.0

        # 2. Binary search to find the highest taxable income in Old Regime where Tax(Old) <= Tax(New)
        low = 0.0
        high = gross_income
        target_taxable_income = 0.0

        # Precision within ₹1
        for _ in range(50):
            mid = (low + high) / 2.0
            old_tax = cls.compute_old_regime_total_tax(mid, assessment_year, category)

            if old_tax <= new_regime_tax:
                target_taxable_income = mid
                low = mid  # Try higher taxable income (less deductions)
            else:
                high = mid  # Need lower taxable income (more deductions)

        breakeven_deductions = max(0.0, gross_income - target_taxable_income)
        return round(breakeven_deductions, 2), round(new_regime_tax, 2)

    @classmethod
    def analyze_breakeven(
        cls,
        profile: TaxpayerProfileInput,
    ) -> BreakevenAnalysis:
        """
        Perform complete breakeven analysis against the taxpayer's current claimed deductions.
        """
        ay = profile.assessment_year
        gross_salary = (
            profile.salary.gross_salary_sec_17_1
            + profile.salary.perquisites_sec_17_2
            + profile.salary.profits_in_lieu_sec_17_3
            if profile.salary.gross_salary_sec_17_1 > 0
            else (
                profile.salary.basic_salary
                + profile.salary.dearness_allowance
                + profile.salary.hra_received
                + profile.salary.lta_received
            )
        )
        total_gross = gross_salary + profile.other_sources.savings_bank_interest + profile.other_sources.fixed_deposit_interest

        breakeven_req, new_tax = cls.solve_breakeven_deductions(
            total_gross, ay, profile.taxpayer_category
        )

        # Compute current claimed deductions under Old Regime
        old_comp = TaxEngine.compute_regime(profile, TaxRegime.OLD)
        current_deductions = (
            old_comp.standard_deduction_sec_16_ia
            + old_comp.exempt_allowances_sec_10
            + old_comp.professional_tax_sec_16_iii
            + old_comp.total_chapter_via_deductions
            + abs(min(0.0, old_comp.income_or_loss_house_property))
        )

        shortfall = max(0.0, breakeven_req - current_deductions)
        surplus = max(0.0, current_deductions - breakeven_req)
        is_beneficial = current_deductions >= breakeven_req

        # Recommendations list
        recs = []
        if is_beneficial:
            summary = (
                f"Your total claimed deductions of ₹{current_deductions:,.0f} exceed the breakeven threshold "
                f"of ₹{breakeven_req:,.0f} by ₹{surplus:,.0f}. The Old Tax Regime is currently more beneficial."
            )
            recs.append("Ensure you collect and preserve valid rent receipts and 80C investment proofs for ITR filing.")
        else:
            summary = (
                f"For your gross income of ₹{total_gross:,.0f}, you require at least ₹{breakeven_req:,.0f} in eligible "
                f"deductions for the Old Regime to save more tax. You currently claim ₹{current_deductions:,.0f}, "
                f"leaving a shortfall of ₹{shortfall:,.0f}."
            )
            # Actionable tax saving tips
            ch = profile.chapter_vi_a
            if ch.section_80c < 150000.0:
                gap_80c = 150000.0 - ch.section_80c
                recs.append(f"Maximize Section 80C (PPF, ELSS, EPF, Life Insurance): Potential additional deduction of ₹{gap_80c:,.0f}.")
            if ch.section_80ccd_1b < 50000.0:
                gap_nps = 50000.0 - ch.section_80ccd_1b
                recs.append(f"Invest in National Pension System (NPS) under Section 80CCD(1B): Exclusive additional deduction up to ₹{gap_nps:,.0f}.")
            if ch.section_80d_self < 25000.0:
                recs.append("Purchase Health Insurance for self/family under Section 80D: Deductions up to ₹25,000 (₹50,000 for Senior Citizens).")
            if profile.salary.rent_paid_annual > 0 and profile.salary.hra_received == 0:
                recs.append("Claim House Rent deduction under Section 80GG (up to ₹60,000/year).")

        return BreakevenAnalysis(
            assessment_year=ay,
            gross_income=round(total_gross, 2),
            new_regime_tax_payable=round(new_tax, 2),
            breakeven_deduction_required=round(breakeven_req, 2),
            current_claimed_deductions=round(current_deductions, 2),
            deduction_shortfall_or_surplus=round(shortfall if shortfall > 0 else -surplus, 2),
            is_old_regime_beneficial=is_beneficial,
            breakeven_summary=summary,
            optimization_recommendations=recs,
        )
