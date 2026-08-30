"""Validation and data normalization data models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """Represents a specific validation finding or mathematical discrepancy."""
    field: str = Field(..., description="Target field name")
    rule_code: str = Field(..., description="Machine-readable rule identifier")
    message: str = Field(..., description="Human-readable explanation of issue")
    severity: ValidationSeverity = Field(..., description="Severity level")
    actual_value: Any | None = Field(default=None, description="Extracted actual value")
    expected_value: Any | None = Field(default=None, description="Expected value if deterministically computed")


class NormalizedTaxpayerProfile(BaseModel):
    """Guaranteed clean, normalized data model consumed by deterministic calculation engine."""
    assessment_year: str = Field(..., description="Normalized Assessment Year (e.g. 2026-27)")
    financial_year: str = Field(..., description="Financial Year (e.g. 2025-26)")

    # Employer & Employee
    employer_name: str | None = None
    employer_tan: str | None = None
    employee_name: str | None = None
    employee_pan: str = Field(..., description="Validated 10-char PAN")

    # Salary components
    gross_salary_17_1: float = Field(default=0.0)
    perquisites_17_2: float = Field(default=0.0)
    profits_in_lieu_17_3: float = Field(default=0.0)
    total_gross_salary: float = Field(..., description="Total Gross Salary")

    # Section 10 Allowances
    exempt_allowances_sec_10: float = Field(default=0.0)
    allowances_itemized: dict[str, float] = Field(default_factory=dict)

    # Section 16 Deductions
    standard_deduction_16_ia: float = Field(default=0.0)
    entertainment_allowance_16_ii: float = Field(default=0.0)
    professional_tax_16_iii: float = Field(default=0.0)
    total_sec_16_deductions: float = Field(default=0.0)
    income_chargeable_salaries: float = Field(..., description="Net income under salaries")

    # Chapter VI-A Deductions
    deduction_80c: float = Field(default=0.0)
    deduction_80ccc: float = Field(default=0.0)
    deduction_80ccd_1: float = Field(default=0.0)
    deduction_80ccd_1b: float = Field(default=0.0)
    deduction_80ccd_2: float = Field(default=0.0)
    deduction_80d: float = Field(default=0.0)
    deduction_80e: float = Field(default=0.0)
    deduction_80g: float = Field(default=0.0)
    deduction_80tta: float = Field(default=0.0)
    deduction_80ttb: float = Field(default=0.0)
    other_chapter_via: dict[str, float] = Field(default_factory=dict)
    total_chapter_via_deductions: float = Field(default=0.0)

    # Tax summary
    total_taxable_income: float = Field(..., description="Reported total taxable income")
    reported_tax_payable: float | None = None
    total_tds_deducted: float = Field(..., description="Reconciled total TDS deducted")


class ValidationReport(BaseModel):
    """Complete validation evaluation and audit report."""
    is_valid: bool = Field(..., description="True if no blocking error severity issues")
    can_proceed: bool = Field(..., description="True if dataset has required data for tax calculation")
    issues: list[ValidationIssue] = Field(default_factory=list, description="All validation issues found")
    normalized_profile: NormalizedTaxpayerProfile | None = Field(default=None, description="Clean normalized profile")
    requires_user_review: bool = Field(default=False, description="True if low confidence or warnings exist")
    review_reasons: list[str] = Field(default_factory=list, description="Reasons requiring user confirmation")
