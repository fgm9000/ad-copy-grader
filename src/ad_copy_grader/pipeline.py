"""Hybrid grading pipeline.

Combines deterministic rules, LLM semantic audit, and authority filters.
"""

import re
import unicodedata

from pydantic import BaseModel

from ad_copy_grader.llm import ChatMessage, LlmClientError, ModelClient, ModelReply
from ad_copy_grader.models import AdInput, GradeResult, Issue, Language
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

GENERIC_CTA_ROOTS: tuple[str, ...] = (
    "book",
    "schedul",
    "consult",
    "evaluat",
    "appoint",
    "contact",
    "agend",
    "avaliac",
    "marqu",
    "orcament",
    "conosco",
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

    asset_text = _referenced_ad_text(ad, issue)
    candidate_numbers = _extract_normalized_numbers(asset_text)
    if not candidate_numbers:
        candidate_numbers = _extract_normalized_numbers(issue.message)

    if candidate_numbers:
        return all(num in lp_numbers or num in lp_norm for num in candidate_numbers)

    # If no numbers exist in the flagged asset, check if it's a generic CTA supported by LP
    asset_norm = _normalize_text(asset_text or issue.message)
    matched_roots = [root for root in GENERIC_CTA_ROOTS if root in asset_norm]
    return bool(matched_roots and any(root in lp_norm for root in matched_roots))


def filter_llm_issues(ad: AdInput, llm_issues: list[Issue]) -> list[Issue]:
    """Apply server authority filters to LLM-generated issues."""
    filtered: list[Issue] = []
    for issue in llm_issues:
        rule_id = issue.rule_id.strip().upper()
        if rule_id.startswith("D") or rule_id not in SEMANTIC_RULE_IDS:
            continue
        if not _is_location_in_bounds(ad, issue):
            continue
        if rule_id == "A01" and _is_a01_supported_by_lp_context(ad, issue):
            continue
        filtered.append(issue.model_copy(update={"rule_id": rule_id, "source": "llm"}))
    return filtered


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
    raw_llm_issues = [item.to_issue() for item in llm_review.issues]
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
    )

    filtered_llm_issues = filter_llm_issues(ad, raw_llm_issues)
    merged_issues = [*deterministic_issues, *filtered_llm_issues]
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
    )

    return PipelineResult(raw=raw_result, final=final_result, usage=usage)


async def grade_with_degradation(
    ad: AdInput,
    client: ModelClient,
) -> GradeResult:
    """Execute full grading pipeline, falling back to deterministic rules if LLM fails."""
    try:
        result = await grade(ad, client)
        return result.final
    except (LlmClientError, LlmOutputError):
        deterministic_issues = run_rules(ad)
        score, grade_10, passed = compute_score(deterministic_issues)
        return GradeResult(
            score=score,
            grade_10=grade_10,
            passed=passed,
            issues=deterministic_issues,
            suggestions=[],
            discarded_suggestions_count=0,
            rules_checked=list(DETERMINISTIC_RULE_IDS),
            model=None,
            degraded_reason=DEGRADED_MESSAGES[ad.lang],
        )


__all__ = [
    "DEGRADED_MESSAGES",
    "PipelineResult",
    "compute_score",
    "filter_llm_issues",
    "grade",
    "grade_with_degradation",
]
