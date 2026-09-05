"""Deterministic ITR Form Recommendation Engine.

Evaluates taxpayer profiles against Indian statutory income tax rules to recommend
the optimal Income Tax Return form (ITR-1 Sahaj, ITR-2, ITR-3, ITR-4 Sugam).
"""

from app.calculator.models import TaxpayerProfileInput
from app.tax.itr_models import (
    BusinessProfessionDetail,
    CapitalGainsDetail,
    ITRFormType,
    ITRRecommendation,
    ITRRuleCheckResult,
    ResidentialStatus,
    TaxpayerFilingType,
    TaxpayerProfileForITR,
)


class ITRSelector:
    """Deterministic Statutory ITR Form Selector and Recommendation Engine."""

    # Statutory Thresholds
    ITR1_MAX_TOTAL_INCOME = 5000000.0  # ₹50 Lakhs
    ITR4_MAX_TOTAL_INCOME = 5000000.0  # ₹50 Lakhs
    MAX_AGRICULTURAL_INCOME_ITR1_ITR4 = 5000.0  # ₹5,000

    @classmethod
    def evaluate_itr1_sahaj(cls, profile: TaxpayerProfileForITR) -> ITRRuleCheckResult:
        """
        Evaluate eligibility for ITR-1 (Sahaj).
        Eligible for Resident Individuals with Total Income <= ₹50 Lakhs from Salary,
        ONE House Property, Other Sources, and Agricultural Income <= ₹5,000.
        """
        positives: list[str] = []
        disqualifications: list[str] = []

        # 1. Entity Type
        if profile.filing_type == TaxpayerFilingType.INDIVIDUAL:
            positives.append("Taxpayer is an Individual.")
        else:
            disqualifications.append(f"ITR-1 is restricted to Individuals only; found entity type '{profile.filing_type.value}'.")

        # 2. Residential Status
        if profile.residential_status == ResidentialStatus.RESIDENT:
            positives.append("Taxpayer is a Resident and Ordinarily Resident (ROR) in India.")
        else:
            disqualifications.append(f"ITR-1 is not available for Non-Residents or RNOR taxpayers (status: '{profile.residential_status.value}').")

        # 3. Total Income Cap (<= ₹50 Lakhs)
        if profile.total_income <= cls.ITR1_MAX_TOTAL_INCOME:
            positives.append(f"Total income (₹{profile.total_income:,.0f}) is within the statutory ₹50 Lakh threshold.")
        else:
            disqualifications.append(f"Total income (₹{profile.total_income:,.0f}) exceeds the ₹50,00,000 limit for ITR-1.")

        # 4. House Property (Max 1, no brought forward losses)
        if profile.house_property_count <= 1:
            positives.append(f"House property count ({profile.house_property_count}) meets the single-property limit.")
        else:
            disqualifications.append(f"Income/loss from more than one house property ({profile.house_property_count} properties) cannot be reported in ITR-1.")

        if profile.has_brought_forward_hp_loss:
            disqualifications.append("Brought forward house property loss cannot be carried forward/set off in ITR-1.")

        # 5. Capital Gains
        cg = profile.capital_gains
        if cg.has_capital_gains or cg.short_term_capital_gains_111a > 0 or cg.short_term_capital_gains_other > 0 or cg.long_term_capital_gains_112a > 0 or cg.long_term_capital_gains_112 > 0 or cg.has_virtual_digital_assets:
            disqualifications.append("Income from Capital Gains (STCG/LTCG/VDAs) is strictly ineligible for ITR-1.")
        else:
            positives.append("No Capital Gains income reported.")

        # 6. Business and Profession (PGBP)
        bp = profile.business_profession
        if bp.has_business_or_profession_income:
            disqualifications.append("Income from Profits and Gains of Business or Profession (PGBP) is ineligible for ITR-1.")
        else:
            positives.append("No Business or Professional income reported.")

        # 7. Agricultural Income (<= ₹5,000)
        if profile.agricultural_income <= cls.MAX_AGRICULTURAL_INCOME_ITR1_ITR4:
            positives.append(f"Agricultural income (₹{profile.agricultural_income:,.0f}) is within the ₹5,000 limit.")
        else:
            disqualifications.append(f"Agricultural income (₹{profile.agricultural_income:,.0f}) exceeds the statutory limit of ₹5,000 for ITR-1.")

        # 8. Company Directorship & Unlisted Equity
        if profile.is_director_in_company:
            disqualifications.append("Holding directorship in an Indian or foreign company disqualifies taxpayer from ITR-1.")
        if profile.holds_unlisted_equity_shares:
            disqualifications.append("Holding unlisted equity shares at any time during the financial year disqualifies taxpayer from ITR-1.")

        # 9. Foreign Assets & Income
        if profile.has_foreign_assets_or_income or profile.has_signing_authority_foreign:
            disqualifications.append("Holding foreign assets, foreign income, or signing authority abroad requires Schedule FA in ITR-2/3.")

        # 10. Special Other Sources & Deductions
        if profile.has_lottery_or_racehorse_income:
            disqualifications.append("Income from lottery, betting, gambling, or horse races cannot be filed in ITR-1.")
        if profile.has_section_57_deduction_other_than_family_pension:
            disqualifications.append("Deductions under Section 57 (other than family pension standard deduction) are disallowed in ITR-1.")
        if profile.has_unabsorbed_depreciation_or_loss:
            disqualifications.append("Carrying forward or setting off unabsorbed depreciation/losses is not permitted in ITR-1.")
        if profile.has_section_194n_tds:
            disqualifications.append("TDS credit deducted under Section 194N cannot be claimed in ITR-1.")
        if profile.has_esop_deferred_tax:
            disqualifications.append("Deferred tax on ESOPs received from an eligible start-up disqualifies filing under ITR-1.")

        is_eligible = len(disqualifications) == 0
        return ITRRuleCheckResult(
            form=ITRFormType.ITR_1_SAHAJ,
            is_eligible=is_eligible,
            positive_factors=positives,
            disqualifications=disqualifications,
        )

    @classmethod
    def evaluate_itr4_sugam(cls, profile: TaxpayerProfileForITR) -> ITRRuleCheckResult:
        """
        Evaluate eligibility for ITR-4 (Sugam).
        Eligible for Resident Individuals, HUFs, and Firms (other than LLP) having
        presumptive business/professional income under Section 44AD, 44ADA, or 44AE
        and Total Income <= ₹50 Lakhs.
        """
        positives: list[str] = []
        disqualifications: list[str] = []

        # 1. Entity Type
        if profile.filing_type in (TaxpayerFilingType.INDIVIDUAL, TaxpayerFilingType.HUF, TaxpayerFilingType.FIRM):
            positives.append(f"Entity type '{profile.filing_type.value}' is eligible for ITR-4.")
        else:
            disqualifications.append(f"ITR-4 cannot be filed by entity type '{profile.filing_type.value}' (LLPs/Companies prohibited).")

        # 2. Residential Status
        if profile.residential_status == ResidentialStatus.RESIDENT:
            positives.append("Taxpayer is a Resident in India.")
        else:
            disqualifications.append("ITR-4 is restricted to Resident taxpayers only; Non-Residents / RNOR are not eligible.")

        # 3. Presumptive Business/Profession Income
        bp = profile.business_profession
        if not bp.has_business_or_profession_income:
            disqualifications.append("No business or professional income reported. (ITR-1 or ITR-2 should be used instead).")
        else:
            is_presumptive = bp.is_presumptive_44ad or bp.is_presumptive_44ada or bp.is_presumptive_44ae
            if is_presumptive:
                positives.append("Income is computed under presumptive taxation schemes (Section 44AD/44ADA/44AE).")
            else:
                disqualifications.append("Business/profession income is not computed under presumptive sections (44AD/44ADA/44AE).")

            if bp.is_books_audited_44ab:
                disqualifications.append("Tax audit required under Section 44AB requires comprehensive filing in ITR-3.")
            if bp.is_partner_in_firm:
                disqualifications.append("Partner in a partnership firm receiving income from firm cannot file ITR-4.")
            if bp.has_speculative_income:
                disqualifications.append("Speculative business income (such as intraday equity trading) is ineligible for ITR-4.")
            if bp.has_agency_or_brokerage_income:
                disqualifications.append("Commission, brokerage, or agency business income is ineligible for presumptive taxation under ITR-4.")

        # 4. Total Income Cap (<= ₹50 Lakhs)
        if profile.total_income <= cls.ITR4_MAX_TOTAL_INCOME:
            positives.append(f"Total income (₹{profile.total_income:,.0f}) is within the statutory ₹50 Lakh threshold.")
        else:
            disqualifications.append(f"Total income (₹{profile.total_income:,.0f}) exceeds the ₹50,00,000 threshold for ITR-4.")

        # 5. House Property
        if profile.house_property_count <= 1:
            positives.append(f"House property count ({profile.house_property_count}) meets the single-property limit.")
        else:
            disqualifications.append(f"Income/loss from more than one house property ({profile.house_property_count} properties) is disallowed in ITR-4.")

        if profile.has_brought_forward_hp_loss:
            disqualifications.append("Brought forward house property loss cannot be adjusted in ITR-4.")

        # 6. Capital Gains
        cg = profile.capital_gains
        if cg.has_capital_gains or cg.short_term_capital_gains_111a > 0 or cg.short_term_capital_gains_other > 0 or cg.long_term_capital_gains_112a > 0 or cg.long_term_capital_gains_112 > 0 or cg.has_virtual_digital_assets:
            disqualifications.append("Income from Capital Gains is not permitted in ITR-4.")
        else:
            positives.append("No Capital Gains income reported.")

        # 7. Agricultural Income (<= ₹5,000)
        if profile.agricultural_income <= cls.MAX_AGRICULTURAL_INCOME_ITR1_ITR4:
            positives.append(f"Agricultural income (₹{profile.agricultural_income:,.0f}) is within the ₹5,000 limit.")
        else:
            disqualifications.append(f"Agricultural income (₹{profile.agricultural_income:,.0f}) exceeds ₹5,000.")

        # 8. Statutory Disqualifications
        if profile.is_director_in_company:
            disqualifications.append("Holding directorship in a company is ineligible for ITR-4.")
        if profile.holds_unlisted_equity_shares:
            disqualifications.append("Holding unlisted equity shares is ineligible for ITR-4.")
        if profile.has_foreign_assets_or_income or profile.has_signing_authority_foreign:
            disqualifications.append("Foreign assets/income requires Schedule FA (file ITR-3).")
        if profile.has_lottery_or_racehorse_income:
            disqualifications.append("Lottery/gambling income is ineligible for ITR-4.")
        if profile.has_esop_deferred_tax:
            disqualifications.append("Deferred tax on ESOPs is ineligible for ITR-4.")

        is_eligible = len(disqualifications) == 0
        return ITRRuleCheckResult(
            form=ITRFormType.ITR_4_SUGAM,
            is_eligible=is_eligible,
            positive_factors=positives,
            disqualifications=disqualifications,
        )

    @classmethod
    def evaluate_itr2(cls, profile: TaxpayerProfileForITR) -> ITRRuleCheckResult:
        """
        Evaluate eligibility for ITR-2.
        Eligible for Individuals and HUFs NOT having income under Profits and Gains of Business or Profession (PGBP).
        Supports Capital Gains, multiple house properties, foreign assets, agricultural income > ₹5,000,
        directorships, unlisted shares, and Total Income > ₹50 Lakhs.
        """
        positives: list[str] = []
        disqualifications: list[str] = []

        # 1. Entity Type
        if profile.filing_type in (TaxpayerFilingType.INDIVIDUAL, TaxpayerFilingType.HUF):
            positives.append(f"Entity type '{profile.filing_type.value}' is eligible for ITR-2.")
        else:
            disqualifications.append(f"ITR-2 is strictly for Individuals and HUFs (found entity type '{profile.filing_type.value}').")

        # 2. Business and Profession (STRICT PROHIBITION)
        bp = profile.business_profession
        if bp.has_business_or_profession_income:
            disqualifications.append("ITR-2 is strictly prohibited for taxpayers with income from Profits and Gains of Business or Profession (PGBP). ITR-3 must be used.")
        else:
            positives.append("No business or professional income declared (satisfies core ITR-2 mandate).")

        # 3. Supported Capabilities (Positives)
        if profile.total_income > cls.ITR1_MAX_TOTAL_INCOME:
            positives.append(f"Accommodates high income (₹{profile.total_income:,.0f} > ₹50 Lakhs).")

        if profile.house_property_count > 1 or profile.has_brought_forward_hp_loss:
            positives.append(f"Accommodates multiple house properties ({profile.house_property_count}) and carried forward losses.")

        cg = profile.capital_gains
        if cg.has_capital_gains or cg.short_term_capital_gains_111a > 0 or cg.long_term_capital_gains_112a > 0 or cg.has_virtual_digital_assets:
            positives.append("Accommodates Short-Term / Long-Term Capital Gains and Virtual Digital Assets (Schedule CG & VDA).")

        if profile.has_foreign_assets_or_income or profile.has_signing_authority_foreign:
            positives.append("Accommodates foreign assets, foreign income, and overseas bank accounts (Schedule FA & FSI).")

        if profile.is_director_in_company or profile.holds_unlisted_equity_shares:
            positives.append("Accommodates company directorships and holdings in unlisted equity shares.")

        if profile.agricultural_income > cls.MAX_AGRICULTURAL_INCOME_ITR1_ITR4:
            positives.append("Accommodates agricultural income exceeding ₹5,000 (Schedule EI).")

        if profile.residential_status in (ResidentialStatus.NON_RESIDENT, ResidentialStatus.RNOR):
            positives.append(f"Supports Non-Resident and RNOR taxpayers (status: '{profile.residential_status.value}').")

        is_eligible = len(disqualifications) == 0
        return ITRRuleCheckResult(
            form=ITRFormType.ITR_2,
            is_eligible=is_eligible,
            positive_factors=positives,
            disqualifications=disqualifications,
        )

    @classmethod
    def evaluate_itr3(cls, profile: TaxpayerProfileForITR) -> ITRRuleCheckResult:
        """
        Evaluate eligibility for ITR-3.
        Eligible for Individuals and HUFs having income from Profits and Gains of Business or Profession (PGBP).
        Comprehensive form supporting audit cases, partner in firms, proprietary business, F&O trading,
        plus all heads of income (Salary, House Property, Capital Gains, Other Sources, Foreign Assets).
        """
        positives: list[str] = []
        disqualifications: list[str] = []

        # 1. Entity Type
        if profile.filing_type in (TaxpayerFilingType.INDIVIDUAL, TaxpayerFilingType.HUF):
            positives.append(f"Entity type '{profile.filing_type.value}' is eligible for ITR-3.")
        else:
            disqualifications.append(f"ITR-3 is for Individuals and HUFs only (found '{profile.filing_type.value}'). Companies/Firms file ITR-5/6.")

        # 2. Business and Profession Income Presence
        bp = profile.business_profession
        if bp.has_business_or_profession_income:
            positives.append("Taxpayer has business or professional income (PGBP), satisfying the primary criteria for ITR-3.")
            if bp.is_books_audited_44ab:
                positives.append("Supports audited accounts under Section 44AB (Balance Sheet, P&L, Tax Audit Report).")
            if bp.is_partner_in_firm:
                positives.append("Supports remuneration, interest, and profit share received as a partner in a partnership firm.")
            if bp.has_speculative_income:
                positives.append("Supports speculative business (intraday trading, futures & options).")
        else:
            disqualifications.append("ITR-3 is intended for taxpayers with Business or Professional income (PGBP). If no business income exists, ITR-1 or ITR-2 is recommended.")

        # 3. Universal compatibility positives
        positives.append("Supports all heads of income: Salary, Multiple Properties, Capital Gains, Foreign Assets, and Presumptive/Audited Business.")

        is_eligible = len(disqualifications) == 0
        return ITRRuleCheckResult(
            form=ITRFormType.ITR_3,
            is_eligible=is_eligible,
            positive_factors=positives,
            disqualifications=disqualifications,
        )

    @classmethod
    def recommend(cls, profile: TaxpayerProfileForITR) -> ITRRecommendation:
        """
        Execute deterministic statutory evaluation across all ITR forms and return
        the recommended form along with transparent rationales, positive factors,
        disqualification reasons for rejected forms, and mandatory legal disclaimers.
        """
        itr1_eval = cls.evaluate_itr1_sahaj(profile)
        itr4_eval = cls.evaluate_itr4_sugam(profile)
        itr2_eval = cls.evaluate_itr2(profile)
        itr3_eval = cls.evaluate_itr3(profile)

        evaluations: dict[str, ITRRuleCheckResult] = {
            ITRFormType.ITR_1_SAHAJ.value: itr1_eval,
            ITRFormType.ITR_4_SUGAM.value: itr4_eval,
            ITRFormType.ITR_2.value: itr2_eval,
            ITRFormType.ITR_3.value: itr3_eval,
        }

        # Check entity type compatibility
        if profile.filing_type not in (TaxpayerFilingType.INDIVIDUAL, TaxpayerFilingType.HUF):
            return ITRRecommendation(
                recommended_form=ITRFormType.NOT_ELIGIBLE_INDIVIDUAL,
                confidence_score=1.0,
                summary_rationale=f"Taxpayer filing entity is '{profile.filing_type.value}'. Individual ITR forms (ITR-1/2/3/4) are not applicable; please file ITR-5 (Partnership/LLP) or ITR-6 (Company).",
                eligibility_reasons=[],
                disqualification_reasons_for_other_forms={k: v.disqualifications for k, v in evaluations.items()},
                all_form_evaluations=evaluations,
                statutory_disclaimers=cls._get_statutory_disclaimers(),
                notes_and_limitations=["Consult a Chartered Accountant for corporate/firm statutory filings."],
            )

        has_business = profile.business_profession.has_business_or_profession_income

        # Decision Hierarchy
        if has_business:
            # Case A: Taxpayer has Business/Profession Income
            if itr4_eval.is_eligible:
                recommended = ITRFormType.ITR_4_SUGAM
                rationale = (
                    "ITR-4 (Sugam) is recommended as you have declared presumptive business or professional "
                    "income under Sections 44AD/44ADA/44AE with total income within ₹50 Lakhs and no capital gains."
                )
                eligibility_reasons = itr4_eval.positive_factors
            else:
                recommended = ITRFormType.ITR_3
                rationale = (
                    "ITR-3 is recommended because you have business or professional income (PGBP) and your profile "
                    "involves audited accounts, regular business bookkeeping, turnover/income exceeding presumptive limits, "
                    "capital gains, multiple properties, or partner remuneration."
                )
                eligibility_reasons = itr3_eval.positive_factors
        else:
            # Case B: Taxpayer does NOT have Business/Profession Income
            if itr1_eval.is_eligible:
                recommended = ITRFormType.ITR_1_SAHAJ
                rationale = (
                    "ITR-1 (Sahaj) is recommended because you are a resident individual with total income "
                    "up to ₹50 Lakhs derived exclusively from Salary/Pension, a single house property, and permitted other sources."
                )
                eligibility_reasons = itr1_eval.positive_factors
            else:
                recommended = ITRFormType.ITR_2
                rationale = (
                    "ITR-2 is recommended because your profile includes factors disqualified from ITR-1 "
                    "(such as total income > ₹50 Lakhs, Capital Gains, multiple house properties, foreign assets, "
                    "or company directorships) and you do not have business or professional income."
                )
                eligibility_reasons = itr2_eval.positive_factors

        # Build disqualification summary for other forms
        disqualifications_dict: dict[str, list[str]] = {}
        for form_name, check_res in evaluations.items():
            if form_name != recommended.value:
                disqualifications_dict[form_name] = check_res.disqualifications

        # Context-specific notes and schedules
        notes = cls._build_filing_notes(recommended, profile)

        return ITRRecommendation(
            recommended_form=recommended,
            confidence_score=1.0,
            summary_rationale=rationale,
            eligibility_reasons=eligibility_reasons,
            disqualification_reasons_for_other_forms=disqualifications_dict,
            all_form_evaluations=evaluations,
            statutory_disclaimers=cls._get_statutory_disclaimers(),
            notes_and_limitations=notes,
        )

    @classmethod
    def from_taxpayer_profile_input(
        cls,
        profile: TaxpayerProfileInput,
        residential_status: ResidentialStatus = ResidentialStatus.RESIDENT,
        has_foreign_assets: bool = False,
        is_director: bool = False,
        holds_unlisted_shares: bool = False,
        has_capital_gains: bool = False,
        has_business_income: bool = False,
        is_presumptive_business: bool = False,
        **extra_kwargs,
    ) -> TaxpayerProfileForITR:
        """
        Helper method to construct a TaxpayerProfileForITR from a standard TaxpayerProfileInput.
        """
        # Calculate gross income estimate
        gross_salary = (
            profile.salary.gross_salary_sec_17_1
            or profile.salary.basic_salary + profile.salary.dearness_allowance + profile.salary.hra_received
        )
        other_inc = (
            profile.other_sources.savings_bank_interest
            + profile.other_sources.fixed_deposit_interest
            + profile.other_sources.dividend_income
            + profile.other_sources.family_pension
            + profile.other_sources.other_taxable_income
        )
        hp_rent = profile.house_property.annual_lettable_value_or_rent
        total_inc = gross_salary + other_inc + max(0.0, hp_rent)

        hp_count = 1
        if hp_rent > 0 and (profile.house_property.housing_loan_interest_sop > 0):
            hp_count = 2

        cg_detail = CapitalGainsDetail(has_capital_gains=has_capital_gains)
        bp_detail = BusinessProfessionDetail(
            has_business_or_profession_income=has_business_income,
            is_presumptive_44ad=is_presumptive_business,
        )

        return TaxpayerProfileForITR(
            filing_type=TaxpayerFilingType.INDIVIDUAL,
            residential_status=residential_status,
            total_income=round(total_inc, 2),
            has_salary_income=gross_salary > 0,
            salary_income_amount=round(gross_salary, 2),
            house_property_count=hp_count,
            has_other_sources_income=other_inc > 0,
            other_sources_amount=round(other_inc, 2),
            is_director_in_company=is_director,
            holds_unlisted_equity_shares=holds_unlisted_shares,
            has_foreign_assets_or_income=has_foreign_assets,
            capital_gains=cg_detail,
            business_profession=bp_detail,
            **extra_kwargs,
        )

    @staticmethod
    def _get_statutory_disclaimers() -> list[str]:
        """Statutory legal disclaimers for ITR recommendation."""
        return [
            "This ITR recommendation is deterministically computed based strictly on the income sources and profile parameters submitted.",
            "Under Section 139(1) of the Income-tax Act, 1961, taxpayers are responsible for the complete accuracy and veracity of declared income.",
            "If you have unreported income from virtual digital assets, foreign bank accounts, or capital gains, you must attach the required statutory schedules.",
            "This output does not constitute formal legal or tax advice. For complex corporate or cross-border filings, consultation with a qualified Chartered Accountant (CA) is recommended.",
        ]

    @staticmethod
    def _build_filing_notes(recommended: ITRFormType, profile: TaxpayerProfileForITR) -> list[str]:
        """Build contextual filing instructions and mandatory schedule reminders."""
        notes: list[str] = []

        if recommended == ITRFormType.ITR_1_SAHAJ:
            notes.append("ITR-1 (Sahaj) is a simplified single-page summary return. No Annexure/Schedule attachments required.")
            if profile.total_income > 4500000.0:
                notes.append("Note: Approaching the ₹50 Lakh threshold. If actual income exceeds ₹50 Lakhs upon AIS reconciliation, switch to ITR-2.")

        elif recommended == ITRFormType.ITR_2:
            if profile.total_income > 5000000.0:
                notes.append("Mandatory Schedule AL (Assets and Liabilities) must be completed as total income exceeds ₹50 Lakhs.")
            if profile.capital_gains.has_capital_gains:
                notes.append("Schedule CG (Capital Gains) and Schedule 112A/111A must be populated for equity and mutual fund gains.")
            if profile.has_foreign_assets_or_income:
                notes.append("Schedule FA (Foreign Assets) and Schedule FSI (Foreign Source Income) are mandatory. Non-disclosure carries severe penalties under the Black Money Act.")
            if profile.is_director_in_company:
                notes.append("Provide Director Identification Number (DIN) and Company PAN in the Part A General schedule.")

        elif recommended == ITRFormType.ITR_3:
            notes.append("Schedule P&L and Schedule BS must be completed unless declaring presumptive income.")
            if profile.business_profession.is_books_audited_44ab:
                notes.append("Form 3CA/3CB and Form 3CD (Tax Audit Report) must be filed electronically prior to the statutory deadline.")
            if profile.business_profession.is_partner_in_firm:
                notes.append("Report partner salary, interest on capital, and profit share in Schedule IF and Schedule BP.")

        elif recommended == ITRFormType.ITR_4_SUGAM:
            notes.append("Schedule BP (Presumptive Business) requires disclosure of Gross Turnover, Bank Receipts, and Cash Receipts.")
            notes.append("Mandatory minimum net profit rate: 8% (or 6% for digital receipts) u/s 44AD; 50% u/s 44ADA.")

        return notes
