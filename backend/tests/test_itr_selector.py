"""Unit and integration test suite for Milestone 9: Deterministic ITR Recommendation Engine."""

from app.calculator.models import (
    HousePropertyInput,
    OtherSourcesInput,
    PropertyType,
    SalaryInput,
    TaxpayerProfileInput,
)
from app.tax.itr_models import (
    BusinessProfessionDetail,
    CapitalGainsDetail,
    ITRFormType,
    ResidentialStatus,
    TaxpayerFilingType,
    TaxpayerProfileForITR,
)
from app.tax.itr_selector import ITRSelector

# ---------------------------------------------------------------------------
# 1. ITR-1 (Sahaj) Unit Tests
# ---------------------------------------------------------------------------

def test_itr1_pure_salaried_under_50_lakhs():
    """Resident individual with salary income <= ₹50L and bank interest qualifies for ITR-1."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1200000.0,
        has_salary_income=True,
        salary_income_amount=1200000.0,
        house_property_count=1,
        has_other_sources_income=True,
        other_sources_amount=25000.0,
        agricultural_income=0.0,
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_1_SAHAJ
    assert rec.confidence_score == 1.0
    assert "ITR-1 (Sahaj) is recommended" in rec.summary_rationale
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is True
    assert len(rec.eligibility_reasons) > 0


def test_itr1_with_single_house_property_and_agricultural_income_5000():
    """Agricultural income <= ₹5,000 and 1 house property remains eligible for ITR-1."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=3500000.0,
        has_salary_income=True,
        house_property_count=1,
        agricultural_income=5000.0,  # Exact statutory boundary
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_1_SAHAJ
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is True


# ---------------------------------------------------------------------------
# 2. ITR-1 Disqualification & Escalation to ITR-2 Tests
# ---------------------------------------------------------------------------

def test_itr1_disqualification_income_above_50_lakhs():
    """Total income exceeding ₹50,00,000 disqualifies ITR-1 and escalates to ITR-2."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=5500000.0,
        has_salary_income=True,
        salary_income_amount=5500000.0,
        house_property_count=1,
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False
    assert any("exceeds the ₹50,00,000 limit" in d for d in rec.disqualification_reasons_for_other_forms[ITRFormType.ITR_1_SAHAJ.value])
    assert any("Schedule AL" in note for note in rec.notes_and_limitations)


def test_itr1_disqualification_multiple_house_properties():
    """Owning multiple house properties disqualifies ITR-1 and escalates to ITR-2."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1800000.0,
        has_salary_income=True,
        house_property_count=2,  # 2 properties
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False
    assert any("more than one house property" in d for d in rec.disqualification_reasons_for_other_forms[ITRFormType.ITR_1_SAHAJ.value])


def test_itr1_disqualification_brought_forward_hp_loss():
    """Brought forward house property loss disqualifies ITR-1 and requires ITR-2."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1500000.0,
        has_salary_income=True,
        house_property_count=1,
        has_brought_forward_hp_loss=True,
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False


def test_itr1_disqualification_capital_gains():
    """Short-term or long-term capital gains disqualifies ITR-1 and escalates to ITR-2."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=2200000.0,
        has_salary_income=True,
        house_property_count=1,
        capital_gains=CapitalGainsDetail(
            has_capital_gains=True,
            short_term_capital_gains_111a=75000.0,
            long_term_capital_gains_112a=150000.0,
        ),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False
    assert any("Schedule CG" in note for note in rec.notes_and_limitations)


def test_itr1_disqualification_virtual_digital_assets():
    """Crypto / Virtual Digital Asset income disqualifies ITR-1 and requires ITR-2."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1600000.0,
        has_salary_income=True,
        capital_gains=CapitalGainsDetail(has_virtual_digital_assets=True),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False


def test_itr1_disqualification_foreign_assets_or_income():
    """Holding foreign bank accounts or overseas ESOPs disqualifies ITR-1 and requires ITR-2."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=2500000.0,
        has_salary_income=True,
        has_foreign_assets_or_income=True,
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False
    assert any("Schedule FA" in note for note in rec.notes_and_limitations)


