"""Custom Promptfoo Python provider for 3-column evaluation (raw, pipeline, degraded)."""

import asyncio
import hashlib
import json
import os
import sys
import tempfile
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ad_copy_grader.llm import (
    ChatMessage,
    FakeModelClient,
    LlmClientError,
    ModelClient,
    ModelReply,
    OpenRouterClient,
)
from ad_copy_grader.models import AdInput
from ad_copy_grader.pipeline import PipelineResult, grade
from ad_copy_grader.prompt import build_degraded_system_prompt

VALID_MODES = ("raw", "pipeline", "degraded")
RETRY_DELAYS_SECONDS = (2.0, 5.0, 10.0)
TRANSIENT_ERROR_MARKERS = ("HTTP 429", "HTTP 5", "timed out", "network communication")

_MEMORY_CACHE: dict[str, dict[str, Any]] = {}


def _is_fake_mode() -> bool:
    """Return True when FAKE_MODEL or EVAL_FAKE_MODEL is enabled."""
    for env_name in ("FAKE_MODEL", "EVAL_FAKE_MODEL"):
        val = os.environ.get(env_name, "").strip().lower()
        if val in ("1", "true", "yes"):
            return True
    return False


def _cache_file_path(cache_key: str) -> Path:
    """Return deterministic temp file path for sharing raw/pipeline results across processes."""
    cache_dir = Path(tempfile.gettempdir()) / "ad_copy_grader_promptfoo_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{cache_key}.json"


