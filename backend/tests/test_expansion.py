"""Tests for Milestone 18: Expansion & Post-MVP modules."""

import pytest
from app.expansion import (
    AISParser,
    AISSummary,
    AggregatedSalaryProfile,
    AssetType,
    BankAccount,
    CapitalGainTransaction,
    CapitalGainsEngine,
    CapitalGainsSummary,
    DocumentVaultService,
    EmployerForm16Input,
    Form26ASData,
    HoldingType,
    ITR1ExportPayload,
    ITRJSONExporter,
    MultiForm16Aggregator,
    PersonalInfo,
    TaxCreditReconciler,
    TDSEntry,
)
from app.tax.rules.base import TaxRegime


# ---------------------------------------------------------------------------
# 1. TASK-18.1: AIS / TIS Parsing Tests
# ---------------------------------------------------------------------------
def test_ais_parser_json_payload():
    ais_json = """{
        "pan": "ABCDE1234F",
        "assessment_year": "2025-26",
        "savings_bank_interest": 12500.0,
        "fixed_deposit_interest": 45000.0,
        "dividend_income": 8000.0,
        "securities_sale_proceeds": 250000.0,
        "mutual_fund_purchases": 100000.0,
        "total_tds_reported": 4500.0,
        "sft_transactions": [
            {
                "code": "SFT-005",
                "description": "Time deposit exceeding 10 Lakhs",
                "reporting_entity": "HDFC Bank Ltd",
                "amount": 1050000.0,
                "date": "2024-11-15"
            }
        ]
    }"""
    summary = AISParser.parse_ais_json(ais_json)
    assert isinstance(summary, AISSummary)
    assert summary.pan == "ABCDE1234F"
    assert summary.savings_interest == 12500.0
    assert summary.term_deposit_interest == 45000.0
    assert summary.dividend_income == 8000.0
    assert summary.total_tax_deducted_reported == 4500.0
    assert len(summary.high_value_transactions) == 1
    assert summary.high_value_transactions[0].source_reporting_entity == "HDFC Bank Ltd"


# ---------------------------------------------------------------------------
# 2. TASK-18.2: Form 26AS Tax Credit Reconciliation Tests
# ---------------------------------------------------------------------------
def test_26as_reconciliation_perfect_match():
    f16_entries = [
        TDSEntry(
            deductor_tan="KOLT12345A",
            deductor_name="Acme Tech India Pvt Ltd",
            total_amount_paid=1200000.0,
            total_tds_deducted=85000.0,
            total_tds_deposited=85000.0,
        )
    ]
    form_26as = Form26ASData(
        pan="ABCDE1234F",
        assessment_year="2025-26",
        financial_year="2024-25",
        part_a_tds_salary=[
            TDSEntry(
                deductor_tan="KOLT12345A",
                deductor_name="Acme Tech India Pvt Ltd",
                total_amount_paid=1200000.0,
                total_tds_deducted=85000.0,
                total_tds_deposited=85000.0,
            )
        ],
        part_c_advance_tax=10000.0,
    )

    report = TaxCreditReconciler.reconcile(f16_entries, form_26as)
    assert report.is_fully_reconciled is True
    assert len(report.mismatches) == 0
    assert report.total_form16_tds == 85000.0
    assert report.total_26as_tds == 85000.0
    assert report.total_advance_tax_claimed == 10000.0


