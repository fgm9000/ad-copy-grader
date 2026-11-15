"""Hybrid grading pipeline.

Combines deterministic rules, LLM semantic audit, and authority filters.
"""

import re
import unicodedata

from pydantic import BaseModel

from ad_copy_grader.llm import ChatMessage, LlmClientError, ModelClient, ModelReply
from ad_copy_grader.models import AdInput, GradeResult, Issue, Language, Location
from ad_copy_grader.parser import LlmOutputError, request_and_parse_review
from ad_copy_grader.prompt import (
    SEMANTIC_RULE_IDS,
    build_system_prompt,
    build_user_message,
)
from ad_copy_grader.rewrite import validate_suggestions
from ad_copy_grader.rules import DETERMINISTIC_RULE_IDS, run_rules

NUMERIC_TOKEN_PATTERN = re.compile(
    r"(?:r\$\s*[\d.,]+|\$\s*[\d.,]+|\b\d+(?:[.,]\d+)?%|\b\d{1,2}x\b|\b\d{2,6}\b)",
    re.IGNORECASE,
)

DEGRADED_MESSAGES: dict[Language, str] = {
    "en": (
        "Semantic LLM review was unavailable; returning deterministic code audit only (D01-D11)."
    ),
    "pt": (
        "A revisão semântica via LLM ficou indisponível; "
        "retornando apenas a auditoria determinística do código (D01-D11)."
    ),
}


class PipelineResult(BaseModel):
    """Dual pipeline output holding raw LLM review and final merged/filtered result."""

    raw: GradeResult
    final: GradeResult
    usage: ModelReply | None = None


def _normalize_text(text: str) -> str:
    """Normalize text for accent- and case-insensitive substring comparison."""
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return stripped.lower()


def _extract_normalized_numbers(text: str) -> list[str]:
    """Extract normalized digit sequences from prices, percentages, or numeric offers."""
    matches = NUMERIC_TOKEN_PATTERN.findall(text)
    digits_list: list[str] = []
    for token in matches:
        digits = re.sub(r"\D", "", token)
        if digits:
            digits_list.append(digits)
    return digits_list


def _referenced_ad_text(ad: AdInput, issue: Issue) -> str:
    """Return the specific ad asset text referenced by an issue location, if valid."""
    loc = issue.location
    if loc is None:
        return ""
    if loc.field == "headline" and loc.index is not None and 0 <= loc.index < len(ad.headlines):
        return ad.headlines[loc.index]
    if (
        loc.field == "description"
        and loc.index is not None
        and 0 <= loc.index < len(ad.descriptions)
    ):
        return ad.descriptions[loc.index]
    if loc.field == "path1" and ad.path1 is not None:
        return ad.path1
    if loc.field == "path2" and ad.path2 is not None:
        return ad.path2
    if loc.field == "final_url":
        return ad.final_url
    return ""


def _is_location_in_bounds(ad: AdInput, issue: Issue) -> bool:
    """Verify that an issue's location points to an existing index or present field."""
    loc = issue.location
    if loc is None:
        return True
    if loc.field == "headline":
        return loc.index is not None and 0 <= loc.index < len(ad.headlines)
    if loc.field == "description":
        return loc.index is not None and 0 <= loc.index < len(ad.descriptions)
    if loc.field == "path1":
        return ad.path1 is not None and loc.index in (None, 0)
    if loc.field == "path2":
        return ad.path2 is not None and loc.index in (None, 0)
    if loc.field == "final_url":
        return loc.index in (None, 0)
    return False


