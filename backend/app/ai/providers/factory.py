"""AI Provider Factory."""

from app.ai.providers.base import AIProvider
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import get_settings


def get_ai_provider(provider_type: str | None = None) -> AIProvider:
    """Instantiate and return AIProvider instance based on configuration or argument."""
    settings = get_settings()
    ptype = (provider_type or settings.DEFAULT_AI_PROVIDER).lower()

    if "openai" in ptype or "gpt" in ptype:
        return OpenAIProvider(model_name=settings.OPENAI_MODEL)
    if "claude" in ptype or "anthropic" in ptype:
        return ClaudeProvider(model_name=settings.CLAUDE_MODEL)
    return GeminiProvider(model_name=settings.GEMINI_MODEL)