def test_26as_reconciliation_mismatch_and_missing_tan():
    f16_entries = [
        TDSEntry(
            deductor_tan="MUMB99999Z",
            deductor_name="Delta Services Ltd",
            total_amount_paid=800000.0,
            total_tds_deducted=50000.0,
            total_tds_deposited=50000.0,
        ),
        TDSEntry(
            deductor_tan="DELA11111B",
            deductor_name="Alpha Infotech",
            total_amount_paid=400000.0,
            total_tds_deducted=20000.0,
            total_tds_deposited=20000.0,
        ),
    ]
    form_26as = Form26ASData(
        pan="ABCDE1234F",
        assessment_year="2025-26",
        financial_year="2024-25",
        part_a_tds_salary=[
            TDSEntry(
                deductor_tan="MUMB99999Z",
                deductor_name="Delta Services Ltd",
                total_amount_paid=800000.0,
                total_tds_deducted=35000.0,
                total_tds_deposited=35000.0,  # ₹15,000 short in 26AS
            )
        ],
    )

    report = TaxCreditReconciler.reconcile(f16_entries, form_26as)
    assert report.is_fully_reconciled is False
    assert len(report.mismatches) == 2
    # Mismatch 1: Short deposit
    m1 = next(m for m in report.mismatches if m.deductor_tan == "MUMB99999Z")
    assert m1.difference == 15000.0
    # Mismatch 2: Missing TAN
    m2 = next(m for m in report.mismatches if m.deductor_tan == "DELA11111B")
    assert m2.difference == 20000.0


# ---------------------------------------------------------------------------
# 3. TASK-18.3: Capital Gains Engine Tests
# ---------------------------------------------------------------------------
def test_capital_gains_stcg_and_ltcg_with_exemption():
    transactions = [
        # STCG 111A: Buy ₹50,000, Sell ₹80,000 -> Gain ₹30,000
        CapitalGainTransaction(
            isin="INE002A01018",
            asset_name="Reliance Industries",
            asset_type=AssetType.EQUITY_SHARE_LISTED,
            buy_date="2024-05-10",
            sell_date="2024-09-15",
            buy_value=50000.0,
            sell_value=80000.0,
            holding_type=HoldingType.SHORT_TERM,
        ),
        # LTCG 112A: Buy ₹200,000, Sell ₹375,000 -> Gain ₹175,000 (₹1.25L exempt, ₹50,000 taxable at 12.5%)
        CapitalGainTransaction(
            isin="INF179K01BE2",
            asset_name="HDFC Flexi Cap Fund",
            asset_type=AssetType.EQUITY_MUTUAL_FUND,
            buy_date="2022-01-10",
            sell_date="2024-10-20",
            buy_value=200000.0,
            sell_value=375000.0,
            holding_type=HoldingType.LONG_TERM,
        ),
    ]

    summary = CapitalGainsEngine.compute_gains(transactions)
    assert summary.stcg_sec111a_equity == 30000.0
    assert summary.ltcg_sec112a_exempt_claimed == 125000.0
    assert summary.ltcg_sec112a_equity == 50000.0
    # STCG Tax: 30,000 * 20% = 6,000
    # LTCG Tax: 50,000 * 12.5% = 6,250
    # Base Tax = 12,250 + 4% cess (490) = 12,740.0
    assert summary.total_capital_gains_tax == 12740.0
    assert summary.requires_itr2_or_itr3 is True


# ---------------------------------------------------------------------------
# 4. TASK-18.4: Multi-Employer Form 16 Aggregator Tests
# ---------------------------------------------------------------------------
def test_multi_form16_aggregator():
    f16_employer1 = EmployerForm16Input(
        employer_name="Company A",
        employer_tan="BLRA12345A",
        gross_salary_sec17_1=600000.0,
        standard_deduction_claimed=75000.0,
        tds_deducted=20000.0,
    )
    f16_employer2 = EmployerForm16Input(
        employer_name="Company B",
        employer_tan="PUNB67890B",
        gross_salary_sec17_1=800000.0,
        standard_deduction_claimed=75000.0,
        tds_deducted=40000.0,
    )

    aggregated = MultiForm16Aggregator.aggregate(
        [f16_employer1, f16_employer2],
        regime=TaxRegime.NEW,
        assessment_year="2025-26",
    )

    assert aggregated.number_of_employers == 2
    assert aggregated.total_gross_salary_sec17 == 1400000.0
    # Standard deduction should be capped at ₹75,000 once (not ₹1,50,000)
    assert aggregated.consolidated_standard_deduction == 75000.0
    assert aggregated.total_tds_deducted == 60000.0
    assert aggregated.duplicate_standard_deduction_warning is True
    assert aggregated.potential_tax_shortfall_warning is True
    assert len(aggregated.warnings) >= 2