def _is_a01_supported_by_lp_context(ad: AdInput, issue: Issue) -> bool:
    """Return True if an A01 issue is a false positive because the offer/price is in lp_context."""
    if not ad.lp_context.strip():
        return False

    lp_norm = _normalize_text(ad.lp_context)
    lp_numbers = set(_extract_normalized_numbers(ad.lp_context))

    candidate_numbers = _extract_normalized_numbers(issue.evidence or "")
    if not candidate_numbers:
        candidate_numbers = _extract_normalized_numbers(_referenced_ad_text(ad, issue))
    if not candidate_numbers:
        candidate_numbers = _extract_normalized_numbers(issue.message)

    # Only numbers are checked: whether a non-numeric phrase "is supported" by the LP is a
    # semantic judgement, which stays with the model.
    return bool(candidate_numbers) and all(
        num in lp_numbers or num in lp_norm for num in candidate_numbers
    )


def _match_key(text: str) -> str:
    """Normalize text for verbatim matching: accents, case, quotes and whitespace."""
    normalized = _normalize_text(unicodedata.normalize("NFC", text))
    normalized = normalized.strip().strip("\"'“”‘’.,;:!?")
    return " ".join(normalized.split())


def _ad_texts(ad: AdInput) -> list[str]:
    return [*ad.headlines, *ad.descriptions, ad.path1 or "", ad.path2 or ""]


def _has_verbatim_evidence(ad: AdInput, issue: Issue) -> bool:
    """Code check of the LLM's quote: the evidence must be a substring of the flagged asset.

    The model judges whether a phrase violates the rule; code only verifies that the quoted
    phrase really exists where the model says it does.
    """
    evidence = _match_key(issue.evidence or "")
    if not evidence:
        return False
    if issue.location is not None:
        return evidence in _match_key(_referenced_ad_text(ad, issue))
    return any(evidence in _match_key(text) for text in _ad_texts(ad))


def filter_llm_issues(ad: AdInput, llm_issues: list[Issue]) -> list[Issue]:
    """Apply server authority filters to LLM-generated issues.

    Every filter here is a verification, not a judgement: rule IDs against the contract,
    locations against the ad, quoted evidence against the asset text, and quoted numbers
    against the landing page.
    """
    filtered: list[Issue] = []
    for issue in llm_issues:
        rule_id = issue.rule_id.strip().upper()
        if rule_id.startswith("D") or rule_id not in SEMANTIC_RULE_IDS:
            continue
        if not _is_location_in_bounds(ad, issue):
            continue
        if rule_id == "A02":
            continue  # decided by code from the verified cta_phrases (decide_a02)
        if not _has_verbatim_evidence(ad, issue):
            continue
        if rule_id == "A01" and _is_a01_supported_by_lp_context(ad, issue):
            continue
        filtered.append(issue.model_copy(update={"rule_id": rule_id, "source": "llm"}))
    return filtered


A02_MESSAGES: dict[Language, str] = {
    "en": "No description contains a call-to-action (no verified CTA phrase).",
    "pt": "Nenhuma descrição contém chamada para ação (nenhuma frase de CTA confirmada).",
}


def verify_cta_phrases(ad: AdInput, phrases: list[str]) -> list[str]:
    """Keep only CTA phrases that exist verbatim in some description (order kept, no repeats)."""
    descriptions = [_match_key(desc) for desc in ad.descriptions]
    verified: list[str] = []
    for phrase in phrases:
        key = _match_key(phrase)
        if key and phrase not in verified and any(key in desc for desc in descriptions):
            verified.append(phrase)
    return verified


def decide_a02(ad: AdInput, cta_phrases: list[str]) -> list[Issue]:
    """A02 = no description has a CTA. The model supplies candidate CTA phrases (proofs of
    existence); code keeps the ones that really exist and flags A02 only when none is left."""
    if cta_phrases:
        return []
    return [
        Issue(
            rule_id="A02",
            severity="warning",
            message=A02_MESSAGES[ad.lang],
            location=Location(field="description", index=0),
            source="code",
        )
    ]


