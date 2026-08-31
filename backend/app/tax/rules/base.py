"""Base classes for modular Assessment Year tax rule engine."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class TaxRegime(str, Enum):
    """Tax regime identifier."""
    OLD = "OLD"
    NEW = "NEW"


@dataclass
class RuleMetadata:
    """Metadata for each tax rule for audit and traceability."""
    assessment_year: str
    rule_name: str
    rule_code: str
    legal_source: str  # e.g., "Finance Act 2024", "Section 87A"
    effective_from: str  # YYYY-MM-DD
    effective_to: str | None = None  # None if still effective
    last_amended: str = ""  # Budget notification if applicable
    notes: str = ""


@dataclass
class TaxSlab:
    """Individual tax slab with rate and limits."""
    lower_limit: float
    upper_limit: float | None  # None for highest slab
    rate_percent: float
    cess_percent: float = 4.0  # Default 4% Health & Education Cess


@dataclass
class RebateRule:
    """Section 87A rebate configuration."""
    max_taxable_income: float
    max_rebate_amount: float
    applicable_regimes: list[TaxRegime]


@dataclass
class StandardDeductionRule:
    """Standard deduction u/s 16(ia) configuration."""
    amount: float
    applicable_regimes: list[TaxRegime]


@dataclass
class SurchargeRule:
    """Surcharge rate configuration by income threshold."""
    income_threshold: float
    rate_percent: float
    marginal_relief: bool = False


class BaseRuleSet(ABC):
    """Abstract base class for Assessment Year rule sets."""

    metadata: RuleMetadata
    tax_regimes: list[TaxRegime]

    @abstractmethod
    def get_slabs(self, regime: TaxRegime) -> list[TaxSlab]:
        """Return tax slabs for the specified regime."""
        pass

    @abstractmethod
    def get_standard_deduction(self, regime: TaxRegime) -> StandardDeductionRule:
        """Return standard deduction rule for the specified regime."""
        pass

    @abstractmethod
    def get_rebate_87a(self, regime: TaxRegime) -> RebateRule:
        """Return Section 87A rebate rule for the specified regime."""
        pass

    @abstractmethod
    def get_surcharge_rates(self) -> list[SurchargeRule]:
        """Return surcharge rate configuration."""
        pass

    @abstractmethod
    def get_cess_rate(self) -> float:
        """Return Health & Education Cess rate (typically 4%)."""
        pass

    @abstractmethod
    def is_deduction_eligible(self, section: str, regime: TaxRegime) -> bool:
        """Check if a deduction section is eligible under the specified regime."""
        pass


class RuleRegistry:
    """Registry for managing Assessment Year rule sets."""

    _instance = None
    _rules: dict[str, BaseRuleSet] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, assessment_year: str, rule_set: BaseRuleSet) -> None:
        """Register a rule set for an Assessment Year."""
        self._rules[assessment_year] = rule_set

    def get_rule_set(self, assessment_year: str) -> BaseRuleSet | None:
        """Retrieve rule set for an Assessment Year."""
        return self._rules.get(assessment_year)

    def get(self, assessment_year: str) -> BaseRuleSet | None:
        """Alias for get_rule_set."""
        return self.get_rule_set(assessment_year)

    def list_registered_ays(self) -> list[str]:
        """List all registered Assessment Years."""
        return sorted(self._rules.keys())

    def is_ay_supported(self, assessment_year: str) -> bool:
        """Check if an Assessment Year is supported."""
        return assessment_year in self._rules


registry = RuleRegistry()
