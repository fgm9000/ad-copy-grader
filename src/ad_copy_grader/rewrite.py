"""Deterministic re-validation of LLM rewrite suggestions.

Applies rules D04, D05, D06, D08, D09, and D10.
"""

import unicodedata

from ad_copy_grader.models import AdInput, Suggestion
from ad_copy_grader.rules import (
    ALLOWED_ACRONYMS,
    REPEATED_PUNCTUATION_PATTERN,
    UPPERCASE_WORD_PATTERN,
    nfc_len,
)


def _has_forbidden_punctuation(text: str) -> bool:
    """Return True if text contains repeated or excessive punctuation (D09)."""
    return bool(REPEATED_PUNCTUATION_PATTERN.search(text))


def _has_forbidden_all_caps(text: str) -> bool:
    """Return True if text contains a 4+ letter ALL CAPS word not in ALLOWED_ACRONYMS (D10)."""
    norm = unicodedata.normalize("NFC", text)
    words = UPPERCASE_WORD_PATTERN.findall(norm)
    return any(w not in ALLOWED_ACRONYMS for w in words)


def _normalize_headline_key(text: str) -> str:
    """Normalize a headline for case-insensitive duplicate comparison (D08)."""
    return unicodedata.normalize("NFC", text).strip().casefold()


def is_suggestion_valid(
    ad: AdInput,
    suggestion: Suggestion,
    accepted_headline_keys: set[str] | None = None,
) -> bool:
    """Check whether a single rewrite suggestion satisfies all deterministic rules."""
    text = suggestion.suggested.strip()
    if not text:
        return False

    if _has_forbidden_punctuation(text) or _has_forbidden_all_caps(text):
        return False

    field = suggestion.location.field
    idx = suggestion.location.index

    if field == "headline":
        if idx is None or idx < 0 or idx >= len(ad.headlines):
            return False
        if nfc_len(text) > 30:
            return False

        candidate_key = _normalize_headline_key(text)
        for other_idx, existing in enumerate(ad.headlines):
            if other_idx != idx and _normalize_headline_key(existing) == candidate_key:
                return False
        return not (accepted_headline_keys and candidate_key in accepted_headline_keys)

    if field == "description":
        if idx is None or idx < 0 or idx >= len(ad.descriptions):
            return False
        return nfc_len(text) <= 90

    if field in ("path1", "path2"):
        return nfc_len(text) <= 15

    return False


def validate_suggestions(
    ad: AdInput,
    suggestions: list[Suggestion],
) -> tuple[list[Suggestion], int]:
    """Filter LLM suggestions through deterministic rules and count discarded items."""
    valid: list[Suggestion] = []
    discarded = 0
    accepted_headline_keys: set[str] = set()

    for suggestion in suggestions:
        if is_suggestion_valid(ad, suggestion, accepted_headline_keys):
            valid.append(suggestion)
            if suggestion.location.field == "headline":
                accepted_headline_keys.add(_normalize_headline_key(suggestion.suggested))
        else:
            discarded += 1

    return valid, discarded


__all__ = [
    "is_suggestion_valid",
    "validate_suggestions",
]
