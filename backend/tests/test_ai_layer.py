"""Comprehensive unit tests for Milestone 4 AI Extraction Layer."""

import pytest

from app.ai.confidence import calculate_field_confidence_scores
from app.ai.json_parser import parse_and_recover_llm_json
from app.ai.prompts.extraction_prompt import (
    EXTRACTION_PROMPT_VERSION,
    build_extraction_user_prompt,
)
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.factory import get_ai_provider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.schemas import (
    ExtractedChapterVIA,
    ExtractedEmployee,
    ExtractedEmployer,
    ExtractedForm16Data,
    ExtractedSalaryBreakdown,
    ExtractedTaxSummary,
)
from app.ai.verification import cross_verify_extractions
from app.documents.models import (
    DocumentClassification,
    ExtractedPage,
    NormalizedDocument,
)


def test_sanitize_and_recover_llm_json():
    """Test JSON parser handles markdown fencing, trailing commas, and numeric coercion."""
    raw_markdown = """```json
    {
      "assessment_year": "2026-27",
      "total_gross_salary": "12,00,000",
      "standard_deduction": "75,000",
      "items": [100, 200, ],
    }
    ```"""
    parsed = parse_and_recover_llm_json(raw_markdown)
    assert parsed["assessment_year"] == "2026-27"
    assert parsed["total_gross_salary"] == 1200000
    assert parsed["standard_deduction"] == 75000
    assert parsed["items"] == [100, 200]


def test_confidence_score_calculation():
    """Test field-level and overall confidence calculation."""
    extracted = ExtractedForm16Data(
        assessment_year="2026-27",
        financial_year="2025-26",
        employer=ExtractedEmployer(tan="DELA12345B"),
        employee=ExtractedEmployee(pan="ABCDE1234F"),
        salary=ExtractedSalaryBreakdown(
            gross_salary_sec_17_1=1200000.0,
            perquisites_sec_17_2=0.0,
            profits_in_lieu_sec_17_3=0.0,
            total_gross_salary=1200000.0,
            standard_deduction_sec_16_ia=75000.0,
            total_deductions_sec_16=75000.0,
            income_chargeable_salaries=1125000.0,
        ),
        deductions=ExtractedChapterVIA(
            section_80c=150000.0,
            total_chapter_via_deductions=150000.0,
        ),
        tax=ExtractedTaxSummary(
            total_taxable_income=975000.0,
            total_tds_deducted=65000.0,
        ),
    )

    scores = calculate_field_confidence_scores(extracted)
    assert scores["assessment_year"] == 1.0
    assert scores["employee_pan"] == 1.0
    assert scores["employer_tan"] == 1.0
    assert scores["total_gross_salary"] == 1.0
    assert scores["income_chargeable_salaries"] == 1.0
    assert scores["total_taxable_income"] == 1.0
    assert scores["overall"] >= 0.95


@pytest.mark.asyncio
async def test_gemini_provider_fallback_extraction():
    """Test Gemini provider extraction with fallback."""
    provider = GeminiProvider()
    doc = NormalizedDocument(
        document_id="doc-123",
        filename="form16.pdf",
        file_size_bytes=1024,
        total_pages=1,
        pages=[ExtractedPage(page_number=1, text="FORM NO. 16 Assessment Year: 2026-27")],
        classification=DocumentClassification(is_form16=True, detected_ay="2026-27"),
        full_text="FORM NO. 16 Assessment Year: 2026-27",
    )

    extracted = await provider.extract_form16(doc)
    assert extracted.assessment_year == "2026-27"
    assert extracted.salary.total_gross_salary == 1200000.0
    assert "overall" in extracted.confidence_scores


@pytest.mark.asyncio
async def test_claude_provider_fallback_extraction():
    """Test Claude provider extraction with fallback."""
    provider = ClaudeProvider()
    doc = NormalizedDocument(
        document_id="doc-456",
        filename="form16.pdf",
        file_size_bytes=1024,
        total_pages=1,
        pages=[ExtractedPage(page_number=1, text="FORM NO. 16 Assessment Year: 2026-27")],
        classification=DocumentClassification(is_form16=True, detected_ay="2026-27"),
        full_text="FORM NO. 16 Assessment Year: 2026-27",
    )

    extracted = await provider.extract_form16(doc)
    assert extracted.assessment_year == "2026-27"
    assert extracted.tax.total_taxable_income == 950000.0


def test_dual_model_verification_agreement():
    """Test cross-verification when both models agree."""
    doc_data = ExtractedForm16Data(
        assessment_year="2026-27",
        salary=ExtractedSalaryBreakdown(total_gross_salary=1000000.0, income_chargeable_salaries=925000.0),
        tax=ExtractedTaxSummary(total_taxable_income=925000.0, total_tds_deducted=50000.0),
    )
    doc_data2 = doc_data.model_copy(deep=True)

    verified, disagreements = cross_verify_extractions(doc_data, doc_data2)
    assert verified.has_dual_verification is True
    assert len(disagreements) == 0


def test_dual_model_verification_disagreement():
    """Test cross-verification flags discrepancies."""
    p = ExtractedForm16Data(
        assessment_year="2026-27",
        salary=ExtractedSalaryBreakdown(total_gross_salary=1000000.0, income_chargeable_salaries=925000.0),
        tax=ExtractedTaxSummary(total_taxable_income=925000.0, total_tds_deducted=50000.0),
    )
    s = p.model_copy(deep=True)
    s.salary.total_gross_salary = 1200000.0  # Disagreement

    verified, disagreements = cross_verify_extractions(p, s)
    assert verified.has_dual_verification is True
    assert len(disagreements) >= 1
    assert "Total Gross Salary disagreement" in disagreements[0]


def test_ai_provider_factory():
    """Test factory produces correct provider types."""
    gemini_p = get_ai_provider("gemini")
    assert isinstance(gemini_p, GeminiProvider)

    claude_p = get_ai_provider("claude")
    assert isinstance(claude_p, ClaudeProvider)


def test_prompt_template_versioning():
    """Test versioned prompt construction."""
    prompt = build_extraction_user_prompt("SAMPLE_TEXT", "2026-27")
    assert EXTRACTION_PROMPT_VERSION == "v1.0.0"
    assert "SAMPLE_TEXT" in prompt
    assert "2026-27" in prompt