def test_itr1_disqualification_director_or_unlisted_shares():
    """Being a company director or holding unlisted equity shares escalates to ITR-2."""
    profile_director = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1800000.0,
        is_director_in_company=True,
    )
    rec_dir = ITRSelector.recommend(profile_director)
    assert rec_dir.recommended_form == ITRFormType.ITR_2

    profile_unlisted = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1800000.0,
        holds_unlisted_equity_shares=True,
    )
    rec_unl = ITRSelector.recommend(profile_unlisted)
    assert rec_unl.recommended_form == ITRFormType.ITR_2


def test_itr1_disqualification_agricultural_income_above_5000():
    """Agricultural income > ₹5,000 escalates to ITR-2 for Schedule EI filing."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1400000.0,
        agricultural_income=25000.0,
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_2
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False


def test_itr1_disqualification_non_resident_or_rnor():
    """Non-Residents and RNOR cannot file ITR-1 or ITR-4, and must file ITR-2 (or ITR-3)."""
    profile_nr = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.NON_RESIDENT,
        total_income=1500000.0,
        has_salary_income=True,
    )
    rec_nr = ITRSelector.recommend(profile_nr)
    assert rec_nr.recommended_form == ITRFormType.ITR_2

    profile_rnor = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RNOR,
        total_income=1500000.0,
        has_salary_income=True,
    )
    rec_rnor = ITRSelector.recommend(profile_rnor)
    assert rec_rnor.recommended_form == ITRFormType.ITR_2


# ---------------------------------------------------------------------------
# 3. ITR-4 (Sugam) Presumptive Taxation Tests
# ---------------------------------------------------------------------------

def test_itr4_sugam_presumptive_business_44ad():
    """Resident individual with 44AD presumptive business income <= ₹50L qualifies for ITR-4."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=2800000.0,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            is_presumptive_44ad=True,
            gross_turnover_or_receipts=15000000.0,
            presumptive_net_profit=1200000.0,
        ),
        house_property_count=1,
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_4_SUGAM
    assert rec.all_form_evaluations[ITRFormType.ITR_4_SUGAM.value].is_eligible is True
    assert rec.all_form_evaluations[ITRFormType.ITR_1_SAHAJ.value].is_eligible is False
    assert any("Schedule BP" in note for note in rec.notes_and_limitations)


def test_itr4_sugam_presumptive_profession_44ada():
    """Freelance software consultant under Section 44ADA qualifies for ITR-4."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=3200000.0,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            is_presumptive_44ada=True,
            gross_turnover_or_receipts=4000000.0,
            presumptive_net_profit=2500000.0,
        ),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_4_SUGAM
    assert rec.all_form_evaluations[ITRFormType.ITR_4_SUGAM.value].is_eligible is True


def test_itr4_disqualification_tax_audit_44ab_escalates_to_itr3():
    """Business requiring Section 44AB tax audit is disqualified from ITR-4 and requires ITR-3."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=4500000.0,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            is_presumptive_44ad=True,
            is_books_audited_44ab=True,
        ),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_3
    assert rec.all_form_evaluations[ITRFormType.ITR_4_SUGAM.value].is_eligible is False
    assert any("Form 3CA/3CB" in note for note in rec.notes_and_limitations)


def test_itr4_disqualification_partner_in_firm_escalates_to_itr3():
    """Partner in a partnership firm cannot file ITR-4 and must file ITR-3."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=2500000.0,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            is_partner_in_firm=True,
        ),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_3
    assert rec.all_form_evaluations[ITRFormType.ITR_4_SUGAM.value].is_eligible is False


def test_itr4_disqualification_capital_gains_with_business():
    """Taxpayer with presumptive business AND capital gains must file ITR-3."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=3000000.0,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            is_presumptive_44ad=True,
        ),
        capital_gains=CapitalGainsDetail(
            has_capital_gains=True,
            short_term_capital_gains_111a=50000.0,
        ),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_3


