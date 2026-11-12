"""Output parser, schema validation, and single self-correction retry for LLM responses."""

import re

from pydantic import BaseModel, Field, ValidationError, field_validator

from ad_copy_grader.llm import ChatMessage, ModelClient, ModelReply
from ad_copy_grader.models import Issue, Language, Location, Severity, Suggestion
from ad_copy_grader.prompt import SEMANTIC_RULE_IDS

CODE_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.DOTALL | re.IGNORECASE,
)


class LlmOutputError(Exception):
    """Raised when the LLM fails schema or rule-coverage validation after retry."""


class LlmIssueItem(BaseModel):
    """Single issue item emitted by the LLM before source tagging."""

    rule_id: str
    severity: Severity
    message: str
    location: Location | None = None

    def to_issue(self) -> Issue:
        """Convert LLM issue item into a domain Issue tagged with source='llm'."""
        return Issue(
            rule_id=self.rule_id,
            severity=self.severity,
            message=self.message,
            location=self.location,
            source="llm",
        )


class LlmReview(BaseModel):
    """Validated JSON structure returned by the semantic reviewer LLM."""

    issues: list[LlmIssueItem] = Field(default_factory=list)
    rules_checked: list[str]
    suggestions: list[Suggestion] = Field(default_factory=list)

    @field_validator("rules_checked")
    @classmethod
    def validate_all_semantic_rules_checked(cls, v: list[str]) -> list[str]:
        """Require that A01, A02, and A03 are all explicitly listed in rules_checked."""
        checked_set = set(v)
        missing = [rule_id for rule_id in SEMANTIC_RULE_IDS if rule_id not in checked_set]
        if missing:
            raise ValueError(
                f"rules_checked is missing required semantic rules: {', '.join(missing)}"
            )
        return v


def extract_json_object(raw_text: str) -> str:
    """Extract a JSON object string from raw LLM output, stripping Markdown fences if present."""
    stripped = raw_text.strip()
    fence_match = CODE_FENCE_PATTERN.search(stripped)
    if fence_match:
        return fence_match.group(1).strip()

    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace : last_brace + 1]
    return stripped


def parse_llm_review(raw_text: str) -> LlmReview:
    """Extract and validate an LlmReview object from raw text."""
    json_str = extract_json_object(raw_text)
    return LlmReview.model_validate_json(json_str)


def _build_retry_instruction(error_detail: str, lang: Language) -> str:
    """Build the self-correction prompt appended when the first attempt fails validation."""
    if lang == "pt":
        return (
            "Sua resposta anterior falhou na validação de schema JSON:\n"
            f"{error_detail}\n"
            "Corrija e devolva APENAS o objeto JSON válido contendo `issues`, "
            "`rules_checked` (incluindo obrigatoriamente A01, A02 e A03) e `suggestions`."
        )
    return (
        "Your previous response failed JSON schema validation:\n"
        f"{error_detail}\n"
        "Fix the output and return ONLY a valid JSON object containing `issues`, "
        "`rules_checked` (which MUST include A01, A02, and A03), and `suggestions`."
    )


async def request_and_parse_review(
    client: ModelClient,
    messages: list[ChatMessage],
    lang: Language = "en",
    max_tokens: int = 2048,
) -> tuple[LlmReview, ModelReply]:
    """Call the LLM and parse the response, performing at most one validation retry."""
    working_messages: list[ChatMessage] = [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]

    first_reply = await client.complete_json(working_messages, max_tokens=max_tokens)
    try:
        review = parse_llm_review(first_reply.content)
        return review, first_reply
    except (ValidationError, ValueError) as first_err:
        error_summary = str(first_err)

    working_messages.append({"role": "assistant", "content": first_reply.content})
    working_messages.append(
        {
            "role": "user",
            "content": _build_retry_instruction(error_summary, lang=lang),
        }
    )

    second_reply = await client.complete_json(working_messages, max_tokens=max_tokens)
    combined_reply = ModelReply(
        content=second_reply.content,
        prompt_tokens=first_reply.prompt_tokens + second_reply.prompt_tokens,
        completion_tokens=first_reply.completion_tokens + second_reply.completion_tokens,
        total_tokens=first_reply.total_tokens + second_reply.total_tokens,
        cost_usd=round(first_reply.cost_usd + second_reply.cost_usd, 8),
        model=second_reply.model,
    )

    try:
        review = parse_llm_review(second_reply.content)
        return review, combined_reply
    except (ValidationError, ValueError) as second_err:
        raise LlmOutputError(
            f"LLM output failed validation after retry: {second_err}"
        ) from second_err


__all__ = [
    "LlmIssueItem",
    "LlmOutputError",
    "LlmReview",
    "extract_json_object",
    "parse_llm_review",
    "request_and_parse_review",
]
