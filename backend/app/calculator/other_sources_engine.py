"""Income from Other Sources Sub-Engine (Section 56 & 57)."""

from app.calculator.models import OtherSourcesInput
from app.tax.rules.base import TaxRegime


class OtherSourcesEngine:
    """Deterministic Income from Other Sources calculation engine."""

    @classmethod
    def compute_other_sources_income(
        cls,
        os_input: OtherSourcesInput,
        regime: TaxRegime,
        assessment_year: str = "2026-27",
    ) -> dict[str, float]:
        """
        Compute total income from other sources, including Section 57(iia) family pension deduction.
        """
        # Family Pension Exemption u/s 57(iia)
        family_pension_raw = os_input.family_pension
        family_pension_deduction = 0.0
        
        if family_pension_raw > 0:
            one_third_pension = (1.0 / 3.0) * family_pension_raw
            # Standard deduction cap for family pension
            if regime == TaxRegime.NEW:
                # Under New Regime for AY 2025-26 and AY 2026-27, limit is ₹25,000
                cap = 25000.0
            else:
                # Under Old Regime, limit is ₹15,000
                cap = 15000.0
            family_pension_deduction = min(one_third_pension, cap)

        taxable_family_pension = max(0.0, family_pension_raw - family_pension_deduction)

        # Aggregate other sources
        total_other_sources = (
            os_input.savings_bank_interest
            + os_input.fixed_deposit_interest
            + os_input.dividend_income
            + taxable_family_pension
            + os_input.other_taxable_income
        )

        return {
            "savings_bank_interest": round(os_input.savings_bank_interest, 2),
            "fixed_deposit_interest": round(os_input.fixed_deposit_interest, 2),
            "dividend_income": round(os_input.dividend_income, 2),
            "gross_family_pension": round(family_pension_raw, 2),
            "family_pension_deduction_sec_57_iia": round(family_pension_deduction, 2),
            "net_family_pension": round(taxable_family_pension, 2),
            "other_taxable_income": round(os_input.other_taxable_income, 2),
            "total_other_sources_income": round(total_other_sources, 2),
        }
