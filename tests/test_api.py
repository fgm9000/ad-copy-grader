"""Tests for FastAPI application, health check, grading endpoints, CORS, and settings."""

import json
import logging
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

from ad_copy_grader.api import app as module_app
from ad_copy_grader.api import create_app, log_grade_event
from ad_copy_grader.limits import RateLimiter
from ad_copy_grader.llm import FakeModelClient, LlmClientError, ModelReply
from ad_copy_grader.models import AdInput, GradeResult
from ad_copy_grader.pipeline import DEGRADED_MESSAGES
from ad_copy_grader.settings import Settings, get_settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def clean_ad_payload_en() -> dict[str, Any]:
    """Load valid clean English ad fixture."""
    with (FIXTURES_DIR / "base_clean_en.json").open("r", encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


@pytest.fixture
def clean_ad_payload_pt() -> dict[str, Any]:
    """Load valid clean Portuguese ad fixture."""
    with (FIXTURES_DIR / "base_clean_pt.json").open("r", encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def test_healthz_endpoint() -> None:
    """Verify GET /healthz returns 200 with status ok and version 0.1.0."""
    app = create_app(settings=Settings(fake_model=True))
    client = TestClient(app)

    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_grade_endpoint_valid_en_and_pt(
    clean_ad_payload_en: dict[str, Any],
    clean_ad_payload_pt: dict[str, Any],
) -> None:
    """Verify POST /v1/grade returns 200 for clean EN and PT ads."""
    app = create_app(settings=Settings(fake_model=True))
    client = TestClient(app)

    # English ad
    response_en = client.post("/v1/grade", json=clean_ad_payload_en)
    assert response_en.status_code == 200
    data_en = response_en.json()
    assert data_en["score"] == 100
    assert data_en["grade_10"] == 10.0
    assert data_en["passed"] is True
    assert data_en["degraded_reason"] is None

    # Portuguese ad
    response_pt = client.post("/v1/grade", json=clean_ad_payload_pt)
    assert response_pt.status_code == 200
    data_pt = response_pt.json()
    assert data_pt["score"] == 100
    assert data_pt["grade_10"] == 10.0
    assert data_pt["passed"] is True
    assert data_pt["degraded_reason"] is None


def test_grade_endpoint_invalid_input(clean_ad_payload_en: dict[str, Any]) -> None:
    """Verify POST /v1/grade returns 422 on schema violation (e.g. headline > 60 chars)."""
    app = create_app(settings=Settings(fake_model=True))
    client = TestClient(app)

    invalid_payload = dict(clean_ad_payload_en)
    invalid_payload["headlines"] = ["A" * 65]
    response = client.post("/v1/grade", json=invalid_payload)
    assert response.status_code == 422


def test_grade_endpoint_rate_limit_per_ip(
    clean_ad_payload_en: dict[str, Any],
    clean_ad_payload_pt: dict[str, Any],
) -> None:
    """Verify POST /v1/grade returns 429 when per-IP rate limit is exceeded (EN and PT)."""
    rate_limiter = RateLimiter(rate_limit_per_minute=2, daily_request_cap=100)
    app = create_app(settings=Settings(fake_model=True), rate_limiter=rate_limiter)
    client = TestClient(app)

    headers = {"X-Forwarded-For": "198.51.100.1"}

    # First two requests succeed
    res1 = client.post("/v1/grade", json=clean_ad_payload_en, headers=headers)
    assert res1.status_code == 200

    res2 = client.post("/v1/grade", json=clean_ad_payload_en, headers=headers)
    assert res2.status_code == 200

    # Third request blocked with English message
    res3 = client.post("/v1/grade", json=clean_ad_payload_en, headers=headers)
    assert res3.status_code == 429
    data3 = res3.json()
    assert data3["reason"] == "ip_rate_limit"
    assert "Rate limit exceeded: maximum 2 requests per minute per IP" in data3["detail"]

    # Fourth request blocked with Portuguese message
    res4 = client.post("/v1/grade", json=clean_ad_payload_pt, headers=headers)
    assert res4.status_code == 429
    data4 = res4.json()
    assert data4["reason"] == "ip_rate_limit"
    assert "Limite de requisições por minuto excedido: máximo de 2 por IP" in data4["detail"]


def test_grade_endpoint_daily_cap(
    clean_ad_payload_en: dict[str, Any],
    clean_ad_payload_pt: dict[str, Any],
) -> None:
    """Verify POST /v1/grade returns 429 when daily cap is reached across IPs (EN and PT)."""
    rate_limiter = RateLimiter(rate_limit_per_minute=10, daily_request_cap=2)
    app = create_app(settings=Settings(fake_model=True), rate_limiter=rate_limiter)
    client = TestClient(app)

    res1 = client.post(
        "/v1/grade", json=clean_ad_payload_en, headers={"X-Forwarded-For": "10.0.0.1"}
    )
    assert res1.status_code == 200

    res2 = client.post(
        "/v1/grade", json=clean_ad_payload_en, headers={"X-Forwarded-For": "10.0.0.2"}
    )
    assert res2.status_code == 200

    # 3rd request blocked by daily cap (English)
    res3 = client.post(
        "/v1/grade", json=clean_ad_payload_en, headers={"X-Forwarded-For": "10.0.0.3"}
    )
    assert res3.status_code == 429
    data3 = res3.json()
    assert data3["reason"] == "daily_cap"
    assert "Daily public demo quota (2 requests/day) reached" in data3["detail"]

    # 4th request blocked by daily cap (Portuguese)
    res4 = client.post(
        "/v1/grade", json=clean_ad_payload_pt, headers={"X-Forwarded-For": "10.0.0.4"}
    )
    assert res4.status_code == 429
    data4 = res4.json()
    assert data4["reason"] == "daily_cap"
    assert (
        "A cota diária da demonstração pública (2 requisições/dia) foi atingida" in data4["detail"]
    )


def test_grade_endpoint_degradation_llm_client_error(
    clean_ad_payload_en: dict[str, Any],
) -> None:
    """Verify graceful degradation on LlmClientError for default and strict_llm mode."""
    sensitive_marker = "private-leak-check-marker-999"
    failing_client = FakeModelClient(
        handler=lambda msgs: (_ for _ in ()).throw(
            LlmClientError(f"Connection failed for id {sensitive_marker}")
        )
    )
    app = create_app(model_client=failing_client)
    client = TestClient(app)

    # 1. Default (strict_llm=false) -> 200 with degraded result
    res_default = client.post("/v1/grade", json=clean_ad_payload_en)
    assert res_default.status_code == 200
    data_default = res_default.json()
    assert data_default["model"] is None
    assert data_default["degraded_reason"] == DEGRADED_MESSAGES["en"]
    assert sensitive_marker not in res_default.text

    # 2. Strict (strict_llm=true) -> 502 with detail and partial_result
    res_strict = client.post("/v1/grade?strict_llm=true", json=clean_ad_payload_en)
    assert res_strict.status_code == 502
    data_strict = res_strict.json()
    assert data_strict["detail"] == DEGRADED_MESSAGES["en"]
    assert data_strict["partial_result"]["model"] is None
    assert data_strict["partial_result"]["degraded_reason"] == DEGRADED_MESSAGES["en"]
    assert sensitive_marker not in res_strict.text


def test_grade_endpoint_degradation_llm_output_error(
    clean_ad_payload_en: dict[str, Any],
) -> None:
    """Verify graceful degradation on invalid output JSON for default and strict_llm mode."""
    bad_output_client = FakeModelClient(
        handler=lambda msgs: ModelReply(content="This is completely invalid non-JSON output")
    )
    app = create_app(model_client=bad_output_client)
    client = TestClient(app)

    # 1. Default (strict_llm=false) -> 200 with degraded result
    res_default = client.post("/v1/grade", json=clean_ad_payload_en)
    assert res_default.status_code == 200
    data_default = res_default.json()
    assert data_default["model"] is None
    assert data_default["degraded_reason"] == DEGRADED_MESSAGES["en"]

    # 2. Strict (strict_llm=true) -> 502 with detail and partial_result
    res_strict = client.post("/v1/grade?strict_llm=true", json=clean_ad_payload_en)
    assert res_strict.status_code == 502
    data_strict = res_strict.json()
    assert data_strict["detail"] == DEGRADED_MESSAGES["en"]
    assert data_strict["partial_result"]["model"] is None
    assert data_strict["partial_result"]["degraded_reason"] == DEGRADED_MESSAGES["en"]


def test_grade_endpoint_strict_llm_success(
    clean_ad_payload_en: dict[str, Any],
) -> None:
    """Verify strict_llm=true returns 200 when LLM review completes successfully."""
    app = create_app(settings=Settings(fake_model=True))
    client = TestClient(app)

    res = client.post("/v1/grade?strict_llm=true", json=clean_ad_payload_en)
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 100
    assert data["passed"] is True
    assert data["degraded_reason"] is None


def test_cors_middleware_headers() -> None:
    """Verify CORS headers for allowed origins and rejection of unlisted origins."""
    settings = Settings(
        allowed_origins=["http://localhost:8000", "https://fgm9000.github.io"],
        fake_model=True,
    )
    app = create_app(settings=settings)
    client = TestClient(app)

    # Allowed origin GET
    res_allowed = client.get("/healthz", headers={"Origin": "http://localhost:8000"})
    assert res_allowed.headers.get("access-control-allow-origin") == "http://localhost:8000"

    # Allowed origin preflight OPTIONS
    res_preflight = client.options(
        "/v1/grade",
        headers={
            "Origin": "https://fgm9000.github.io",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert res_preflight.status_code == 200
    assert res_preflight.headers.get("access-control-allow-origin") == "https://fgm9000.github.io"
    assert "POST" in res_preflight.headers.get("access-control-allow-methods", "")

    # Unlisted origin
    res_unlisted = client.get("/healthz", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in res_unlisted.headers


def test_settings_allowed_origins_parsing() -> None:
    """Verify parsing of allowed_origins from list, JSON array string, and comma string."""
    # 1. From list of strings
    s1 = Settings(allowed_origins=["https://a.com", "  https://b.com  ", ""])
    assert s1.allowed_origins == ["https://a.com", "https://b.com"]

    # 2. From JSON array string via model_validate
    s2 = Settings.model_validate({"allowed_origins": '["https://a.com", " https://b.com "]'})
    assert s2.allowed_origins == ["https://a.com", "https://b.com"]

    # 3. From comma-separated string via model_validate
    s3 = Settings.model_validate({"allowed_origins": "https://a.com, https://b.com, "})
    assert s3.allowed_origins == ["https://a.com", "https://b.com"]

    # 4. From whitespace / empty string via model_validate
    s4 = Settings.model_validate({"allowed_origins": "   "})
    assert s4.allowed_origins == []

    # 5. From invalid JSON string fallback to comma split via model_validate
    s5 = Settings.model_validate({"allowed_origins": "[https://a.com,https://b.com]"})
    assert s5.allowed_origins == ["[https://a.com", "https://b.com]"]

    # 6. From non-list non-string type via model_validate
    s6 = Settings.model_validate({"allowed_origins": None})
    assert s6.allowed_origins == []

    # 7. Direct validator method invocation
    assert Settings.parse_allowed_origins(12345) == []

    # 8. Helper get_settings() returns Settings instance
    cached = get_settings()
    assert isinstance(cached, Settings)


def test_structured_logging_output(
    clean_ad_payload_en: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify log_grade_event logs JSON payload without sensitive ad content."""
    app = create_app(settings=Settings(fake_model=True))
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="ad_copy_grader.api"):
        res = client.post("/v1/grade", json=clean_ad_payload_en)
        assert res.status_code == 200

    grade_logs = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "ad_copy_grader.api"
    ]
    assert len(grade_logs) >= 1
    log_event = grade_logs[0]
    assert log_event["event"] == "grade_completed"
    assert log_event["lang"] == "en"
    assert log_event["headline_count"] == 15
    assert log_event["description_count"] == 4
    assert isinstance(log_event["rules_triggered"], list)
    assert log_event["score"] == 100
    assert log_event["grade_10"] == 10.0
    assert log_event["passed"] is True
    assert log_event["degraded"] is False
    assert isinstance(log_event["latency_ms"], float)
    assert log_event["latency_ms"] >= 0.0

    # Ensure sensitive ad copy text is NEVER in any log message
    for record in caplog.records:
        assert "Dental Implants Specialist" not in record.message
        assert "BrightSmile Dental Clinic" not in record.message


def test_log_grade_event_direct(clean_ad_payload_en: dict[str, Any]) -> None:
    """Verify log_grade_event helper with direct call."""
    ad = AdInput.model_validate(clean_ad_payload_en)
    result = GradeResult(
        score=90,
        grade_10=9.0,
        passed=True,
        issues=[],
        suggestions=[],
        discarded_suggestions_count=0,
        rules_checked=["D01"],
        model="test-model",
        degraded_reason=None,
    )
    log_grade_event(ad, result, 12.345)


def test_create_app_defaults_and_branches() -> None:
    """Verify create_app initialization branches including OpenRouter client creation."""
    # Settings with fake_model=False creates OpenRouterClient
    settings = Settings(openrouter_api_key="test-key", fake_model=False)
    app = create_app(settings=settings)
    assert app is not None

    # Module-level app instance
    assert module_app is not None
