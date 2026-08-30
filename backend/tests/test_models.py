"""Unit tests for SQLAlchemy models."""

from app.models.analysis import Analysis, AnalysisStatus
from app.models.document import Document, DocumentStatus
from app.models.job import Job, JobStatus, JobType
from app.models.tax_calculation import TaxCalculation, TaxRegime


def test_document_model_creation():
    """Test creating a Document model instance."""
    doc = Document(
        id="doc-123",
        filename="sanitized_form16.pdf",
        original_filename="My Form 16.pdf",
        content_type="application/pdf",
        file_size_bytes=1048576,
        storage_path="/uploads/sanitized_form16.pdf",
        status=DocumentStatus.UPLOADED,
    )
    assert doc.id == "doc-123"
    assert doc.filename == "sanitized_form16.pdf"
    assert doc.status == DocumentStatus.UPLOADED
    assert doc.file_size_bytes == 1048576


def test_job_model_creation():
    """Test creating a Job model instance."""
    job = Job(
        id="job-123",
        document_id="doc-123",
        job_type=JobType.FORM16_EXTRACTION,
        status=JobStatus.PENDING,
        progress_percentage=0,
    )
    assert job.id == "job-123"
    assert job.status == JobStatus.PENDING
    assert job.job_type == JobType.FORM16_EXTRACTION


def test_analysis_model_creation():
    """Test creating an Analysis model instance."""
    analysis = Analysis(
        id="analysis-123",
        document_id="doc-123",
        assessment_year="2026-27",
        financial_year="2025-26",
        status=AnalysisStatus.EXTRACTED,
        extracted_data={"gross_salary": 1200000},
    )
    assert analysis.id == "analysis-123"
    assert analysis.assessment_year == "2026-27"
    assert analysis.status == AnalysisStatus.EXTRACTED


def test_tax_calculation_model_creation():
    """Test creating a TaxCalculation model instance."""
    calc = TaxCalculation(
        id="calc-123",
        analysis_id="analysis-123",
        assessment_year="2026-27",
        regime=TaxRegime.NEW,
        gross_income=1200000.0,
        total_deductions=75000.0,
        taxable_income=1125000.0,
        tax_before_rebate=65000.0,
        rebate_87a=0.0,
        cess=2600.0,
        total_tax_liability=67600.0,
        tds_credit=100000.0,
        tax_payable=0.0,
        refund_due=32400.0,
        calculation_breakdown={"slabs": []},
    )
    assert calc.regime == TaxRegime.NEW
    assert calc.refund_due == 32400.0
    assert calc.total_tax_liability == 67600.0