class RetryingEvalModelClient:
    """Wraps a ModelClient with exponential backoff for transient 429/5xx errors during evals."""

    def __init__(
        self,
        inner: ModelClient,
        delays: tuple[float, ...] = RETRY_DELAYS_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._inner = inner
        self._delays = delays
        self._sleep_fn = sleep_fn

    async def complete_json(
        self,
        messages: list[ChatMessage],
        max_tokens: int = 2048,
    ) -> ModelReply:
        """Call inner client with retry on transient rate-limit or upstream 5xx errors."""
        attempt = 0
        while True:
            try:
                return await self._inner.complete_json(messages, max_tokens=max_tokens)
            except LlmClientError as exc:
                msg = str(exc)
                is_transient = any(marker in msg for marker in TRANSIENT_ERROR_MARKERS)
                if attempt >= len(self._delays) or not is_transient:
                    raise
                self._sleep_fn(self._delays[attempt])
                attempt += 1


def _build_cache_key(
    payload_dict: dict[str, Any], use_fake: bool, model_name: str, case_name: str = ""
) -> str:
    """Compute SHA-256 key so raw and pipeline columns share a single model call per case."""
    canonical = json.dumps(
        {
            "payload": payload_dict,
            "fake": use_fake,
            "model": model_name,
            "case": case_name,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def _run_single_evaluation(
    ad: AdInput,
    mode: str,
    use_fake: bool,
    api_key: str,
    model_name: str,
    case_name: str = "",
) -> tuple[dict[str, Any], dict[str, int], float]:
    """Execute or reuse grading result for the given mode (raw, pipeline, or degraded)."""
    base_client: ModelClient
    if use_fake:
        if case_name == "07_en_verified_price_in_lp_no_false_positive":
            mock_reply = ModelReply(
                content=json.dumps(
                    {
                        "issues": [
                            {
                                "rule_id": "A01",
                                "severity": "error",
                                "message": (
                                    "Price or promo '$899' in headline not verified by "
                                    "landing page context."
                                ),
                                "location": {"field": "headline", "index": 10},
                            }
                        ],
                        "rules_checked": ["A01", "A02", "A03"],
                        "suggestions": [],
                    }
                ),
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost_usd=0.0001,
                model="fake-model",
            )
            base_client = FakeModelClient(responses=[mock_reply])
        else:
            base_client = FakeModelClient()
    else:
        base_client = RetryingEvalModelClient(OpenRouterClient(api_key=api_key, model=model_name))

    if mode == "degraded":
        degraded_prompt = build_degraded_system_prompt(ad.lang)
        degraded_res: PipelineResult = await grade(
            ad,
            base_client,
            system_prompt_override=degraded_prompt,
        )
        usage = degraded_res.usage
        tokens = {
            "prompt": usage.prompt_tokens if usage else 0,
            "completion": usage.completion_tokens if usage else 0,
            "total": usage.total_tokens if usage else 0,
        }
        cost = usage.cost_usd if usage else 0.0
        return degraded_res.raw.model_dump(mode="json"), tokens, cost

    payload_dict = ad.model_dump(mode="json")
    cache_key = _build_cache_key(
        payload_dict, use_fake=use_fake, model_name=model_name, case_name=case_name
    )

    if cache_key in _MEMORY_CACHE:
        cached = _MEMORY_CACHE[cache_key]
        output_obj = cached["final"] if mode == "pipeline" else cached["raw"]
        return output_obj, {"prompt": 0, "completion": 0, "total": 0}, 0.0

    cache_file = _cache_file_path(cache_key)
    if not use_fake and cache_file.exists() and (time.time() - cache_file.stat().st_mtime < 300):
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            _MEMORY_CACHE[cache_key] = cached
            output_obj = cached["final"] if mode == "pipeline" else cached["raw"]
            return output_obj, {"prompt": 0, "completion": 0, "total": 0}, 0.0
        except ValueError:
            pass

    res = await grade(ad, base_client)
    usage = res.usage
    raw_dict = res.raw.model_dump(mode="json")
    final_dict = res.final.model_dump(mode="json")

    final_issue_keys = {
        (
            iss["rule_id"],
            iss.get("location", {}).get("field") if iss.get("location") else None,
            iss.get("location", {}).get("index") if iss.get("location") else None,
        )
        for iss in final_dict.get("issues", [])
    }
    dropped_issues = [
        iss
        for iss in raw_dict.get("issues", [])
        if (
            iss["rule_id"],
            iss.get("location", {}).get("field") if iss.get("location") else None,
            iss.get("location", {}).get("index") if iss.get("location") else None,
        )
        not in final_issue_keys
    ]
    final_dict["dropped_issues"] = dropped_issues

    record = {
        "raw": raw_dict,
        "final": final_dict,
    }
    _MEMORY_CACHE[cache_key] = record
    if not use_fake:
        cache_file.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")

    tokens = {
        "prompt": usage.prompt_tokens if usage else 0,
        "completion": usage.completion_tokens if usage else 0,
        "total": usage.total_tokens if usage else 0,
    }
    cost = usage.cost_usd if usage else 0.0
    output_obj = record["final"] if mode == "pipeline" else record["raw"]
    return output_obj, tokens, cost


def _run_async(
    coro: Awaitable[tuple[dict[str, Any], dict[str, int], float]],
) -> tuple[dict[str, Any], dict[str, int], float]:
    """Run coroutine safely in a new event loop."""
    return asyncio.run(coro)


def call_api(
    prompt: str,
    options: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Promptfoo Python provider entrypoint."""
    _ = prompt
    config = options.get("config") or {}
    mode = str(config.get("mode") or "")
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid provider config.mode '{mode}'. Expected one of {VALID_MODES}.")

    use_fake = _is_fake_mode()
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    model_name = os.environ.get("LLM_MODEL", "google/gemini-2.5-flash").strip()

    if not use_fake and not api_key:
        return {
            "error": (
                "OPENROUTER_API_KEY is not set. Set FAKE_MODEL=1 for offline CI evaluation "
                "or provide OPENROUTER_API_KEY for live model evaluation."
            )
        }

    vars_dict = context.get("vars") or {}
    raw_payload = vars_dict.get("payload")
    case_name = str(vars_dict.get("name") or "")
    if raw_payload is None:
        return {"error": "Missing 'payload' in test case vars."}

    try:
        payload_data = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
        ad = AdInput.model_validate(payload_data)
        output_dict, token_usage, cost = _run_async(
            _run_single_evaluation(
                ad=ad,
                mode=mode,
                use_fake=use_fake,
                api_key=api_key,
                model_name=model_name,
                case_name=case_name,
            )
        )
        return {
            "output": json.dumps(output_dict, ensure_ascii=False),
            "tokenUsage": token_usage,
            "cost": cost,
            "metadata": {"mode": mode},
        }
    except Exception as exc:
        err_msg = str(exc)
        if api_key:
            err_msg = err_msg.replace(api_key, "***")
        return {"error": err_msg}
