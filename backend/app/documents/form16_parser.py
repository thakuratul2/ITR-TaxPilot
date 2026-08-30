"""Direct deterministic parser for Form 16 text to extract exact financial values."""

import re
from typing import Any


def parse_form16_text_deterministically(full_text: str) -> dict[str, Any]:
    """Parse Form 16 text using multi-pattern deterministic regexes for Part A and Part B."""
    data: dict[str, Any] = {
        "pan": None,
        "tan": None,
        "assessment_year": "2026-27",
        "financial_year": "2025-26",
        "employee_name": "Taxpayer",
        "employer_name": "Employer Organization",
        "gross_salary": 0.0,
        "exempt_allowances_sec10": 0.0,
        "standard_deduction_sec16ia": 75000.0,
        "professional_tax_sec16iii": 0.0,
        "total_deductions_chapter_vi_a": 0.0,
        "deductions_chapter_vi_a": [],
        "total_tds_deducted": 0.0,
        "confidence_scores": {},
    }

    clean_text = full_text.replace(",", "")

    # 1. Assessment Year
    ay_match = re.search(r"(?:Assessment\s*Year|AY)\s*[:\-]?\s*(202[0-9]\s*[-–/]\s*[0-9]{2,4})", full_text, re.I)
    if ay_match:
        data["assessment_year"] = ay_match.group(1).replace(" ", "").replace("–", "-")
    elif "2026-27" in full_text:
        data["assessment_year"] = "2026-27"
    elif "2025-26" in full_text:
        data["assessment_year"] = "2025-26"

    # 2. PAN & TAN
    pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", full_text)
    if pan_match:
        data["pan"] = pan_match.group(1)

    tan_match = re.search(r"\b([A-Z]{4}[0-9]{5}[A-Z])\b", full_text)
    if tan_match:
        data["tan"] = tan_match.group(1)

    # 3. Part A Quarter Table Parsing (Amount paid/credited & TDS)
    # Quarter amounts e.g., Q1 ... 77222.00 ... 0.00
    quarter_amounts = []
    for q_num in ["Q1", "Q2", "Q3", "Q4"]:
        q_match = re.search(rf"{q_num}\s+[A-Z0-9]+\s+([0-9]+\.[0-9]{{2}}|[0-9]+)", clean_text)
        if q_match:
            try:
                quarter_amounts.append(float(q_match.group(1)))
            except ValueError:
                pass

    # Total (Rs.) in Part A
    total_match = re.search(r"Total\s*(?:\(Rs\.?\))?\s*[:\-]?\s*([0-9]+\.[0-9]{{2}}|[0-9]+)\s+([0-9]+\.[0-9]{{2}}|[0-9]+)?", clean_text, re.I)
    total_from_table = 0.0
    if total_match:
        try:
            total_from_table = float(total_match.group(1))
            if total_match.group(2):
                data["total_tds_deducted"] = float(total_match.group(2))
        except ValueError:
            pass

    # Gross salary from Part B or Part A
    gross_part_b_match = re.search(r"(?:Gross\s*Salary|Salary\s*as\s*per\s*provisions\s*contained\s*in\s*sec\.?\s*17\(1\))\s*[:\-]?\s*([0-9]+\.[0-9]{{2}}|[0-9]+)", clean_text, re.I)

    if gross_part_b_match:
        data["gross_salary"] = float(gross_part_b_match.group(1))
    elif total_from_table > 0:
        data["gross_salary"] = total_from_table
    elif quarter_amounts:
        data["gross_salary"] = sum(quarter_amounts)
    else:
        # Check any large number following paid/credited
        amt_match = re.search(r"Amount\s*paid/credited[^\d]+([0-9]+\.[0-9]{2})", clean_text, re.I)
        if amt_match:
            data["gross_salary"] = float(amt_match.group(1))

    # 4. Standard Deduction
    std_match = re.search(r"(?:Standard\s*Deduction|16\(ia\))\s*[:\-]?\s*([0-9]+\.[0-9]{{2}}|[0-9]+)", clean_text, re.I)
    if std_match:
        data["standard_deduction_sec16ia"] = float(std_match.group(1))

    # 5. Professional Tax
    pt_match = re.search(r"(?:Professional\s*Tax|Tax\s*on\s*employment|16\(iii\))\s*[:\-]?\s*([0-9]+\.[0-9]{{2}}|[0-9]+)", clean_text, re.I)
    if pt_match:
        data["professional_tax_sec16iii"] = float(pt_match.group(1))

    # 6. Chapter VI-A Deductions
    ded_80c_match = re.search(r"(?:80C|Section\s*80C)[^\d]+([0-9]+\.[0-9]{{2}}|[0-9]+)", clean_text, re.I)
    if ded_80c_match:
        val = float(ded_80c_match.group(1))
        if 0 < val <= 150000:
            data["deductions_chapter_vi_a"].append({"section": "80C", "amount": val})

    ded_80d_match = re.search(r"(?:80D|Section\s*80D)[^\d]+([0-9]+\.[0-9]{{2}}|[0-9]+)", clean_text, re.I)
    if ded_80d_match:
        val = float(ded_80d_match.group(1))
        if 0 < val <= 100000:
            data["deductions_chapter_vi_a"].append({"section": "80D", "amount": val})

    data["total_deductions_chapter_vi_a"] = sum(d["amount"] for d in data["deductions_chapter_vi_a"])

    return data
