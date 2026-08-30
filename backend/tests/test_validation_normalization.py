"""Comprehensive unit tests for Milestone 5 Validation & Data Normalization."""

from app.ai.schemas import (
    ExtractedChapterVIA,
    ExtractedEmployee,
    ExtractedEmployer,
    ExtractedForm16Data,
    ExtractedSalaryBreakdown,
    ExtractedTaxSummary,
)
from app.tax.validation.arithmetic_checker import check_arithmetic_consistency
from app.tax.validation.currency_validator import validate_currency_and_boundaries
from app.tax.validation.models import ValidationSeverity
from app.tax.validation.normalizer import DataNormalizationService
from app.tax.validation.pan_ay_validator import validate_pan_tan_ay
from app.tax.validation.reconciliation import (
    reconcile_part_a_and_part_b,
    resolve_duplicate_breakdown_items,
)


def create_valid_form16_data() -> ExtractedForm16Data:
    """Fixture returning mathematically consistent Form 16 extraction."""
    return ExtractedForm16Data(
        assessment_year="2026-27",
        financial_year="2025-26",
        employer=ExtractedEmployer(name="Acme Corp", tan="DELA12345B"),
        employee=ExtractedEmployee(name="John Doe", pan="ABCDE1234F"),
        salary=ExtractedSalaryBreakdown(
            gross_salary_sec_17_1=1200000.0,
            perquisites_sec_17_2=0.0,
            profits_in_lieu_sec_17_3=0.0,
            total_gross_salary=1200000.0,
            allowances_sec_10=0.0,
            standard_deduction_sec_16_ia=75000.0,
            total_deductions_sec_16=75000.0,
            income_chargeable_salaries=1125000.0,
        ),
        deductions=ExtractedChapterVIA(
            section_80c=150000.0,
            section_80d=25000.0,
            total_chapter_via_deductions=175000.0,
        ),
        tax=ExtractedTaxSummary(
            total_taxable_income=950000.0,
            total_tds_deducted=67600.0,
            total_tax_payable=67600.0,
        ),
        confidence_scores={"overall": 0.98},
    )


def test_pan_tan_ay_validation_valid():
    """Test PAN, TAN, AY validation on valid inputs."""
    issues = validate_pan_tan_ay("ABCDE1234F", "DELA12345B", "2026-27", "2025-26")
    errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
    assert len(errors) == 0


def test_pan_validation_invalid_format():
    """Test invalid PAN raises ERROR issue."""
    issues = validate_pan_tan_ay("INVALIDPAN", "DELA12345B", "2026-27", "2025-26")
    errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
    assert len(errors) == 1
    assert errors[0].rule_code == "PAN_INVALID_FORMAT"


def test_ay_validation_non_consecutive():
    """Test non-consecutive Assessment Year is flagged as ERROR."""
    issues = validate_pan_tan_ay("ABCDE1234F", "DELA12345B", "2026-29", "2025-26")
    errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
    assert len(errors) == 1
    assert errors[0].rule_code == "AY_YEAR_MISMATCH"


def test_currency_negative_validation():
    """Test negative gross salary is rejected with ERROR."""
    data = create_valid_form16_data()
    data.salary.total_gross_salary = -50000.0
    issues = validate_currency_and_boundaries(data)
    errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
    assert len(errors) >= 1
    assert "CURRENCY_NEGATIVE" in errors[0].rule_code


def test_standard_deduction_boundary_warning():
    """Test standard deduction exceeding statutory max emits WARNING."""
    data = create_valid_form16_data()
    data.salary.standard_deduction_sec_16_ia = 90000.0
    issues = validate_currency_and_boundaries(data)
    warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
    assert len(warnings) >= 1
    assert warnings[0].rule_code == "CURRENCY_STANDARD_DEDUCTION_EXCEEDS_STATUTORY_MAX"


def test_part_a_part_b_tds_reconciliation():
    """Test mismatch between Part A and Part B TDS produces WARNING."""
    data = create_valid_form16_data()
    issues = reconcile_part_a_and_part_b(data, part_a_tds_total=70000.0)
    assert len(issues) == 1
    assert issues[0].rule_code == "TDS_PART_A_PART_B_MISMATCH"


def test_duplicate_items_resolution():
    """Test duplicate allowances are consolidated cleanly."""
    raw_allowances = {"HRA": 50000.0, "hra ": 25000.0, "LTA": 15000.0}
    consolidated, issues = resolve_duplicate_breakdown_items(raw_allowances)
    assert consolidated["HRA"] == 75000.0
    assert consolidated["LTA"] == 15000.0
    assert len(issues) == 1


def test_arithmetic_consistency_clean():
    """Test valid data produces 0 arithmetic warnings."""
    data = create_valid_form16_data()
    issues = check_arithmetic_consistency(data)
    assert len(issues) == 0


def test_arithmetic_consistency_discrepancy():
    """Test altered taxable income triggers arithmetic warning."""
    data = create_valid_form16_data()
    data.tax.total_taxable_income = 800000.0  # Incorrect (should be 950000)
    issues = check_arithmetic_consistency(data)
    assert len(issues) == 1
    assert issues[0].rule_code == "ARITHMETIC_TAXABLE_INCOME_MISMATCH"


def test_full_normalization_pipeline_success():
    """Test DataNormalizationService creates normalized profile."""
    data = create_valid_form16_data()
    report = DataNormalizationService.validate_and_normalize(data, part_a_tds_total=67600.0)
    assert report.is_valid is True
    assert report.can_proceed is True
    assert report.normalized_profile is not None
    assert report.normalized_profile.employee_pan == "ABCDE1234F"
    assert report.normalized_profile.total_gross_salary == 1200000.0
    assert report.normalized_profile.total_chapter_via_deductions == 175000.0
    assert report.normalized_profile.total_taxable_income == 950000.0
