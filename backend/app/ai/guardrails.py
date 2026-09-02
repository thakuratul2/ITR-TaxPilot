"""Strict Anti-Hallucination and Numerical Verification Guardrails for Explanation AI.

Ensures that AI-generated tax explanations never alter, hallucinate, or misrepresent
deterministic calculation figures, tax liabilities, deductions, or regime outcomes.
"""

import re
from typing import Any

from app.ai.schemas import ExplanationOutputSchema
from app.core.logging import get_logger

logger = get_logger("app.ai.guardrails")


class ExplanationGuardrail:
    """Strict numerical verifier and anti-hallucination guardrail."""

    # Currency and numeric pattern extractor
    # Matches ₹12,00,000, Rs. 75,000, 1,20,000, 150000.0, 4%, etc.
    NUMERIC_PATTERN = re.compile(
        r"(?:₹|Rs\.?|INR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
        re.IGNORECASE,
    )


    # Years, sections, and small ordinal numbers to ignore during strict financial audit
    IGNORED_NUMBERS = {
        0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 16.0, 17.0, 18.0,
        20.0, 24.0, 25.0, 30.0, 31.0, 44.0, 50.0, 56.0, 57.0, 80.0, 87.0, 89.0, 100.0, 111.0, 112.0,
        115.0, 139.0, 192.0, 194.0, 234.0, 288.0, 2024.0, 2025.0, 2026.0, 2027.0, 2028.0,
    }


    @classmethod
    def extract_monetary_numbers(cls, text: str) -> list[float]:
        """Extract all candidate numeric and monetary values from a text passage."""
        found: list[float] = []
        for match in cls.NUMERIC_PATTERN.finditer(text):
            val_str = match.group(1).replace(",", "")
            try:
                val = float(val_str)
                if val not in cls.IGNORED_NUMBERS and val > 100.0:  # Focus on financial amounts > 100
                    found.append(round(val, 2))
            except ValueError:
                continue
        return found

    @classmethod
    def verify_explanation(
        cls,
        explanation: ExplanationOutputSchema,
        permissible_numbers: set[float] | list[float],
    ) -> tuple[bool, list[str]]:
        """
        Perform strict numerical audit of all fields in the explanation against
        the whitelist of verified numbers from the deterministic tax engine.
        """
        whitelist_set = {round(float(n), 2) for n in permissible_numbers}
        unverified: list[str] = []

        # Texts to scan
        scan_targets = [
            ("Executive Summary", explanation.executive_summary),
            ("Regime Narrative", explanation.regime_comparison_narrative),
            ("Take Home Impact", explanation.take_home_impact),
        ]
        for idx, hl in enumerate(explanation.tax_breakdown_highlights):
            scan_targets.append((f"Highlight #{idx+1}", hl))

        for section_name, text in scan_targets:
            cited_nums = cls.extract_monetary_numbers(text)
            for num in cited_nums:
                # Check with small delta tolerance for floating-point representations
                matched = any(abs(num - w) < 1.5 for w in whitelist_set)
                if not matched:
                    flag = f"Unverified financial amount ₹{num:,.0f} cited in '{section_name}'."
                    unverified.append(flag)

        # Verify recommended regime matches
        is_clean = len(unverified) == 0
        return is_clean, unverified

    @classmethod
    def enforce_guardrails(
        cls,
        explanation: ExplanationOutputSchema,
        context: dict[str, Any],
    ) -> ExplanationOutputSchema:
        """
        Validate explanation and apply corrective sanitization if any hallucinations or
        regime contradictions are detected.
        """
        whitelist = context.get("permissible_numbers_whitelist", [])
        is_clean, issues = cls.verify_explanation(explanation, whitelist)

        expected_regime = context.get("winning_regime", "NEW")
        interventions: list[str] = []

        # 1. Regime match enforcement
        if explanation.recommended_regime.upper() != expected_regime.upper():
            interventions.append(
                f"Corrected recommended regime from '{explanation.recommended_regime}' to statutory winner '{expected_regime}'."
            )
            explanation.recommended_regime = expected_regime

        # 2. Hallucinated numbers handling
        if not is_clean:
            logger.warning("Explanation AI guardrail flagged %d unverified numbers: %s", len(issues), issues)
            interventions.extend(issues)
            explanation.is_verified_against_calculation = False
        else:
            explanation.is_verified_against_calculation = True

        explanation.guardrail_interventions = interventions
        return explanation
