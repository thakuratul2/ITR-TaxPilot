"""Arithmetic relationship validator and zero vs unknown resolver."""


from app.ai.schemas import ExtractedForm16Data
from app.tax.validation.models import ValidationIssue, ValidationSeverity

ARITHMETIC_TOLERANCE_INR = 10.0


def check_arithmetic_consistency(extracted: ExtractedForm16Data) -> list[ValidationIssue]:
    """Verify internal mathematical consistency across Form 16 components."""
    issues: list[ValidationIssue] = []
    salary = extracted.salary
    deductions = extracted.deductions
    tax = extracted.tax

    # 1. Gross Salary Components vs Total Gross Salary
    sec17_sum = (
        (salary.gross_salary_sec_17_1 or 0.0)
        + (salary.perquisites_sec_17_2 or 0.0)
        + (salary.profits_in_lieu_sec_17_3 or 0.0)
    )
    if sec17_sum > 0 and abs(sec17_sum - salary.total_gross_salary) > ARITHMETIC_TOLERANCE_INR:
        issues.append(
            ValidationIssue(
                field="total_gross_salary",
                rule_code="ARITHMETIC_GROSS_SALARY_MISMATCH",
                message=(
                    f"Sum of Section 17 components (₹{sec17_sum:,.2f}) does not match "
                    f"reported Total Gross Salary (₹{salary.total_gross_salary:,.2f})."
                ),
                severity=ValidationSeverity.WARNING,
                actual_value=salary.total_gross_salary,
                expected_value=sec17_sum,
            )
        )

    # 2. Section 16 Deductions
    sec16_sum = (
        (salary.standard_deduction_sec_16_ia or 0.0)
        + (salary.entertainment_allowance_sec_16_ii or 0.0)
        + (salary.professional_tax_sec_16_iii or 0.0)
    )
    if salary.total_deductions_sec_16 is not None and abs(sec16_sum - salary.total_deductions_sec_16) > ARITHMETIC_TOLERANCE_INR:
        issues.append(
            ValidationIssue(
                field="total_deductions_sec_16",
                rule_code="ARITHMETIC_SEC16_DEDUCTIONS_MISMATCH",
                message=(
                    f"Sum of Section 16 deductions (₹{sec16_sum:,.2f}) does not match "
                    f"reported Total Section 16 Deductions (₹{salary.total_deductions_sec_16:,.2f})."
                ),
                severity=ValidationSeverity.WARNING,
                actual_value=salary.total_deductions_sec_16,
                expected_value=sec16_sum,
            )
        )

    # 3. Income Chargeable Under Salaries (Net Salary)
    total_sec16_ded = salary.total_deductions_sec_16 if salary.total_deductions_sec_16 is not None else sec16_sum
    expected_net_salary = max(0.0, salary.total_gross_salary - (salary.allowances_sec_10 or 0.0) - total_sec16_ded)

    if abs(expected_net_salary - salary.income_chargeable_salaries) > ARITHMETIC_TOLERANCE_INR:
        issues.append(
            ValidationIssue(
                field="income_chargeable_salaries",
                rule_code="ARITHMETIC_NET_SALARY_MISMATCH",
                message=(
                    f"Computed Net Salary (₹{expected_net_salary:,.2f}) differs from reported "
                    f"Income under Salaries (₹{salary.income_chargeable_salaries:,.2f})."
                ),
                severity=ValidationSeverity.WARNING,
                actual_value=salary.income_chargeable_salaries,
                expected_value=expected_net_salary,
            )
        )

    # 4. Chapter VI-A Total
    computed_via_total = (
        (deductions.section_80c or 0.0)
        + (deductions.section_80ccc or 0.0)
        + (deductions.section_80ccd_1 or 0.0)
        + (deductions.section_80ccd_1b or 0.0)
        + (deductions.section_80ccd_2 or 0.0)
        + (deductions.section_80d or 0.0)
        + (deductions.section_80e or 0.0)
        + (deductions.section_80g or 0.0)
        + (deductions.section_80tta or 0.0)
        + (deductions.section_80ttb or 0.0)
        + sum(deductions.other_deductions.values())
    )
    if deductions.total_chapter_via_deductions > 0 and abs(computed_via_total - deductions.total_chapter_via_deductions) > ARITHMETIC_TOLERANCE_INR:
        issues.append(
            ValidationIssue(
                field="total_chapter_via_deductions",
                rule_code="ARITHMETIC_CHAPTER_VIA_MISMATCH",
                message=(
                    f"Sum of Chapter VI-A deductions (₹{computed_via_total:,.2f}) does not match "
                    f"reported Total Chapter VI-A (₹{deductions.total_chapter_via_deductions:,.2f})."
                ),
                severity=ValidationSeverity.WARNING,
                actual_value=deductions.total_chapter_via_deductions,
                expected_value=computed_via_total,
            )
        )

    # 5. Total Taxable Income
    via_deduction_to_use = (
        deductions.total_chapter_via_deductions if deductions.total_chapter_via_deductions > 0 else computed_via_total
    )
    expected_taxable_income = max(0.0, salary.income_chargeable_salaries - via_deduction_to_use)

    if abs(expected_taxable_income - tax.total_taxable_income) > ARITHMETIC_TOLERANCE_INR:
        issues.append(
            ValidationIssue(
                field="total_taxable_income",
                rule_code="ARITHMETIC_TAXABLE_INCOME_MISMATCH",
                message=(
                    f"Computed Taxable Income (₹{expected_taxable_income:,.2f}) differs from reported "
                    f"Taxable Income (₹{tax.total_taxable_income:,.2f})."
                ),
                severity=ValidationSeverity.WARNING,
                actual_value=tax.total_taxable_income,
                expected_value=expected_taxable_income,
            )
        )

    return issues
