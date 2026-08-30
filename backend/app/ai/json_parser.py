"""Resilient JSON parsing, sanitation, and coercion recovery for LLM extraction outputs."""

import json
import re
from typing import Any


def sanitize_raw_llm_json(raw_text: str) -> str:
    """Strip markdown fencing and isolate JSON object text."""
    text = raw_text.strip()

    # Strip markdown code blocks
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()

    # Find boundaries of the JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    # Remove trailing commas before closing braces/brackets
    text = re.sub(r",\s*([\]}])", r"\1", text)

    return text


def coerce_numeric_values(obj: Any) -> Any:
    """Recursively convert numeric strings with commas/rupee symbols to float/int."""
    if isinstance(obj, dict):
        return {k: coerce_numeric_values(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [coerce_numeric_values(elem) for elem in obj]
    if isinstance(obj, str):
        cleaned = obj.strip().replace(",", "").replace("₹", "").replace("Rs.", "").replace("INR", "").strip()
        # Check if it matches an integer or float pattern
        if re.match(r"^-?\d+(\.\d+)?$", cleaned):
            try:
                return float(cleaned) if "." in cleaned else int(cleaned)
            except ValueError:
                return obj
    return obj


def parse_and_recover_llm_json(raw_response: str) -> dict[str, Any]:
    """Parse LLM output safely with robust recovery techniques."""
    sanitized = sanitize_raw_llm_json(raw_response)

    try:
        data = json.loads(sanitized)
    except json.JSONDecodeError:
        # Secondary recovery: replace single quotes with double quotes
        try:
            alt_sanitized = re.sub(r"'([^']*)'", r'"\1"', sanitized)
            data = json.loads(alt_sanitized)
        except json.JSONDecodeError as err:
            raise ValueError(f"Failed to parse LLM response into JSON: {err}. Raw: {raw_response[:200]}") from err

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at root, received: {type(data)}")

    return coerce_numeric_values(data)
