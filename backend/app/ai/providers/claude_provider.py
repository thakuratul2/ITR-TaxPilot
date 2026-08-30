"""Anthropic Claude AI provider implementation."""

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

logger = get_logger("app.ai.claude")


class ClaudeProvider(AIProvider):
    """Anthropic Claude extraction provider."""

    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self.model_name = model_name or settings.CLAUDE_MODEL
        self.api_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY", "")
        self.client = None

        if self.api_key and self.api_key != "mock_key_for_dev":
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=self.api_key)
            except Exception as e:
                logger.warning("Failed to initialize Anthropic Client: %s", str(e))

    async def extract_form16(
        self,
        document: NormalizedDocument,
        temperature: float = 0.0,
    ) -> ExtractedForm16Data:
        """Execute extraction using Anthropic Claude."""
        user_prompt = build_extraction_user_prompt(
            document_text=document.full_text,
            detected_ay=document.classification.detected_ay,
        )

        raw_text = ""
        if self.client:
            try:
                response = await self.client.messages.create(
                    model=self.model_name,
                    max_tokens=4096,
                    temperature=temperature,
                    system=FORM16_EXTRACTION_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                if response.content and len(response.content) > 0:
                    raw_text = response.content[0].text
            except Exception as err:
                logger.error("Claude API extraction failed: %s", str(err))
                raise AIProviderError("Claude", f"Extraction failed: {err}") from err
        else:
            logger.info("Using Claude provider deterministic fallback (no live API key)")
            from app.ai.providers.gemini_provider import GeminiProvider
            raw_text = GeminiProvider()._generate_fallback_json(document)

        parsed_dict = parse_and_recover_llm_json(raw_text)
        extracted = ExtractedForm16Data(
            **parsed_dict,
            model_name=self.model_name,
        )

        extracted.confidence_scores = calculate_field_confidence_scores(extracted)
        return extracted

    async def explain_tax_calculation(
        self,
        context: dict[str, Any],
        temperature: float = 0.2,
    ) -> str:
        """Generate tax explanation using Claude."""
        if not self.client:
            regime = context.get("recommended_regime", "NEW")
            savings = context.get("tax_savings", 0.0)
            return (
                f"Based on your salary and deduction figures, the {regime} tax regime "
                f"is recommended, providing estimated tax savings of ₹{savings:,.2f}."
            )

        try:
            explanation_prompt = (
                f"Explain the following Indian Income Tax calculation clearly to a taxpayer in 3 concise paragraphs:\n"
                f"{context}\nHighlight regime comparison, major deductions, and the optimal ITR filing form."
            )
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                temperature=temperature,
                messages=[{"role": "user", "content": explanation_prompt}],
            )
            return response.content[0].text if response.content else "Tax calculation explained."
        except Exception as e:
            logger.warning("Claude explanation generation error: %s", str(e))
            return "Tax computation completed successfully."
