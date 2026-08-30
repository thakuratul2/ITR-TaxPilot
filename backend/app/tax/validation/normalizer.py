"""Data normalization and validation orchestrator."""

from app.ai.schemas import ExtractedForm16Data
from app.core.logging import get_logger
from app.tax.validation.arithmetic_checker import check_arithmetic_consistency
from app.tax.validation.confidence_filter import (
    evaluate_confidence_and_review_requirements,
)
from app.tax.validation.currency_validator import validate_currency_and_boundaries
from app.tax.validation.models import (
    NormalizedTaxpayerProfile,
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)
from app.tax.validation.pan_ay_validator import validate_pan_tan_ay
from app.tax.validation.reconciliation import (
    reconcile_part_a_and_part_b,
    resolve_duplicate_breakdown_items,
)

logger = get_logger("app.tax.validation.normalizer")


class DataNormalizationService:
    """Service to validate extracted Form 16 data and build a normalized taxpayer calculation profile."""

    @staticmethod
    def validate_and_normalize(
        extracted: ExtractedForm16Data,
        part_a_tds_total: float | None = None,
    ) -> ValidationReport:
        """Run all validation suites and produce a normalized data profile."""
        issues: list[ValidationIssue] = []

        # 1. PAN, TAN, and AY validation
        pan_issues = validate_pan_tan_ay(
            pan=extracted.employee.pan,
            tan=extracted.employer.tan,
            assessment_year=extracted.assessment_year,
            financial_year=extracted.financial_year,
        )
        issues.extend(pan_issues)

        # 2. Currency and statutory boundary checks
        currency_issues = validate_currency_and_boundaries(extracted)
        issues.extend(currency_issues)

        # 3. Part A vs Part B reconciliation
        reconcile_issues = reconcile_part_a_and_part_b(extracted, part_a_tds_total)
        issues.extend(reconcile_issues)

        # 4. Duplicate line resolution for allowances and deductions
        cleaned_allowances, dup_allowance_issues = resolve_duplicate_breakdown_items(
            extracted.salary.allowances_breakdown
        )
        issues.extend(dup_allowance_issues)

        cleaned_other_deductions, dup_ded_issues = resolve_duplicate_breakdown_items(
            extracted.deductions.other_deductions
        )
        issues.extend(dup_ded_issues)

        # 5. Arithmetic checks
        arithmetic_issues = check_arithmetic_consistency(extracted)
        issues.extend(arithmetic_issues)

        # Check for blocking errors
        has_errors = any(i.severity == ValidationSeverity.ERROR for i in issues)
        is_valid = not has_errors
        can_proceed = is_valid and (extracted.salary.total_gross_salary >= 0)

        # 6. Evaluate confidence and review requirements
        requires_review, review_reasons = evaluate_confidence_and_review_requirements(extracted, issues)

        # Build clean NormalizedTaxpayerProfile if can proceed
        normalized_profile = None
        if can_proceed:
            salary = extracted.salary
            deductions = extracted.deductions
            tax = extracted.tax

            total_sec16 = salary.total_deductions_sec_16 or (
                (salary.standard_deduction_sec_16_ia or 0.0)
                + (salary.entertainment_allowance_sec_16_ii or 0.0)
                + (salary.professional_tax_sec_16_iii or 0.0)
            )

            # Reconciled total deductions under Chapter VI-A
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
                + sum(cleaned_other_deductions.values())
            )
            final_via_deductions = (
                deductions.total_chapter_via_deductions
                if deductions.total_chapter_via_deductions > 0
                else computed_via_total
            )

            normalized_profile = NormalizedTaxpayerProfile(
                assessment_year=extracted.assessment_year,
                financial_year=extracted.financial_year or "2025-26",
                employer_name=extracted.employer.name,
                employer_tan=extracted.employer.tan,
                employee_name=extracted.employee.name,
                employee_pan=extracted.employee.pan or "UNKNOWN",
                gross_salary_17_1=salary.gross_salary_sec_17_1 or salary.total_gross_salary,
                perquisites_17_2=salary.perquisites_sec_17_2 or 0.0,
                profits_in_lieu_17_3=salary.profits_in_lieu_sec_17_3 or 0.0,
                total_gross_salary=salary.total_gross_salary,
                exempt_allowances_sec_10=salary.allowances_sec_10 or 0.0,
                allowances_itemized=cleaned_allowances,
                standard_deduction_16_ia=salary.standard_deduction_sec_16_ia or 0.0,
                entertainment_allowance_16_ii=salary.entertainment_allowance_sec_16_ii or 0.0,
                professional_tax_16_iii=salary.professional_tax_sec_16_iii or 0.0,
                total_sec_16_deductions=total_sec16,
                income_chargeable_salaries=salary.income_chargeable_salaries,
                deduction_80c=deductions.section_80c or 0.0,
                deduction_80ccc=deductions.section_80ccc or 0.0,
                deduction_80ccd_1=deductions.section_80ccd_1 or 0.0,
                deduction_80ccd_1b=deductions.section_80ccd_1b or 0.0,
                deduction_80ccd_2=deductions.section_80ccd_2 or 0.0,
                deduction_80d=deductions.section_80d or 0.0,
                deduction_80e=deductions.section_80e or 0.0,
                deduction_80g=deductions.section_80g or 0.0,
                deduction_80tta=deductions.section_80tta or 0.0,
                deduction_80ttb=deductions.section_80ttb or 0.0,
                other_chapter_via=cleaned_other_deductions,
                total_chapter_via_deductions=final_via_deductions,
                total_taxable_income=tax.total_taxable_income,
                reported_tax_payable=tax.total_tax_payable,
                total_tds_deducted=tax.total_tds_deducted,
            )

        logger.info(
            "Validation & normalization complete: is_valid=%s, issues=%d, requires_review=%s",
            is_valid,
            len(issues),
            requires_review,
        )

        return ValidationReport(
            is_valid=is_valid,
            can_proceed=can_proceed,
            issues=issues,
            normalized_profile=normalized_profile,
            requires_user_review=requires_review,
            review_reasons=review_reasons,
        )
