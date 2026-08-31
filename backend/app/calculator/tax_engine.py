"""Master Deterministic Tax Computation Engine."""

from app.calculator.deduction_engine import DeductionEngine
from app.calculator.house_property_engine import HousePropertyEngine
from app.calculator.interest_engine import InterestEngine
from app.calculator.models import (
    RegimeComparisonResult,
    RegimeComputation,
    TaxpayerProfileInput,
)
from app.calculator.other_sources_engine import OtherSourcesEngine
from app.calculator.rebate_engine import RebateEngine
from app.calculator.regime_comparator import RegimeComparator
from app.calculator.salary_engine import SalaryEngine
from app.calculator.slab_engine import SlabEngine
from app.calculator.surcharge_engine import SurchargeEngine
from app.tax.rules.base import TaxRegime


class TaxEngine:
    """Master Deterministic Tax Calculator Facade."""

    @classmethod
    def compute_regime(
        cls,
        profile: TaxpayerProfileInput,
        regime: TaxRegime,
    ) -> RegimeComputation:
        """
        Execute end-to-end tax computation for a specific regime.
        """
        ay = profile.assessment_year
        category = profile.taxpayer_category

        # 1. Salary Income Head
        sal_res = SalaryEngine.compute_salary_income(profile.salary, regime, ay)
        net_sal = sal_res["net_salary_income"]

        # 2. House Property Income Head
        hp_res = HousePropertyEngine.compute_house_property_income(profile.house_property, regime)
        net_hp = hp_res["net_house_property_income"]

        # 3. Other Sources Income Head
        os_res = OtherSourcesEngine.compute_other_sources_income(profile.other_sources, regime, ay)
        net_os = os_res["total_other_sources_income"]

        # 4. Gross Total Income (GTI)
        gti = max(0.0, net_sal + net_hp + net_os)

        # 5. Chapter VI-A Deductions
        ch_res = DeductionEngine.compute_chapter_via_deductions(
            profile.chapter_vi_a, profile.other_sources, gti, regime, category
        )
        total_deductions = ch_res["total_deductions"]

        # 6. Total Taxable Income (Rounded to nearest ₹10 per Section 288A)
        raw_taxable = max(0.0, gti - total_deductions)
        total_taxable_income = RegimeComparator.round_to_nearest_10(raw_taxable)

        # 7. Progressive Slab Computation
        base_tax, slab_details = SlabEngine.compute_slab_tax(
            total_taxable_income, regime, ay, category
        )

        # 8. Section 87A Rebate & Section 87A Marginal Relief
        rebate_res = RebateEngine.compute_rebate_and_marginal_relief(
            total_taxable_income, base_tax, regime, ay
        )
        rebate_claimed = rebate_res["rebate_87a_claimed"]
        marginal_relief_87a = rebate_res["marginal_relief_87a"]
        tax_after_87a = rebate_res["tax_after_87a"]

        # 9. Surcharge & Surcharge Marginal Relief
        sur_res = SurchargeEngine.compute_surcharge_and_marginal_relief(
            total_taxable_income, tax_after_87a, regime, ay, category
        )
        net_surcharge = sur_res["net_surcharge"]

        # 10. Health & Education Cess (4% on Tax + Surcharge)
        tax_plus_surcharge = tax_after_87a + net_surcharge
        cess_amount = round(0.04 * tax_plus_surcharge, 2)
        total_tax_and_cess = tax_plus_surcharge + cess_amount

        # 11. Section 89 Relief
        relief_89 = min(total_tax_and_cess, profile.relief_sec_89)
        net_tax_liability = max(0.0, total_tax_and_cess - relief_89)

        # 12. Advance Tax & Section 234A/B/C Interest
        int_res = InterestEngine.compute_interest_234abc(
            total_tax_and_cess, relief_89, profile.advance_tax, ay
        )
        total_interest = int_res["total_interest_234"]

        # 13. Aggregate Liability & Section 288B Rounding
        gross_liability = net_tax_liability + total_interest
        aggregate_liability = RegimeComparator.round_to_nearest_10(gross_liability)

        # 14. Prepaid Taxes & Balance Refund/Payable
        total_prepaid = (
            profile.advance_tax.total_tds_tcs_deducted
            + profile.advance_tax.self_assessment_tax_paid
            + max(
                profile.advance_tax.advance_tax_paid_q4_mar15,
                profile.advance_tax.advance_tax_paid_mar31,
            )
        )
        net_payable_or_refund = RegimeComparator.round_to_nearest_10(aggregate_liability - total_prepaid)

        effective_rate = (
            round((aggregate_liability / gti * 100.0), 2) if gti > 0 else 0.0
        )

        return RegimeComputation(
            regime_name=regime.value,
            assessment_year=ay,
            gross_salary=sal_res["gross_salary"],
            exempt_allowances_sec_10=sal_res["exempt_allowances_sec_10"],
            standard_deduction_sec_16_ia=sal_res["standard_deduction_sec_16_ia"],
            professional_tax_sec_16_iii=sal_res["professional_tax_sec_16_iii"],
            entertainment_allowance_sec_16_ii=sal_res["entertainment_allowance_sec_16_ii"],
            net_salary_income=net_sal,
            income_or_loss_house_property=net_hp,
            income_other_sources=net_os,
            gross_total_income=round(gti, 2),
            total_chapter_via_deductions=round(total_deductions, 2),
            itemized_chapter_via=ch_res["itemized"],
            total_taxable_income=total_taxable_income,
            slab_breakdown=slab_details,
            base_tax_on_income=base_tax,
            rebate_87a_claimed=rebate_claimed,
            marginal_relief_87a=marginal_relief_87a,
            tax_after_87a=tax_after_87a,
            surcharge_rate_percentage=sur_res["surcharge_rate_percentage"],
            gross_surcharge=sur_res["gross_surcharge"],
            surcharge_marginal_relief=sur_res["surcharge_marginal_relief"],
            net_surcharge=net_surcharge,
            cess_amount=cess_amount,
            total_tax_and_cess=round(total_tax_and_cess, 2),
            relief_sec_89=round(relief_89, 2),
            net_tax_liability=round(net_tax_liability, 2),
            interest_234a=int_res["interest_234a"],
            interest_234b=int_res["interest_234b"],
            interest_234c=int_res["interest_234c"],
            total_interest_234=total_interest,
            aggregate_liability=aggregate_liability,
            total_prepaid_taxes=round(total_prepaid, 2),
            net_payable_or_refund=net_payable_or_refund,
            effective_tax_rate_percentage=effective_rate,
        )

    @classmethod
    def calculate_all(cls, profile: TaxpayerProfileInput) -> RegimeComparisonResult:
        """
        Compute Old and New Tax Regimes side-by-side and return optimal comparison result.
        """
        old_comp = cls.compute_regime(profile, TaxRegime.OLD)
        new_comp = cls.compute_regime(profile, TaxRegime.NEW)
        return RegimeComparator.compare(old_comp, new_comp, profile)
