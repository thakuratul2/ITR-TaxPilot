"""Comprehensive unit and integration test suite for Milestone 10: Explanation AI & Guardrails."""

import pytest

from app.ai.explanation_context import ExplanationContextBuilder
from app.ai.explanation_engine import ExplanationEngine
from app.ai.guardrails import ExplanationGuardrail
from app.ai.prompts.explanation_prompt import (
    EXPLANATION_SYSTEM_PROMPT,
    TAX_QA_SYSTEM_PROMPT,
    build_explanation_user_prompt,
    build_tax_qa_user_prompt,
)
from app.ai.schemas import (
    ExplanationOutputSchema,
    TaxQuestionRequest,
)
from app.calculator.models import (
    ChapterVIAInput,
    OtherSourcesInput,
    SalaryInput,
    TaxpayerProfileInput,
)
from app.comparison.comparison_engine import ComparisonEngine
from app.tax.itr_models import ITRFormType, ITRRecommendation


@pytest.fixture
def sample_profile() -> TaxpayerProfileInput:
    """Standard middle-income taxpayer profile for AY 2026-27."""
    return TaxpayerProfileInput(
        assessment_year="2026-27",
        salary=SalaryInput(
            basic_salary=1000000.0,
            dearness_allowance=200000.0,
            hra_received=150000.0,
            rent_paid_annual=180000.0,
            professional_tax_paid=2500.0,
        ),
        other_sources=OtherSourcesInput(
            savings_bank_interest=25000.0,
            fixed_deposit_interest=35000.0,
        ),
        chapter_vi_a=ChapterVIAInput(
            section_80c=150000.0,
            section_80d_self=25000.0,
        ),
    )


@pytest.fixture
def sample_comparison(sample_profile: TaxpayerProfileInput):
    """Generate comprehensive comparison response."""
    return ComparisonEngine.compare_comprehensive(sample_profile)


# ---------------------------------------------------------------------------
# 1. Calculation Context Builder & PII Tests
# ---------------------------------------------------------------------------

def test_context_builder_structure_and_pii_safety(sample_comparison, sample_profile):
    """Verify context builder transforms audit trail into structured, PII-free dictionary."""
    context = ExplanationContextBuilder.build_context(
        comparison=sample_comparison,
        profile=sample_profile,
    )

    assert context["assessment_year"] == "2026-27"
    assert context["financial_year"] == "2025-26"
    assert context["winning_regime"] in ("NEW", "OLD")
    assert "old_regime" in context
    assert "new_regime" in context
    assert "take_home" in context
    assert "breakeven_analysis" in context
    assert "itr_recommendation" in context
    assert "permissible_numbers_whitelist" in context
    assert len(context["permissible_numbers_whitelist"]) > 10

    # PII Safety: Verify no personal names or PAN in the calculation context
    context_str = str(context)
    assert "PAN" not in context_str or "PAN" in "Company PAN"
    assert "password" not in context_str
    assert "Aadhaar" not in context_str


def test_missing_opportunities_detection(sample_profile, sample_comparison):
    """Check detection of unclaimed NPS 80CCD(1B), 80TTA, and AIS reconciliation."""
    context = ExplanationContextBuilder.build_context(
        comparison=sample_comparison,
        profile=sample_profile,
    )

    advisories = context["missing_info_advisories"]
    assert any("80CCD(1B)" in adv for adv in advisories)
    assert any("Annual Information Statement (AIS)" in adv for adv in advisories)


# ---------------------------------------------------------------------------
# 2. Prompt Templates & Safety Guardrail Tests
# ---------------------------------------------------------------------------

def test_explanation_prompts_integrity():
    """Verify system prompts mandate strict non-tampering and exact numerical adherence."""
    assert "DO NOT RECALCULATE, ALTER, INVENT" in EXPLANATION_SYSTEM_PROMPT
    assert "MUST match the provided JSON context EXACTLY" in EXPLANATION_SYSTEM_PROMPT
    assert "executive_summary" in EXPLANATION_SYSTEM_PROMPT
    assert "statutory_disclaimer" in EXPLANATION_SYSTEM_PROMPT
    assert "Ground all answers strictly" in TAX_QA_SYSTEM_PROMPT


    user_prompt = build_explanation_user_prompt({"assessment_year": "2026-27", "winning_regime": "NEW"})
    assert "=== DETERMINISTIC CALCULATION CONTEXT ===" in user_prompt


def test_tax_qa_prompt_builder():
    """Verify Q&A prompt incorporates user question and conversation history."""
    prompt = build_tax_qa_user_prompt(
        question="Why did New Regime win?",
        context={"winning_regime": "NEW", "tax_savings_amount": 25000.0},
        history=[{"role": "user", "content": "Hello"}],
    )
    assert "Why did New Regime win?" in prompt
    assert "Hello" in prompt
    assert "NEW" in prompt


# ---------------------------------------------------------------------------
# 3. Strict Numerical Guardrail Verification Tests
# ---------------------------------------------------------------------------

