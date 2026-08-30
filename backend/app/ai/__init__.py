"""AI extraction and reasoning package."""

from app.ai.confidence import calculate_field_confidence_scores
from app.ai.json_parser import parse_and_recover_llm_json
from app.ai.prompts.extraction_prompt import (
    EXTRACTION_PROMPT_VERSION,
    FORM16_EXTRACTION_SYSTEM_PROMPT,
    build_extraction_user_prompt,
)
from app.ai.providers.base import AIProvider
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

__all__ = [
    "ExtractedForm16Data",
    "ExtractedSalaryBreakdown",
    "ExtractedChapterVIA",
    "ExtractedTaxSummary",
    "ExtractedEmployer",
    "ExtractedEmployee",
    "AIProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "get_ai_provider",
    "parse_and_recover_llm_json",
    "calculate_field_confidence_scores",
    "cross_verify_extractions",
    "EXTRACTION_PROMPT_VERSION",
    "FORM16_EXTRACTION_SYSTEM_PROMPT",
    "build_extraction_user_prompt",
]
