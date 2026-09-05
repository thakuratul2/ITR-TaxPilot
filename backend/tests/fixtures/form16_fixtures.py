"""Synthetic and anonymized Form 16 test fixtures for test suites."""

from app.schemas.tax_models import (
    Form16ExtractionResult,
    PartAInfo,
    PartBAllowances,
    PartBChapterVIA,
    PartBDeductions,
    PartBSalary,
)

SAMPLE_FORM16_STANDARD_SALARIED = Form16ExtractionResult(
    assessment_year="2025-26",
    part_a=PartAInfo(
        employer_name="Tech Innovations Pvt Ltd",
        employer_tan="DELT12345F",
        employer_pan="AAACT1234F",
        employee_name="Rahul Sharma",
        employee_pan="ABCDE1234F",
        total_tds_deposited=45000.0,
    ),
    part_b_salary=PartBSalary(
        gross_salary_17_1=1200000.0,
        perquisites_17_2=0.0,
        profits_in_lieu_17_3=0.0,
        total_gross_salary=1200000.0,
    ),
    part_b_allowances=PartBAllowances(
        hra_10_13a=60000.0,
        lta_10_5=0.0,
        total_exempt_allowances=60000.0,
    ),
    part_b_deductions=PartBDeductions(
        standard_deduction_16ia=75000.0,
        entertainment_16ii=0.0,
        professional_tax_16iii=2500.0,
        total_section_16=77500.0,
    ),
    part_b_chapter_via=PartBChapterVIA(
        section_80c=150000.0,
        section_80ccd_1b=50000.0,
        section_80d=25000.0,
        section_80tta=10000.0,
        total_chapter_via=235000.0,
    ),
    income_from_house_property=0.0,
    income_from_other_sources=20000.0,
    gross_total_income=1082500.0,
    total_taxable_income=847500.0,
    total_tax_payable=0.0,
    confidence_score=0.98,
    extraction_source="fitz_exact",
)

SAMPLE_FORM16_ZERO_TAX = Form16ExtractionResult(
    assessment_year="2025-26",
    part_a=PartAInfo(
        employer_name="Startup Global Ltd",
        employer_tan="BLRS56789G",
        employee_name="Priya Patel",
        employee_pan="BCDEF2345G",
        total_tds_deposited=0.0,
    ),
    part_b_salary=PartBSalary(
        gross_salary_17_1=550000.0,
        total_gross_salary=550000.0,
    ),
    part_b_allowances=PartBAllowances(),
    part_b_deductions=PartBDeductions(
        standard_deduction_16ia=75000.0,
        total_section_16=75000.0,
    ),
    part_b_chapter_via=PartBChapterVIA(
        section_80c=50000.0,
        total_chapter_via=50000.0,
    ),
    gross_total_income=475000.0,
    total_taxable_income=425000.0,
    confidence_score=0.99,
    extraction_source="fitz_exact",
)

SAMPLE_FORM16_HIGH_NET_WORTH = Form16ExtractionResult(
    assessment_year="2025-26",
    part_a=PartAInfo(
        employer_name="Enterprise MegaCorp",
        employer_tan="MUMB99887H",
        employee_name="Vikramaditya Singhania",
        employee_pan="CDEFG3456H",
        total_tds_deposited=1850000.0,
    ),
    part_b_salary=PartBSalary(
        gross_salary_17_1=7500000.0,
        total_gross_salary=7500000.0,
    ),
    part_b_allowances=PartBAllowances(
        hra_10_13a=250000.0,
        total_exempt_allowances=250000.0,
    ),
    part_b_deductions=PartBDeductions(
        standard_deduction_16ia=75000.0,
        professional_tax_16iii=2500.0,
        total_section_16=77500.0,
    ),
    part_b_chapter_via=PartBChapterVIA(
        section_80c=150000.0,
        section_80d=50000.0,
        total_chapter_via=200000.0,
    ),
    income_from_house_property=-200000.0,
    income_from_other_sources=150000.0,
    gross_total_income=7122500.0,
    total_taxable_income=6922500.0,
    confidence_score=0.97,
    extraction_source="fitz_exact",
)
