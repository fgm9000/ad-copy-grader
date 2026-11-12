"""Unit tests for deterministic validation of LLM rewrite suggestions."""

import pytest

from ad_copy_grader.models import AdInput, Location, Suggestion
from ad_copy_grader.rewrite import is_suggestion_valid, validate_suggestions


@pytest.fixture
def sample_ad() -> AdInput:
    """Return a baseline valid AdInput for rewrite testing."""
    return AdInput(
        headlines=[
            "Dental Implants Specialist",
            "Affordable Dental Implants",
            "Permanent Dental Implants",
        ],
        descriptions=[
            "Restore your smile with titanium dental implants today.",
            "Book your consultation with experienced oral surgeons.",
        ],
        path1="implants",
        path2="clinic",
        final_url="https://example.com/implants",
        primary_service="Dental Implants",
        lp_context="Titanium implants available.",
        lang="en",
    )


def test_valid_headline_and_description_rewrite(sample_ad: AdInput) -> None:
    """Accept valid headline (<= 30 chars) and valid description (<= 90 chars)."""
    valid_headline_sug = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Expert Implant Surgeons",  # 23 chars
        reason="Better clarity.",
    )
    assert is_suggestion_valid(sample_ad, valid_headline_sug) is True

    valid_desc_sug = Suggestion(
        location=Location(field="description", index=0),
        original="Restore your smile with titanium dental implants today.",
        suggested="Restore your smile today with gentle and precise dental implants.",  # 65 chars
        reason="Adds gentle care messaging.",
    )
    assert is_suggestion_valid(sample_ad, valid_desc_sug) is True


def test_discard_headline_exceeding_30_chars(sample_ad: AdInput) -> None:
    """Discard headline suggestion with 31 or more characters (D04)."""
    sug = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Valid lowercase headline text 1",  # 31 chars
        reason="Too long.",
    )
    assert is_suggestion_valid(sample_ad, sug) is False


def test_discard_description_exceeding_90_chars(sample_ad: AdInput) -> None:
    """Discard description suggestion with 91 or more characters (D05)."""
    sug = Suggestion(
        location=Location(field="description", index=0),
        original="Sample description",
        suggested="B" * 91,
        reason="Too long.",
    )
    assert is_suggestion_valid(sample_ad, sug) is False


def test_path_length_validation(sample_ad: AdInput) -> None:
    """Validate path suggestions <= 15 chars and discard >= 16 chars (D06)."""
    valid_path1 = Suggestion(
        location=Location(field="path1"),
        original="implants",
        suggested="dental-care",  # 11 chars
        reason="Cleaner slug.",
    )
    assert is_suggestion_valid(sample_ad, valid_path1) is True

    valid_path2 = Suggestion(
        location=Location(field="path2"),
        original="clinic",
        suggested="expert-surgeons",  # 15 chars
        reason="Targeted slug.",
    )
    assert is_suggestion_valid(sample_ad, valid_path2) is True

    too_long_path = Suggestion(
        location=Location(field="path1"),
        original="implants",
        suggested="implant-specialists",  # 19 chars (> 15)
        reason="Too long.",
    )
    assert is_suggestion_valid(sample_ad, too_long_path) is False


def test_discard_duplicate_headline(sample_ad: AdInput) -> None:
    """Discard headline suggestions duplicating another headline or accepted suggestion (D08)."""
    # Duplicate existing headline at index 1
    dup_existing = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Affordable Dental Implants",  # matches headline at index 1
        reason="Duplicate headline.",
    )
    assert is_suggestion_valid(sample_ad, dup_existing) is False

    # Duplicate already accepted headline suggestion
    accepted_keys = {"quality dental implants"}
    dup_accepted = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Quality Dental Implants",
        reason="Duplicate suggestion.",
    )
    assert is_suggestion_valid(sample_ad, dup_accepted, accepted_keys) is False


def test_discard_repeated_punctuation(sample_ad: AdInput) -> None:
    """Discard rewrite suggestion containing repeated punctuation like '!!' (D09)."""
    sug_exclamation = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Best Dental Care!!",
        reason="Repeated exclamation mark.",
    )
    assert is_suggestion_valid(sample_ad, sug_exclamation) is False

    sug_question = Suggestion(
        location=Location(field="description", index=0),
        original="Sample",
        suggested="Want a new smile?? Book today.",
        reason="Repeated question mark.",
    )
    assert is_suggestion_valid(sample_ad, sug_question) is False