# ---------------------------------------------------------------------------
# 5. TASK-18.5: CBDT ITR JSON Export & Schema Validation Tests
# ---------------------------------------------------------------------------
def test_itr_json_exporter_and_validation():
    payload = ITR1ExportPayload(
        assessment_year="2025-26",
        regime_selected=TaxRegime.NEW,
        personal_info=PersonalInfo(
            pan="ABCDE1234F",
            first_name="Rahul",
            last_name="Sharma",
            dob="1990-05-15",
            aadhaar_number="123456789012",
            mobile="9876543210",
            email="rahul.sharma@example.com",
            city="Bengaluru",
            state="29",
            pincode="560001",
        ),
        gross_salary=1200000.0,
        standard_deduction=75000.0,
        income_from_salary=1125000.0,
        gross_total_income=1125000.0,
        total_taxable_income=1125000.0,
        total_tax_computed=75000.0,
        health_and_education_cess=3000.0,
        total_tax_liability=78000.0,
        total_tds_claimed=85000.0,
        net_tax_payable_or_refund=-7000.0,
        is_refund=True,
        bank_accounts=[
            BankAccount(
                account_number="12345678901234",
                ifsc_code="HDFC0001234",
                bank_name="HDFC Bank",
                selected_for_refund=True,
            )
        ],
    )

    schema_dict = ITRJSONExporter.generate_itr1_json(payload)
    assert "ITR" in schema_dict
    assert schema_dict["ITR"]["ITR1"]["PersonalInfo"]["PAN"] == "ABCDE1234F"
    assert schema_dict["ITR"]["ITR1"]["TaxComputation"]["RefundDue"] == 7000.0

    errors = ITRJSONExporter.validate_schema(schema_dict)
    assert len(errors) == 0

    json_str = ITRJSONExporter.export_to_json_string(payload)
    assert "ABCDE1234F" in json_str
    assert "HDFC0001234" in json_str


# ---------------------------------------------------------------------------
# 6. TASK-18.6: Secure Tax Vault Service Tests
# ---------------------------------------------------------------------------
def test_vault_service_lifecycle():
    vault_service = DocumentVaultService()
    user_id = "user_test_999"
    pan = "ABCDE1234F"

    # 1. Add document
    doc = vault_service.add_document(
        user_id=user_id,
        pan=pan,
        assessment_year="2025-26",
        doc_type="FORM16",
        filename="Form16_FY2425.pdf",
        file_size_bytes=245000,
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    assert doc.doc_type == "FORM16"
    assert doc.is_encrypted is True

    # 2. Record Filing
    filing = vault_service.record_filing(
        user_id=user_id,
        pan=pan,
        assessment_year="2025-26",
        regime="NEW",
        gross_income=1200000.0,
        total_tax_paid=78000.0,
        refund_or_due_amount=7000.0,
        is_refund=True,
        ack_number="ACK1234567890",
    )
    assert filing.assessment_year == "2025-26"

    # 3. Query documents
    docs_2526 = vault_service.list_documents_by_ay(user_id, "2025-26")
    assert len(docs_2526) == 1
    assert docs_2526[0].filename == "Form16_FY2425.pdf"

    history = vault_service.get_filing_history(user_id)
    assert len(history) == 1
    assert history[0].acknowledgment_number == "ACK1234567890"

    # 4. DPDP Act Data Export
    exported = vault_service.export_user_data(user_id)
    assert exported is not None
    assert exported["pan"] == "ABCDE1234F"
    assert len(exported["documents"]) == 1

    # 5. Right to Erasure / Purge
    assert vault_service.purge_user_vault(user_id) is True
    assert vault_service.export_user_data(user_id) is None