def compute_score(issues: list[Issue]) -> tuple[int, float, bool]:
    """Compute 0-100 score, 0.0-10.0 grade_10, and pass boolean from issues."""
    errors = sum(1 for issue in issues if issue.severity == "error")
    warnings = sum(1 for issue in issues if issue.severity == "warning")
    score = max(0, 100 - 15 * errors - 5 * warnings)
    grade_10 = round(score / 10, 1)
    passed = errors == 0
    return score, grade_10, passed


async def grade(
    ad: AdInput,
    client: ModelClient,
    system_prompt_override: str | None = None,
) -> PipelineResult:
    """Execute deterministic audit, LLM semantic audit, authority filtering, and rewrite checks."""
    deterministic_issues = run_rules(ad)
    system_prompt = (
        system_prompt_override
        if system_prompt_override is not None
        else build_system_prompt(ad.lang)
    )
    messages: list[ChatMessage] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": build_user_message(ad, deterministic_issues)},
    ]

    llm_review, usage = await request_and_parse_review(client, messages, lang=ad.lang)
    llm_issues = [item.to_issue() for item in llm_review.issues]
    # Raw column = the model alone: its issues, plus A02 if it listed no CTA phrase at all
    # (its own extraction, before any verification).
    raw_llm_issues = [
        *(i for i in llm_issues if i.rule_id.strip().upper() != "A02"),
        *decide_a02(ad, list(llm_review.cta_phrases)),
    ]
    raw_score, raw_grade_10, raw_passed = compute_score(raw_llm_issues)

    raw_result = GradeResult(
        score=raw_score,
        grade_10=raw_grade_10,
        passed=raw_passed,
        issues=raw_llm_issues,
        suggestions=list(llm_review.suggestions),
        discarded_suggestions_count=0,
        rules_checked=list(llm_review.rules_checked),
        model=usage.model,
        degraded_reason=None,
        cta_phrases=list(llm_review.cta_phrases),
    )

    filtered_llm_issues = filter_llm_issues(ad, llm_issues)
    verified_ctas = verify_cta_phrases(ad, list(llm_review.cta_phrases))
    merged_issues = [*deterministic_issues, *filtered_llm_issues, *decide_a02(ad, verified_ctas)]
    valid_suggestions, discarded_count = validate_suggestions(ad, llm_review.suggestions)
    final_score, final_grade_10, final_passed = compute_score(merged_issues)
    all_rules_checked = [*DETERMINISTIC_RULE_IDS, *SEMANTIC_RULE_IDS]

    final_result = GradeResult(
        score=final_score,
        grade_10=final_grade_10,
        passed=final_passed,
        issues=merged_issues,
        suggestions=valid_suggestions,
        discarded_suggestions_count=discarded_count,
        rules_checked=all_rules_checked,
        model=usage.model,
        degraded_reason=None,
        cta_phrases=verified_ctas,
    )

    return PipelineResult(raw=raw_result, final=final_result, usage=usage)


def build_degraded_result(ad: AdInput) -> GradeResult:
    """Build deterministic-only GradeResult when the semantic LLM review fails."""
    code_issues = run_rules(ad)
    score, grade_10, passed = compute_score(code_issues)
    return GradeResult(
        score=score,
        grade_10=grade_10,
        passed=passed,
        issues=code_issues,
        suggestions=[],
        discarded_suggestions_count=0,
        rules_checked=list(DETERMINISTIC_RULE_IDS),
        model=None,
        degraded_reason=DEGRADED_MESSAGES[ad.lang],
    )


async def grade_with_degradation(
    ad: AdInput,
    client: ModelClient,
) -> GradeResult:
    """Execute full grading pipeline, falling back to deterministic rules if LLM fails."""
    try:
        result = await grade(ad, client)
        return result.final
    except (LlmClientError, LlmOutputError):
        return build_degraded_result(ad)


__all__ = [
    "DEGRADED_MESSAGES",
    "PipelineResult",
    "build_degraded_result",
    "compute_score",
    "filter_llm_issues",
    "grade",
    "grade_with_degradation",
]
