"""Base abstract interface for AI providers."""

from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas import ExtractedForm16Data
from app.documents.models import NormalizedDocument


class AIProvider(ABC):
    """Abstract interface defining required methods for all LLM extraction and explanation providers."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def extract_form16(
        self,
        document: NormalizedDocument,
        temperature: float = 0.0,
    ) -> ExtractedForm16Data:
        """Extract structured Form 16 data from normalized document representation."""
        pass

    @abstractmethod
    async def explain_tax_calculation(
        self,
        context: dict[str, Any],
        temperature: float = 0.2,
    ) -> str:
        """Generate human-understandable tax regime explanation from deterministic calculation."""
        pass
