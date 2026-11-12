"""LLM client protocol, OpenRouter HTTP client, and deterministic FakeModelClient."""

import json
import re
from collections.abc import Callable, Sequence
from typing import Literal, Protocol, TypedDict

import httpx
from pydantic import BaseModel

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_LLM_MODEL = "google/gemini-2.5-flash"

PRICE_OR_PROMO_PATTERN = re.compile(
    r"(?:r\$\s*\d[\d.,]*|\$\s*\d[\d.,]*|\b\d{1,2}%\s*(?:off|de\s+desconto)\b|\b\d{1,2}x\s+sem\s+juros\b)",
    re.IGNORECASE,
)
CTA_PATTERN = re.compile(
    r"\b(?:book|schedule|call|contact|request|claim|get|start|visit|learn\s+more|"
    r"agende|marque|ligue|fale|solicite|peça|peca|garanta|saiba\s+mais|confira|clique)\b",
    re.IGNORECASE,
)
GUARANTEE_PATTERN = re.compile(
    r"\b(?:guaranteed|100%|cure|cures|painless|risk-free|instant\s+results|"
    r"garantid[oa]s?|cura|sem\s+dor|risco\s+zero|resultado\s+imediato)\b",
    re.IGNORECASE,
)


class ChatMessage(TypedDict):
    """Single message in a chat completion conversation."""

    role: Literal["system", "user", "assistant"]
    content: str


class ModelReply(BaseModel):
    """Structured response and token/cost telemetry from a model call."""

    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    model: str = "fake-model"


class LlmClientError(Exception):
    """Raised when an upstream LLM call fails due to timeout, HTTP error, or empty payload."""


class ModelClient(Protocol):
    """Protocol for JSON-mode LLM completion clients."""

    async def complete_json(
        self,
        messages: list[ChatMessage],
        max_tokens: int = 2048,
    ) -> ModelReply:
        """Complete a chat prompt and return a JSON string wrapped in ModelReply."""


