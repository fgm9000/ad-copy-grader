"""Unit tests for Promptfoo evaluation suite providers and bilingual test cases."""

import json
from typing import Any

import pytest

from ad_copy_grader.llm import (
    ChatMessage,
    LlmClientError,
    ModelClient,
    ModelReply,
)
from ad_copy_grader.models import AdInput
from evals.cases import assert_case, build_eval_cases, get_tests
from evals.provider import _MEMORY_CACHE, RetryingEvalModelClient, call_api


@pytest.fixture(autouse=True)
def clear_eval_cache() -> None:
    """Clear memory cache between test runs."""
    _MEMORY_CACHE.clear()


def test_get_tests_structure() -> None:
    """Verify get_tests returns 16 valid test cases covering English and Portuguese."""
    tests = get_tests()
    assert len(tests) == 16

    languages = set()
    for test in tests:
        assert "description" in test
        assert "vars" in test
        assert "assert" in test
        assert len(test["assert"]) == 1
        assert test["assert"][0]["type"] == "javascript"

        vars_dict = test["vars"]
        assert "name" in vars_dict
        assert "payload" in vars_dict
        assert "expected_llm_rules" in vars_dict
        assert "expected_code_rules" in vars_dict

        ad = AdInput.model_validate(vars_dict["payload"])
        assert ad.headlines
        assert ad.descriptions
        assert ad.final_url
        languages.add(ad.lang)

    assert "en" in languages
    assert "pt" in languages


def test_build_eval_cases_coverage() -> None:
    """Verify build_eval_cases produces exactly 16 distinct single-mutation scenarios."""
    cases = build_eval_cases()
    assert len(cases) == 16
    case_ids = [c["id"] for c in cases]
    assert len(set(case_ids)) == 16


def test_call_api_verified_price_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test raw, pipeline, and degraded modes on verified price scenario."""
    monkeypatch.setenv("FAKE_MODEL", "1")

    base_cases = {c["name"]: c for c in build_eval_cases()}
    verified_case = base_cases.get("05_verified_price_in_lp_en")
    assert verified_case is not None
    payload = verified_case["payload"]

    case_name = "07_en_verified_price_in_lp_no_false_positive"
    context: dict[str, Any] = {
        "vars": {
            "name": case_name,
            "payload": payload,
        }
    }

    # 1. Raw mode: A01 is present (simulated raw model false positive)
    raw_res = call_api("prompt", {"config": {"mode": "raw"}}, context)
    assert "error" not in raw_res
    raw_data = json.loads(raw_res["output"])
    raw_issues = raw_data.get("issues", [])
    assert any(i.get("rule_id") == "A01" for i in raw_issues)

    # 2. Pipeline mode: A01 is removed from issues and present in dropped_issues
    pipeline_res = call_api("prompt", {"config": {"mode": "pipeline"}}, context)
    assert "error" not in pipeline_res
    pipeline_data = json.loads(pipeline_res["output"])
    pipeline_issues = pipeline_data.get("issues", [])
    assert not any(i.get("rule_id") == "A01" for i in pipeline_issues)
    dropped_issues = pipeline_data.get("dropped_issues", [])
    assert any(i.get("rule_id") == "A01" for i in dropped_issues)

    # 3. Degraded mode: A01 is present
    degraded_res = call_api("prompt", {"config": {"mode": "degraded"}}, context)
    assert "error" not in degraded_res
    degraded_data = json.loads(degraded_res["output"])
    degraded_issues = degraded_data.get("issues", [])
    assert any(i.get("rule_id") == "A01" for i in degraded_issues)


def test_call_api_invalid_mode() -> None:
    """Test call_api with unsupported mode raises ValueError."""
    with pytest.raises(ValueError, match="Invalid provider config.mode"):
        call_api("prompt", {"config": {"mode": "unsupported"}}, {"vars": {}})


def test_call_api_missing_api_key_when_fake_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test call_api with FAKE_MODEL=0 and empty OPENROUTER_API_KEY returns error dictionary."""
    monkeypatch.setenv("FAKE_MODEL", "0")
    monkeypatch.setenv("EVAL_FAKE_MODEL", "0")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    res = call_api("prompt", {"config": {"mode": "pipeline"}}, {"vars": {}})
    assert "error" in res
    assert "OPENROUTER_API_KEY is not set" in res["error"]


def test_call_api_missing_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test call_api with missing payload in context vars returns error dictionary."""
    monkeypatch.setenv("FAKE_MODEL", "1")
    res = call_api("prompt", {"config": {"mode": "pipeline"}}, {"vars": {}})
    assert "error" in res
    assert "Missing 'payload'" in res["error"]


@pytest.mark.anyio
async def test_retrying_client_transient_retry() -> None:
    """Test RetryingEvalModelClient retries on HTTP 429 and records sleep intervals."""
    sleep_calls: list[float] = []

    def record_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    class FlakyClient(ModelClient):
        def __init__(self) -> None:
            self.call_count = 0

        async def complete_json(
            self, messages: list[ChatMessage], max_tokens: int = 2048
        ) -> ModelReply:
            self.call_count += 1
            if self.call_count < 3:
                raise LlmClientError("OpenRouter returned HTTP 429: Rate limit exceeded")
            return ModelReply(
                content="{}",
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                cost_usd=0.0001,
                model="test-model",
            )

    flaky = FlakyClient()
    retrying = RetryingEvalModelClient(
        inner=flaky,
        delays=(0.01, 0.02, 0.04),
        sleep_fn=record_sleep,
    )

    reply = await retrying.complete_json([])
    assert flaky.call_count == 3
    assert sleep_calls == [0.01, 0.02]
    assert reply.model == "test-model"


@pytest.mark.anyio
async def test_retrying_client_non_transient_raises_immediately() -> None:
    """Test RetryingEvalModelClient raises non-transient HTTP 400 error immediately."""
    sleep_calls: list[float] = []

    def record_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    class BadRequestClient(ModelClient):
        async def complete_json(
            self, messages: list[ChatMessage], max_tokens: int = 2048
        ) -> ModelReply:
            raise LlmClientError("OpenRouter returned HTTP 400: Bad request")

    retrying = RetryingEvalModelClient(
        inner=BadRequestClient(),
        delays=(0.01, 0.02),
        sleep_fn=record_sleep,
    )

    with pytest.raises(LlmClientError, match="HTTP 400"):
        await retrying.complete_json([])

    assert len(sleep_calls) == 0


def test_assert_case_evaluator() -> None:
    """Test assert_case python assertion verification logic."""
    output = json.dumps(
        {
            "passed": True,
            "grade_10": 10.0,
            "issues": [],
        }
    )
    context: dict[str, Any] = {
        "providerResponse": {"metadata": {"mode": "pipeline"}},
        "vars": {
            "expected_llm_rules": [],
            "expected_code_rules": [],
        },
    }
    result = assert_case(output, context)
    assert result["pass"] is True
    assert result["score"] == 1.0
