"""Pydantic data schemas for the Deterministic Tax Engine."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class MetroCityType(str, Enum):
    """City type for HRA exemption percentage."""
    METRO = "metro"          # 50% of Basic
    NON_METRO = "non_metro"  # 40% of Basic


class PropertyType(str, Enum):
    """House property occupancy classification."""
    SELF_OCCUPIED = "self_occupied"
    LET_OUT = "let_out"
    DEEMED_LET_OUT = "deemed_let_out"


class SeniorCitizenCategory(str, Enum):
    """Age bracket for statutory tax slab & deduction rules."""
    INDIVIDUAL = "individual"              # Age < 60
    SENIOR_CITIZEN = "senior_citizen"      # Age 60 to 79
    SUPER_SENIOR = "super_senior"          # Age 80+


class SalaryInput(BaseModel):
    """Income from Salaries (Section 17 & Section 10)."""
    basic_salary: float = Field(default=0.0, ge=0.0, description="Basic salary component")
    dearness_allowance: float = Field(default=0.0, ge=0.0, description="Dearness Allowance forming part of salary")
    hra_received: float = Field(default=0.0, ge=0.0, description="House Rent Allowance received from employer")
    rent_paid_annual: float = Field(default=0.0, ge=0.0, description="Actual rent paid per annum")
    is_metro: bool = Field(default=False, description="True if residing in Mumbai, Delhi, Kolkata, Chennai")

    # Section 17 breakdown
    gross_salary_sec_17_1: float = Field(default=0.0, ge=0.0, description="Salary as per Section 17(1)")
    perquisites_sec_17_2: float = Field(default=0.0, ge=0.0, description="Value of perquisites u/s 17(2)")
    profits_in_lieu_sec_17_3: float = Field(default=0.0, ge=0.0, description="Profits in lieu of salary u/s 17(3)")

    # Section 10 other allowances
    lta_received: float = Field(default=0.0, ge=0.0, description="Leave Travel Allowance")
    lta_exempt: float = Field(default=0.0, ge=0.0, description="Exempt LTA claimed")
    other_exempt_allowances: float = Field(default=0.0, ge=0.0, description="Other Section 10 exemptions (Gratuity, Leave Encashment, etc.)")

    # Section 16 Deductions
    professional_tax_paid: float = Field(default=0.0, ge=0.0, le=2500.0, description="Professional tax paid u/s 16(iii)")
    entertainment_allowance: float = Field(default=0.0, ge=0.0, description="Entertainment allowance for Govt employees u/s 16(ii)")
    is_govt_employee: bool = Field(default=False, description="True if Central or State Government employee")


class HousePropertyInput(BaseModel):
    """Income / Loss from House Property (Section 22 to 27)."""
    property_type: PropertyType = Field(default=PropertyType.SELF_OCCUPIED)
    annual_lettable_value_or_rent: float = Field(default=0.0, ge=0.0, description="Gross rent received or receivable")
    municipal_taxes_paid: float = Field(default=0.0, ge=0.0, description="Municipal / local property taxes paid by owner")
    housing_loan_interest_sop: float = Field(default=0.0, ge=0.0, description="Interest on housing loan for Self-Occupied property u/s 24(b)")
    housing_loan_interest_lop: float = Field(default=0.0, ge=0.0, description="Interest on housing loan for Let-Out property u/s 24(b)")


class OtherSourcesInput(BaseModel):
    """Income from Other Sources (Section 56 & 57)."""
    savings_bank_interest: float = Field(default=0.0, ge=0.0, description="Interest from savings bank accounts")
    fixed_deposit_interest: float = Field(default=0.0, ge=0.0, description="Interest from fixed/recurring deposits")
    dividend_income: float = Field(default=0.0, ge=0.0, description="Dividend income from shares & mutual funds")
    family_pension: float = Field(default=0.0, ge=0.0, description="Family pension received")
    other_taxable_income: float = Field(default=0.0, ge=0.0, description="Any other taxable receipts")


class ChapterVIAInput(BaseModel):
    """Deductions under Chapter VI-A."""
    section_80c: float = Field(default=0.0, ge=0.0, description="EPF, PPF, ELSS, Life Insurance, Tuition Fees, Principal Home Loan (max ₹1.5L)")
    section_80ccc: float = Field(default=0.0, ge=0.0, description="Pension Fund annuity premiums (within ₹1.5L cap)")
    section_80ccd_1: float = Field(default=0.0, ge=0.0, description="Employee contribution to NPS (within ₹1.5L cap)")
    section_80ccd_1b: float = Field(default=0.0, ge=0.0, description="Voluntary NPS Tier-1 contribution (exclusive additional ₹50,000)")
    section_80ccd_2: float = Field(default=0.0, ge=0.0, description="Employer contribution to NPS (up to 14% for Govt / 10% for Non-Govt)")

    # 80D Health Insurance
    section_80d_self: float = Field(default=0.0, ge=0.0, description="Health insurance premium: Self, spouse, children (max ₹25k / ₹50k senior)")
    section_80d_parents: float = Field(default=0.0, ge=0.0, description="Health insurance premium: Parents (max ₹25k / ₹50k senior parents)")
    section_80d_preventive: float = Field(default=0.0, ge=0.0, description="Preventive health check-up (max ₹5,000 within 80D limit)")
    parents_are_senior_citizens: bool = Field(default=False, description="True if either parent is 60+ years old")

    # 80E Education Loan
    section_80e: float = Field(default=0.0, ge=0.0, description="Interest paid on higher education loan (no upper limit)")

    # 80EEA / 80EEB
    section_80eea: float = Field(default=0.0, ge=0.0, description="Interest on loan for affordable housing (max ₹1.5L)")
    section_80eeb: float = Field(default=0.0, ge=0.0, description="Interest on loan for electric vehicle purchase (max ₹1.5L)")

    # 80G Donations
    section_80g_100_no_limit: float = Field(default=0.0, ge=0.0, description="Donations with 100% deduction without qualifying limit (PM Cares, etc.)")
    section_80g_50_no_limit: float = Field(default=0.0, ge=0.0, description="Donations with 50% deduction without qualifying limit (PMNRF, etc.)")
    section_80g_100_qualifying: float = Field(default=0.0, ge=0.0, description="Donations with 100% deduction with 10% Adjusted Gross Total Income qualifying limit")
    section_80g_50_qualifying: float = Field(default=0.0, ge=0.0, description="Donations with 50% deduction with 10% Adjusted Gross Total Income qualifying limit")

    # 80TTA / 80TTB
    section_80tta: float = Field(default=0.0, ge=0.0, description="Savings bank interest deduction for non-seniors (max ₹10,000)")
    section_80ttb: float = Field(default=0.0, ge=0.0, description="Interest on deposits for senior citizens (max ₹50,000)")

    # Other Deductions (80GG, 80U, 80DD, 80DDB)
    section_80gg: float = Field(default=0.0, ge=0.0, description="Rent paid when HRA not received (max ₹60,000/yr u/s 80GG)")
    section_80u: float = Field(default=0.0, ge=0.0, description="Deduction for person with disability (₹75k / ₹1.25L severe)")
    section_80dd: float = Field(default=0.0, ge=0.0, description="Maintenance/medical treatment of disabled dependent (₹75k / ₹1.25L)")
    section_80ddb: float = Field(default=0.0, ge=0.0, description="Medical treatment of specified diseases (₹40k / ₹1L senior)")


class AdvanceTaxScheduleInput(BaseModel):
    """Advance tax payments for Section 234A/B/C interest."""
    total_tds_tcs_deducted: float = Field(default=0.0, ge=0.0, description="Total TDS/TCS credited")
    self_assessment_tax_paid: float = Field(default=0.0, ge=0.0, description="Self-assessment tax paid before filing")

    # Advance Tax Installment payments
    advance_tax_paid_q1_june15: float = Field(default=0.0, ge=0.0, description="Advance tax paid on or before June 15")
    advance_tax_paid_q2_sept15: float = Field(default=0.0, ge=0.0, description="Advance tax paid on or before Sept 15 (cumulative)")
    advance_tax_paid_q3_dec15: float = Field(default=0.0, ge=0.0, description="Advance tax paid on or before Dec 15 (cumulative)")
    advance_tax_paid_q4_mar15: float = Field(default=0.0, ge=0.0, description="Advance tax paid on or before March 15 (cumulative)")
    advance_tax_paid_mar31: float = Field(default=0.0, ge=0.0, description="Advance tax paid between March 16 and March 31 (cumulative)")

    actual_filing_date: date | None = Field(default=None, description="Actual date of filing ITR")
    due_date_filing: date | None = Field(default=None, description="Statutory due date of filing ITR (usually July 31)")


class TaxpayerProfileInput(BaseModel):
    """Complete Taxpayer Financial Profile for calculation."""
    assessment_year: str = Field(default="2026-27", description="Assessment Year (e.g. '2026-27' or '2025-26')")
    taxpayer_category: SeniorCitizenCategory = Field(default=SeniorCitizenCategory.INDIVIDUAL)
    salary: SalaryInput = Field(default_factory=SalaryInput)
    house_property: HousePropertyInput = Field(default_factory=HousePropertyInput)
    other_sources: OtherSourcesInput = Field(default_factory=OtherSourcesInput)
    chapter_vi_a: ChapterVIAInput = Field(default_factory=ChapterVIAInput)
    advance_tax: AdvanceTaxScheduleInput = Field(default_factory=AdvanceTaxScheduleInput)
    relief_sec_89: float = Field(default=0.0, ge=0.0, description="Relief u/s 89 for salary arrears")


# Output Schemas

class SlabBracketDetail(BaseModel):
    """Itemized tax computed within a single slab bracket."""
    bracket_min: float
    bracket_max: float | None
    rate_percentage: float
    taxable_in_bracket: float
    tax_amount: float


class RegimeComputation(BaseModel):
    """Detailed tax calculation result for a single regime."""
    regime_name: str
    assessment_year: str

    # Heads of Income
    gross_salary: float
    exempt_allowances_sec_10: float
    standard_deduction_sec_16_ia: float
    professional_tax_sec_16_iii: float
    entertainment_allowance_sec_16_ii: float
    net_salary_income: float

    income_or_loss_house_property: float
    income_other_sources: float
    gross_total_income: float

    # Chapter VI-A Deductions
    total_chapter_via_deductions: float
    itemized_chapter_via: dict[str, float] = Field(default_factory=dict)

    # Net Taxable Income (Rounded u/s 288A)
    total_taxable_income: float

    # Progressive Slabs
    slab_breakdown: list[SlabBracketDetail] = Field(default_factory=list)
    base_tax_on_income: float

    # Section 87A Rebate & Marginal Relief
    rebate_87a_claimed: float
    marginal_relief_87a: float
    tax_after_87a: float

    # Surcharge & Surcharge Marginal Relief
    surcharge_rate_percentage: float
    gross_surcharge: float
    surcharge_marginal_relief: float
    net_surcharge: float

    # Health & Education Cess (4%)
    cess_amount: float
    total_tax_and_cess: float

    # Section 89 Relief
    relief_sec_89: float
    net_tax_liability: float

    # Interest Section 234A, 234B, 234C
    interest_234a: float
    interest_234b: float
    interest_234c: float
    total_interest_234: float

    # Total Final Liability & TDS Reconciliation (Rounded u/s 288B)
    aggregate_liability: float
    total_prepaid_taxes: float
    net_payable_or_refund: float  # Positive = Payable, Negative = Refund
    effective_tax_rate_percentage: float


class RegimeComparisonResult(BaseModel):
    """Side-by-side winning comparison of Old vs New Tax Regimes."""
    assessment_year: str
    recommended_regime: str  # "NEW" or "OLD"
    tax_savings_amount: float
    percentage_savings: float

    old_regime: RegimeComputation
    new_regime: RegimeComputation

    # Key differential drivers
    deduction_difference: float
    slab_tax_difference: float
    recommended_itr_form: str
    explanation: str
