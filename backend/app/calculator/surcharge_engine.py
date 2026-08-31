"""Surcharge and Surcharge Marginal Relief Sub-Engine."""

from app.calculator.models import SeniorCitizenCategory
from app.calculator.slab_engine import SlabEngine
from app.tax.rules.base import TaxRegime


class SurchargeEngine:
    """Deterministic Surcharge & Marginal Relief Calculator."""

    @staticmethod
    def get_surcharge_rate(taxable_income: float, regime: TaxRegime) -> float:
        """Determine statutory surcharge percentage."""
        if taxable_income <= 5000000.0:
            return 0.0
        elif taxable_income <= 10000000.0:
            return 0.10
        elif taxable_income <= 20000000.0:
            return 0.15
        elif taxable_income <= 50000000.0:
            return 0.25
        else:
            # Above ₹5 Crores: 25% in New Regime, 37% in Old Regime
            return 0.25 if regime == TaxRegime.NEW else 0.37

    @classmethod
    def compute_surcharge_and_marginal_relief(
        cls,
        taxable_income: float,
        tax_after_87a: float,
        regime: TaxRegime,
        assessment_year: str = "2026-27",
        category: SeniorCitizenCategory = SeniorCitizenCategory.INDIVIDUAL,
    ) -> dict[str, float]:
        """
        Calculate gross surcharge, evaluate marginal relief at threshold transitions, and return net surcharge.
        """
        rate = cls.get_surcharge_rate(taxable_income, regime)
        if rate == 0.0 or tax_after_87a == 0.0:
            return {
                "surcharge_rate_percentage": 0.0,
                "gross_surcharge": 0.0,
                "surcharge_marginal_relief": 0.0,
                "net_surcharge": 0.0,
            }

        gross_surcharge = tax_after_87a * rate
        marginal_relief = 0.0

        # Determine the immediate lower threshold
        thresholds = [5000000.0, 10000000.0, 20000000.0, 50000000.0]
        active_threshold = 0.0
        for t in reversed(thresholds):
            if taxable_income > t:
                active_threshold = t
                break

        if active_threshold > 0:
            # 1. Compute tax + surcharge at the threshold boundary
            threshold_base_tax, _ = SlabEngine.compute_slab_tax(
                active_threshold, regime, assessment_year, category
            )
            threshold_surcharge_rate = cls.get_surcharge_rate(active_threshold, regime)
            threshold_total = threshold_base_tax + (threshold_base_tax * threshold_surcharge_rate)

            # 2. Maximum allowable tax + surcharge at current income
            excess_income = taxable_income - active_threshold
            max_allowable_total = threshold_total + excess_income

            # 3. Current total (tax + gross surcharge)
            current_total = tax_after_87a + gross_surcharge

            if current_total > max_allowable_total:
                marginal_relief = current_total - max_allowable_total

        net_surcharge = max(0.0, gross_surcharge - marginal_relief)

        return {
            "surcharge_rate_percentage": round(rate * 100, 2),
            "gross_surcharge": round(gross_surcharge, 2),
            "surcharge_marginal_relief": round(marginal_relief, 2),
            "net_surcharge": round(net_surcharge, 2),
        }
