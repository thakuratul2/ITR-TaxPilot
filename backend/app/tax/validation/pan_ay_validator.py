"""PAN, TAN, and Assessment Year syntax and semantic validator."""

import re

from app.tax.validation.models import ValidationIssue, ValidationSeverity

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
TAN_REGEX = re.compile(r"^[A-Z]{4}[0-9]{5}[A-Z]$")
AY_REGEX = re.compile(r"^(202[0-9])-([0-9]{2})$")


def validate_pan_tan_ay(
    pan: str | None,
    tan: str | None,
    assessment_year: str | None,
    financial_year: str | None,
) -> list[ValidationIssue]:
    """Validate format and semantic logic of identification markers and assessment years."""
    issues: list[ValidationIssue] = []

    # 1. PAN validation
    if not pan:
        issues.append(
            ValidationIssue(
                field="employee_pan",
                rule_code="PAN_MISSING",
                message="Employee PAN is mandatory for ITR tax calculation.",
                severity=ValidationSeverity.ERROR,
            )
        )
    elif not PAN_REGEX.match(pan):
        issues.append(
            ValidationIssue(
                field="employee_pan",
                rule_code="PAN_INVALID_FORMAT",
                message=f"Invalid PAN format: '{pan}'. Expected 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F).",
                severity=ValidationSeverity.ERROR,
                actual_value=pan,
            )
        )
    else:
        # Check entity type (4th character)
        pan_type = pan[3]
        if pan_type not in ("P", "H", "C", "F", "A", "T", "B", "L", "J", "G"):
            issues.append(
                ValidationIssue(
                    field="employee_pan",
                    rule_code="PAN_UNKNOWN_ENTITY_TYPE",
                    message=f"PAN 4th character '{pan_type}' represents an unusual entity type.",
                    severity=ValidationSeverity.WARNING,
                    actual_value=pan,
                )
            )

    # 2. TAN validation
    if tan and not TAN_REGEX.match(tan):
        issues.append(
            ValidationIssue(
                field="employer_tan",
                rule_code="TAN_INVALID_FORMAT",
                message=f"Invalid TAN format: '{tan}'. Expected 4 letters, 5 digits, 1 letter (e.g., DELA12345B).",
                severity=ValidationSeverity.WARNING,
                actual_value=tan,
            )
        )

    # 3. Assessment Year validation
    if not assessment_year:
        issues.append(
            ValidationIssue(
                field="assessment_year",
                rule_code="AY_MISSING",
                message="Assessment Year is mandatory.",
                severity=ValidationSeverity.ERROR,
            )
        )
    else:
        ay_match = AY_REGEX.match(assessment_year)
        if not ay_match:
            issues.append(
                ValidationIssue(
                    field="assessment_year",
                    rule_code="AY_INVALID_FORMAT",
                    message=f"Invalid Assessment Year format '{assessment_year}'. Expected YYYY-YY (e.g., 2026-27).",
                    severity=ValidationSeverity.ERROR,
                    actual_value=assessment_year,
                )
            )
        else:
            start_yr = int(ay_match.group(1))
            end_short = int(ay_match.group(2))
            expected_end_short = (start_yr + 1) % 100
            if end_short != expected_end_short:
                issues.append(
                    ValidationIssue(
                        field="assessment_year",
                        rule_code="AY_YEAR_MISMATCH",
                        message=f"Assessment Year range '{assessment_year}' is non-consecutive.",
                        severity=ValidationSeverity.ERROR,
                        actual_value=assessment_year,
                        expected_value=f"{start_yr}-{expected_end_short:02d}",
                    )
                )

    # 4. Financial Year vs Assessment Year alignment
    if assessment_year and financial_year and AY_REGEX.match(assessment_year) and AY_REGEX.match(financial_year):
        ay_start = int(assessment_year.split("-")[0])
        fy_start = int(financial_year.split("-")[0])
        if ay_start != fy_start + 1:
            issues.append(
                ValidationIssue(
                    field="financial_year",
                    rule_code="FY_AY_MISMATCH",
                    message=f"Financial Year {financial_year} does not precede Assessment Year {assessment_year}.",
                    severity=ValidationSeverity.WARNING,
                    actual_value=financial_year,
                    expected_value=f"{ay_start - 1}-{(ay_start) % 100:02d}",
                )
            )

    return issues
