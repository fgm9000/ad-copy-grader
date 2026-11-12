"""FastAPI application, endpoints, rate limiting, and structured logging."""

import json
import logging
import time

from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ad_copy_grader import __version__
from ad_copy_grader.limits import RateLimiter, extract_client_ip
from ad_copy_grader.llm import (
    FakeModelClient,
    LlmClientError,
    ModelClient,
    OpenRouterClient,
)
from ad_copy_grader.models import AdInput, GradeResult
from ad_copy_grader.parser import LlmOutputError
from ad_copy_grader.pipeline import grade, grade_with_degradation
from ad_copy_grader.settings import Settings, get_settings

logger = logging.getLogger("ad_copy_grader.api")


def log_grade_event(
    ad: AdInput,
    result: GradeResult,
    latency_ms: float,
) -> None:
    """Log structured event for ad grading completion without sensitive data."""
    payload = {
        "event": "grade_completed",
        "lang": ad.lang,
        "headline_count": len(ad.headlines),
        "description_count": len(ad.descriptions),
        "rules_triggered": [issue.rule_id for issue in result.issues],
        "score": result.score,
        "grade_10": result.grade_10,
        "passed": result.passed,
        "degraded": result.degraded_reason is not None,
        "latency_ms": round(latency_ms, 2),
    }
    logger.info(json.dumps(payload))


def create_app(
    settings: Settings | None = None,
    model_client: ModelClient | None = None,
    rate_limiter: RateLimiter | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application instance."""
    resolved_settings = settings or get_settings()

    limiter = (
        rate_limiter
        if rate_limiter is not None
        else RateLimiter(
            rate_limit_per_minute=resolved_settings.rate_limit_per_minute,
            daily_request_cap=resolved_settings.daily_request_cap,
        )
    )

    client: ModelClient
    if model_client is not None:
        client = model_client
    elif resolved_settings.fake_model:
        client = FakeModelClient()
    else:
        client = OpenRouterClient(
            api_key=resolved_settings.openrouter_api_key,
            model=resolved_settings.llm_model,
        )

    app = FastAPI(
        title="Ad Copy Grader API",
        version=__version__,
        description="Hybrid deterministic and LLM-powered Google Ads RSA copy grader API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        """Return service health status and current version."""
        return {"status": "ok", "version": __version__}

    @app.post("/v1/grade", response_model=GradeResult)
    async def grade_endpoint(
        ad: AdInput,
        request: Request,
        strict_llm: bool = Query(default=False),
    ) -> Response | GradeResult:
        """Grade a Responsive Search Ad with deterministic and LLM evaluation."""
        client_ip = extract_client_ip(
            request.headers.get("x-forwarded-for"),
            request.client.host if request.client else None,
        )

        allowed, reason, message = limiter.check_and_record(client_ip, lang=ad.lang)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": message, "reason": reason},
            )

        start_time = time.perf_counter()
        if strict_llm:
            try:
                pipeline_result = await grade(ad, client)
                result = pipeline_result.final
            except (LlmClientError, LlmOutputError):
                fallback = await grade_with_degradation(ad, client)
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                log_grade_event(ad, fallback, latency_ms)
                return JSONResponse(
                    status_code=502,
                    content={
                        "detail": fallback.degraded_reason,
                        "partial_result": fallback.model_dump(mode="json"),
                    },
                )
        else:
            result = await grade_with_degradation(ad, client)

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        log_grade_event(ad, result, latency_ms)
        return result

    return app


app = create_app()

__all__ = [
    "app",
    "create_app",
    "log_grade_event",
]
