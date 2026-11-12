"""Unit tests for the hybrid grading pipeline and authority filtering."""

import json
from pathlib import Path
from typing import Any

import pytest

from ad_copy_grader.llm import FakeModelClient, LlmClientError, ModelReply
from ad_copy_grader.models import AdInput, Issue, Location
from ad_copy_grader.pipeline import (
    DEGRADED_MESSAGES,
    _extract_normalized_numbers,
    _is_a01_supported_by_lp_context,
    _is_location_in_bounds,
    _normalize_text,
    _referenced_ad_text,
    compute_score,
    filter_llm_issues,
    grade,
    grade_with_degradation,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def anyio_backend() -> str:
    """Specify anyio backend for async tests."""
    return "asyncio"


@pytest.fixture
def clean_ad_en() -> AdInput:
    """Load clean English RSA ad fixture."""
    data = json.loads((FIXTURES_DIR / "base_clean_en.json").read_text(encoding="utf-8"))
    return AdInput.model_validate(data)


@pytest.fixture
def clean_ad_pt() -> AdInput:
    """Load clean Portuguese RSA ad fixture."""
    data = json.loads((FIXTURES_DIR / "base_clean_pt.json").read_text(encoding="utf-8"))
    return AdInput.model_validate(data)


def _make_llm_reply(
    issues: list[dict[str, Any]],
    rules_checked: list[str] | None = None,
    suggestions: list[dict[str, Any]] | None = None,
) -> ModelReply:
    """Helper to generate a structured JSON ModelReply."""
    content = json.dumps(
        {
            "issues": issues,
            "rules_checked": rules_checked or ["A01", "A02", "A03"],
            "suggestions": suggestions or [],
        }
    )
    return ModelReply(
        content=content,
        prompt_tokens=150,
        completion_tokens=60,
        total_tokens=210,
        cost_usd=0.0005,
        model="fake-pipeline-model",
    )


def test_compute_score_scenarios() -> None:
    """Test score computation for various issue severity combinations and score floor."""
    # Clean ad
    score, grade_10, passed = compute_score([])
    assert score == 100
    assert grade_10 == 10.0
    assert passed is True

    # One warning: 100 - 5 = 95
    warning_issue = Issue(
        rule_id="A02",
        severity="warning",
        message="Missing CTA",
        source="llm",
    )
    score, grade_10, passed = compute_score([warning_issue])
    assert score == 95
    assert grade_10 == 9.5
    assert passed is True

    # One error: 100 - 15 = 85
    error_issue = Issue(
        rule_id="A01",
        severity="error",
        message="Unverified price",
        source="llm",
    )
    score, grade_10, passed = compute_score([error_issue])
    assert score == 85
    assert grade_10 == 8.5
    assert passed is False

    # Many errors hitting zero floor
    many_errors = [error_issue] * 10
    score, grade_10, passed = compute_score(many_errors)
    assert score == 0
    assert grade_10 == 0.0
    assert passed is False


def test_helper_text_and_number_normalization() -> None:
    """Verify text normalization and numeric token extraction."""
    assert _normalize_text("Atenção à Saúde!") == "atencao a saude!"
    numbers = _extract_normalized_numbers("De R$ 1.200,50 por $899 ou 12x com 20% off")
    assert "120050" in numbers
    assert "899" in numbers
    assert "12" in numbers
    assert "20" in numbers


def test_referenced_ad_text_and_bounds_coverage(clean_ad_en: AdInput) -> None:
    """Exercise _referenced_ad_text and _is_location_in_bounds across all field branches."""
    # None location
    issue_no_loc = Issue(rule_id="D01", severity="error", message="err", source="code")
    assert _referenced_ad_text(clean_ad_en, issue_no_loc) == ""
    assert _is_location_in_bounds(clean_ad_en, issue_no_loc) is True

    # Headline
    issue_h0 = Issue(
        rule_id="A01",
        severity="error",
        message="err",
        location=Location(field="headline", index=0),
        source="llm",
    )
    assert _referenced_ad_text(clean_ad_en, issue_h0) == clean_ad_en.headlines[0]
    assert _is_location_in_bounds(clean_ad_en, issue_h0) is True

    issue_h_none = Issue(
        rule_id="A01",
        severity="error",
        message="err",
        location=Location(field="headline", index=None),
        source="llm",
    )
    assert _referenced_ad_text(clean_ad_en, issue_h_none) == ""
    assert _is_location_in_bounds(clean_ad_en, issue_h_none) is False

    issue_h_oob = Issue(
        rule_id="A01",
        severity="error",
        message="err",
        location=Location(field="headline", index=99),
        source="llm",
    )
    assert _referenced_ad_text(clean_ad_en, issue_h_oob) == ""
    assert _is_location_in_bounds(clean_ad_en, issue_h_oob) is False

    # Description
    issue_d0 = Issue(
        rule_id="A01",
        severity="error",
        message="err",
        location=Location(field="description", index=0),
        source="llm",
    )
    assert _referenced_ad_text(clean_ad_en, issue_d0) == clean_ad_en.descriptions[0]
    assert _is_location_in_bounds(clean_ad_en, issue_d0) is True

    issue_d_none = Issue(
        rule_id="A01",
        severity="error",
        message="err",
        location=Location(field="description", index=None),
        source="llm",
    )
    assert _referenced_ad_text(clean_ad_en, issue_d_none) == ""
    assert _is_location_in_bounds(clean_ad_en, issue_d_none) is False

    # Paths and URL
    issue_p1 = Issue(
        rule_id="D06",
        severity="error",
        message="err",
        location=Location(field="path1", index=0),
        source="code",
    )
    assert _referenced_ad_text(clean_ad_en, issue_p1) == "implants"
    assert _is_location_in_bounds(clean_ad_en, issue_p1) is True

    issue_p1_invalid_idx = Issue(
        rule_id="D06",
        severity="error",
        message="err",
        location=Location(field="path1", index=5),
        source="code",
    )
    assert _is_location_in_bounds(clean_ad_en, issue_p1_invalid_idx) is False

    issue_p2 = Issue(
        rule_id="D06",
        severity="error",
        message="err",
        location=Location(field="path2"),
        source="code",
    )
    assert _referenced_ad_text(clean_ad_en, issue_p2) == "consultation"
    assert _is_location_in_bounds(clean_ad_en, issue_p2) is True

    issue_url = Issue(
        rule_id="D11",
        severity="error",
        message="err",
        location=Location(field="final_url"),
        source="code",
    )
    assert _referenced_ad_text(clean_ad_en, issue_url) == clean_ad_en.final_url
    assert _is_location_in_bounds(clean_ad_en, issue_url) is True

    # Ad without paths
    ad_no_paths = clean_ad_en.model_copy(update={"path1": None, "path2": None})
    assert _referenced_ad_text(ad_no_paths, issue_p1) == ""
    assert _is_location_in_bounds(ad_no_paths, issue_p1) is False
    assert _referenced_ad_text(ad_no_paths, issue_p2) == ""
    assert _is_location_in_bounds(ad_no_paths, issue_p2) is False

    # Unknown field location
    issue_unknown = Issue.model_construct(
        rule_id="D01",
        severity="error",
        message="err",
        location=Location.model_construct(field="custom_field", index=0),
        source="code",
    )
    assert _referenced_ad_text(clean_ad_en, issue_unknown) == ""
    assert _is_location_in_bounds(clean_ad_en, issue_unknown) is False


def test_is_a01_supported_by_lp_context_variations(clean_ad_en: AdInput) -> None:
    """Verify A01 verification logic against lp_context."""
    # Empty lp_context
    ad_empty_lp = clean_ad_en.model_copy(update={"lp_context": ""})
    issue_price = Issue(
        rule_id="A01",
        severity="error",
        message="Price $899 in headline.",
        location=Location(field="headline", index=0),
        source="llm",
    )
    assert _is_a01_supported_by_lp_context(ad_empty_lp, issue_price) is False

    # Price in asset matches lp_context ($899 in lp_context)
    ad_with_price = clean_ad_en.model_copy(
        update={"headlines": ["Dental Implants $899", *clean_ad_en.headlines[1:]]}
    )
    assert _is_a01_supported_by_lp_context(ad_with_price, issue_price) is True

    # Price in issue message matches lp_context when asset has no numbers
    assert _is_a01_supported_by_lp_context(clean_ad_en, issue_price) is True

    # Generic CTA when lp_context mentions consultation/evaluation
    issue_cta = Issue(
        rule_id="A01",
        severity="error",
        message="Unverified CTA offer: Book an evaluation today.",
        location=Location(field="headline", index=4),
        source="llm",
    )
    assert _is_a01_supported_by_lp_context(clean_ad_en, issue_cta) is True

    # Generic CTA when lp_context mentions unrelated topics only
    ad_unrelated_lp = clean_ad_en.model_copy(update={"lp_context": "Only selling toothbrushes."})
    assert _is_a01_supported_by_lp_context(ad_unrelated_lp, issue_cta) is False


@pytest.mark.anyio
async def test_grade_clean_fixtures_en_and_pt(clean_ad_en: AdInput, clean_ad_pt: AdInput) -> None:
    """Grade clean English and Portuguese fixtures.

    Asserts score == 100, grade_10 == 10.0, and passed is True.
    """
    client_en = FakeModelClient()
    result_en = await grade(clean_ad_en, client_en)
    assert result_en.final.score == 100
    assert result_en.final.grade_10 == 10.0
    assert result_en.final.passed is True
    assert result_en.final.issues == []
    assert result_en.final.degraded_reason is None

    client_pt = FakeModelClient()
    result_pt = await grade(clean_ad_pt, client_pt)
    assert result_pt.final.score == 100
    assert result_pt.final.grade_10 == 10.0
    assert result_pt.final.passed is True
    assert result_pt.final.issues == []
    assert result_pt.final.degraded_reason is None


@pytest.mark.anyio
async def test_llm_emitting_d04_stripped_by_filter(clean_ad_en: AdInput) -> None:
    """LLM emitting D04 issue is present in raw but stripped from final by filter_llm_issues."""
    llm_reply = _make_llm_reply(
        issues=[
            {
                "rule_id": "D04",
                "severity": "error",
                "message": "LLM attempting to enforce headline character limit.",
                "location": {"field": "headline", "index": 0},
            }
        ]
    )
    client = FakeModelClient(responses=[llm_reply])
    result = await grade(clean_ad_en, client)

    raw_rule_ids = [i.rule_id for i in result.raw.issues]
    assert "D04" in raw_rule_ids

    final_rule_ids = [i.rule_id for i in result.final.issues]
    assert "D04" not in final_rule_ids
    assert result.final.passed is True


@pytest.mark.anyio
async def test_llm_emitting_a01_verified_price_stripped(
    clean_ad_en: AdInput, clean_ad_pt: AdInput
) -> None:
    """A01 issue when price is in lp_context is present in raw but stripped from final."""
    # English test with $899 in lp_context
    reply_en = _make_llm_reply(
        issues=[
            {
                "rule_id": "A01",
                "severity": "error",
                "message": "Unverified price $899 in headline.",
                "location": {"field": "headline", "index": 0},
            }
        ]
    )
    result_en = await grade(clean_ad_en, FakeModelClient(responses=[reply_en]))
    assert any(i.rule_id == "A01" for i in result_en.raw.issues)
    assert not any(i.rule_id == "A01" for i in result_en.final.issues)
    assert result_en.final.passed is True

    # Portuguese test with R$ 390 in lp_context
    reply_pt = _make_llm_reply(
        issues=[
            {
                "rule_id": "A01",
                "severity": "error",
                "message": "Preço R$ 390 no título não confirmado.",
                "location": {"field": "headline", "index": 0},
            }
        ]
    )
    result_pt = await grade(clean_ad_pt, FakeModelClient(responses=[reply_pt]))
    assert any(i.rule_id == "A01" for i in result_pt.raw.issues)
    assert not any(i.rule_id == "A01" for i in result_pt.final.issues)
    assert result_pt.final.passed is True


@pytest.mark.anyio
async def test_llm_emitting_a01_unverified_price_kept(clean_ad_en: AdInput) -> None:
    """A01 issue when price ($499) is NOT in lp_context is kept in final and passed is False."""
    ad_with_499 = clean_ad_en.model_copy(
        update={"headlines": ["Dental Implants for $499", *clean_ad_en.headlines[1:]]}
    )
    reply = _make_llm_reply(
        issues=[
            {
                "rule_id": "A01",
                "severity": "error",
                "message": "Price $499 is not mentioned in landing page context.",
                "location": {"field": "headline", "index": 0},
            }
        ]
    )
    result = await grade(ad_with_499, FakeModelClient(responses=[reply]))

    assert any(i.rule_id == "A01" for i in result.final.issues)
    assert result.final.passed is False
    assert result.final.score < 100


@pytest.mark.anyio
async def test_llm_emitting_a01_generic_booking_cta_stripped(clean_ad_en: AdInput) -> None:
    """A01 issue on generic booking CTA when lp_context has booking is stripped."""
    reply = _make_llm_reply(
        issues=[
            {
                "rule_id": "A01",
                "severity": "error",
                "message": "Unverified consultation offer: Book your consultation today.",
                "location": {"field": "headline", "index": 4},
            }
        ]
    )
    result = await grade(clean_ad_en, FakeModelClient(responses=[reply]))

    assert any(i.rule_id == "A01" for i in result.raw.issues)
    assert not any(i.rule_id == "A01" for i in result.final.issues)
    assert result.final.passed is True


@pytest.mark.anyio
async def test_llm_emitting_out_of_bounds_location_stripped(clean_ad_en: AdInput) -> None:
    """LLM emitting out-of-bounds location index is stripped from final issues."""
    reply = _make_llm_reply(
        issues=[
            {
                "rule_id": "A03",
                "severity": "warning",
                "message": "Guaranteed results at headline 99.",
                "location": {"field": "headline", "index": 99},
            }
        ]
    )
    result = await grade(clean_ad_en, FakeModelClient(responses=[reply]))

    assert any(i.rule_id == "A03" for i in result.raw.issues)
    assert not any(i.rule_id == "A03" for i in result.final.issues)


def test_filter_llm_issues_unknown_rule_and_normalization(clean_ad_en: AdInput) -> None:
    """Filter strips unknown rule IDs and normalizes casing/source."""
    raw_issues = [
        Issue(
            rule_id="X99",
            severity="warning",
            message="Unknown rule.",
            location=Location(field="headline", index=0),
            source="llm",
        ),
        Issue(
            rule_id="a03",
            severity="warning",
            message="Absolute guarantee.",
            location=Location(field="headline", index=0),
            source="llm",
        ),
    ]
    filtered = filter_llm_issues(clean_ad_en, raw_issues)
    assert len(filtered) == 1
    assert filtered[0].rule_id == "A03"
    assert filtered[0].source == "llm"


@pytest.mark.anyio
async def test_grade_with_system_prompt_override(clean_ad_en: AdInput) -> None:
    """Support system_prompt_override during grading."""
    client = FakeModelClient()
    result = await grade(clean_ad_en, client, system_prompt_override="Custom system prompt")
    assert client.calls[0][0]["content"] == "Custom system prompt"
    assert result.final.passed is True


@pytest.mark.anyio
async def test_grade_with_degradation_llm_client_error(
    clean_ad_en: AdInput, clean_ad_pt: AdInput
) -> None:
    """Degrade gracefully to deterministic code audit on LlmClientError for EN and PT."""
    # English degradation
    client_err_en = FakeModelClient(responses=[LlmClientError("OpenRouter down")])
    result_en = await grade_with_degradation(clean_ad_en, client_err_en)

    assert result_en.model is None
    assert result_en.degraded_reason == DEGRADED_MESSAGES["en"]
    assert result_en.rules_checked == [
        "D01",
        "D02",
        "D03",
        "D04",
        "D05",
        "D06",
        "D07",
        "D08",
        "D09",
        "D10",
        "D11",
    ]
    assert result_en.score == 100

    # Portuguese degradation
    client_err_pt = FakeModelClient(responses=[LlmClientError("OpenRouter offline")])
    result_pt = await grade_with_degradation(clean_ad_pt, client_err_pt)

    assert result_pt.model is None
    assert result_pt.degraded_reason == DEGRADED_MESSAGES["pt"]
    assert result_pt.score == 100


@pytest.mark.anyio
async def test_grade_with_degradation_llm_output_error(
    clean_ad_en: AdInput, clean_ad_pt: AdInput
) -> None:
    """Degrade gracefully to deterministic code audit on LlmOutputError for EN and PT."""
    # English output error (two invalid responses)
    client_err_en = FakeModelClient(
        responses=[ModelReply(content="invalid 1"), ModelReply(content="invalid 2")]
    )
    result_en = await grade_with_degradation(clean_ad_en, client_err_en)
    assert result_en.model is None
    assert result_en.degraded_reason == DEGRADED_MESSAGES["en"]

    # Portuguese output error
    client_err_pt = FakeModelClient(
        responses=[ModelReply(content="invalido 1"), ModelReply(content="invalido 2")]
    )
    result_pt = await grade_with_degradation(clean_ad_pt, client_err_pt)
    assert result_pt.model is None
    assert result_pt.degraded_reason == DEGRADED_MESSAGES["pt"]


@pytest.mark.anyio
async def test_grade_with_degradation_success(clean_ad_en: AdInput) -> None:
    """Return result.final on successful grading without degradation."""
    client = FakeModelClient()
    result = await grade_with_degradation(clean_ad_en, client)
    assert result.score == 100
    assert result.degraded_reason is None
    assert result.model == "fake-model"
