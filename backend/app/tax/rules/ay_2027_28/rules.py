"""Assessment Year 2027-28 (Financial Year 2026-27) tax rule template for future implementation."""

from app.tax.rules.base import (
    BaseRuleSet,
    RebateRule,
    RuleMetadata,
    StandardDeductionRule,
    SurchargeRule,
    TaxRegime,
    TaxSlab,
)


class AY2027_28RuleSet(BaseRuleSet):
    """Template implementation for Assessment Year 2027-28 (FY 2026-27).

    NOTE: This is a placeholder structure for future AY implementation.
    Actual rules should be updated based on Finance Act 2026 amendments.
    """

    def __init__(self):
        self.metadata = RuleMetadata(
            assessment_year="2027-28",
            rule_name="AY 2027-28 Tax Rules (Template)",
            rule_code="AY_2027_28",
            legal_source="Finance Act 2026 (Pending), Income Tax Act 1961",
            effective_from="2026-04-01",
            effective_to="2027-03-31",
            last_amended="Pending Budget 2026",
            notes="Template structure for future implementation. Update with actual rules.",
        )
        self.tax_regimes = [TaxRegime.OLD, TaxRegime.NEW]

    def get_slabs(self, regime: TaxRegime) -> list[TaxSlab]:
        """Return tax slabs for the specified regime.

        NOTE: These are placeholder values from AY 2026-27.
        Update with actual Finance Act 2026 amendments.
        """
        if regime == TaxRegime.OLD:
            return [
                TaxSlab(lower_limit=0, upper_limit=250000, rate_percent=0),
                TaxSlab(lower_limit=250000, upper_limit=500000, rate_percent=5),
                TaxSlab(lower_limit=500000, upper_limit=1000000, rate_percent=20),
                TaxSlab(lower_limit=1000000, upper_limit=None, rate_percent=30),
            ]
        elif regime == TaxRegime.NEW:
            return [
                TaxSlab(lower_limit=0, upper_limit=300000, rate_percent=0),
                TaxSlab(lower_limit=300000, upper_limit=700000, rate_percent=5),
                TaxSlab(lower_limit=700000, upper_limit=1000000, rate_percent=10),
                TaxSlab(lower_limit=1000000, upper_limit=1200000, rate_percent=15),
                TaxSlab(lower_limit=1200000, upper_limit=1500000, rate_percent=20),
                TaxSlab(lower_limit=1500000, upper_limit=None, rate_percent=30),
            ]
        else:
            raise ValueError(f"Unknown regime: {regime}")

    def get_standard_deduction(self, _regime: TaxRegime) -> StandardDeductionRule:
        """Return standard deduction rule for the specified regime.

        NOTE: This is a placeholder value from AY 2026-27.
        Update with actual Finance Act 2026 amendments.
        """
        return StandardDeductionRule(
            amount=75000,  # Placeholder - update based on actual amendments
            applicable_regimes=[TaxRegime.OLD, TaxRegime.NEW],
        )

    def get_rebate_87a(self, regime: TaxRegime) -> RebateRule:
        """Return Section 87A rebate rule for the specified regime.

        NOTE: These are placeholder values from AY 2026-27.
        Update with actual Finance Act 2026 amendments.
        """
        if regime == TaxRegime.OLD:
            return RebateRule(
                max_taxable_income=500000,
                max_rebate_amount=12500,
                applicable_regimes=[TaxRegime.OLD],
            )
        elif regime == TaxRegime.NEW:
            return RebateRule(
                max_taxable_income=700000,
                max_rebate_amount=25000,
                applicable_regimes=[TaxRegime.NEW],
            )
        else:
            raise ValueError(f"Unknown regime: {regime}")

    def get_surcharge_rates(self) -> list[SurchargeRule]:
        """Return surcharge rate configuration.

        NOTE: These are placeholder values from AY 2026-27.
        Update with actual Finance Act 2026 amendments.
        """
        return [
            SurchargeRule(income_threshold=50000000, rate_percent=10),
            SurchargeRule(income_threshold=100000000, rate_percent=15),
            SurchargeRule(income_threshold=200000000, rate_percent=25),
            SurchargeRule(income_threshold=500000000, rate_percent=37),
        ]

    def get_cess_rate(self) -> float:
        """Return Health & Education Cess rate (typically 4%)."""
        return 4.0

    def is_deduction_eligible(self, section: str, regime: TaxRegime) -> bool:
        """Check if a deduction section is eligible under the specified regime.

        NOTE: These are placeholder values from AY 2026-27.
        Update with actual Finance Act 2026 amendments.
        """
        old_regime_deductions = {
            "80C", "80CCC", "80CCD(1)", "80CCD(1B)", "80CCD(2)",
            "80D", "80E", "80G", "80TTA", "80TTB",
            "24(b)", "80EE", "80EEA", "80EEB",
        }

        new_regime_deductions = {
            "80CCD(2)",  # Employer NPS contribution
            "44AA", "44ADA",  # Presumptive taxation
        }

        if regime == TaxRegime.OLD:
            return section in old_regime_deductions
        elif regime == TaxRegime.NEW:
            return section in new_regime_deductions
        else:
            raise ValueError(f"Unknown regime: {regime}")