def test_itr4_disqualification_income_above_50_lakhs_with_business():
    """Presumptive business with total income > ₹50L escalates to ITR-3."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=6500000.0,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            is_presumptive_44ad=True,
        ),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_3


# ---------------------------------------------------------------------------
# 4. ITR-3 Unit Tests & ITR-2 Prohibition Tests
# ---------------------------------------------------------------------------

def test_itr3_comprehensive_business_with_salary_and_multiple_properties():
    """Taxpayer with regular proprietary business, salary, and multiple properties requires ITR-3."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=8500000.0,
        has_salary_income=True,
        house_property_count=3,
        business_profession=BusinessProfessionDetail(
            has_business_or_profession_income=True,
            has_speculative_income=True,  # Intraday / F&O trading
        ),
        capital_gains=CapitalGainsDetail(has_capital_gains=True),
    )

    rec = ITRSelector.recommend(profile)
    assert rec.recommended_form == ITRFormType.ITR_3
    assert rec.all_form_evaluations[ITRFormType.ITR_3.value].is_eligible is True
    # Verify strict prohibition in ITR-2
    assert rec.all_form_evaluations[ITRFormType.ITR_2.value].is_eligible is False
    assert any("strictly prohibited for taxpayers with income from Profits and Gains" in d for d in rec.all_form_evaluations[ITRFormType.ITR_2.value].disqualifications)


def test_itr2_strictly_disqualified_with_any_business_income():
    """Check that evaluate_itr2 strictly returns is_eligible=False when business income is present."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=2000000.0,
        business_profession=BusinessProfessionDetail(has_business_or_profession_income=True),
    )

    eval_res = ITRSelector.evaluate_itr2(profile)
    assert eval_res.is_eligible is False
    assert len(eval_res.disqualifications) > 0


# ---------------------------------------------------------------------------
# 5. Non-Individual Entity & Disclaimers Tests
# ---------------------------------------------------------------------------

def test_non_individual_entity_rejection():
    """Companies and LLPs cannot file individual forms."""
    profile_company = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.COMPANY,
        total_income=50000000.0,
    )
    rec = ITRSelector.recommend(profile_company)
    assert rec.recommended_form == ITRFormType.NOT_ELIGIBLE_INDIVIDUAL
    assert "ITR-5" in rec.summary_rationale or "ITR-6" in rec.summary_rationale


def test_recommendation_payload_completeness():
    """Verify all statutory disclaimers, authority, and evaluations are present."""
    profile = TaxpayerProfileForITR(
        filing_type=TaxpayerFilingType.INDIVIDUAL,
        residential_status=ResidentialStatus.RESIDENT,
        total_income=1000000.0,
    )
    rec = ITRSelector.recommend(profile)
    assert len(rec.statutory_disclaimers) >= 3
    assert "Income Tax Department" in rec.statutory_authority
    assert len(rec.all_form_evaluations) == 4
    assert ITRFormType.ITR_1_SAHAJ.value in rec.all_form_evaluations
    assert ITRFormType.ITR_2.value in rec.all_form_evaluations
    assert ITRFormType.ITR_3.value in rec.all_form_evaluations
    assert ITRFormType.ITR_4_SUGAM.value in rec.all_form_evaluations


# ---------------------------------------------------------------------------
# 6. Helper & Profile Conversion Tests
# ---------------------------------------------------------------------------

def test_from_taxpayer_profile_input_conversion():
    """Verify from_taxpayer_profile_input maps properties cleanly."""
    profile_input = TaxpayerProfileInput(
        salary=SalaryInput(basic_salary=1500000.0, hra_received=300000.0),
        house_property=HousePropertyInput(
            property_type=PropertyType.LET_OUT,
            annual_lettable_value_or_rent=360000.0,
            housing_loan_interest_sop=150000.0,
        ),
        other_sources=OtherSourcesInput(savings_bank_interest=45000.0),
    )

    itr_profile = ITRSelector.from_taxpayer_profile_input(
        profile_input,
        residential_status=ResidentialStatus.RESIDENT,
        has_capital_gains=False,
    )

    assert itr_profile.total_income > 2000000.0
    assert itr_profile.house_property_count == 2
    assert itr_profile.has_salary_income is True

    rec = ITRSelector.recommend(itr_profile)
    # 2 house properties should route to ITR-2
    assert rec.recommended_form == ITRFormType.ITR_2
