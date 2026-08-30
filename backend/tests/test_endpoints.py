"""Tests for Milestone 2 API routes and stubs."""

import io

from fastapi.testclient import TestClient

from tests.test_document_pipeline import create_sample_form16_pdf


def test_upload_form16_success(client: TestClient):
    """Test POST /api/v1/documents/form16 with valid PDF."""
    pdf_content = create_sample_form16_pdf()
    files = {"file": ("form16_2026.pdf", io.BytesIO(pdf_content), "application/pdf")}

    response = client.post("/api/v1/documents/form16", files=files)
    assert response.status_code == 202

    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None
    assert "document_id" in payload["data"]
    assert "job_id" in payload["data"]
    assert payload["data"]["status"] == "pending"


def test_upload_invalid_mime_type(client: TestClient):
    """Test POST /api/v1/documents/form16 with unsupported MIME type returns 415."""
    txt_content = b"Not a PDF file"
    files = {"file": ("form16.txt", io.BytesIO(txt_content), "text/plain")}

    response = client.post("/api/v1/documents/form16", files=files)
    assert response.status_code == 415

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INVALID_FILE_FORMAT"


def test_get_job_status(client: TestClient):
    """Test GET /api/v1/jobs/{job_id}."""
    test_job_id = "test-job-uuid-123"
    response = client.get(f"/api/v1/jobs/{test_job_id}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["job_id"] == test_job_id
    assert payload["data"]["status"] == "processing"
    assert payload["data"]["progress_percentage"] >= 0


def test_get_analysis_result(client: TestClient):
    """Test GET /api/v1/analysis/{analysis_id}."""
    test_analysis_id = "test-analysis-uuid-456"
    response = client.get(f"/api/v1/analysis/{test_analysis_id}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["analysis_id"] == test_analysis_id
    assert payload["data"]["assessment_year"] == "2026-27"
    assert len(payload["data"]["calculations"]) == 2
    assert payload["data"]["calculations"][0]["regime"] in ["OLD", "NEW"]


def test_frontend_index_route(client: TestClient):
    """Test GET / serves the frontend single page app."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ITR-TaxPilot" in response.text
    assert "Section 115BAC" in response.text


def test_admin_ai_providers_endpoint(client: TestClient):
    """Test GET /api/v1/admin/ai-providers returns configured providers."""
    response = client.get("/api/v1/admin/ai-providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["provider"] == "OpenAI" for p in data)
    assert any(p["provider"] == "Google Gemini" for p in data)
    assert any(p["provider"] == "Anthropic Claude" for p in data)


def test_frontend_admin_page_route(client: TestClient):
    """Test GET /admin.html serves the admin dashboard."""
    response = client.get("/admin.html")
    assert response.status_code == 200
    assert "Admin & Telemetry Portal" in response.text
