"""Unit tests for prompt building, LLM clients, and output parser."""

import json
import unittest.mock
from typing import Any

import httpx
import pytest

from ad_copy_grader.llm import (
    ChatMessage,
    FakeModelClient,
    LlmClientError,
    ModelReply,
    OpenRouterClient,
)
from ad_copy_grader.models import AdInput, Issue, Location
from ad_copy_grader.parser import (
    LlmOutputError,
    extract_json_object,
    parse_llm_review,
    request_and_parse_review,
)
from ad_copy_grader.prompt import (
    DEGRADED_SENTINEL_EN,
    DEGRADED_SENTINEL_PT,
    build_degraded_system_prompt,
    build_system_prompt,
    build_user_message,
)


@pytest.fixture
def anyio_backend() -> str:
    """Specify anyio backend for async tests."""
    return "asyncio"


def test_extract_json_object_raw() -> None:
    """Extract raw JSON without markdown fences."""
    raw = '{"issues": [], "rules_checked": ["A01", "A02", "A03"], "suggestions": []}'
    assert extract_json_object(raw) == raw


def test_extract_json_object_code_fence() -> None:
    """Extract JSON wrapped in markdown code fences."""
    payload = '{"issues": [], "rules_checked": ["A01", "A02", "A03"]}'
    fenced_json = f"```json\n{payload}\n```"
    assert extract_json_object(fenced_json) == payload

    fenced_plain = f"```\n{payload}\n```"
    assert extract_json_object(fenced_plain) == payload


def test_extract_json_object_with_surrounding_prose() -> None:
    """Extract JSON object with leading and trailing conversational text."""
    payload = '{"issues": [], "rules_checked": ["A01", "A02", "A03"]}'
    wrapped = f"Here is the result:\n{payload}\nHope this helps!"
    assert extract_json_object(wrapped) == payload


def test_extract_json_object_no_braces() -> None:
    """Return stripped text when no braces are found."""
    raw = "   no braces here   "
    assert extract_json_object(raw) == "no braces here"


def test_parse_llm_review_valid_en() -> None:
    """Parse valid English LLM review output."""
    raw = json.dumps(
        {
            "issues": [
                {
                    "rule_id": "A01",
                    "severity": "error",
                    "message": "Unverified price claim.",
                    "location": {"field": "headline", "index": 0},
                }
            ],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [
                {
                    "location": {"field": "headline", "index": 0},
                    "original": "Dental Implants $499",
                    "suggested": "Quality Dental Implants",
                    "reason": "Remove unverified price.",
                }
            ],
        }
    )
    review = parse_llm_review(raw)
    assert len(review.issues) == 1
    assert review.issues[0].rule_id == "A01"
    assert review.rules_checked == ["A01", "A02", "A03"]
    assert len(review.suggestions) == 1

    domain_issue = review.issues[0].to_issue()
    assert domain_issue.source == "llm"
    assert domain_issue.severity == "error"


def test_parse_llm_review_valid_pt() -> None:
    """Parse valid Portuguese LLM review output."""
    raw = json.dumps(
        {
            "issues": [
                {
                    "rule_id": "A02",
                    "severity": "warning",
                    "message": "Nenhuma descrição possui CTA clara.",
                    "location": {"field": "description", "index": 0},
                }
            ],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [],
        }
    )
    review = parse_llm_review(raw)
    assert len(review.issues) == 1
    assert review.issues[0].rule_id == "A02"
    assert review.rules_checked == ["A01", "A02", "A03"]


def test_parse_llm_review_missing_semantic_rule() -> None:
    """Raise ValueError when rules_checked omits required semantic rules."""
    raw = json.dumps(
        {
            "issues": [],
            "rules_checked": ["A01", "A02"],
            "suggestions": [],
        }
    )
    with pytest.raises(ValueError, match="missing required semantic rules: A03"):
        parse_llm_review(raw)


@pytest.mark.anyio
async def test_request_and_parse_review_success_first_attempt() -> None:
    """Parse output on the first attempt without needing self-correction retry."""
    payload = json.dumps(
        {
            "issues": [],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [],
        }
    )
    client = FakeModelClient(
        responses=[
            ModelReply(
                content=payload,
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost_usd=0.001,
                model="test-model",
            )
        ]
    )
    messages: list[ChatMessage] = [{"role": "user", "content": "audit"}]
    review, reply = await request_and_parse_review(client, messages, lang="en")

    assert review.rules_checked == ["A01", "A02", "A03"]
    assert reply.prompt_tokens == 100
    assert reply.completion_tokens == 50
    assert reply.total_tokens == 150
    assert reply.cost_usd == 0.001
    assert len(client.calls) == 1