def test_all_caps_validation_and_allowed_acronyms(sample_ad: AdInput) -> None:
    """Discard forbidden 4+ letter ALL CAPS words (D10) while permitting allowed acronyms."""
    # Forbidden ALL CAPS word
    sug_forbidden = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="FREE Consultation Today",  # FREE is not in ALLOWED_ACRONYMS
        reason="ALL CAPS promotional word.",
    )
    assert is_suggestion_valid(sample_ad, sug_forbidden) is False

    # Allowed acronym HTTPS
    sug_allowed_https = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Secure HTTPS Booking",
        reason="Contains allowed acronym.",
    )
    assert is_suggestion_valid(sample_ad, sug_allowed_https) is True

    # Allowed acronym LGPD
    sug_allowed_lgpd = Suggestion(
        location=Location(field="description", index=0),
        original="Sample",
        suggested="Clínica em conformidade total com a LGPD. Agende agora.",
        reason="Contains allowed LGPD acronym.",
    )
    assert is_suggestion_valid(sample_ad, sug_allowed_lgpd) is True


def test_discard_invalid_index_and_empty_text(sample_ad: AdInput) -> None:
    """Discard suggestions with empty text, out-of-bounds index, or unsupported fields."""
    # Empty suggestion text
    empty_sug = Suggestion(
        location=Location(field="headline", index=0),
        original="Original",
        suggested="   ",
        reason="Empty.",
    )
    assert is_suggestion_valid(sample_ad, empty_sug) is False

    # Negative headline index
    neg_headline_sug = Suggestion(
        location=Location(field="headline", index=-1),
        original="Original",
        suggested="Valid Text",
        reason="Negative index.",
    )
    assert is_suggestion_valid(sample_ad, neg_headline_sug) is False

    # Out of bounds headline index
    oob_headline_sug = Suggestion(
        location=Location(field="headline", index=99),
        original="Original",
        suggested="Valid Text",
        reason="Out of bounds.",
    )
    assert is_suggestion_valid(sample_ad, oob_headline_sug) is False

    # None headline index
    none_headline_sug = Suggestion(
        location=Location(field="headline", index=None),
        original="Original",
        suggested="Valid Text",
        reason="Index is None.",
    )
    assert is_suggestion_valid(sample_ad, none_headline_sug) is False

    # Negative description index
    neg_desc_sug = Suggestion(
        location=Location(field="description", index=-1),
        original="Original",
        suggested="Valid description text.",
        reason="Negative index.",
    )
    assert is_suggestion_valid(sample_ad, neg_desc_sug) is False

    # Out of bounds description index
    oob_desc_sug = Suggestion(
        location=Location(field="description", index=10),
        original="Original",
        suggested="Valid description text.",
        reason="Out of bounds index.",
    )
    assert is_suggestion_valid(sample_ad, oob_desc_sug) is False

    # None description index
    none_desc_sug = Suggestion(
        location=Location(field="description", index=None),
        original="Original",
        suggested="Valid description text.",
        reason="Index is None.",
    )
    assert is_suggestion_valid(sample_ad, none_desc_sug) is False

    # Unsupported field (e.g. final_url)
    url_sug = Suggestion(
        location=Location(field="final_url"),
        original="https://example.com",
        suggested="https://example.com/new",
        reason="Cannot rewrite URL.",
    )
    assert is_suggestion_valid(sample_ad, url_sug) is False


def test_validate_suggestions_batch_filtering(sample_ad: AdInput) -> None:
    """Filter batch of suggestions, tracking discarded count and inter-suggestion duplicates."""
    sug_valid1 = Suggestion(
        location=Location(field="headline", index=0),
        original="Dental Implants Specialist",
        suggested="Gentle Dental Implants",
        reason="Valid 1",
    )
    sug_duplicate_of_sug1 = Suggestion(
        location=Location(field="headline", index=2),
        original="Permanent Dental Implants",
        suggested="Gentle Dental Implants",  # Duplicate of sug_valid1
        reason="Duplicate of first suggestion",
    )
    sug_too_long = Suggestion(
        location=Location(field="description", index=0),
        original="Old desc",
        suggested="X" * 95,
        reason="Exceeds 90 chars",
    )
    sug_valid2 = Suggestion(
        location=Location(field="description", index=1),
        original="Old desc 2",
        suggested="Schedule your consultation with our experienced dental team today.",
        reason="Valid 2",
    )

    valid_list, discarded = validate_suggestions(
        sample_ad, [sug_valid1, sug_duplicate_of_sug1, sug_too_long, sug_valid2]
    )

    assert len(valid_list) == 2
    assert valid_list[0].suggested == "Gentle Dental Implants"
    assert valid_list[1].suggested == (
        "Schedule your consultation with our experienced dental team today."
    )
    assert discarded == 2
