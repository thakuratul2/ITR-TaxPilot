"""Server-side PDF tax report generation service using PyMuPDF."""

import logging
from datetime import UTC, datetime
from typing import Any

import pymupdf

from app.core.security import mask_pan

logger = logging.getLogger("app.services.report_service")


class ReportService:
    """Generates professional, printable, deterministic PDF tax assessment reports."""

    @classmethod
    def generate_tax_report_pdf(
        cls,
        analysis_id: str,
        data: dict[str, Any],
        taxpayer_pan: str | None = None,
    ) -> bytes:
        """Render calculation results and regime comparison into a styled PDF document."""
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)  # A4 standard portrait (595 x 842 points)

        ay = data.get("assessment_year", "2026-27")
        fy = data.get("financial_year") or ("2025-26" if ay == "2026-27" else "2024-25")
        now_str = datetime.now(UTC).strftime("%d %B %Y, %H:%M UTC")

        # Mask PAN if provided
        masked_pan = mask_pan(taxpayer_pan) if taxpayer_pan else "ABCDE****F"

        # Colors (RGB normalized 0.0 - 1.0)
        COLOR_PRIMARY = (0.08, 0.28, 0.58)      # Deep Navy #144794
        COLOR_BG_LIGHT = (0.95, 0.97, 1.0)      # Very light blue
        COLOR_TEXT_DARK = (0.12, 0.14, 0.17)    # Charcoal
        COLOR_TEXT_MUTED = (0.42, 0.45, 0.50)   # Gray
        COLOR_SUCCESS = (0.05, 0.55, 0.25)      # Green #0D8C40
        COLOR_BORDER = (0.85, 0.88, 0.92)

        # -------------------------------------------------------------------
        # 1. Header Banner & Branding
        # -------------------------------------------------------------------
        header_rect = pymupdf.Rect(30, 30, 565, 95)
        page.draw_rect(header_rect, color=None, fill=COLOR_PRIMARY)

        page.insert_text(
            (45, 60),
            "ITR-TaxPilot",
            fontsize=20,
            color=(1, 1, 1),
            fontname="helv",
        )
        page.insert_text(
            (45, 80),
            "AI-Powered Income Tax Analysis & Regime Optimizer",
            fontsize=9,
            color=(0.85, 0.92, 1.0),
            fontname="helv",
        )
        page.insert_text(
            (410, 55),
            f"AY: {ay} | FY: {fy}",
            fontsize=10,
            color=(1, 1, 1),
            fontname="helv",
        )
        page.insert_text(
            (410, 70),
            f"PAN: {masked_pan}",
            fontsize=9,
            color=(0.85, 0.92, 1.0),
            fontname="helv",
        )
        page.insert_text(
            (410, 85),
            f"Date: {now_str[:11]}",
            fontsize=8,
            color=(0.85, 0.92, 1.0),
            fontname="helv",
        )

        # -------------------------------------------------------------------
        # 2. Key Highlights & Recommendation Box
        # -------------------------------------------------------------------
        comparison = data.get("comparison") or {}
        rec_regime = comparison.get("recommended_regime") or data.get("recommended_regime", "NEW")
        savings = float(comparison.get("tax_savings_amount", 0.0) or data.get("tax_savings", 0.0))
        rec_itr = comparison.get("recommended_itr_form") or data.get("recommended_itr", "ITR-1 (Sahaj)")

        card_rect = pymupdf.Rect(30, 105, 565, 175)
        page.draw_rect(card_rect, color=COLOR_BORDER, fill=COLOR_BG_LIGHT)

        page.insert_text((45, 125), "EXECUTIVE TAX SUMMARY & RECOMMENDATION", fontsize=10, color=COLOR_PRIMARY, fontname="helv")

        # Metric 1: Recommended Regime
        page.insert_text((45, 148), "Recommended Regime:", fontsize=9, color=COLOR_TEXT_MUTED, fontname="helv")
        page.insert_text((45, 164), f"{rec_regime} TAX REGIME", fontsize=12, color=COLOR_SUCCESS if rec_regime == "NEW" else COLOR_PRIMARY, fontname="helv")

        # Metric 2: Annual Tax Savings
        page.insert_text((220, 148), "Annual Tax Savings:", fontsize=9, color=COLOR_TEXT_MUTED, fontname="helv")
        page.insert_text((220, 164), f"INR {savings:,.0f}", fontsize=12, color=COLOR_SUCCESS, fontname="helv")

        # Metric 3: Recommended ITR Form
        page.insert_text((390, 148), "Recommended ITR Form:", fontsize=9, color=COLOR_TEXT_MUTED, fontname="helv")
        page.insert_text((390, 164), str(rec_itr), fontsize=12, color=COLOR_PRIMARY, fontname="helv")

        # -------------------------------------------------------------------
        # 3. Side-by-Side Tax Regime Comparison Table
        # -------------------------------------------------------------------
        y_pos = 195
        page.insert_text((30, y_pos), "DETAILED TAX REGIME COMPARISON BREAKDOWN", fontsize=10, color=COLOR_PRIMARY, fontname="helv")
        y_pos += 10

        # Table Header
        th_rect = pymupdf.Rect(30, y_pos, 565, y_pos + 20)
        page.draw_rect(th_rect, color=None, fill=COLOR_PRIMARY)
        page.insert_text((40, y_pos + 14), "Tax Component / Line Item", fontsize=8, color=(1, 1, 1), fontname="helv")
        page.insert_text((290, y_pos + 14), "Old Regime (INR)", fontsize=8, color=(1, 1, 1), fontname="helv")
        page.insert_text((385, y_pos + 14), "New Regime (INR)", fontsize=8, color=(1, 1, 1), fontname="helv")
        page.insert_text((485, y_pos + 14), "Difference (INR)", fontsize=8, color=(1, 1, 1), fontname="helv")
        y_pos += 20

        # Extract line items or build default comparison lines
        line_items = comparison.get("line_items") or []
        if not line_items:
            # Fallback from calculations list
            calcs = {c.get("regime", ""): c for c in data.get("calculations", [])}
            old_c = calcs.get("OLD", {})
            new_c = calcs.get("NEW", {})
            line_items = [
                {"label": "Gross Salary Income", "old_value": old_c.get("gross_income", 0.0), "new_value": new_c.get("gross_income", 0.0)},
                {"label": "Total Deductions (Sec 16 & VI-A)", "old_value": old_c.get("total_deductions", 0.0), "new_value": new_c.get("total_deductions", 0.0)},
                {"label": "Net Taxable Income (Sec 288A)", "old_value": old_c.get("taxable_income", 0.0), "new_value": new_c.get("taxable_income", 0.0)},
                {"label": "Total Tax Liability (with Cess)", "old_value": old_c.get("total_tax_liability", 0.0), "new_value": new_c.get("total_tax_liability", 0.0)},
                {"label": "TDS / Prepaid Tax Credit", "old_value": old_c.get("tds_credit", 0.0), "new_value": new_c.get("tds_credit", 0.0)},
                {"label": "Net Tax Refund Due", "old_value": old_c.get("refund_due", 0.0), "new_value": new_c.get("refund_due", 0.0)},
                {"label": "Net Tax Balance Payable", "old_value": old_c.get("tax_payable", 0.0), "new_value": new_c.get("tax_payable", 0.0)},
            ]

        for idx, item in enumerate(line_items[:14]):  # Fit cleanly on Page 1
            row_bg = (0.97, 0.98, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0)
            row_rect = pymupdf.Rect(30, y_pos, 565, y_pos + 18)
            page.draw_rect(row_rect, color=COLOR_BORDER, fill=row_bg)

            label = str(item.get("label", ""))
            old_val = float(item.get("old_value", 0.0))
            new_val = float(item.get("new_value", 0.0))
            diff = float(item.get("difference", old_val - new_val))

            is_bold = "Total" in label or "Taxable" in label or "Liability" in label or "Refund" in label or "Payable" in label
            font_choice = "helv"
            font_size = 8
            label_color = COLOR_PRIMARY if is_bold else COLOR_TEXT_DARK

            page.insert_text((40, y_pos + 12), label[:45], fontsize=font_size, color=label_color, fontname=font_choice)
            page.insert_text((290, y_pos + 12), f"{old_val:,.2f}", fontsize=font_size, color=label_color, fontname=font_choice)
            page.insert_text((385, y_pos + 12), f"{new_val:,.2f}", fontsize=font_size, color=label_color, fontname=font_choice)
            page.insert_text((485, y_pos + 12), f"{diff:,.2f}", fontsize=font_size, color=COLOR_SUCCESS if diff > 0 else label_color, fontname=font_choice)

            y_pos += 18

        # -------------------------------------------------------------------
        # 4. Narrative Analysis & AI Explanation
        # -------------------------------------------------------------------
        y_pos += 15
        page.insert_text((30, y_pos), "TAX ADVISORY & STATUTORY ANALYSIS", fontsize=10, color=COLOR_PRIMARY, fontname="helv")
        y_pos += 10

        narrative = comparison.get("narrative_summary") or data.get("explanation") or (
            f"Under the {rec_regime} Tax Regime for AY {ay}, you save INR {savings:,.0f} compared to the alternative regime. "
            f"Ensure all AIS and Form 26AS entries are reconciled before filing your {rec_itr} return."
        )

        note_rect = pymupdf.Rect(30, y_pos, 565, y_pos + 50)
        page.draw_rect(note_rect, color=COLOR_BORDER, fill=COLOR_BG_LIGHT)

        # Word wrap text into textbox
        page.insert_textbox(
            pymupdf.Rect(40, y_pos + 8, 555, y_pos + 42),
            narrative,
            fontsize=8,
            color=COLOR_TEXT_DARK,
            fontname="helv",
        )
        y_pos += 60

        # -------------------------------------------------------------------
        # 5. Statutory Legal Disclaimers & Notice
        # -------------------------------------------------------------------
        disclaimer_rect = pymupdf.Rect(30, 740, 565, 815)
        page.draw_rect(disclaimer_rect, color=COLOR_BORDER, fill=(0.98, 0.98, 0.98))

        page.insert_text((40, 752), "STATUTORY LEGAL NOTICE & DISCLAIMER", fontsize=7.5, color=COLOR_TEXT_MUTED, fontname="helv")
        disclaimer_text = (
            "1. This tax summary is deterministically computed based on submitted Form 16 documents and declared financial parameters.\n"
            "2. In accordance with Section 139(1) of the Income-tax Act, 1961, the taxpayer is solely responsible for complete and accurate disclosure.\n"
            "3. This automated report does not constitute formal legal or Chartered Accountant tax advice. Please verify with a CA before final submission.\n"
            "4. Generated by ITR-TaxPilot (https://itrtaxpilot.com) — Confidential & PII Masked."
        )
        page.insert_textbox(
            pymupdf.Rect(40, 758, 555, 810),
            disclaimer_text,
            fontsize=6.5,
            color=COLOR_TEXT_MUTED,
            fontname="helv",
        )

        pdf_bytes = doc.tobytes()
        doc.close()
        logger.info("Generated PDF report for analysis %s (%d bytes)", analysis_id, len(pdf_bytes))
        return pdf_bytes