@pytest.mark.anyio
async def test_request_and_parse_review_recovers_on_retry_en() -> None:
    """Recover on second attempt after first attempt has invalid JSON, summing telemetry."""
    valid_payload = json.dumps(
        {
            "issues": [],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [],
        }
    )
    first_reply = ModelReply(
        content="not-json",
        prompt_tokens=80,
        completion_tokens=20,
        total_tokens=100,
        cost_usd=0.0005,
        model="test-model",
    )
    second_reply = ModelReply(
        content=valid_payload,
        prompt_tokens=120,
        completion_tokens=40,
        total_tokens=160,
        cost_usd=0.001,
        model="test-model",
    )
    client = FakeModelClient(responses=[first_reply, second_reply])
    messages: list[ChatMessage] = [{"role": "user", "content": "audit"}]

    review, combined = await request_and_parse_review(client, messages, lang="en")

    assert review.rules_checked == ["A01", "A02", "A03"]
    assert combined.prompt_tokens == 200
    assert combined.completion_tokens == 60
    assert combined.total_tokens == 260
    assert combined.cost_usd == 0.0015
    assert len(client.calls) == 2
    assert "Your previous response failed JSON schema validation" in client.calls[1][2]["content"]


@pytest.mark.anyio
async def test_request_and_parse_review_recovers_missing_rule_pt() -> None:
    """Recover on second attempt when first attempt misses A03 in rules_checked with PT prompt."""
    invalid_payload = json.dumps(
        {
            "issues": [],
            "rules_checked": ["A01", "A02"],
            "suggestions": [],
        }
    )
    valid_payload = json.dumps(
        {
            "issues": [],
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": [],
        }
    )
    first_reply = ModelReply(
        content=invalid_payload,
        prompt_tokens=70,
        completion_tokens=30,
        total_tokens=100,
        cost_usd=0.0004,
        model="test-model",
    )
    second_reply = ModelReply(
        content=valid_payload,
        prompt_tokens=110,
        completion_tokens=50,
        total_tokens=160,
        cost_usd=0.0008,
        model="test-model",
    )
    client = FakeModelClient(responses=[first_reply, second_reply])
    messages: list[ChatMessage] = [{"role": "user", "content": "audite"}]

    review, combined = await request_and_parse_review(client, messages, lang="pt")

    assert review.rules_checked == ["A01", "A02", "A03"]
    assert combined.total_tokens == 260
    assert combined.cost_usd == 0.0012
    assert (
        "Sua resposta anterior falhou na validação de schema JSON" in client.calls[1][2]["content"]
    )


@pytest.mark.anyio
async def test_request_and_parse_review_both_attempts_fail() -> None:
    """Raise LlmOutputError when both first and second attempts fail validation."""
    first_reply = ModelReply(content="invalid 1")
    second_reply = ModelReply(content="invalid 2")
    client = FakeModelClient(responses=[first_reply, second_reply])
    messages: list[ChatMessage] = [{"role": "user", "content": "audit"}]

    with pytest.raises(LlmOutputError, match="LLM output failed validation after retry"):
        await request_and_parse_review(client, messages, lang="en")


def test_build_system_prompts() -> None:
    """Verify system prompts and degraded prompts contain expected sentinels."""
    en = build_system_prompt("en")
    assert DEGRADED_SENTINEL_EN in en
    assert "A01" in en and "A02" in en and "A03" in en

    pt = build_system_prompt("pt")
    assert DEGRADED_SENTINEL_PT in pt
    assert "A01" in pt and "A02" in pt and "A03" in pt

    degraded_en = build_degraded_system_prompt("en")
    assert DEGRADED_SENTINEL_EN not in degraded_en
    assert "A01" in degraded_en

    degraded_pt = build_degraded_system_prompt("pt")
    assert DEGRADED_SENTINEL_PT not in degraded_pt
    assert "A01" in degraded_pt


def test_build_degraded_system_prompt_missing_sentinel() -> None:
    """Raise RuntimeError when sentinel is missing from base prompt."""
    with (
        unittest.mock.patch("ad_copy_grader.prompt.build_system_prompt", return_value="custom"),
        pytest.raises(RuntimeError, match="Degraded sentinel line not found"),
    ):
        build_degraded_system_prompt("en")


