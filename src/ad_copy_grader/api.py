"""FastAPI application, endpoints, rate limiting, and structured logging."""

import json
import logging
import time
from typing import Annotated, Any

from fastapi import Body, FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

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
from ad_copy_grader.pipeline import build_degraded_result, grade, grade_with_degradation
from ad_copy_grader.settings import Settings, get_settings

logger = logging.getLogger("ad_copy_grader.api")

OPENAPI_EXAMPLES: dict[str, Any] = {
    "1_hybrid_errors_en": {
        "summary": "1. Hybrid Audit — Unverified Price (A01) + Length/Dup (D04/D08) [EN]",
        "description": (
            "Demonstrates the full hybrid grader: Headline #2 claims '$499' while the "
            "Landing Page states '$899' (Rule A01), Headline #3 exceeds 30 chars (Rule D04), "
            "Headline #4 contains an absolute guarantee (Rule A03), and Headline #5 is a "
            "duplicate (Rule D08)."
        ),
        "value": {
            "headlines": [
                "Dental Implants Clinic",
                "Implants Starting At $499",
                "Comprehensive Full Arch Dental Implant Rehabilitation",
                "100% Guaranteed Results",
                "Dental Implants Clinic",
                "Top Dental Implants Care",
                "Best Dental Implants Team",
                "Modern 3D Smile Design",
                "Sedation Dentistry Options",
                "Restore Your Natural Smile",
                "Experienced Oral Surgeons",
                "Flexible Monthly Financing",
                "Same Day Implant Consults",
                "Trusted Local Specialists",
                "Book Your Evaluation Today",
            ],
            "descriptions": [
                "Restore your smile with permanent titanium dental implants. "
                "Schedule your consultation today.",
                "Experienced oral surgeons, 3D CBCT digital imaging, and "
                "flexible 12x payment plans available.",
            ],
            "path1": "implants",
            "path2": "austin",
            "final_url": "https://example.com/dental-implants",
            "primary_service": "Dental Implants",
            "lp_context": (
                "Welcome to BrightSmile Dental Implants Center in Austin. For over 15 years, "
                "our board-certified oral surgeons have restored over 5,000 smiles using guided "
                "3D CBCT digital tomography and medical-grade titanium fixtures.\n\n"
                "Transparent Pricing & Packages: Single-tooth dental implants start at $899 per "
                "fixture, and complete zirconia crown restorations are available with 0% APR "
                "financing in up to 12x monthly installments. Every new patient package includes "
                "a comprehensive oral exam and 3D panoramic scan.\n\n"
                "Clinic Hours & Booking: Open Monday through Saturday from 8:00 AM to 6:00 PM. "
                "Schedule your consultation online today or call our patient care team."
            ),
            "lang": "en",
        },
    },
    "2_authority_filter_en": {
        "summary": "2. Code Authority Filter — LP-Verified Price ($899 in LP) [EN]",
        "description": (
            "Headline #2 claims '$899', which is explicitly verified in the middle section "
            "of the Landing Page text. The Server Code Authority Filter suppresses any A01 "
            "false positive."
        ),
        "value": {
            "headlines": [
                "Dental Implants Specialist",
                "Dental Implants From $899",
                "Permanent Dental Implants",
                "BrightSmile Dental Clinic",
                "Book Your 3D Scan Today",
                "Restore Your Natural Smile",
                "Experienced Oral Surgeons",
                "State of the Art Dental Care",
                "Flexible Financing Available",
                "Over 15 Years of Experience",
                "Custom Treatment Plans",
                "Same Day Consultations",
                "Gentle and Caring Team",
                "Modern Dental Technology",
                "Schedule Evaluation Online",
            ],
            "descriptions": [
                "Restore your confidence with titanium dental implants. "
                "Schedule your consultation today.",
                "Advanced 3D digital planning and gentle oral surgery. "
                "Flexible payment options available.",
            ],
            "path1": "implants",
            "path2": "consultation",
            "final_url": "https://example.com/dental-implants",
            "primary_service": "Dental Implants",
            "lp_context": (
                "BrightSmile Dental Clinic is Austin's premier center for permanent tooth "
                "replacement with over 15 years of clinical excellence and 98% patient "
                "satisfaction.\n\n"
                "Special Implant Offer: Titanium dental implants starting at $899 with flexible "
                "12x monthly payment plans and complimentary 3D digital tomography on your "
                "first visit.\n\n"
                "Conveniently located downtown with free parking. Book your evaluation online "
                "today."
            ),
            "lang": "en",
        },
    },
    "3_clean_10_en": {
        "summary": "3. Clean Compliant RSA — Perfect 10.0 Score [EN]",
        "description": (
            "Fully compliant 15-headline, 2-description RSA that passes all 14 deterministic "
            "and semantic rules."
        ),
        "value": {
            "headlines": [
                "Dental Implants Specialist",
                "Affordable Dental Implants",
                "Permanent Dental Implants",
                "BrightSmile Dental Clinic",
                "Book Your 3D Scan Today",
                "Restore Your Natural Smile",
                "Experienced Oral Surgeons",
                "State of the Art Dental Care",
                "Flexible Financing Available",
                "Over 15 Years of Experience",
                "Custom Treatment Plans",
                "Same Day Consultations",
                "Gentle and Caring Team",
                "Modern Dental Technology",
                "Schedule Evaluation Online",
            ],
            "descriptions": [
                "Restore your confidence with titanium dental implants. "
                "Schedule your consultation today.",
                "Advanced 3D digital planning and gentle oral surgery. "
                "Flexible payment options available.",
            ],
            "path1": "implants",
            "path2": "consultation",
            "final_url": "https://example.com/dental-implants",
            "primary_service": "Dental Implants",
            "lp_context": (
                "BrightSmile Dental Clinic offers permanent titanium dental implants with 3D "
                "digital planning and over 15 years of surgical experience.\n\n"
                "Our treatment packages start at $899 with flexible 12x financing and include "
                "a full clinical evaluation.\n\n"
                "Contact our clinic Monday through Saturday or book your consultation online "
                "today."
            ),
            "lang": "en",
        },
    },
    "4_auditoria_hibrida_pt": {
        "summary": "4. Auditoria Híbrida PT-BR — Preço (A01) + Limite (D04) [PT-BR]",
        "description": (
            "Exemplo em Português (lang='pt'): Título #2 anuncia 'R$ 499' divergente da "
            "Landing Page ('R$ 390'), Título #3 excede 30 caracteres (D04) e Título #4 faz "
            "promessa clínica absoluta (A03)."
        ),
        "value": {
            "headlines": [
                "Implante Dentário em SP",
                "Implantes a Partir de R$ 499",
                "Reabilitação Oral Completa com Implantes",
                "Resultado 100% Garantido",
                "Clínica de Implante Dentário",
                "Implante Dentário Moderno",
                "Cirurgiões Credenciados",
                "Recupere Seu Sorriso Hoje",
                "Sedação Consciente Segura",
                "Planejamento Digital 3D",
                "Atendimento Humanizado",
                "Opções de Parcelamento",
                "Tecnologia Odontológica",
                "Consultório Especializado",
                "Agende Sua Avaliação Hoje",
            ],
            "descriptions": [
                "Recupere a segurança ao sorrir com implantes dentários. "
                "Agende sua avaliação hoje.",
                "Planejamento digital 3D e cirurgia guiada de alta precisão. "
                "Parcelamento em até 12x.",
            ],
            "path1": "implantes",
            "path2": "avaliacao",
            "final_url": "https://exemplo.com.br/implante-dentario",
            "primary_service": "Implante Dentário",
            "lp_context": (
                "Bem-vindo à Clínica Sorriso São Paulo. Há mais de 15 anos somos referência "
                "em reabilitação oral e implante dentário guiado por tomografia computadorizada "
                "3D, com mais de 4.500 procedimentos realizados com segurança.\n\n"
                "Valores e Condições de Pagamento: Tratamentos de implante dentário com parcelas "
                "a partir de R$ 390 mensais e parcelamento facilitado em até 12x no cartão. "
                "A primeira consulta inclui check-up digital completo.\n\n"
                "Atendimento de segunda a sábado das 8h às 19h próximo à Av. Paulista. Agende "
                "sua avaliação online pelo site ou fale com nossa equipe."
            ),
            "lang": "pt",
        },
    },
}


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
        description=(
            "Hybrid deterministic (`D01–D11`) and LLM-powered (`A01–A03`) Google Ads RSA copy "
            "grader API. Explore the **[Interactive Web Playground]"
            "(https://fgm9000.github.io/ad-copy-grader/)** or view the "
            "**[GitHub Repository](https://github.com/fgm9000/ad-copy-grader)**."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        """Redirect root URL requests to the interactive Swagger UI documentation."""
        return RedirectResponse(url="/docs")

    @app.get("/health", summary="Service Health Check", tags=["System"])
    @app.get("/healthz", include_in_schema=False)
    async def health() -> dict[str, str]:
        """Return service health status and current version."""
        return {"status": "ok", "version": __version__}

    @app.post(
        "/v1/grade",
        response_model=GradeResult,
        summary="Audit & Grade a Google Ads RSA",
        tags=["Grading"],
    )
    async def grade_endpoint(
        request: Request,
        ad: Annotated[AdInput, Body(openapi_examples=OPENAPI_EXAMPLES)],
        strict_llm: Annotated[bool, Query()] = False,
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
                fallback = build_degraded_result(ad)
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
    "OPENAPI_EXAMPLES",
    "app",
    "create_app",
    "log_grade_event",
]
