"""Master Tax Explanation Generation Service and AI Orchestrator.

Combines deterministic calculation context, LLM explanation prompts,
fallback generation, and strict numerical verification guardrails.
"""

from typing import Any

from app.ai.explanation_context import ExplanationContextBuilder
from app.ai.guardrails import ExplanationGuardrail
from app.ai.json_parser import parse_and_recover_llm_json
from app.ai.providers.base import AIProvider
from app.ai.schemas import (
    ExplanationOutputSchema,
    TaxQuestionRequest,
    TaxQuestionResponse,
)
from app.calculator.models import TaxpayerProfileInput
from app.comparison.models import ComprehensiveComparisonResponse
from app.core.logging import get_logger
from app.tax.itr_models import ITRRecommendation

logger = get_logger("app.ai.explanation")


class ExplanationEngine:
    """Master Explanation Engine coordinating LLMs, fallbacks, and guardrails."""

    @classmethod
    async def generate_explanation(
        cls,
        comparison: ComprehensiveComparisonResponse,
        profile: TaxpayerProfileInput | None = None,
        itr_recommendation: ITRRecommendation | None = None,
        provider: AIProvider | None = None,
    ) -> ExplanationOutputSchema:
        """
        Generate a comprehensive, verified plain-English tax explanation.
        """
        context = ExplanationContextBuilder.build_context(
            comparison=comparison,
            profile=profile,
            itr_recommendation=itr_recommendation,
        )

        raw_llm_response = ""
        if provider:
            try:
                raw_llm_response = await provider.explain_tax_calculation(
                    context=context,
                    temperature=0.1,
                )
            except Exception as err:
                logger.warning("AI explanation provider failed (%s); falling back to deterministic generator.", str(err))
                raw_llm_response = ""

        # Parse LLM response or use deterministic generator
        if raw_llm_response:
            try:
                parsed_json = parse_and_recover_llm_json(raw_llm_response)
                explanation = ExplanationOutputSchema.model_validate(parsed_json)
                # Verify and enforce guardrails
                verified_explanation = ExplanationGuardrail.enforce_guardrails(explanation, context)
                return verified_explanation
            except Exception as parse_err:
                logger.warning("Failed to validate LLM explanation schema (%s); using deterministic fallback.", str(parse_err))

        # Deterministic Fallback Generator
        fallback = cls.generate_deterministic_fallback(context)
        return fallback

    @classmethod
    def generate_deterministic_fallback(cls, context: dict[str, Any]) -> ExplanationOutputSchema:
        """
        Generate a 100% verified, rich plain-English explanation directly from deterministic calculation data.
        """
        ay = context["assessment_year"]
        winning = context["winning_regime"]
        savings = context["tax_savings_amount"]
        pct_savings = context["percentage_savings"]
        take_home = context["take_home"]
        old = context["old_regime"]
        new = context["new_regime"]
        breakeven = context["breakeven_analysis"]
        itr = context["itr_recommendation"]
        missing_adv = context["missing_info_advisories"]

        diff_monthly = take_home["monthly_in_hand_difference"]

        # 1. Executive Summary
        if winning == "NEW":
            if savings > 0:
                exec_sum = (
                    f"For Assessment Year {ay}, the New Tax Regime (Section 115BAC) is the optimal choice, "
                    f"saving you ₹{savings:,.0f} in annual taxes (a {pct_savings:.1f}% reduction) and increasing "
                    f"your monthly in-hand take-home pay by ₹{diff_monthly:,.0f}."
                )
            else:
                exec_sum = (
                    f"For Assessment Year {ay}, your computed tax liability is ₹0 in both tax regimes. "
                    f"The New Tax Regime is recommended as the statutory default regime."
                )
        else:
            exec_sum = (
                f"For Assessment Year {ay}, the Old Tax Regime is significantly more beneficial, "
                f"saving you ₹{savings:,.0f} in annual taxes (₹{diff_monthly:,.0f} higher monthly take-home) "
                f"because your total deductions of ₹{breakeven['current_claimed_deductions']:,.0f} exceed the breakeven point."
            )

        # 2. Regime Comparison Narrative
        if winning == "NEW":
            narrative = (
                f"Under the New Tax Regime for AY {ay}, you benefit from lower progressive tax slab rates "
                f"and an enhanced Standard Deduction of ₹{new['standard_deduction']:,.0f} (compared to ₹{old['standard_deduction']:,.0f} in the Old Regime). "
                f"Your net taxable income is computed at ₹{new['taxable_income']:,.0f}, yielding a final annual tax liability of ₹{new['total_tax_liability']:,.0f}.\n\n"
                f"In comparison, the Old Regime results in a tax liability of ₹{old['total_tax_liability']:,.0f}. "
                f"Because your claimed Chapter VI-A deductions (₹{old['total_chapter_via_deductions']:,.0f}) do not meet the "
                f"breakeven threshold of ₹{breakeven['breakeven_deduction_required']:,.0f}, the New Regime is clearly more economical."
            )
        else:
            narrative = (
                f"Under the Old Tax Regime for AY {ay}, your extensive itemized deductions "
                f"(Total Chapter VI-A: ₹{old['total_chapter_via_deductions']:,.0f}, Section 10 exemptions: ₹{old['exempt_allowances_sec_10']:,.0f}) "
                f"reduce your taxable income to ₹{old['taxable_income']:,.0f}, resulting in a net tax liability of ₹{old['total_tax_liability']:,.0f}.\n\n"
                f"In the New Regime, most Chapter VI-A and Section 10 deductions are disallowed, leading to a higher tax liability "
                f"of ₹{new['total_tax_liability']:,.0f}. Your deductions surpass the statutory breakeven threshold by ₹{abs(breakeven['deduction_shortfall_or_surplus']):,.0f}."
            )

        # 3. Highlights
        highlights = [
            f"Gross Total Income: ₹{old['gross_total_income']:,.0f}",
            f"New Regime Tax Payable: ₹{new['total_tax_liability']:,.0f} vs Old Regime: ₹{old['total_tax_liability']:,.0f}",
            f"TDS Credited from Form 16: ₹{old['prepaid_tds']:,.0f}",
            f"Net Balance: {'Refund Due of ₹' + f'{abs(new['net_payable_or_refund']):,.0f}' if new['net_payable_or_refund'] < 0 else 'Tax Payable of ₹' + f'{new['net_payable_or_refund']:,.0f}'}",
        ]

        # 4. Take Home Impact
        take_home_str = (
            f"Your estimated monthly in-hand salary is ₹{take_home['new_regime_monthly_in_hand']:,.0f} under the New Regime "
            f"versus ₹{take_home['old_regime_monthly_in_hand']:,.0f} under the Old Regime, giving an extra ₹{diff_monthly:,.0f} per month."
        )

        # 5. ITR Guidance
        itr_str = (
            f"Recommended Return Form: {itr['recommended_form']}. "
            + (" ".join(itr["notes_and_schedules"]) if itr["notes_and_schedules"] else "File on or before July 31.")
        )

        # 6. Planning Tips
        planning_tips = [
            "Consider maximizing voluntary NPS Tier-1 contributions under Section 80CCD(1B) for additional tax deductions.",
            "Maintain digital records of Section 80D health insurance premiums and medical checkups for prompt verification.",
            "Cross-verify your Form 26AS and AIS on the e-filing portal prior to submitting your ITR.",
        ]

        disclaimer = (
            "Tax estimations and explanations are deterministically computed based on provided Form 16 details. "
            "Under Section 139(1) of the Income-tax Act, 1961, taxpayers must ensure full declaration of all worldwide income."
        )

        return ExplanationOutputSchema(
            executive_summary=exec_sum,
            recommended_regime=winning,
            regime_comparison_narrative=narrative,
            tax_breakdown_highlights=highlights,
            take_home_impact=take_home_str,
            itr_form_guidance=itr_str,
            missing_information_advisories=missing_adv,
            tax_planning_tips=planning_tips,
            statutory_disclaimer=disclaimer,
            is_verified_against_calculation=True,
            guardrail_interventions=[],
        )

    @classmethod
    async def answer_tax_question(
        cls,
        request: TaxQuestionRequest,
        context: dict[str, Any],
        history: list[dict[str, str]] | None = None,
        provider: AIProvider | None = None,
    ) -> TaxQuestionResponse:
        """
        Answer interactive taxpayer questions grounded strictly in the calculation context.
        """
        q = request.question.strip()

        # Deterministic instant answers for common questions
        q_lower = q.lower()
        if "which regime" in q_lower or "which is better" in q_lower or "recommend" in q_lower:
            win = context.get("winning_regime", "NEW")
            sav = context.get("tax_savings_amount", 0.0)
            ans = f"The {win} Tax Regime is optimal for you, saving ₹{sav:,.0f} per year."
            return TaxQuestionResponse(
                answer=ans,
                relevant_figures=[f"₹{sav:,.0f}"],
                disclaimer="Grounded in deterministic AY 2026-27 calculations.",
            )

        if "how much tax" in q_lower or "total tax" in q_lower:
            win = context.get("winning_regime", "NEW")
            regime_key = "new_regime" if win == "NEW" else "old_regime"
            tax_val = context.get(regime_key, {}).get("total_tax_liability", 0.0)
            ans = f"Your total annual tax liability under the recommended {win} Regime is ₹{tax_val:,.0f}."
            return TaxQuestionResponse(
                answer=ans,
                relevant_figures=[f"₹{tax_val:,.0f}"],
                disclaimer="Includes statutory 4% Health & Education Cess.",
            )

        if "which itr" in q_lower or "form" in q_lower:
            itr_form = context.get("itr_recommendation", {}).get("recommended_form", "ITR-1 (Sahaj)")
            ans = f"You should file {itr_form} based on your submitted income sources and resident individual profile."
            return TaxQuestionResponse(
                answer=ans,
                relevant_figures=[itr_form],
                disclaimer="Subject to Schedule requirements.",
            )

        # Fallback general answer
        ans = (
            f"Based on your Form 16 analysis for AY {context.get('assessment_year', '2026-27')}, "
            f"your Gross Total Income is ₹{context.get('old_regime', {}).get('gross_total_income', 0.0):,.0f} and the "
            f"{context.get('winning_regime', 'NEW')} Tax Regime saves you ₹{context.get('tax_savings_amount', 0.0):,.0f} annually."
        )
        return TaxQuestionResponse(
            answer=ans,
            relevant_figures=[f"₹{context.get('tax_savings_amount', 0.0):,.0f}"],
            disclaimer="Educational tax analysis.",
        )