def test_build_user_message_en_and_pt() -> None:
    """Build serialized user messages for English and Portuguese ad payloads."""
    ad = AdInput(
        headlines=["H1", "H2", "H3"],
        descriptions=["D1", "D2"],
        path1="p1",
        path2="p2",
        final_url="https://example.com",
        primary_service="Dental",
        lp_context="context",
        lang="en",
    )
    det_issues = [
        Issue(
            rule_id="D02",
            severity="warning",
            message="Fewer than 15 headlines.",
            location=Location(field="headline", index=0),
            source="code",
        ),
        Issue(
            rule_id="D01",
            severity="error",
            message="Global issue without location.",
            location=None,
            source="code",
        ),
    ]

    msg_en = build_user_message(ad, det_issues)
    assert "Audit the following RSA ad JSON payload" in msg_en
    assert "<ad_payload>" in msg_en
    assert "deterministic_issues_for_rewrite" in msg_en
    assert "D02" in msg_en

    ad_pt = ad.model_copy(update={"lang": "pt"})
    msg_pt = build_user_message(ad_pt)
    assert "Audite o seguinte payload JSON de anúncio RSA" in msg_pt
    assert "deterministic_issues_for_rewrite" not in msg_pt


@pytest.mark.anyio
async def test_openrouter_client_200_ok_with_telemetry() -> None:
    """Execute OpenRouterClient call with mocked 200 response and parse telemetry."""
    payload: dict[str, Any] = {
        "model": "google/gemini-2.5-flash",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"issues": [], "rules_checked": ["A01", "A02", "A03"]}',
                }
            }
        ],
        "usage": {
            "prompt_tokens": 120,
            "completion_tokens": 45,
            "total_tokens": 165,
            "cost": 0.00042,
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["HTTP-Referer"] == "https://github.com/fgm9000/ad-copy-grader"
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="test-key", http_client=http_client)
        assert client.model_name == "google/gemini-2.5-flash"
        reply = await client.complete_json([{"role": "user", "content": "hi"}])

    assert reply.prompt_tokens == 120
    assert reply.completion_tokens == 45
    assert reply.total_tokens == 165
    assert reply.cost_usd == 0.00042
    assert reply.model == "google/gemini-2.5-flash"


