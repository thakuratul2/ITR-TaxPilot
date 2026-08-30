"""Versioned Assessment Year tax rule sets."""

from app.tax.rules.ay_2025_26 import AY2025_26RuleSet
from app.tax.rules.ay_2026_27 import AY2026_27RuleSet
from app.tax.rules.ay_2027_28 import AY2027_28RuleSet
from app.tax.rules.base import (
    RebateRule,
    RuleMetadata,
    RuleRegistry,
    StandardDeductionRule,
    SurchargeRule,
    TaxRegime,
    TaxSlab,
)
from app.tax.rules.deduction_catalog import (
    DeductionCatalog,
    DeductionInfo,
    deduction_catalog,
)

# Auto-register rule sets
_registry = RuleRegistry()
_registry.register("2025-26", AY2025_26RuleSet())
_registry.register("2026-27", AY2026_27RuleSet())
_registry.register("2027-28", AY2027_28RuleSet())

# Export registry instance
registry = _registry

__all__ = [
    "AY2025_26RuleSet",
    "AY2026_27RuleSet",
    "AY2027_28RuleSet",
    "RebateRule",
    "RuleMetadata",
    "RuleRegistry",
    "StandardDeductionRule",
    "SurchargeRule",
    "TaxRegime",
    "TaxSlab",
    "DeductionCatalog",
    "DeductionInfo",
    "deduction_catalog",
    "registry",
]
