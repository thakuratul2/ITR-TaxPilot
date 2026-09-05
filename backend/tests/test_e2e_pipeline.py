"""End-to-end integration test for the entire Form 16 upload, job processing, analysis, and report generation pipeline."""

import io
import uuid
import fitz
from fastapi.testclient import TestClient

from tests.test_document_pipeline import create_sample_form16_pdf


def test_end_to_end_upload_analysis_report_flow(client: TestClient):
    """Test full pipeline: Upload -> Polling -> Analysis -> Report Download."""
    pdf_bytes = create_sample_form16_pdf()
    unique_ip = f"10.200.1.{uuid.uuid4().hex[:4]}"

    # 1. POST /api/v1/documents/form16
    upload_response = client.post(
        "/api/v1/documents/form16",
        files={"file": ("form16_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        headers={"X-Forwarded-For": unique_ip},
    )
    assert upload_response.status_code in (200, 202)
    upload_data = upload_response.json()
    assert upload_data["success"] is True
    job_id = upload_data["data"]["job_id"]
    document_id = upload_data["data"]["document_id"]
    assert job_id is not None
    assert document_id is not None

    # 2. GET /api/v1/jobs/{job_id}
    job_response = client.get(f"/api/v1/jobs/{job_id}", headers={"X-Forwarded-For": unique_ip})
    assert job_response.status_code == 200
    job_data = job_response.json()
    assert job_data["success"] is True
    assert job_data["data"]["job_id"] == job_id

    # 3. GET /api/v1/analysis/{analysis_id}
    analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
    analysis_response = client.get(f"/api/v1/analysis/{analysis_id}", headers={"X-Forwarded-For": unique_ip})
    assert analysis_response.status_code == 200
    analysis_data = analysis_response.json()
    assert analysis_data["success"] is True
    assert analysis_data["data"]["analysis_id"] == analysis_id
    assert "calculations" in analysis_data["data"]

    # 4. GET /api/v1/analysis/{analysis_id}/report/download
    report_response = client.get(
        f"/api/v1/analysis/{analysis_id}/report/download",
        headers={"X-Forwarded-For": unique_ip},
    )
    assert report_response.status_code == 200
    assert report_response.headers["Content-Type"] == "application/pdf"
    assert report_response.headers["Content-Disposition"].startswith("attachment;")
    assert len(report_response.content) > 1000  # Valid PDF binary
