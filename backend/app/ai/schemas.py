"""Strict Pydantic schemas for AI Form 16 extraction and confidence scoring."""

from pydantic import BaseModel, Field


class ExtractedEmployer(BaseModel):
    """Employer and Deductor details."""
    name: str | None = Field(default=None, description="Employer/Deductor organization name")
    tan: str | None = Field(default=None, description="TAN of the Deductor")
    pan: str | None = Field(default=None, description="PAN of the Deductor")
    address: str | None = Field(default=None, description="Employer address")


class ExtractedEmployee(BaseModel):
    """Employee identification details."""
    name: str | None = Field(default=None, description="Employee name")
    pan: str | None = Field(default=None, description="PAN of the Employee")
    designation: str | None = Field(default=None, description="Employee designation")


class ExtractedSalaryBreakdown(BaseModel):
    """Detailed salary breakdown as reported in Form 16 Part B."""
    gross_salary_sec_17_1: float | None = Field(default=None, description="Salary as per section 17(1)")
    perquisites_sec_17_2: float | None = Field(default=None, description="Value of perquisites under section 17(2)")
    profits_in_lieu_sec_17_3: float | None = Field(default=None, description="Profits in lieu of salary under section 17(3)")
    total_gross_salary: float = Field(..., description="Total Gross Salary (17(1) + 17(2) + 17(3))")

    # Section 10 Allowances
    allowances_sec_10: float | None = Field(default=0.0, description="Total exempt allowances under section 10")
    allowances_breakdown: dict[str, float] = Field(default_factory=dict, description="Itemized section 10 allowances (HRA, LTA, etc.)")

    # Section 16 Deductions
    standard_deduction_sec_16_ia: float | None = Field(default=None, description="Standard deduction u/s 16(ia)")
    entertainment_allowance_sec_16_ii: float | None = Field(default=0.0, description="Entertainment allowance u/s 16(ii)")
    professional_tax_sec_16_iii: float | None = Field(default=0.0, description="Tax on employment / professional tax u/s 16(iii)")
    total_deductions_sec_16: float | None = Field(default=None, description="Total deductions under section 16")

    # Net Salary
    income_chargeable_salaries: float = Field(..., description="Net income chargeable under the head 'Salaries'")


class ExtractedChapterVIA(BaseModel):
    """Itemized Chapter VI-A deductions."""
    section_80c: float | None = Field(default=0.0, description="Section 80C deductions (EPF, PPF, ELSS, LIC, etc.)")
    section_80ccc: float | None = Field(default=0.0, description="Section 80CCC pension funds")
    section_80ccd_1: float | None = Field(default=0.0, description="Section 80CCD(1) employee NPS")
    section_80ccd_1b: float | None = Field(default=0.0, description="Section 80CCD(1B) additional NPS")
    section_80ccd_2: float | None = Field(default=0.0, description="Section 80CCD(2) employer NPS contribution")
    section_80d: float | None = Field(default=0.0, description="Section 80D health insurance premium")
    section_80e: float | None = Field(default=0.0, description="Section 80E higher education loan interest")
    section_80g: float | None = Field(default=0.0, description="Section 80G eligible donations")
    section_80tta: float | None = Field(default=0.0, description="Section 80TTA savings interest deduction")
    section_80ttb: float | None = Field(default=0.0, description="Section 80TTB senior citizen interest deduction")
    other_deductions: dict[str, float] = Field(default_factory=dict, description="Other Chapter VI-A deductions")
    total_chapter_via_deductions: float = Field(default=0.0, description="Total aggregated Chapter VI-A deductions")


class ExtractedTaxSummary(BaseModel):
    """Tax computation summary as shown on Form 16."""
    total_taxable_income: float = Field(..., description="Total taxable income (rounded to nearest 10)")
    tax_on_total_income: float | None = Field(default=None, description="Gross tax on total income")
    rebate_87a: float | None = Field(default=0.0, description="Rebate under section 87A")
    surcharge: float | None = Field(default=0.0, description="Surcharge if applicable")
    health_and_education_cess: float | None = Field(default=None, description="4% Health & Education Cess")
    total_tax_payable: float | None = Field(default=None, description="Total tax payable after cess")
    relief_89: float | None = Field(default=0.0, description="Relief under section 89")
    net_tax_payable: float | None = Field(default=None, description="Net tax payable")
    total_tds_deducted: float = Field(..., description="Total TDS deducted as per Part A and Part B")


class ExtractedForm16Data(BaseModel):
    """Complete structured Form 16 extraction result."""
    assessment_year: str = Field(..., description="Assessment Year in YYYY-YY format (e.g. '2026-27')")
    financial_year: str | None = Field(default=None, description="Financial Year (e.g. '2025-26')")
    employer: ExtractedEmployer = Field(default_factory=ExtractedEmployer)
    employee: ExtractedEmployee = Field(default_factory=ExtractedEmployee)
    salary: ExtractedSalaryBreakdown = Field(..., description="Extracted salary details")
    deductions: ExtractedChapterVIA = Field(default_factory=ExtractedChapterVIA)
    tax: ExtractedTaxSummary = Field(..., description="Extracted tax and TDS summary")
    confidence_scores: dict[str, float] = Field(default_factory=dict, description="Field-level confidence scores 0.0-1.0")
    model_name: str = Field(default="unknown", description="AI Model used for extraction")
    has_dual_verification: bool = Field(default=False, description="True if cross-verified by secondary model")
    disagreements: list[str] = Field(default_factory=list, description="Fields with model disagreements if any")
