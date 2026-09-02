"""Side-by-side Regime Comparison Engine with Take-Home & Line-by-Line Delta."""

from app.calculator.models import TaxpayerProfileInput
from app.calculator.tax_engine import TaxEngine
from app.comparison.breakeven_solver import BreakevenSolver
from app.comparison.models import (
    ComparisonLineItem,
    ComprehensiveComparisonResponse,
    TakeHomeAnalysis,
)
from app.tax.itr_selector import ITRSelector
from app.tax.rules.base import TaxRegime


class ComparisonEngine:
    """Master Side-by-Side Tax Regime Comparison and Take-Home Engine."""

    @classmethod
    def generate_line_items(
        cls,
        old_comp,
        new_comp,
    ) -> list[ComparisonLineItem]:
        """Generate structured line-by-line comparison delta."""
        items: list[ComparisonLineItem] = []

        def add_item(cat: str, label: str, old_val: float, new_val: float, note: str = ""):
            items.append(
                ComparisonLineItem(
                    category=cat,
                    label=label,
                    old_value=round(old_val, 2),
                    new_value=round(new_val, 2),
                    difference=round(old_val - new_val, 2),
                    notes=note,
                )
            )

        # 1. Salary & Exemptions
        add_item("Income", "Gross Salary", old_comp.gross_salary, new_comp.gross_salary)
        add_item("Deduction", "Section 10 Exemptions (HRA/LTA)", old_comp.exempt_allowances_sec_10, new_comp.exempt_allowances_sec_10, "Disallowed in New Regime")
        add_item("Deduction", "Standard Deduction u/s 16(ia)", old_comp.standard_deduction_sec_16_ia, new_comp.standard_deduction_sec_16_ia, "₹75,000 in New vs ₹50,000 in Old (AY 26-27)")
        add_item("Deduction", "Professional Tax u/s 16(iii)", old_comp.professional_tax_sec_16_iii, new_comp.professional_tax_sec_16_iii, "Old Regime only")
        add_item("Income", "Net Salary Income", old_comp.net_salary_income, new_comp.net_salary_income)

        # 2. Other Heads
        add_item("Income", "House Property (SOP Interest / Loss)", old_comp.income_or_loss_house_property, new_comp.income_or_loss_house_property, "Max -₹2L SOP loss in Old; ₹0 in New")
        add_item("Income", "Other Sources (Interest / Dividend)", old_comp.income_other_sources, new_comp.income_other_sources)
        add_item("Summary", "Gross Total Income (GTI)", old_comp.gross_total_income, new_comp.gross_total_income)

        # 3. Chapter VI-A Deductions
        add_item("Chapter VI-A", "Total Chapter VI-A Deductions", old_comp.total_chapter_via_deductions, new_comp.total_chapter_via_deductions, "Only 80CCD(2) allowed in New Regime")

        # 4. Taxable Income & Tax Computation
        add_item("Summary", "Total Taxable Income (Sec 288A)", old_comp.total_taxable_income, new_comp.total_taxable_income, "Rounded to nearest ₹10")
        add_item("Tax Calculation", "Computed Base Slab Tax", old_comp.base_tax_on_income, new_comp.base_tax_on_income)
        add_item("Tax Relief", "Section 87A Rebate", old_comp.rebate_87a_claimed, new_comp.rebate_87a_claimed, "Up to ₹25k in New (<=₹7L) vs ₹12.5k in Old (<=₹5L)")
        add_item("Tax Relief", "Section 87A Marginal Relief", old_comp.marginal_relief_87a, new_comp.marginal_relief_87a, "Protects income marginally above ₹7 Lakhs")
        add_item("Tax Calculation", "Surcharge", old_comp.net_surcharge, new_comp.net_surcharge)
        add_item("Tax Calculation", "Health & Education Cess (4%)", old_comp.cess_amount, new_comp.cess_amount)
        add_item("Summary", "Total Annual Tax Liability", old_comp.aggregate_liability, new_comp.aggregate_liability, "Final statutory tax liability")
        add_item("Settlement", "Prepaid Taxes (TDS / Advance Tax)", old_comp.total_prepaid_taxes, new_comp.total_prepaid_taxes)
        add_item("Settlement", "Net Balance Payable / Refund (Sec 288B)", old_comp.net_payable_or_refund, new_comp.net_payable_or_refund)

        return items

    @classmethod
    def compare_comprehensive(
        cls,
        profile: TaxpayerProfileInput,
    ) -> ComprehensiveComparisonResponse:
        """
        Execute comprehensive parallel regime comparison, take-home calculations, and breakeven intelligence.
        """
        ay = profile.assessment_year
        
        # Parallel / fast sequential execution of both regimes
        old_comp = TaxEngine.compute_regime(profile, TaxRegime.OLD)
        new_comp = TaxEngine.compute_regime(profile, TaxRegime.NEW)

        old_tax = old_comp.aggregate_liability
        new_tax = new_comp.aggregate_liability

        # Winning regime & savings
        if new_tax <= old_tax:
            recommended = "NEW"
            savings = old_tax - new_tax
            pct_savings = (savings / old_tax * 100.0) if old_tax > 0 else 0.0
        else:
            recommended = "OLD"
            savings = new_tax - old_tax
            pct_savings = (savings / new_tax * 100.0) if new_tax > 0 else 0.0

        # Take-home pay calculations
        total_gross = max(old_comp.gross_salary, new_comp.gross_salary) + old_comp.income_other_sources
        old_monthly_in_hand = max(0.0, (total_gross - old_tax) / 12.0)
        new_monthly_in_hand = max(0.0, (total_gross - new_tax) / 12.0)
        monthly_diff = abs(new_monthly_in_hand - old_monthly_in_hand)

        take_home = TakeHomeAnalysis(
            annual_gross_income=round(total_gross, 2),
            old_regime_annual_tax=round(old_tax, 2),
            new_regime_annual_tax=round(new_tax, 2),
            old_regime_monthly_in_hand=round(old_monthly_in_hand, 2),
            new_regime_monthly_in_hand=round(new_monthly_in_hand, 2),
            monthly_in_hand_difference=round(monthly_diff, 2),
            optimal_monthly_regime=recommended,
        )

        # Breakeven Analysis
        breakeven = BreakevenSolver.analyze_breakeven(profile)

        # Detailed line items
        line_items = cls.generate_line_items(old_comp, new_comp)

        # Deterministic ITR Recommendation
        itr_profile = ITRSelector.from_taxpayer_profile_input(profile)
        itr_rec = ITRSelector.recommend(itr_profile)
        itr_form = itr_rec.recommended_form.value

        # Narrative Summary
        if recommended == "NEW":
            if savings > 0:
                narrative = (
                    f"The New Tax Regime (Section 115BAC) is the optimal choice for AY {ay}, saving you ₹{savings:,.0f} "
                    f"per year (₹{monthly_diff:,.0f} more take-home per month) due to lower progressive tax slabs and an "
                    f"enhanced standard deduction of ₹75,000."
                )
            else:
                narrative = (
                    f"Both tax regimes yield zero tax liability for AY {ay}. The New Tax Regime is recommended "
                    f"as the statutory default regime."
                )
        else:
            narrative = (
                f"The Old Tax Regime is more beneficial for AY {ay}, saving you ₹{savings:,.0f} per year "
                f"(₹{monthly_diff:,.0f} more take-home per month) because your total claimed deductions of "
                f"₹{breakeven.current_claimed_deductions:,.0f} surpass the breakeven threshold of ₹{breakeven.breakeven_deduction_required:,.0f}."
            )

        return ComprehensiveComparisonResponse(
            assessment_year=ay,
            recommended_regime=recommended,
            tax_savings_amount=round(savings, 2),
            percentage_savings=round(pct_savings, 2),
            effective_tax_rate_old=old_comp.effective_tax_rate_percentage,
            effective_tax_rate_new=new_comp.effective_tax_rate_percentage,
            take_home_analysis=take_home,
            breakeven_analysis=breakeven,
            line_items=line_items,
            old_regime=old_comp,
            new_regime=new_comp,
            recommended_itr_form=itr_form,
            itr_recommendation=itr_rec,
            narrative_summary=narrative,
        )

