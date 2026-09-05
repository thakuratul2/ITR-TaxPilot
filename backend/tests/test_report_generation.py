"""Unit and integration test suite for Milestone 13: Report Generation."""

import pymupdf
from fastapi.testclient import TestClient

from app.services.report_service import ReportService


def test_pdf_report_generation_valid_bytes():
    """Test generating PDF report bytes with valid structure and PDF header."""
    sample_data = {
        "assessment_year": "2026-27",
        "financial_year": "2025-26",
        "recommended_regime": "NEW",
        "tax_savings": 49400.0,
        "recommended_itr": "ITR-1 (Sahaj)",
        "explanation": "New Tax Regime saves INR 49,400.",
        "calculations": [
            {"regime": "OLD", "gross_income": 1200000.0, "total_deductions": 200000.0, "taxable_income": 1000000.0, "total_tax_liability": 117000.0, "tds_credit": 120000.0, "refund_due": 3000.0, "tax_payable": 0.0},
            {"regime": "NEW", "gross_income": 1200000.0, "total_deductions": 75000.0, "taxable_income": 1125000.0, "total_tax_liability": 67600.0, "tds_credit": 120000.0, "refund_due": 52400.0, "tax_payable": 0.0},
        ],
    }

    pdf_bytes = ReportService.generate_tax_report_pdf(
        analysis_id="test-analysis-pdf-1",
        data=sample_data,
        taxpayer_pan="ABCDE1234F",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")

    # Read back generated PDF using PyMuPDF
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    assert len(doc) >= 1
    page_text = doc[0].get_text("text")
    doc.close()

    assert "ITR-TaxPilot" in page_text
    assert "AY: 2026-27" in page_text
    assert "ABCDE****F" in page_text
    assert "ABCDE1234F" not in page_text  # Verify PAN masking (Zero PII leakage)
    assert "Section 139(1)" in page_text
    assert "NEW TAX REGIME" in page_text


def test_pdf_report_download_analysis_endpoint(client: TestClient):
    """Test GET /api/v1/analysis/{analysis_id}/report/download streams PDF."""
    analysis_id = "test-analysis-dl-1"
    response = client.get(f"/api/v1/analysis/{analysis_id}/report/download")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "attachment" in response.headers.get("Content-Disposition", "")
    assert f"ITR_Tax_Report_{analysis_id}.pdf" in response.headers.get("Content-Disposition", "")
    assert response.content.startswith(b"%PDF-")


def test_pdf_report_download_reports_endpoint(client: TestClient):
    """Test GET /api/v1/reports/{analysis_id}/download streams PDF."""
    analysis_id = "test-rep-dl-2"
    response = client.get(f"/api/v1/reports/{analysis_id}/download")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")


def test_get_report_metadata_endpoint(client: TestClient):
    """Test GET /api/v1/reports/{analysis_id} returns report metadata."""
    analysis_id = "test-meta-3"
    response = client.get(f"/api/v1/reports/{analysis_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["analysis_id"] == analysis_id
    assert data["data"]["assessment_year"] == "2026-27"
    assert data["data"]["report_download_url"] == f"/api/v1/reports/{analysis_id}/download"


def test_pdf_report_with_comparison_engine_output():
    """Test PDF report generation directly with full comparison model payload."""
    from app.calculator.models import SalaryInput, TaxpayerProfileInput
    from app.comparison.comparison_engine import ComparisonEngine

    profile = TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(gross_salary_sec_17_1=1500000.0, basic_salary=1500000.0),
    )
    comp_resp = ComparisonEngine.compare_comprehensive(profile)
    pdf_bytes = ReportService.generate_tax_report_pdf(
        analysis_id="test-full-comp-1",
        data={"comparison": comp_resp.model_dump(), "assessment_year": "2026-27"},
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")
