"""Progressive Tax Slab Computation Sub-Engine."""

from app.calculator.models import SeniorCitizenCategory, SlabBracketDetail
from app.tax.rules import registry
from app.tax.rules.base import TaxRegime, TaxSlab


class SlabEngine:
    """Deterministic Progressive Slab Tax Calculator."""

    @classmethod
    def get_slabs(
        cls,
        regime: TaxRegime,
        assessment_year: str,
        category: SeniorCitizenCategory = SeniorCitizenCategory.INDIVIDUAL,
    ) -> list[TaxSlab]:
        """Fetch registered statutory tax slabs for the regime and assessment year."""
        rule_set = registry.get(assessment_year)
        slabs = rule_set.get_slabs(regime)

        # In Old Regime, adjust base exemption for Senior Citizens
        if regime == TaxRegime.OLD and category != SeniorCitizenCategory.INDIVIDUAL:
            if category == SeniorCitizenCategory.SENIOR_CITIZEN:
                # ₹3,00,000 basic exemption
                return [
                    TaxSlab(lower_limit=0.0, upper_limit=300000.0, rate_percent=0.0),
                    TaxSlab(lower_limit=300000.0, upper_limit=500000.0, rate_percent=5.0),
                    TaxSlab(lower_limit=500000.0, upper_limit=1000000.0, rate_percent=20.0),
                    TaxSlab(lower_limit=1000000.0, upper_limit=None, rate_percent=30.0),
                ]
            elif category == SeniorCitizenCategory.SUPER_SENIOR:
                # ₹5,00,000 basic exemption
                return [
                    TaxSlab(lower_limit=0.0, upper_limit=500000.0, rate_percent=0.0),
                    TaxSlab(lower_limit=500000.0, upper_limit=1000000.0, rate_percent=20.0),
                    TaxSlab(lower_limit=1000000.0, upper_limit=None, rate_percent=30.0),
                ]

        return slabs

    @classmethod
    def compute_slab_tax(
        cls,
        taxable_income: float,
        regime: TaxRegime,
        assessment_year: str = "2026-27",
        category: SeniorCitizenCategory = SeniorCitizenCategory.INDIVIDUAL,
    ) -> tuple[float, list[SlabBracketDetail]]:
        """
        Execute progressive slab tax calculation and produce bracket-by-bracket trace.
        """
        if taxable_income <= 0:
            return 0.0, []

        slabs = cls.get_slabs(regime, assessment_year, category)
        total_tax = 0.0
        details: list[SlabBracketDetail] = []

        for slab in slabs:
            min_inc = getattr(slab, "lower_limit", getattr(slab, "min_income", 0.0))
            max_inc = getattr(slab, "upper_limit", getattr(slab, "max_income", None))

            # Rate can be in percent (5.0) or fraction (0.05)
            if hasattr(slab, "rate_percent"):
                rate_pct = slab.rate_percent
                rate = rate_pct / 100.0
            else:
                rate = getattr(slab, "rate", 0.0)
                rate_pct = rate * 100.0 if rate <= 1.0 else rate
                if rate > 1.0:
                    rate = rate / 100.0

            if taxable_income <= min_inc:
                # Income does not reach this slab
                taxable_in_bracket = 0.0
                tax_in_bracket = 0.0
            elif max_inc is None or taxable_income > max_inc:
                # Income exceeds this bracket entirely
                taxable_in_bracket = (max_inc - min_inc) if max_inc is not None else (taxable_income - min_inc)
                tax_in_bracket = taxable_in_bracket * rate
            else:
                # Income falls within this bracket
                taxable_in_bracket = taxable_income - min_inc
                tax_in_bracket = taxable_in_bracket * rate

            total_tax += tax_in_bracket

            details.append(
                SlabBracketDetail(
                    bracket_min=min_inc,
                    bracket_max=max_inc,
                    rate_percentage=round(rate_pct, 2),
                    taxable_in_bracket=round(taxable_in_bracket, 2),
                    tax_amount=round(tax_in_bracket, 2),
                )
            )

        return round(total_tax, 2), details
