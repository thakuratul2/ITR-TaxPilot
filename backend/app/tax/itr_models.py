"""Pydantic data schemas and models for the ITR Form Recommendation Engine."""

from enum import Enum
from pydantic import BaseModel, Field


class ITRFormType(str, Enum):
    """Statutory Indian Income Tax Return Form types."""
    ITR_1_SAHAJ = "ITR-1 (Sahaj)"
    ITR_2 = "ITR-2"
    ITR_3 = "ITR-3"
    ITR_4_SUGAM = "ITR-4 (Sugam)"
    NOT_ELIGIBLE_INDIVIDUAL = "Other Form / Not Supported for Individual"


class ResidentialStatus(str, Enum):
    """Taxpayer statutory residential status in India."""
    RESIDENT = "resident"  # Resident and Ordinarily Resident (ROR)
    RNOR = "rnor"          # Resident but Not Ordinarily Resident
    NON_RESIDENT = "non_resident"  # Non-Resident (NR)


class TaxpayerFilingType(str, Enum):
    """Legal entity classification of the taxpayer."""
    INDIVIDUAL = "individual"
    HUF = "huf"
    FIRM = "firm"
    LLP = "llp"
    COMPANY = "company"
    AOP_BOI = "aop_boi"
    TRUST = "trust"


class CapitalGainsDetail(BaseModel):
    """Capital gains income attributes for ITR determination."""
    has_capital_gains: bool = Field(default=False, description="True if any STCG or LTCG earned")
    short_term_capital_gains_111a: float = Field(default=0.0, ge=0.0, description="STCG on listed equity/MFs u/s 111A")
    short_term_capital_gains_other: float = Field(default=0.0, ge=0.0, description="Other STCG taxed at normal slab rates")
    long_term_capital_gains_112a: float = Field(default=0.0, ge=0.0, description="LTCG on listed equity/MFs u/s 112A")
    long_term_capital_gains_112: float = Field(default=0.0, ge=0.0, description="Other LTCG u/s 112")
    has_virtual_digital_assets: bool = Field(default=False, description="Income from crypto / VDAs u/s 115BBH")


class BusinessProfessionDetail(BaseModel):
    """Business and Profession income attributes for ITR-3 & ITR-4 determination."""
    has_business_or_profession_income: bool = Field(default=False, description="Has income under PGBP head")
    is_presumptive_44ad: bool = Field(default=False, description="Eligible and opted for 44AD presumptive business")
    is_presumptive_44ada: bool = Field(default=False, description="Eligible and opted for 44ADA presumptive profession")
    is_presumptive_44ae: bool = Field(default=False, description="Eligible and opted for 44AE presumptive goods transport")
    gross_turnover_or_receipts: float = Field(default=0.0, ge=0.0, description="Gross receipts or turnover from business/profession")
    presumptive_net_profit: float = Field(default=0.0, ge=0.0, description="Declared presumptive net profit")
    is_books_audited_44ab: bool = Field(default=False, description="Tax audit required under Section 44AB")
    is_partner_in_firm: bool = Field(default=False, description="Partner in a partnership firm receiving remuneration/profit")
    has_speculative_income: bool = Field(default=False, description="Intraday trading / speculative business income")
    has_agency_or_brokerage_income: bool = Field(default=False, description="Income from commission / brokerage / agency business")


class TaxpayerProfileForITR(BaseModel):
    """Comprehensive taxpayer profile for deterministic ITR form recommendation."""
    filing_type: TaxpayerFilingType = Field(default=TaxpayerFilingType.INDIVIDUAL, description="Taxpayer entity type")
    residential_status: ResidentialStatus = Field(default=ResidentialStatus.RESIDENT, description="Residential status")
    
    # Income metrics
    total_income: float = Field(default=0.0, ge=0.0, description="Gross Total Income or Total Taxable Income in INR")
    has_salary_income: bool = Field(default=True, description="True if salary or pension income present")
    salary_income_amount: float = Field(default=0.0, ge=0.0, description="Net salary/pension income")
    
    # House Property
    house_property_count: int = Field(default=1, ge=0, description="Number of house properties owned (0, 1, 2+)")
    has_brought_forward_hp_loss: bool = Field(default=False, description="Has brought forward house property loss")
    
    # Other Sources
    has_other_sources_income: bool = Field(default=False, description="Has income from other sources (interest, dividends, etc.)")
    other_sources_amount: float = Field(default=0.0, ge=0.0, description="Total income from other sources")
    has_lottery_or_racehorse_income: bool = Field(default=False, description="Winnings from lottery, betting, gambling, horse races")
    has_section_57_deduction_other_than_family_pension: bool = Field(
        default=False, 
        description="Claimed deductions u/s 57 other than family pension standard deduction"
    )
    
    # Agriculture
    agricultural_income: float = Field(default=0.0, ge=0.0, description="Net agricultural income in INR")
    
    # Statutory Flags & Disqualifications
    is_director_in_company: bool = Field(default=False, description="Director in an Indian or foreign company")
    holds_unlisted_equity_shares: bool = Field(default=False, description="Held unlisted equity shares at any time during FY")
    has_foreign_assets_or_income: bool = Field(default=False, description="Foreign assets, foreign bank accounts, or foreign income")
    has_signing_authority_foreign: bool = Field(default=False, description="Signing authority in any account located outside India")
    has_unabsorbed_depreciation_or_loss: bool = Field(default=False, description="Has brought forward or carry forward losses under any head")
    has_section_194n_tds: bool = Field(default=False, description="TDS deducted under Section 194N (cash withdrawals)")
    has_esop_deferred_tax: bool = Field(default=False, description="Tax on ESOP deferred u/s 191(2) or 192(1C)")
    
    # Sub-models
    capital_gains: CapitalGainsDetail = Field(default_factory=CapitalGainsDetail)
    business_profession: BusinessProfessionDetail = Field(default_factory=BusinessProfessionDetail)


class ITRRuleCheckResult(BaseModel):
    """Evaluation result for an individual ITR form."""
    form: ITRFormType = Field(..., description="ITR form evaluated")
    is_eligible: bool = Field(..., description="True if taxpayer satisfies all statutory conditions")
    positive_factors: list[str] = Field(default_factory=list, description="Statutory criteria satisfied")
    disqualifications: list[str] = Field(default_factory=list, description="Statutory clauses violated / disqualifying factors")


class ITRRecommendation(BaseModel):
    """Complete statutory ITR recommendation payload."""
    recommended_form: ITRFormType = Field(..., description="Primary recommended ITR form")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Engine recommendation confidence (1.0 = deterministic)")
    summary_rationale: str = Field(..., description="Plain-English explanation of why this form is recommended")
    eligibility_reasons: list[str] = Field(default_factory=list, description="Primary reasons supporting the recommended form")
    disqualification_reasons_for_other_forms: dict[str, list[str]] = Field(
        default_factory=dict, 
        description="Why simpler/alternative ITR forms were ruled out"
    )
    all_form_evaluations: dict[str, ITRRuleCheckResult] = Field(
        default_factory=dict, 
        description="Detailed evaluation results for all considered ITR forms"
    )
    statutory_disclaimers: list[str] = Field(
        default_factory=list, 
        description="Mandatory legal and regulatory disclaimers"
    )
    notes_and_limitations: list[str] = Field(
        default_factory=list, 
        description="Specific notes on schedule attachments and verification instructions"
    )
    statutory_authority: str = Field(
        default="Income Tax Department, Government of India", 
        description="Governing tax administration"
    )
