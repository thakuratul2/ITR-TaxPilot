"""Non-negative currency and financial boundaries validation."""


from app.ai.schemas import ExtractedForm16Data
from app.tax.validation.models import ValidationIssue, ValidationSeverity


def validate_currency_and_boundaries(extracted: ExtractedForm16Data) -> list[ValidationIssue]:
    """Validate that numeric amounts are non-negative and within reasonable statutory limits."""
    issues: list[ValidationIssue] = []

    # 1. Total Gross Salary checks
    salary = extracted.salary
    if salary.total_gross_salary < 0:
        issues.append(
            ValidationIssue(
                field="total_gross_salary",
                rule_code="CURRENCY_NEGATIVE_GROSS_SALARY",
                message="Gross salary cannot be a negative value.",
                severity=ValidationSeverity.ERROR,
                actual_value=salary.total_gross_salary,
            )
        )

    # 2. Section 16 Standard Deduction
    std_ded = salary.standard_deduction_sec_16_ia
    if std_ded is not None:
        if std_ded < 0:
            issues.append(
                ValidationIssue(
                    field="standard_deduction_sec_16_ia",
                    rule_code="CURRENCY_NEGATIVE_STANDARD_DEDUCTION",
                    message="Standard deduction cannot be negative.",
                    severity=ValidationSeverity.ERROR,
                    actual_value=std_ded,
                )
            )
        elif std_ded > 75000:
            issues.append(
                ValidationIssue(
                    field="standard_deduction_sec_16_ia",
                    rule_code="CURRENCY_STANDARD_DEDUCTION_EXCEEDS_STATUTORY_MAX",
                    message=f"Standard deduction ₹{std_ded:,.2f} exceeds statutory maximum ₹75,000.",
                    severity=ValidationSeverity.WARNING,
                    actual_value=std_ded,
                    expected_value=75000.0,
                )
            )

    # 3. Professional Tax
    pt = salary.professional_tax_sec_16_iii or 0.0
    if pt < 0:
        issues.append(
            ValidationIssue(
                field="professional_tax_sec_16_iii",
                rule_code="CURRENCY_NEGATIVE_PROFESSIONAL_TAX",
                message="Professional tax cannot be negative.",
                severity=ValidationSeverity.ERROR,
                actual_value=pt,
            )
        )
    elif pt > 2500:
        issues.append(
            ValidationIssue(
                field="professional_tax_sec_16_iii",
                rule_code="CURRENCY_PROFESSIONAL_TAX_EXCEEDS_CAP",
                message=f"Professional tax ₹{pt:,.2f} exceeds annual statutory limit of ₹2,500.",
                severity=ValidationSeverity.WARNING,
                actual_value=pt,
                expected_value=2500.0,
            )
        )

    # 4. Chapter VI-A Deductions
    deductions = extracted.deductions
    for field_name, amount in [
        ("section_80c", deductions.section_80c),
        ("section_80ccc", deductions.section_80ccc),
        ("section_80ccd_1", deductions.section_80ccd_1),
        ("section_80ccd_1b", deductions.section_80ccd_1b),
        ("section_80ccd_2", deductions.section_80ccd_2),
        ("section_80d", deductions.section_80d),
        ("section_80e", deductions.section_80e),
        ("section_80g", deductions.section_80g),
        ("section_80tta", deductions.section_80tta),
        ("section_80ttb", deductions.section_80ttb),
    ]:
        val = amount or 0.0
        if val < 0:
            issues.append(
                ValidationIssue(
                    field=field_name,
                    rule_code=f"CURRENCY_NEGATIVE_{field_name.upper()}",
                    message=f"Deduction under {field_name} cannot be negative.",
                    severity=ValidationSeverity.ERROR,
                    actual_value=val,
                )
            )

    # 5. Tax Payable and TDS checks
    tax = extracted.tax
    if tax.total_tds_deducted < 0:
        issues.append(
            ValidationIssue(
                field="total_tds_deducted",
                rule_code="CURRENCY_NEGATIVE_TDS",
                message="Total TDS deducted cannot be negative.",
                severity=ValidationSeverity.ERROR,
                actual_value=tax.total_tds_deducted,
            )
        )

    return issues
