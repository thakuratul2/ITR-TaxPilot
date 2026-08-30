"""AI Provider Factory."""

from app.ai.providers.base import AIProvider
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.core.config import get_settings


def get_ai_provider(provider_type: str | None = None) -> AIProvider:
    """Instantiate and return AIProvider instance based on configuration or argument."""
    settings = get_settings()
    ptype = (provider_type or settings.DEFAULT_AI_PROVIDER).lower()

    if ptype == "claude" or "anthropic" in ptype:
        return ClaudeProvider(model_name=settings.CLAUDE_MODEL)
    return GeminiProvider(model_name=settings.GEMINI_MODEL)