@pytest.mark.anyio
async def test_openrouter_client_missing_api_key() -> None:
    """Raise LlmClientError when API key is empty or whitespace."""
    client_empty = OpenRouterClient(api_key="")
    with pytest.raises(LlmClientError, match="API key is not configured"):
        await client_empty.complete_json([{"role": "user", "content": "test"}])

    client_whitespace = OpenRouterClient(api_key="   ")
    with pytest.raises(LlmClientError, match="API key is not configured"):
        await client_whitespace.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_http_500_error() -> None:
    """Raise LlmClientError when OpenRouter returns non-200 HTTP status."""
    transport = httpx.MockTransport(lambda req: httpx.Response(500, text="Internal Error"))
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="key", http_client=http_client)
        with pytest.raises(LlmClientError, match="OpenRouter returned HTTP 500"):
            await client.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_non_json_error() -> None:
    """Raise LlmClientError when response body is not JSON."""
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=b"not-json-content"))
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="key", http_client=http_client)
        with pytest.raises(LlmClientError, match="non-JSON HTTP body"):
            await client.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_empty_choices_error() -> None:
    """Raise LlmClientError when choices array is missing or empty."""
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={"choices": []}))
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="key", http_client=http_client)
        with pytest.raises(LlmClientError, match="contained no choices"):
            await client.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_empty_content_error() -> None:
    """Raise LlmClientError when message content is empty string."""
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"choices": [{"message": {"content": "   "}}]})
    )
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="key", http_client=http_client)
        with pytest.raises(LlmClientError, match="empty message content"):
            await client.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_timeout_error() -> None:
    """Raise LlmClientError on request timeout."""

    def raise_timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Connection timed out", request=request)

    transport = httpx.MockTransport(raise_timeout)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="key", http_client=http_client, timeout_seconds=1.0)
        with pytest.raises(LlmClientError, match="timed out after 1.0s"):
            await client.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_network_error() -> None:
    """Raise LlmClientError on network failure."""

    def raise_connect_error(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Network unreachable", request=request)

    transport = httpx.MockTransport(raise_connect_error)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = OpenRouterClient(api_key="key", http_client=http_client)
        with pytest.raises(LlmClientError, match="network communication failed"):
            await client.complete_json([{"role": "user", "content": "test"}])


@pytest.mark.anyio
async def test_openrouter_client_default_http_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify default httpx.AsyncClient context manager execution when http_client is None."""
    payload: dict[str, Any] = {
        "model": "custom-model",
        "choices": [{"message": {"role": "assistant", "content": '{"ok": true}'}}],
    }
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json=payload))

    class MockAsyncClient(httpx.AsyncClient):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(transport=transport, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)
    client = OpenRouterClient(api_key="test-key")
    reply = await client.complete_json([{"role": "user", "content": "ping"}])
    assert reply.content == '{"ok": true}'
    assert reply.model == "custom-model"


@pytest.mark.anyio
async def test_fake_model_client_features() -> None:
    """Exercise FakeModelClient handlers, exceptions, and automatic fallback audit."""
    # Invalid JSON inside <ad_payload>
    client_invalid_payload = FakeModelClient()
    reply_bad_payload = await client_invalid_payload.complete_json(
        [
            {"role": "user", "content": "<ad_payload>{invalid json}</ad_payload>"},
        ]
    )
    assert "A02" in reply_bad_payload.content

    # String response
    client_str = FakeModelClient(responses=['{"str_resp": true}'])
    reply_from_str = await client_str.complete_json([{"role": "user", "content": "test"}])
    assert reply_from_str.content == '{"str_resp": true}'

    # Exception response
    client_exc = FakeModelClient(responses=[LlmClientError("Custom error")])
    with pytest.raises(LlmClientError, match="Custom error"):
        await client_exc.complete_json([{"role": "user", "content": "test"}])

    # Handler returning str
    client_handler_str = FakeModelClient(handler=lambda msgs: '{"handled": true}')
    reply_str = await client_handler_str.complete_json([{"role": "user", "content": "test"}])
    assert reply_str.content == '{"handled": true}'
    assert client_handler_str.model_name == "fake-model"

    # Handler returning ModelReply
    client_handler_reply = FakeModelClient(
        handler=lambda msgs: ModelReply(content="ok", cost_usd=0.002)
    )
    reply_obj = await client_handler_reply.complete_json([{"role": "user", "content": "test"}])
    assert reply_obj.content == "ok"
    assert reply_obj.cost_usd == 0.002

    # Default fake audit simulating violations (headline price, description price, missing CTA)
    ad_payload = {
        "lang": "en",
        "primary_service": "Dental Implants",
        "headlines": ["Implants $499", "Guaranteed Smile Restoration"],
        "descriptions": [
            "Titanium implants for only $899.",
            "100% cure guaranteed for missing teeth.",
        ],
    }
    user_msg = f"<ad_payload>{json.dumps(ad_payload)}</ad_payload>"
    default_client = FakeModelClient()
    audit_reply = await default_client.complete_json(
        [
            {"role": "system", "content": "custom"},
            {"role": "user", "content": user_msg},
        ]
    )
    audit_data = json.loads(audit_reply.content)
    rule_ids = [issue["rule_id"] for issue in audit_data["issues"]]
    assert "A01" in rule_ids
    assert "A02" in rule_ids
    assert "A03" in rule_ids
    assert "D04" in rule_ids  # Degraded mode because system prompt lacked sentinel

    # Portuguese fake audit with CTA present
    ad_payload_pt = {
        "lang": "pt",
        "primary_service": "Implantes",
        "headlines": ["Implantes R$ 500", "Resultado Imediato"],
        "descriptions": ["Implantes dentários de titânio. Agende sua consulta hoje."],
    }
    user_msg_pt = f"<ad_payload>{json.dumps(ad_payload_pt)}</ad_payload>"
    audit_pt = await default_client.complete_json(
        [
            {"role": "system", "content": build_system_prompt("pt")},
            {"role": "user", "content": user_msg_pt},
        ]
    )
    audit_pt_data = json.loads(audit_pt.content)
    pt_rules = [issue["rule_id"] for issue in audit_pt_data["issues"]]
    assert "A01" in pt_rules
    assert "A03" in pt_rules
    assert "A02" not in pt_rules
    assert "D04" not in pt_rules  # Not degraded because sentinel was present
