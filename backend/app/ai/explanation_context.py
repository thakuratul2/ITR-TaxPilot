"""Structured Calculation Context Builder for Explanation AI.

Transforms deterministic calculation audit trails and regime comparison results
into an immutable, PII-free, structured context for AI explanation generation
and strict numerical verification.
"""

from typing import Any

from app.calculator.models import TaxpayerProfileInput
from app.comparison.models import ComprehensiveComparisonResponse
from app.tax.itr_models import ITRRecommendation


class ExplanationContextBuilder:
    """Builds structured, sanitized prompt contexts and number whitelists."""

    @classmethod
    def build_context(
        cls,
        comparison: ComprehensiveComparisonResponse,
        profile: TaxpayerProfileInput | None = None,
        itr_recommendation: ITRRecommendation | None = None,
    ) -> dict[str, Any]:
        """
        Build an immutable, structured context dictionary from deterministic comparison output.
        """
        ay = comparison.assessment_year
        winning = comparison.recommended_regime
        savings = comparison.tax_savings_amount
        old = comparison.old_regime
        new = comparison.new_regime
        take_home = comparison.take_home_analysis
        breakeven = comparison.breakeven_analysis

        # Detect missing info / unclaimed tax optimization opportunities
        missing_advisories = cls._detect_missing_opportunities(profile, old, new)

        # Build whitelist of permissible exact numbers
        whitelist = cls.extract_permissible_numbers(comparison, profile)

        # Recommended ITR details
        itr_rec = itr_recommendation or comparison.itr_recommendation
        itr_form = comparison.recommended_itr_form
        itr_reasons = itr_rec.eligibility_reasons if itr_rec else []
        itr_notes = itr_rec.notes_and_limitations if itr_rec else []

        context = {
            "assessment_year": ay,
            "financial_year": cls._derive_financial_year(ay),
            "winning_regime": winning,
            "tax_savings_amount": savings,
            "percentage_savings": comparison.percentage_savings,
            "take_home": {
                "annual_gross_income": take_home.annual_gross_income,
                "old_regime_monthly_in_hand": take_home.old_regime_monthly_in_hand,
                "new_regime_monthly_in_hand": take_home.new_regime_monthly_in_hand,
                "monthly_in_hand_difference": take_home.monthly_in_hand_difference,
                "optimal_monthly_regime": take_home.optimal_monthly_regime,
            },
            "old_regime": {
                "regime_name": "Old Tax Regime",
                "gross_salary": old.gross_salary,
                "exempt_allowances_sec_10": old.exempt_allowances_sec_10,
                "standard_deduction": old.standard_deduction_sec_16_ia,
                "professional_tax": old.professional_tax_sec_16_iii,
                "net_salary_income": old.net_salary_income,
                "house_property_loss": old.income_or_loss_house_property,
                "other_sources": old.income_other_sources,
                "gross_total_income": old.gross_total_income,
                "total_chapter_via_deductions": old.total_chapter_via_deductions,
                "itemized_deductions": old.itemized_chapter_via,
                "taxable_income": old.total_taxable_income,
                "base_tax": old.base_tax_on_income,
                "rebate_87a": old.rebate_87a_claimed,
                "surcharge": old.net_surcharge,
                "cess": old.cess_amount,
                "total_tax_liability": old.aggregate_liability,
                "prepaid_tds": old.total_prepaid_taxes,
                "net_payable_or_refund": old.net_payable_or_refund,
                "effective_tax_rate": old.effective_tax_rate_percentage,
            },
            "new_regime": {
                "regime_name": "New Tax Regime (Section 115BAC)",
                "gross_salary": new.gross_salary,
                "standard_deduction": new.standard_deduction_sec_16_ia,
                "net_salary_income": new.net_salary_income,
                "gross_total_income": new.gross_total_income,
                "total_chapter_via_deductions": new.total_chapter_via_deductions,
                "taxable_income": new.total_taxable_income,
                "base_tax": new.base_tax_on_income,
                "rebate_87a": new.rebate_87a_claimed,
                "marginal_relief_87a": new.marginal_relief_87a,
                "surcharge": new.net_surcharge,
                "cess": new.cess_amount,
                "total_tax_liability": new.aggregate_liability,
                "prepaid_tds": new.total_prepaid_taxes,
                "net_payable_or_refund": new.net_payable_or_refund,
                "effective_tax_rate": new.effective_tax_rate_percentage,
            },
            "breakeven_analysis": {
                "breakeven_deduction_required": breakeven.breakeven_deduction_required,
                "current_claimed_deductions": breakeven.current_claimed_deductions,
                "deduction_shortfall_or_surplus": breakeven.deduction_shortfall_or_surplus,
                "is_old_regime_beneficial": breakeven.is_old_regime_beneficial,
                "summary": breakeven.breakeven_summary,
            },
            "itr_recommendation": {
                "recommended_form": itr_form,
                "eligibility_reasons": itr_reasons,
                "notes_and_schedules": itr_notes,
            },
            "missing_info_advisories": missing_advisories,
            "permissible_numbers_whitelist": list(whitelist),
        }

        return context

    @classmethod
    def extract_permissible_numbers(
        cls,
        comparison: ComprehensiveComparisonResponse,
        profile: TaxpayerProfileInput | None = None,
    ) -> set[float]:
        """
        Collect all legitimate numerical values present in the calculation results
        to serve as an anti-hallucination whitelist.
        """
        numbers: set[float] = {
            0.0, 4.0, 5.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 50.0, 100.0,  # Common percentages & months
            75000.0, 50000.0, 150000.0, 200000.0, 300000.0, 700000.0, 1000000.0, 5000000.0, # Slabs/Standard limits
        }

        # Assessment year years (e.g. 2026, 2027, 2025, 2026)
        try:
            parts = comparison.assessment_year.split("-")
            numbers.add(float(parts[0]))
        except Exception:
            pass

        # Helper to add float variants
        def add_variants(val: float | int):
            f_val = float(val)
            numbers.add(round(f_val, 2))
            numbers.add(round(f_val, 1))
            numbers.add(round(f_val, 0))
            numbers.add(float(int(f_val)))
            numbers.add(float(int(round(f_val))))

        # Comparison metrics
        add_variants(comparison.tax_savings_amount)
        add_variants(comparison.percentage_savings)
        add_variants(comparison.effective_tax_rate_old)
        add_variants(comparison.effective_tax_rate_new)

        # Take home
        th = comparison.take_home_analysis
        for val in (th.annual_gross_income, th.old_regime_annual_tax, th.new_regime_annual_tax,
                    th.old_regime_monthly_in_hand, th.new_regime_monthly_in_hand, th.monthly_in_hand_difference):
            add_variants(val)

        # Breakeven
        be = comparison.breakeven_analysis
        for val in (be.gross_income, be.new_regime_tax_payable, be.breakeven_deduction_required,
                    be.current_claimed_deductions, be.deduction_shortfall_or_surplus):
            add_variants(abs(val))


        # Old and New computations
        for comp in (comparison.old_regime, comparison.new_regime):
            for attr in (
                "gross_salary", "exempt_allowances_sec_10", "standard_deduction_sec_16_ia",
                "professional_tax_sec_16_iii", "entertainment_allowance_sec_16_ii", "net_salary_income",
                "income_or_loss_house_property", "income_other_sources", "gross_total_income",
                "total_chapter_via_deductions", "total_taxable_income", "base_tax_on_income",
                "rebate_87a_claimed", "marginal_relief_87a", "surcharge_rate_percentage",
                "gross_surcharge", "surcharge_marginal_relief", "net_surcharge", "cess_amount",
                "total_tax_and_cess", "relief_sec_89", "net_tax_liability", "aggregate_liability",
                "total_prepaid_taxes", "net_payable_or_refund", "effective_tax_rate_percentage",
            ):
                val = getattr(comp, attr, 0.0)
                if isinstance(val, (int, float)):
                    numbers.add(round(abs(float(val)), 2))
                    numbers.add(float(int(abs(val))))

            for item_val in comp.itemized_chapter_via.values():
                numbers.add(round(abs(float(item_val)), 2))
                numbers.add(float(int(abs(item_val))))

            for slab in comp.slab_breakdown:
                numbers.add(round(slab.bracket_min, 2))
                if slab.bracket_max:
                    numbers.add(round(slab.bracket_max, 2))
                numbers.add(round(slab.rate_percentage, 2))
                numbers.add(round(slab.taxable_in_bracket, 2))
                numbers.add(round(slab.tax_amount, 2))

        # Profile inputs if provided
        if profile:
            if profile.salary:
                for k, v in profile.salary.model_dump().items():
                    if isinstance(v, (int, float)):
                        numbers.add(round(float(v), 2))
            if profile.chapter_vi_a:
                for k, v in profile.chapter_vi_a.model_dump().items():
                    if isinstance(v, (int, float)):
                        numbers.add(round(float(v), 2))

        return numbers

    @staticmethod
    def _detect_missing_opportunities(
        profile: TaxpayerProfileInput | None,
        old_comp,
        new_comp,
    ) -> list[str]:
        """Detect potential missing deductions, unverified claims, and AIS reconciliation items."""
        advisories: list[str] = []

        if profile:
            cvia = profile.chapter_vi_a
            # 1. 80CCD(1B) NPS ₹50k additional
            if cvia.section_80ccd_1b == 0.0:
                advisories.append("Additional ₹50,000 NPS contribution under Section 80CCD(1B) was not claimed; this offers exclusive tax reduction over and above Section 80C.")

            # 2. 80D Health Insurance
            if cvia.section_80d_self == 0.0 and cvia.section_80d_parents == 0.0:
                advisories.append("Health insurance premium under Section 80D is ₹0; up to ₹25,000 (self/family) and ₹50,000 (senior parents) can be claimed with valid policy receipts.")

            # 3. 80TTA / 80TTB
            if cvia.section_80tta == 0.0 and cvia.section_80ttb == 0.0 and profile.other_sources.savings_bank_interest > 0:
                advisories.append("Savings bank interest deduction under Section 80TTA (up to ₹10,000) was not claimed in Old Regime.")

            # 4. HRA vs Rent Paid
            if profile.salary.hra_received > 0 and profile.salary.rent_paid_annual == 0:
                advisories.append("House Rent Allowance (HRA) received from employer was not exempted because annual rent paid was recorded as ₹0. Verify rent receipts.")

        # General standard filing checklists
        advisories.append("Verify your Annual Information Statement (AIS) and Form 26AS on the Income Tax e-filing portal to capture any unreported interest or dividend receipts.")
        advisories.append("Ensure employer TDS matches Part A of Form 16 before final return submission.")

        return advisories

    @staticmethod
    def _derive_financial_year(ay: str) -> str:
        """Derive FY from AY (e.g. '2026-27' -> '2025-26')."""
        try:
            start_year = int(ay.split("-")[0])
            fy_start = start_year - 1
            fy_end = str(start_year)[-2:]
            return f"{fy_start}-{fy_end}"
        except Exception:
            return "2025-26"