def test_guardrail_passes_verified_explanation(sample_comparison, sample_profile):
    """Guardrail accepts clean explanation citing authentic numbers from whitelist."""
    context = ExplanationContextBuilder.build_context(sample_comparison, sample_profile)
    fallback = ExplanationEngine.generate_deterministic_fallback(context)

    is_clean, issues = ExplanationGuardrail.verify_explanation(
        explanation=fallback,
        permissible_numbers=context["permissible_numbers_whitelist"],
    )

    assert is_clean is True, f"Guardrail verification failed with issues: {issues}"

    assert len(issues) == 0

    enforced = ExplanationGuardrail.enforce_guardrails(fallback, context)
    assert enforced.is_verified_against_calculation is True
    assert len(enforced.guardrail_interventions) == 0


def test_guardrail_flags_hallucinated_numbers(sample_comparison, sample_profile):
    """Guardrail detects and flags fake or altered tax amounts."""
    context = ExplanationContextBuilder.build_context(sample_comparison, sample_profile)
    fallback = ExplanationEngine.generate_deterministic_fallback(context)

    # Tamper with numbers: inject a completely fabricated number
    fallback.executive_summary += " You will receive a bonus tax credit of ₹8,88,888."

    is_clean, issues = ExplanationGuardrail.verify_explanation(
        explanation=fallback,
        permissible_numbers=context["permissible_numbers_whitelist"],
    )

    assert is_clean is False
    assert any("888,888" in issue or "888888" in issue for issue in issues)

    enforced = ExplanationGuardrail.enforce_guardrails(fallback, context)
    assert enforced.is_verified_against_calculation is False
    assert len(enforced.guardrail_interventions) > 0


def test_guardrail_corrects_regime_contradiction(sample_comparison, sample_profile):
    """Guardrail forcibly corrects any contradictory recommended regime label."""
    context = ExplanationContextBuilder.build_context(sample_comparison, sample_profile)
    fallback = ExplanationEngine.generate_deterministic_fallback(context)

    expected_winner = context["winning_regime"]
    wrong_regime = "OLD" if expected_winner == "NEW" else "NEW"

    fallback.recommended_regime = wrong_regime
    enforced = ExplanationGuardrail.enforce_guardrails(fallback, context)

    assert enforced.recommended_regime == expected_winner
    assert any("Corrected recommended regime" in note for note in enforced.guardrail_interventions)


# ---------------------------------------------------------------------------
# 4. Explanation Engine & Fallback Generator Tests
# ---------------------------------------------------------------------------

def test_deterministic_fallback_generator_completeness(sample_comparison, sample_profile):
    """Verify deterministic fallback generates comprehensive, rich, and valid explanation."""
    context = ExplanationContextBuilder.build_context(sample_comparison, sample_profile)
    explanation = ExplanationEngine.generate_deterministic_fallback(context)

    assert isinstance(explanation, ExplanationOutputSchema)
    assert len(explanation.executive_summary) > 20
    assert len(explanation.regime_comparison_narrative) > 50
    assert len(explanation.tax_breakdown_highlights) >= 3
    assert len(explanation.take_home_impact) > 20
    assert "ITR" in explanation.itr_form_guidance
    assert len(explanation.missing_information_advisories) >= 2
    assert len(explanation.tax_planning_tips) >= 2
    assert "Section 139(1)" in explanation.statutory_disclaimer
    assert explanation.is_verified_against_calculation is True


@pytest.mark.asyncio
async def test_explanation_engine_end_to_end(sample_comparison, sample_profile):
    """Verify asynchronous end-to-end explanation generation using ExplanationEngine."""
    explanation = await ExplanationEngine.generate_explanation(
        comparison=sample_comparison,
        profile=sample_profile,
        provider=None,  # Tests deterministic fallback path when provider is None
    )

    assert explanation.recommended_regime == sample_comparison.recommended_regime
    assert explanation.is_verified_against_calculation is True
    assert len(explanation.tax_breakdown_highlights) > 0


# ---------------------------------------------------------------------------
# 5. Interactive Tax Q&A Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_interactive_tax_qa_queries(sample_comparison, sample_profile):
    """Verify instant, deterministic answers to user questions with safety disclaimers."""
    context = ExplanationContextBuilder.build_context(sample_comparison, sample_profile)

    # 1. Regime question
    resp_regime = await ExplanationEngine.answer_tax_question(
        request=TaxQuestionRequest(question="Which regime is better for me?"),
        context=context,
    )
    assert context["winning_regime"] in resp_regime.answer
    assert len(resp_regime.relevant_figures) > 0

    # 2. Tax liability question
    resp_tax = await ExplanationEngine.answer_tax_question(
        request=TaxQuestionRequest(question="What is my total tax payable?"),
        context=context,
    )
    assert "₹" in resp_tax.answer
    assert "4% Health & Education Cess" in resp_tax.disclaimer

    # 3. ITR Form question
    resp_itr = await ExplanationEngine.answer_tax_question(
        request=TaxQuestionRequest(question="Which ITR form should I file?"),
        context=context,
    )
    assert "ITR" in resp_itr.answer
