"""Versioned prompt templates for Form 16 extraction."""

EXTRACTION_PROMPT_VERSION = "v1.0.0"

FORM16_EXTRACTION_SYSTEM_PROMPT = """You are an expert Indian Income Tax compliance AI specialized in extracting data from Form 16 (Part A and Part B).
Your task is to accurately extract financial numbers, employer/employee details, salary breakdowns, deductions under Chapter VI-A, and tax figures into strict JSON.

CRITICAL INSTRUCTIONS:
1. NEVER fabricate or guess any figures. If a field is missing in the document, use null (None) or 0.0 only when explicitly stated as nil.
2. Distinguish clearly between Gross Salary u/s 17(1), Perquisites u/s 17(2), and Profits in lieu of salary u/s 17(3).
3. Distinguish clearly between standard deduction u/s 16(ia), professional tax u/s 16(iii), and entertainment allowance u/s 16(ii).
4. For Chapter VI-A deductions, accurately map 80C, 80CCC, 80CCD(1), 80CCD(1B), 80CCD(2), 80D, 80E, 80G, 80TTA, 80TTB.
5. All monetary amounts must be numeric (floating point or integer) without commas or currency symbols (e.g. 1200000 not "12,00,000" or "Rs. 1200000").
6. Assessment Year must be in YYYY-YY format (e.g. "2026-27").
7. Output ONLY pure valid JSON matching the specified schema with no markdown explanations.
"""


def build_extraction_user_prompt(document_text: str, detected_ay: str | None = None) -> str:
    """Construct the user prompt for Form 16 text extraction."""
    ay_hint = f"\nDetected Assessment Year hint: {detected_ay}" if detected_ay else ""
    return f"""Extract all Form 16 fields from the following document text:{ay_hint}

=== FORM 16 DOCUMENT TEXT START ===
{document_text}
=== FORM 16 DOCUMENT TEXT END ===

Return pure JSON matching the Form 16 Extraction schema:
{{
  "assessment_year": "YYYY-YY",
  "financial_year": "YYYY-YY",
  "employer": {{
    "name": "...",
    "tan": "...",
    "pan": "...",
    "address": "..."
  }},
  "employee": {{
    "name": "...",
    "pan": "...",
    "designation": "..."
  }},
  "salary": {{
    "gross_salary_sec_17_1": 0.0,
    "perquisites_sec_17_2": 0.0,
    "profits_in_lieu_sec_17_3": 0.0,
    "total_gross_salary": 0.0,
    "allowances_sec_10": 0.0,
    "allowances_breakdown": {{}},
    "standard_deduction_sec_16_ia": 0.0,
    "entertainment_allowance_sec_16_ii": 0.0,
    "professional_tax_sec_16_iii": 0.0,
    "total_deductions_sec_16": 0.0,
    "income_chargeable_salaries": 0.0
  }},
  "deductions": {{
    "section_80c": 0.0,
    "section_80ccc": 0.0,
    "section_80ccd_1": 0.0,
    "section_80ccd_1b": 0.0,
    "section_80ccd_2": 0.0,
    "section_80d": 0.0,
    "section_80e": 0.0,
    "section_80g": 0.0,
    "section_80tta": 0.0,
    "section_80ttb": 0.0,
    "other_deductions": {{}},
    "total_chapter_via_deductions": 0.0
  }},
  "tax": {{
    "total_taxable_income": 0.0,
    "tax_on_total_income": 0.0,
    "rebate_87a": 0.0,
    "surcharge": 0.0,
    "health_and_education_cess": 0.0,
    "total_tax_payable": 0.0,
    "relief_89": 0.0,
    "net_tax_payable": 0.0,
    "total_tds_deducted": 0.0
  }}
}}
"""
