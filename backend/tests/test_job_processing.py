"""Tests for background job lifecycle and worker pipeline."""

import pytest
from fastapi.testclient import TestClient

from app.models.job import JobStatus, JobType
from app.services.job_service import JobService
from tests.test_document_pipeline import create_sample_form16_pdf


@pytest.mark.asyncio
async def test_job_lifecycle_state_transitions():
    """Test full job lifecycle state progression: QUEUED -> EXTRACTING -> CALCULATING -> COMPLETED."""
    # 1. Create Job (QUEUED)
    job = await JobService.create_job(document_id="test-doc-lifecycle-1", job_type=JobType.FORM16_EXTRACTION)
    assert job.status == JobStatus.QUEUED.value
    assert job.progress_percentage == 0
    assert job.job_id is not None

    # 2. Transition to EXTRACTING (30%)
    job = await JobService.update_job(
        job_id=job.job_id,
        status=JobStatus.EXTRACTING,
        progress_percentage=30,
        step_description="Parsing Form 16 text",
    )
    assert job.status == JobStatus.EXTRACTING.value
    assert job.progress_percentage == 30

    # 3. Transition to CALCULATING (70%)
    job = await JobService.update_job(
        job_id=job.job_id,
        status=JobStatus.CALCULATING,
        progress_percentage=70,
        step_description="Running tax rules",
    )
    assert job.status == JobStatus.CALCULATING.value
    assert job.progress_percentage == 70

    # 4. Transition to COMPLETED (100%)
    mock_result = {"tax_payable": 0, "regime": "NEW"}
    job = await JobService.update_job(
        job_id=job.job_id,
        status=JobStatus.COMPLETED,
        progress_percentage=100,
        step_description="Calculation complete",
        result_id="test-doc-lifecycle-1",
        result_data=mock_result,
    )
    assert job.status == JobStatus.COMPLETED.value
    assert job.progress_percentage == 100
    assert job.result_data == mock_result

    # 5. Verify retrieval via get_job
    fetched = await JobService.get_job(job.job_id)
    assert fetched is not None
    assert fetched.status == JobStatus.COMPLETED.value
    assert fetched.progress_percentage == 100
    assert fetched.result_id == "test-doc-lifecycle-1"


@pytest.mark.asyncio
async def test_job_failure_handling():
    """Test job error capturing and FAILED state transition."""
    job = await JobService.create_job(document_id="test-doc-fail-1")

    failed_job = await JobService.update_job(
        job_id=job.job_id,
        status=JobStatus.FAILED,
        progress_percentage=0,
        step_description="Processing failed",
        error_message="Corrupted PDF bytes encountered",
    )

    assert failed_job.status == JobStatus.FAILED.value
    assert failed_job.error_message == "Corrupted PDF bytes encountered"

    fetched = await JobService.get_job(job.job_id)
    assert fetched.status == JobStatus.FAILED.value
    assert fetched.error_message == "Corrupted PDF bytes encountered"


@pytest.mark.asyncio
async def test_background_worker_pipeline_execution():
    """Test non-blocking background document processing worker."""
    pdf_bytes = create_sample_form16_pdf()
    job = await JobService.create_job()

    task = JobService.start_background_processing(
        job_id=job.job_id,
        filename="worker_test.pdf",
        content_type="application/pdf",
        file_bytes=pdf_bytes,
    )

    # Await background worker completion
    await task

    # Verify completed job
    finished = await JobService.get_job(job.job_id)
    assert finished is not None
    assert finished.status == JobStatus.COMPLETED.value
    assert finished.progress_percentage == 100
    assert finished.result_data is not None
    assert "comparison" in finished.result_data
    assert "extracted" in finished.result_data


@pytest.mark.asyncio
async def test_job_polling_api_endpoint(client: TestClient):
    """Test GET /api/v1/jobs/{job_id} endpoint returns real data."""
    job = await JobService.create_job(document_id="doc_poll_test")
    await JobService.update_job(
        job_id=job.job_id,
        status=JobStatus.CALCULATING,
        progress_percentage=65,
        step_description="Testing polling endpoint",
    )

    response = client.get(f"/api/v1/jobs/{job.job_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["job_id"] == job.job_id
    assert body["data"]["status"] == "calculating"
    assert body["data"]["progress_percentage"] == 65
    assert body["data"]["step_description"] == "Testing polling endpoint"
