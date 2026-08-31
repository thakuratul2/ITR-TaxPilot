"""Section 87A Rebate and Marginal Relief Sub-Engine."""

from app.tax.rules.base import TaxRegime


class RebateEngine:
    """Deterministic Section 87A Rebate & Section 87A Marginal Relief computation."""

    @classmethod
    def compute_rebate_and_marginal_relief(
        cls,
        taxable_income: float,
        base_tax: float,
        regime: TaxRegime,
        assessment_year: str = "2026-27",
    ) -> dict[str, float]:
        """
        Calculate Section 87A rebate and Section 87A Marginal Relief for New Regime.
        """
        rebate_claimed = 0.0
        marginal_relief = 0.0

        if regime == TaxRegime.OLD:
            # Old Regime: Rebate up to ₹12,500 if income <= ₹5,00,000
            if taxable_income <= 500000.0:
                rebate_claimed = min(base_tax, 12500.0)
            else:
                rebate_claimed = 0.0
            tax_after_87a = max(0.0, base_tax - rebate_claimed)

        else:
            # New Regime (Section 115BAC):
            # Threshold is ₹7,00,000 (Max rebate ₹25,000)
            threshold = 700000.0
            max_rebate = 25000.0

            if taxable_income <= threshold:
                rebate_claimed = min(base_tax, max_rebate)
                tax_after_87a = max(0.0, base_tax - rebate_claimed)
            else:
                # Income exceeds ₹7,00,000 - evaluate Section 87A Marginal Relief
                excess_income = taxable_income - threshold
                if base_tax > excess_income:
                    # Tax payable cannot exceed the income exceeding ₹7 Lakhs
                    marginal_relief = base_tax - excess_income
                    tax_after_87a = excess_income
                else:
                    marginal_relief = 0.0
                    tax_after_87a = base_tax

        return {
            "rebate_87a_claimed": round(rebate_claimed, 2),
            "marginal_relief_87a": round(marginal_relief, 2),
            "tax_after_87a": round(tax_after_87a, 2),
        }
