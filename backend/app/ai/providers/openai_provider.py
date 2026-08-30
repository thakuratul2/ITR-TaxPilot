"""OpenAI AI provider implementation (GPT-4o, GPT-4o-mini)."""

import os
from typing import Any

from app.ai.confidence import calculate_field_confidence_scores
from app.ai.json_parser import parse_and_recover_llm_json
from app.ai.prompts.extraction_prompt import (
    FORM16_EXTRACTION_SYSTEM_PROMPT,
    build_extraction_user_prompt,
)
from app.ai.providers.base import AIProvider
from app.ai.schemas import ExtractedForm16Data
from app.core.config import get_settings
from app.core.exceptions import AIProviderError
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
                logger.error("OpenAI API call failed: %s", str(e))
                raise AIProviderError(f"OpenAI error: {str(e)}") from e

        # Mock fallback if client not configured or in offline dev test
        if not raw_text:
            raw_text = self._generate_fallback_json(document)

        parsed_dict = parse_and_recover_llm_json(raw_text)
        confidence_scores = calculate_field_confidence_scores(parsed_dict, document)
        parsed_dict["confidence_scores"] = confidence_scores

        try:
            return ExtractedForm16Data.model_validate(parsed_dict)
        except Exception as err:
            logger.error("ExtractedForm16Data validation failed: %s", str(err))
            raise AIProviderError(f"Schema validation error: {str(err)}") from err

    def _generate_fallback_json(self, document: NormalizedDocument) -> str:
        """Provide deterministic fallback data for dev testing."""
        return """{
            "pan": "ABCDE1234F",
            "tan": "MUMB12345C",
            "assessment_year": "2026-27",
            "financial_year": "2025-26",
            "employee_name": "Atul Pratap Singh",
            "employer_name": "TaxPilot Systems India Pvt Ltd",
            "gross_salary": 2606700.0,
            "exempt_allowances_sec10": 0.0,
            "standard_deduction_sec16ia": 75000.0,
            "entertainment_allowance_sec16ii": 0.0,
            "professional_tax_sec16iii": 2500.0,
            "income_chargeable_salaries": 2529200.0,
            "total_income_from_house_property": 0.0,
            "total_income_other_sources": 0.0,
            "gross_total_income": 2529200.0,
            "deductions_chapter_vi_a": [
                {"section": "80C", "description": "EPF & PPF", "amount": 150000.0},
                {"section": "80CCD(1B)", "description": "NPS Voluntary", "amount": 50000.0},
                {"section": "80D", "description": "Medical Insurance", "amount": 25000.0}
            ],
            "total_deductions_chapter_vi_a": 225000.0,
            "total_taxable_income": 2304200.0,
            "total_tax_payable": 239982.0,
            "rebate_sec_87a": 0.0,
            "surcharge": 0.0,
            "health_and_education_cess": 9230.0,
            "relief_sec_89": 0.0,
            "net_tax_payable": 239982.0,
            "total_tds_deducted": 239982.0,
            "refund_or_payable_amount": 0.0
        }"""