class OpenRouterClient:
    """Async OpenRouter chat completion client enforcing JSON object output."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_LLM_MODEL,
        timeout_seconds: float = 20.0,
        base_url: str = OPENROUTER_API_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_seconds
        self._base_url = base_url
        self._http_client = http_client

    @property
    def model_name(self) -> str:
        """Return configured model identifier."""
        return self._model

    async def complete_json(
        self,
        messages: list[ChatMessage],
        max_tokens: int = 2048,
    ) -> ModelReply:
        """Send chat completion request to OpenRouter without exposing secrets on error."""
        if not self._api_key or not self._api_key.strip():
            raise LlmClientError("OpenRouter API key is not configured.")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/fgm9000/ad-copy-grader",
            "X-Title": "Ad Copy Grader",
        }
        body: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "usage": {"include": True},
        }

        try:
            if self._http_client is not None:
                response = await self._http_client.post(
                    self._base_url,
                    headers=headers,
                    json=body,
                    timeout=self._timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        self._base_url,
                        headers=headers,
                        json=body,
                    )
        except httpx.TimeoutException as exc:
            raise LlmClientError(f"OpenRouter request timed out after {self._timeout}s.") from exc
        except httpx.HTTPError as exc:
            raise LlmClientError("OpenRouter network communication failed.") from exc

        if response.status_code != 200:
            raise LlmClientError(f"OpenRouter returned HTTP {response.status_code}.")

        try:
            data = response.json()
        except ValueError as exc:
            raise LlmClientError("OpenRouter returned non-JSON HTTP body.") from exc

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LlmClientError("OpenRouter response contained no choices.")

        first_choice = choices[0] if isinstance(choices[0], dict) else {}
        message_obj = first_choice.get("message")
        content = message_obj.get("content") if isinstance(message_obj, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise LlmClientError("OpenRouter returned empty message content.")

        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens) or 0)
        cost_usd = float(usage.get("cost", 0.0) or 0.0)
        resolved_model = str(data.get("model") or self._model)

        return ModelReply(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            model=resolved_model,
        )


def _extract_ad_payload(messages: Sequence[ChatMessage]) -> dict[str, object] | None:
    """Extract the serialized <ad_payload> JSON object from user messages if present."""
    for msg in reversed(messages):
        if msg["role"] == "user":
            match = re.search(
                r"<ad_payload>\s*(\{.*?\})\s*</ad_payload>",
                msg["content"],
                re.DOTALL,
            )
            if match:
                try:
                    loaded = json.loads(match.group(1))
                    if isinstance(loaded, dict):
                        return loaded
                except ValueError:
                    return None
    return None


def _price_digits_in_lp(offer_str: str, lp_context: str) -> bool:
    """Return True if all numeric digit groups in offer_str appear in lp_context."""
    if not lp_context.strip():
        return False
    lp_digits = {re.sub(r"\D", "", m) for m in re.findall(r"\d[\d.,]*", lp_context)}
    offer_digits = [re.sub(r"\D", "", m) for m in re.findall(r"\d[\d.,]*", offer_str)]
    offer_digits = [d for d in offer_digits if d]
    if not offer_digits:
        return False
    return all(d in lp_digits or d in lp_context for d in offer_digits)


def _default_fake_audit(messages: Sequence[ChatMessage]) -> str:
    """Produce a deterministic JSON review for testing and offline CI evaluation."""
    payload = _extract_ad_payload(messages) or {}
    lang = "pt" if payload.get("lang") == "pt" else "en"
    raw_headlines = payload.get("headlines")
    headlines = (
        [str(h) for h in raw_headlines if isinstance(h, str)]
        if isinstance(raw_headlines, list)
        else []
    )
    raw_descriptions = payload.get("descriptions")
    descriptions = (
        [str(d) for d in raw_descriptions if isinstance(d, str)]
        if isinstance(raw_descriptions, list)
        else []
    )
    primary_service = str(payload.get("primary_service") or "Service")
    lp_context = str(payload.get("lp_context") or "")

    system_text = next((m["content"] for m in messages if m["role"] == "system"), "")
    is_degraded = system_text == "custom"

    issues: list[dict[str, object]] = []
    suggestions: list[dict[str, object]] = []

    # Check A01 on headlines and descriptions when price/promo is absent from lp_context
    for idx, headline in enumerate(headlines):
        price_match = PRICE_OR_PROMO_PATTERN.search(headline)
        if price_match and not _price_digits_in_lp(price_match.group(0), lp_context):
            offer_str = price_match.group(0)
            msg = (
                f"Preço ou oferta '{offer_str}' no título não confirmado na landing page."
                if lang == "pt"
                else f"Price or offer '{offer_str}' in headline not verified in landing page."
            )
            issues.append(
                {
                    "rule_id": "A01",
                    "severity": "error",
                    "message": msg,
                    "location": {"field": "headline", "index": idx},
                }
            )
            rewritten = (
                f"{primary_service[:22]} Today" if lang == "en" else f"{primary_service[:22]} Hoje"
            )
            suggestions.append(
                {
                    "location": {"field": "headline", "index": idx},
                    "original": headline,
                    "suggested": rewritten[:30],
                    "reason": (
                        "Remove preço não verificado na página."
                        if lang == "pt"
                        else "Removes unverified price claim."
                    ),
                }
            )

    for idx, desc in enumerate(descriptions):
        price_match = PRICE_OR_PROMO_PATTERN.search(desc)
        if price_match and not _price_digits_in_lp(price_match.group(0), lp_context):
            offer_str = price_match.group(0)
            msg = (
                f"Preço ou oferta '{offer_str}' na descrição não confirmado na landing page."
                if lang == "pt"
                else f"Price or offer '{offer_str}' in description not verified in landing page."
            )
            issues.append(
                {
                    "rule_id": "A01",
                    "severity": "error",
                    "message": msg,
                    "location": {"field": "description", "index": idx},
                }
            )

    # Check A02 (no description has a clear CTA)
    if descriptions and not any(CTA_PATTERN.search(d) for d in descriptions):
        issues.append(
            {
                "rule_id": "A02",
                "severity": "warning",
                "message": (
                    "Nenhuma descrição possui uma chamada para ação (CTA) clara."
                    if lang == "pt"
                    else "None of the descriptions contain a clear Call-to-Action (CTA)."
                ),
                "location": {"field": "description", "index": 0},
            }
        )
        suggestions.append(
            {
                "location": {"field": "description", "index": 0},
                "original": descriptions[0],
                "suggested": (
                    f"Agende sua avaliação de {primary_service.lower()} com nossa equipe hoje."[:90]
                    if lang == "pt"
                    else (f"Book your {primary_service.lower()} consultation with our team today.")[
                        :90
                    ]
                ),
                "reason": (
                    "Adiciona chamada para ação clara."
                    if lang == "pt"
                    else "Adds a clear call to action."
                ),
            }
        )

    # Check A03 (absolute outcome guarantee)
    for idx, headline in enumerate(headlines):
        if GUARANTEE_PATTERN.search(headline):
            issues.append(
                {
                    "rule_id": "A03",
                    "severity": "warning",
                    "message": (
                        "Promessa absoluta ou garantia de resultado no título."
                        if lang == "pt"
                        else "Absolute outcome guarantee or regulated promise in headline."
                    ),
                    "location": {"field": "headline", "index": idx},
                }
            )
            suggestions.append(
                {
                    "location": {"field": "headline", "index": idx},
                    "original": headline,
                    "suggested": (
                        f"Especialistas em {primary_service}"[:30]
                        if lang == "pt"
                        else f"Trusted {primary_service} Care"[:30]
                    ),
                    "reason": (
                        "Substitui garantia absoluta por afirmação adequada."
                        if lang == "pt"
                        else "Replaces absolute guarantee with compliant phrasing."
                    ),
                }
            )

    for idx, desc in enumerate(descriptions):
        if GUARANTEE_PATTERN.search(desc):
            issues.append(
                {
                    "rule_id": "A03",
                    "severity": "warning",
                    "message": (
                        "Promessa absoluta ou garantia de resultado na descrição."
                        if lang == "pt"
                        else "Absolute outcome guarantee or regulated promise in description."
                    ),
                    "location": {"field": "description", "index": idx},
                }
            )

    # In degraded mode (when the D-rule prohibition line is removed), simulate LLM
    # overreach by emitting a D04 issue so the 3-column Promptfoo eval proves the filter.
    if is_degraded:
        issues.append(
            {
                "rule_id": "D04",
                "severity": "error",
                "message": "Simulated LLM deterministic rule overreach in degraded prompt mode.",
                "location": {"field": "headline", "index": 0},
            }
        )

    return json.dumps(
        {
            "issues": issues,
            "rules_checked": ["A01", "A02", "A03"],
            "suggestions": suggestions,
        },
        ensure_ascii=False,
    )


class FakeModelClient:
    """In-memory deterministic model client for unit tests, CI, and demo fallback."""

    def __init__(
        self,
        responses: Sequence[str | ModelReply | Exception] | None = None,
        handler: Callable[[list[ChatMessage]], str | ModelReply] | None = None,
        model_name: str = "fake-model",
    ) -> None:
        self._responses = list(responses) if responses is not None else []
        self._handler = handler
        self._model_name = model_name
        self.calls: list[list[ChatMessage]] = []

    @property
    def model_name(self) -> str:
        """Return fake model identifier."""
        return self._model_name

    async def complete_json(
        self,
        messages: list[ChatMessage],
        max_tokens: int = 2048,
    ) -> ModelReply:
        """Return next queued response, handler result, or deterministic fake audit."""
        _ = max_tokens
        snapshot: list[ChatMessage] = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        self.calls.append(snapshot)

        if self._responses:
            item = self._responses.pop(0)
            if isinstance(item, Exception):
                raise item
            if isinstance(item, ModelReply):
                return item
            return ModelReply(
                content=item,
                prompt_tokens=120,
                completion_tokens=60,
                total_tokens=180,
                cost_usd=0.0,
                model=self._model_name,
            )

        if self._handler is not None:
            result = self._handler(messages)
            if isinstance(result, ModelReply):
                return result
            return ModelReply(
                content=result,
                prompt_tokens=120,
                completion_tokens=60,
                total_tokens=180,
                cost_usd=0.0,
                model=self._model_name,
            )

        return ModelReply(
            content=_default_fake_audit(messages),
            prompt_tokens=150,
            completion_tokens=75,
            total_tokens=225,
            cost_usd=0.0,
            model=self._model_name,
        )


__all__ = [
    "ChatMessage",
    "DEFAULT_LLM_MODEL",
    "FakeModelClient",
    "LlmClientError",
    "ModelClient",
    "ModelReply",
    "OPENROUTER_API_URL",
    "OpenRouterClient",
]
