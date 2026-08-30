"""Field-level and overall confidence score computation for Form 16 extractions."""

import re

from app.ai.schemas import ExtractedForm16Data

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
TAN_REGEX = re.compile(r"^[A-Z]{4}[0-9]{5}[A-Z]$")
AY_REGEX = re.compile(r"^202[0-9]-[0-9]{2}$")


def calculate_field_confidence_scores(extracted: ExtractedForm16Data) -> dict[str, float]:
    """Compute confidence scores (0.0 to 1.0) for extracted fields based on formatting and math consistency."""
    scores: dict[str, float] = {}

    # 1. Assessment Year
    if extracted.assessment_year and AY_REGEX.match(extracted.assessment_year):
        scores["assessment_year"] = 1.0
    elif extracted.assessment_year:
        scores["assessment_year"] = 0.7
    else:
        scores["assessment_year"] = 0.0

    # 2. Employee PAN
    emp_pan = extracted.employee.pan
    if emp_pan and PAN_REGEX.match(emp_pan):
        scores["employee_pan"] = 1.0
    elif emp_pan:
        scores["employee_pan"] = 0.5
    else:
        scores["employee_pan"] = 0.0

    # 3. Employer TAN
    emp_tan = extracted.employer.tan
    if emp_tan and TAN_REGEX.match(emp_tan):
        scores["employer_tan"] = 1.0
    elif emp_tan:
        scores["employer_tan"] = 0.5
    else:
        scores["employer_tan"] = 0.0

    # 4. Salary breakdown arithmetic consistency
    salary = extracted.salary
    calculated_gross = (
        (salary.gross_salary_sec_17_1 or 0.0)
        + (salary.perquisites_sec_17_2 or 0.0)
        + (salary.profits_in_lieu_sec_17_3 or 0.0)
    )

    if calculated_gross > 0 and abs(calculated_gross - salary.total_gross_salary) <= 1.0:
        scores["total_gross_salary"] = 1.0
    elif salary.total_gross_salary > 0:
        scores["total_gross_salary"] = 0.9
    else:
        scores["total_gross_salary"] = 0.3

    # 5. Net Salary consistency
    total_sec16 = salary.total_deductions_sec_16 or (
        (salary.standard_deduction_sec_16_ia or 0.0)
        + (salary.entertainment_allowance_sec_16_ii or 0.0)
        + (salary.professional_tax_sec_16_iii or 0.0)
    )
    expected_net_salary = salary.total_gross_salary - (salary.allowances_sec_10 or 0.0) - total_sec16

    if abs(expected_net_salary - salary.income_chargeable_salaries) <= 10.0:
        scores["income_chargeable_salaries"] = 1.0
    else:
        scores["income_chargeable_salaries"] = 0.8

    # 6. Chapter VI-A & Total Taxable Income consistency
    deductions = extracted.deductions
    tax = extracted.tax
    expected_taxable = max(0.0, salary.income_chargeable_salaries - deductions.total_chapter_via_deductions)

    if abs(expected_taxable - tax.total_taxable_income) <= 10.0:
        scores["total_taxable_income"] = 1.0
    else:
        scores["total_taxable_income"] = 0.85

    # 7. Total TDS
    scores["total_tds_deducted"] = 1.0 if tax.total_tds_deducted >= 0.0 else 0.0

    # Overall weighted average
    overall = sum(scores.values()) / max(1, len(scores))
    scores["overall"] = round(overall, 2)

    return scores
