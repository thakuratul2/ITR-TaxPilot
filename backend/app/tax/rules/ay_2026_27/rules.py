"""Assessment Year 2026-27 (Financial Year 2025-26) tax rule implementation."""

from app.tax.rules.base import (
    BaseRuleSet,
    RebateRule,
    RuleMetadata,
    StandardDeductionRule,
    SurchargeRule,
    TaxRegime,
    TaxSlab,
)


class AY2026_27RuleSet(BaseRuleSet):
    """Implementation of tax rules for Assessment Year 2026-27 (FY 2025-26)."""

    def __init__(self):
        self.metadata = RuleMetadata(
            assessment_year="2026-27",
            rule_name="AY 2026-27 Tax Rules",
            rule_code="AY_2026_27",
            legal_source="Finance Act 2025, Income Tax Act 1961",
            effective_from="2025-04-01",
            effective_to="2026-03-31",
            last_amended="Budget 2025",
            notes="Standard deduction increased to ₹75,000. Revised rebate limits.",
        )
        self.tax_regimes = [TaxRegime.OLD, TaxRegime.NEW]

    def get_slabs(self, regime: TaxRegime) -> list[TaxSlab]:
        """Return tax slabs for the specified regime."""
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
        """Return standard deduction rule for the specified regime."""
        return StandardDeductionRule(
            amount=75000,  # Increased from ₹50,000
            applicable_regimes=[TaxRegime.OLD, TaxRegime.NEW],
        )

    def get_rebate_87a(self, regime: TaxRegime) -> RebateRule:
        """Return Section 87A rebate rule for the specified regime."""
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
        """Return surcharge rate configuration."""
        return [
            SurchargeRule(income_threshold=50000000, rate_percent=10),  # 50L - 1Cr
            SurchargeRule(income_threshold=100000000, rate_percent=15),  # 1Cr - 2Cr
            SurchargeRule(income_threshold=200000000, rate_percent=25),  # 2Cr - 5Cr
            SurchargeRule(income_threshold=500000000, rate_percent=37),  # Above 5Cr
        ]

    def get_cess_rate(self) -> float:
        """Return Health & Education Cess rate (typically 4%)."""
        return 4.0

    def is_deduction_eligible(self, section: str, regime: TaxRegime) -> bool:
        """Check if a deduction section is eligible under the specified regime."""
        # Deductions generally available under OLD regime
        old_regime_deductions = {
            "80C", "80CCC", "80CCD(1)", "80CCD(1B)", "80CCD(2)",
            "80D", "80E", "80G", "80TTA", "80TTB",
            "24(b)", "80EE", "80EEA", "80EEB",
        }

        # Limited deductions under NEW regime
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
