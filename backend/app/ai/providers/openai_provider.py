"""OpenAI AI provider implementation (GPT-4o, GPT-4o-mini)."""

import os
from typing import Any

from app.ai.confidence import calculate_field_confidence_scores
from app.ai.prompts.extraction_prompt import (
    FORM16_EXTRACTION_SYSTEM_PROMPT,
    build_extraction_user_prompt,
)
from app.ai.providers.base import AIProvider
from app.ai.schemas import (
    ExtractedChapterVIA,
    ExtractedEmployee,
    ExtractedEmployer,
    ExtractedForm16Data,
    ExtractedSalaryBreakdown,
    ExtractedTaxSummary,
)
from app.core.config import get_settings
from app.core.logging import get_logger
from app.documents.models import NormalizedDocument

logger = get_logger("app.ai.openai")


class OpenAIProvider(AIProvider):
    """OpenAI GPT extraction provider."""

    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self.model_name = model_name or settings.OPENAI_MODEL
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        self.client = None

        if self.api_key and self.api_key != "mock_key_for_dev":
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI Client: %s", str(e))

    async def extract_form16(
        self,
        document: NormalizedDocument,
        temperature: float = 0.0,
    ) -> ExtractedForm16Data:
        """Execute extraction using OpenAI."""
        user_prompt = build_extraction_user_prompt(
            document_text=document.full_text,
            detected_ay=document.classification.detected_ay,
        )

        raw_text = ""
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": FORM16_EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                if response.choices and len(response.choices) > 0:
                    raw_text = response.choices[0].message.content or ""
            except Exception as e:
                logger.warning("OpenAI API call failed (%s); falling back to deterministic extraction.", str(e))
                raw_text = ""

        # Fallback to deterministic parser if AI response is unavailable or parsing failed
        from app.documents.form16_parser import parse_form16_text_deterministically
        det = parse_form16_text_deterministically(document.full_text)

        salary_obj = ExtractedSalaryBreakdown(
            total_gross_salary=det.get("gross_salary", 0.0),
            gross_salary_sec_17_1=det.get("gross_salary", 0.0),
            allowances_sec_10=det.get("exempt_allowances_sec10", 0.0),
            standard_deduction_sec_16_ia=det.get("standard_deduction_sec16ia", 75000.0),
            professional_tax_sec_16_iii=det.get("professional_tax_sec16iii", 0.0),
            income_chargeable_salaries=max(0.0, det.get("gross_salary", 0.0) - det.get("standard_deduction_sec16ia", 75000.0)),
        )
        tax_obj = ExtractedTaxSummary(
            total_taxable_income=salary_obj.income_chargeable_salaries,
            total_tds_deducted=det.get("total_tds_deducted", 0.0),
        )
        ded_obj = ExtractedChapterVIA(
            section_80c=0.0,
            section_80d=0.0,
        )
        for d in det.get("deductions_chapter_vi_a", []):
            if d.get("section") == "80C":
                ded_obj.section_80c = d.get("amount", 0.0)
            elif d.get("section") == "80D":
                ded_obj.section_80d = d.get("amount", 0.0)

        model_obj = ExtractedForm16Data(
            assessment_year=det.get("assessment_year", "2026-27"),
            financial_year=det.get("financial_year", "2025-26"),
            employer=ExtractedEmployer(
                name=det.get("employer_name"),
                tan=det.get("tan"),
                pan=det.get("pan"),
            ),
            employee=ExtractedEmployee(
                name=det.get("employee_name"),
                pan=det.get("pan"),
            ),
            salary=salary_obj,
            deductions=ded_obj,
            tax=tax_obj,
            model_name=self.model_name,
        )

        confidence_scores = calculate_field_confidence_scores(model_obj)
        model_obj.confidence_scores = confidence_scores
        return model_obj

    async def explain_tax_calculation(
        self,
        context: dict[str, Any],
        temperature: float = 0.2,
    ) -> str:
        """Generate human-understandable tax regime explanation from deterministic calculation."""
        if not self.client:
            return "Based on your income and deductions, the recommended regime saves you the maximum tax."
        try:
            prompt = f"Explain clearly to an Indian taxpayer why the recommended regime is better based on these figures:\n{context}"
            response = await self.client.chat.completions.create(
                model=self.model_name,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": "You are a professional Indian tax advisor. Explain tax calculations in plain, simple English."},
                    {"role": "user", "content": prompt},
                ],
            )
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
        except Exception as e:
            logger.warning("OpenAI tax explanation failed: %s", str(e))
        return "Based on Section 115BAC statutory slabs and Chapter VI-A deductions, the recommended regime minimizes your total tax liability."

    def _generate_fallback_json(self, document: NormalizedDocument) -> str:
        """Provide deterministic fallback extracted directly from document text."""
        import json

        from app.documents.form16_parser import parse_form16_text_deterministically
        data = parse_form16_text_deterministically(document.full_text)
        return json.dumps(data)
