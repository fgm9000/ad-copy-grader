"""Unit tests for deterministic rules engine (D01-D11) and domain models."""

import json
import unicodedata
from pathlib import Path

import pytest
from pydantic import ValidationError

from ad_copy_grader.models import (
    AdInput,
    GradeResult,
    Issue,
    Location,
    Suggestion,
)
from ad_copy_grader.rules import (
    ALLOWED_ACRONYMS,
    DETERMINISTIC_RULE_IDS,
    RULE_MESSAGES,
    check_d01,
    check_d02,
    check_d03,
    check_d04,
    check_d05,
    check_d06,
    check_d07,
    check_d08,
    check_d09,
    check_d10,
    check_d11,
    nfc_len,
    run_rules,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def clean_en_payload() -> dict[str, object]:
    """Load clean English RSA fixture payload."""
    with open(FIXTURES_DIR / "base_clean_en.json", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


@pytest.fixture
def clean_pt_payload() -> dict[str, object]:
    """Load clean Portuguese RSA fixture payload."""
    with open(FIXTURES_DIR / "base_clean_pt.json", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


@pytest.fixture
def clean_en_ad(clean_en_payload: dict[str, object]) -> AdInput:
    """Create clean English AdInput instance."""
    return AdInput.model_validate(clean_en_payload)


@pytest.fixture
def clean_pt_ad(clean_pt_payload: dict[str, object]) -> AdInput:
    """Create clean Portuguese AdInput instance."""
    return AdInput.model_validate(clean_pt_payload)


# --- Base Fixture Clean Runs ---


def test_clean_en_passes_all_rules(clean_en_ad: AdInput) -> None:
    """Clean English base ad should trigger zero deterministic issues."""
    issues = run_rules(clean_en_ad)
    assert issues == []


def test_clean_pt_passes_all_rules(clean_pt_ad: AdInput) -> None:
    """Clean Portuguese base ad should trigger zero deterministic issues."""
    issues = run_rules(clean_pt_ad)
    assert issues == []


# --- D01: Headline count bounds ---


def test_d01_too_few_headlines(clean_en_ad: AdInput) -> None:
    """Flag error when fewer than 3 headlines are provided."""
    data = clean_en_ad.model_dump()
    data["headlines"] = ["Dental Implants Clinic", "Affordable Dental Implants"]
    ad = AdInput.model_validate(data)

    issues = check_d01(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D01"
    assert issues[0].severity == "error"
    assert issues[0].location is None
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D01"]["en"]


def test_d01_too_many_headlines(clean_en_ad: AdInput) -> None:
    """Flag error when more than 15 headlines are provided."""
    data = clean_en_ad.model_dump()
    data["headlines"] = [f"Headline Number {i}" for i in range(16)]
    ad = AdInput.model_validate(data)

    issues = check_d01(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D01"
    assert issues[0].severity == "error"
    assert issues[0].location is None
    assert issues[0].source == "code"


def test_d01_valid_boundaries(clean_en_ad: AdInput) -> None:
    """Boundary counts 3 and 15 should pass D01 without errors."""
    data3 = clean_en_ad.model_dump()
    data3["headlines"] = clean_en_ad.headlines[:3]
    ad3 = AdInput.model_validate(data3)
    assert check_d01(ad3) == []

    data15 = clean_en_ad.model_dump()
    data15["headlines"] = clean_en_ad.headlines[:15]
    ad15 = AdInput.model_validate(data15)
    assert check_d01(ad15) == []


# --- D02: Recommended headline coverage ---


def test_d02_fewer_than_15_headlines_warning(clean_en_ad: AdInput) -> None:
    """Flag warning when headlines are between 3 and 14."""
    data = clean_en_ad.model_dump()
    data["headlines"] = clean_en_ad.headlines[:14]
    ad = AdInput.model_validate(data)

    issues = check_d02(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D02"
    assert issues[0].severity == "warning"
    assert issues[0].location is None
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D02"]["en"]


def test_d02_optimal_15_headlines_passes(clean_en_ad: AdInput) -> None:
    """Provide exactly 15 headlines should not trigger D02."""
    assert check_d02(clean_en_ad) == []


def test_d02_does_not_fire_when_below_min(clean_en_ad: AdInput) -> None:
    """Headline count < 3 is an error handled by D01, not D02 warning."""
    data = clean_en_ad.model_dump()
    data["headlines"] = clean_en_ad.headlines[:2]
    ad = AdInput.model_validate(data)
    assert check_d02(ad) == []


# --- D03: Description count bounds ---


def test_d03_too_few_descriptions(clean_en_ad: AdInput) -> None:
    """Flag error when fewer than 2 descriptions are provided."""
    data = clean_en_ad.model_dump()
    data["descriptions"] = clean_en_ad.descriptions[:1]
    ad = AdInput.model_validate(data)

    issues = check_d03(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D03"
    assert issues[0].severity == "error"
    assert issues[0].location is None
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D03"]["en"]


def test_d03_too_many_descriptions(clean_en_ad: AdInput) -> None:
    """Flag error when more than 4 descriptions are provided."""
    data = clean_en_ad.model_dump()
    data["descriptions"] = [f"Description number {i} text for testing." for i in range(5)]
    ad = AdInput.model_validate(data)

    issues = check_d03(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D03"
    assert issues[0].severity == "error"
    assert issues[0].location is None
    assert issues[0].source == "code"


def test_d03_valid_description_counts(clean_en_ad: AdInput) -> None:
    """Description counts of 2, 3, and 4 should pass D03."""
    for count in (2, 3, 4):
        data = clean_en_ad.model_dump()
        data["descriptions"] = clean_en_ad.descriptions[:count]
        ad = AdInput.model_validate(data)
        assert check_d03(ad) == []


# --- D04: Headline character limit (<= 30 NFC chars) ---


def test_d04_headline_exceeds_30_chars(clean_en_ad: AdInput) -> None:
    """Flag error for headline longer than 30 characters."""
    data = clean_en_ad.model_dump()
    # 31 chars
    data["headlines"][2] = "This Headline Exceeds 30 Chars!"
    ad = AdInput.model_validate(data)

    issues = check_d04(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D04"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="headline", index=2)
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D04"]["en"]


def test_d04_headline_exactly_30_chars_passes(clean_en_ad: AdInput) -> None:
    """Headline with exactly 30 characters passes D04."""
    data = clean_en_ad.model_dump()
    data["headlines"][0] = "123456789012345678901234567890"  # exactly 30 chars
    ad = AdInput.model_validate(data)
    assert check_d04(ad) == []


# --- D05: Description character limit (<= 90 NFC chars) ---


def test_d05_description_exceeds_90_chars(clean_en_ad: AdInput) -> None:
    """Flag error for description longer than 90 characters."""
    data = clean_en_ad.model_dump()
    # 91 chars
    data["descriptions"][1] = "A" * 91
    ad = AdInput.model_validate(data)

    issues = check_d05(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D05"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="description", index=1)
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D05"]["en"]


def test_d05_description_exactly_90_chars_passes(clean_en_ad: AdInput) -> None:
    """Description with exactly 90 characters passes D05."""
    data = clean_en_ad.model_dump()
    data["descriptions"][0] = "B" * 90
    ad = AdInput.model_validate(data)
    assert check_d05(ad) == []


# --- D06: Display path character limit (<= 15 NFC chars) ---


def test_d06_path1_exceeds_15_chars(clean_en_ad: AdInput) -> None:
    """Flag error when path1 exceeds 15 characters."""
    data = clean_en_ad.model_dump()
    data["path1"] = "path-too-long-here"  # 18 chars
    ad = AdInput.model_validate(data)

    issues = check_d06(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D06"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="path1", index=None)
    assert issues[0].source == "code"


def test_d06_path2_exceeds_15_chars(clean_en_ad: AdInput) -> None:
    """Flag error when path2 exceeds 15 characters."""
    data = clean_en_ad.model_dump()
    data["path2"] = "sixteen-letters-"  # 16 chars
    ad = AdInput.model_validate(data)

    issues = check_d06(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D06"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="path2", index=None)
    assert issues[0].source == "code"


def test_d06_both_paths_exceed_15_chars(clean_en_ad: AdInput) -> None:
    """Flag separate errors when both path1 and path2 exceed 15 characters."""
    data = clean_en_ad.model_dump()
    data["path1"] = "toolongpathone12"
    data["path2"] = "toolongpathtwo12"
    ad = AdInput.model_validate(data)

    issues = check_d06(ad)
    assert len(issues) == 2
    assert [i.location.field for i in issues if i.location] == ["path1", "path2"]


def test_d06_none_or_valid_paths_pass(clean_en_ad: AdInput) -> None:
    """Paths with None or <= 15 chars pass D06."""
    data = clean_en_ad.model_dump()
    data["path1"] = None
    data["path2"] = "exactly-15-char"  # 15 chars
    ad = AdInput.model_validate(data)
    assert check_d06(ad) == []


# --- D07: Primary service relevance in top 5 headlines ---


def test_d07_fewer_than_3_mentions_in_top_5(clean_en_ad: AdInput) -> None:
    """Flag warning when fewer than 3 of top 5 headlines reference primary service."""
    data = clean_en_ad.model_dump()
    # Replace top headlines so only 1 mentions "Dental Implants"
    data["headlines"][0] = "Dental Implants Specialist"
    data["headlines"][1] = "Restore Your Beautiful Smile"
    data["headlines"][2] = "Modern Clinic Equipment"
    data["headlines"][3] = "Experienced Doctor Team"
    data["headlines"][4] = "Schedule Your Visit Now"
    ad = AdInput.model_validate(data)

    issues = check_d07(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D07"
    assert issues[0].severity == "warning"
    assert issues[0].location is None
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D07"]["en"]


def test_d07_passes_with_accents_and_singular_plural_stems(clean_pt_ad: AdInput) -> None:
    """Matches singular/plural and accents like Implante Dentário vs Implantes Dentários."""
    # Top 3 headlines in clean_pt_ad:
    # 0: "Implante Dentário Especialista"
    # 1: "Implantes Dentários Seguros"
    # 2: "Implante Dentário Avançado"
    assert check_d07(clean_pt_ad) == []


def test_d07_ignored_when_fewer_than_5_headlines(clean_en_ad: AdInput) -> None:
    """D07 is only evaluated when len(headlines) >= 5."""
    data = clean_en_ad.model_dump()
    data["headlines"] = [
        "Unrelated Headline One",
        "Unrelated Headline Two",
        "Unrelated Headline Three",
        "Unrelated Headline Four",
    ]
    ad = AdInput.model_validate(data)
    assert check_d07(ad) == []


def test_d07_short_words_primary_service_fallback(clean_en_ad: AdInput) -> None:
    """Test primary service with short words (< 3 chars) or exact match."""
    data = clean_en_ad.model_dump()
    data["primary_service"] = "3D"
    data["headlines"] = [
        "Special 3D Dental Care",
        "Get 3D Scans Today",
        "Advanced 3D Smile Tech",
        "Clinic Overview Visit",
        "Friendly Doctors Here",
    ] + clean_en_ad.headlines[5:]
    ad = AdInput.model_validate(data)
    assert check_d07(ad) == []


# --- D08: Duplicate headlines ---


def test_d08_duplicate_headlines(clean_en_ad: AdInput) -> None:
    """Flag error for duplicate headlines after NFC normalization, strip, and casefold."""
    data = clean_en_ad.model_dump()
    # Headline at index 0 is "Dental Implants Specialist"
    # Set index 6 to exact case-insensitive duplicate with whitespace
    data["headlines"][6] = "  dental implants specialist  "
    ad = AdInput.model_validate(data)

    issues = check_d08(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D08"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="headline", index=6)
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D08"]["en"]


def test_d08_multiple_duplicates(clean_en_ad: AdInput) -> None:
    """Flag each subsequent occurrence of a duplicate headline."""
    data = clean_en_ad.model_dump()
    data["headlines"][3] = data["headlines"][0]
    data["headlines"][7] = data["headlines"][0].upper()
    ad = AdInput.model_validate(data)

    issues = check_d08(ad)
    assert len(issues) == 2
    indices = [i.location.index for i in issues if i.location]
    assert indices == [3, 7]


# --- D09: Repeated / excessive punctuation ---


def test_d09_repeated_punctuation_headline(clean_en_ad: AdInput) -> None:
    """Flag error when exclamation/question/ellipsis repeats in headline."""
    for punct in ("!!", "???", "....", "…"):
        data = clean_en_ad.model_dump()
        data["headlines"][1] = f"Best Offer{punct}"
        ad = AdInput.model_validate(data)

        issues = check_d09(ad)
        assert len(issues) == 1
        assert issues[0].rule_id == "D09"
        assert issues[0].severity == "error"
        assert issues[0].location == Location(field="headline", index=1)
        assert issues[0].source == "code"


def test_d09_repeated_punctuation_description(clean_en_ad: AdInput) -> None:
    """Flag error when repeated punctuation occurs in description."""
    data = clean_en_ad.model_dump()
    data["descriptions"][2] = "Restore your smile today!! Book your consultation online now."
    ad = AdInput.model_validate(data)

    issues = check_d09(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D09"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="description", index=2)


def test_d09_standard_punctuation_passes(clean_en_ad: AdInput) -> None:
    """Single punctuation marks (one '!', one '?', one '.') pass D09."""
    data = clean_en_ad.model_dump()
    data["headlines"][0] = "Restore Your Smile Today!"
    data["headlines"][1] = "Need A New Smile?"
    data["headlines"][2] = "Top Care. Book Now."
    ad = AdInput.model_validate(data)
    assert check_d09(ad) == []


# --- D10: Excessive capitalization (ALL CAPS >= 4 chars) ---


def test_d10_excessive_caps_in_headline(clean_en_ad: AdInput) -> None:
    """Flag warning when whole word of >= 4 uppercase letters is not an allowed acronym."""
    data = clean_en_ad.model_dump()
    data["headlines"][1] = "FREE Dental Consultation"
    ad = AdInput.model_validate(data)

    issues = check_d10(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D10"
    assert issues[0].severity == "warning"
    assert issues[0].location == Location(field="headline", index=1)
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D10"]["en"]


def test_d10_excessive_caps_in_description(clean_en_ad: AdInput) -> None:
    """Flag warning for unallowed ALL CAPS in description."""
    data = clean_en_ad.model_dump()
    data["descriptions"][0] = (
        "Restore your smile with PROMO titanium implants. Schedule your consultation today."
    )
    ad = AdInput.model_validate(data)

    issues = check_d10(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D10"
    assert issues[0].severity == "warning"
    assert issues[0].location == Location(field="description", index=0)


def test_d10_allowed_acronyms_pass(clean_en_ad: AdInput) -> None:
    """Allowed acronyms (HTML, GDPR, LGPD, CADCAM, CBCT, etc.) should not trigger D10."""
    data = clean_en_ad.model_dump()
    data["headlines"][0] = "Modern CBCT 3D Scanning"
    data["headlines"][1] = "Accurate CADCAM Planning"
    data["descriptions"][0] = (
        "Our clinic complies with GDPR and LGPD regulations. Book your consultation today."
    )
    ad = AdInput.model_validate(data)
    assert check_d10(ad) == []


def test_d10_short_caps_under_4_chars_pass(clean_en_ad: AdInput) -> None:
    """Words with 1 to 3 uppercase letters (e.g. 'NEW', 'TOP', '3D') pass D10."""
    data = clean_en_ad.model_dump()
    data["headlines"][0] = "NEW Dental Implants Tech"
    data["headlines"][1] = "TOP Care For Your Smile"
    ad = AdInput.model_validate(data)
    assert check_d10(ad) == []


# --- D11: Valid HTTPS final URL ---


def test_d11_non_https_url(clean_en_ad: AdInput) -> None:
    """Flag error when final_url does not use HTTPS."""
    data = clean_en_ad.model_dump()
    data["final_url"] = "http://example.com/implants"
    ad = AdInput.model_validate(data)

    issues = check_d11(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D11"
    assert issues[0].severity == "error"
    assert issues[0].location == Location(field="final_url", index=None)
    assert issues[0].source == "code"
    assert issues[0].message == RULE_MESSAGES["D11"]["en"]


def test_d11_url_with_whitespace(clean_en_ad: AdInput) -> None:
    """Flag error when final_url contains whitespace."""
    data = clean_en_ad.model_dump()
    data["final_url"] = "https://example .com/implants"
    ad = AdInput.model_validate(data)

    issues = check_d11(ad)
    assert len(issues) == 1
    assert issues[0].rule_id == "D11"


def test_d11_url_missing_domain_dot(clean_en_ad: AdInput) -> None:
    """Flag error when final_url domain has no dot or starts/ends with dot."""
    for bad_url in (
        "https://localhost/path",
        "https://.com/path",
        "https://example./path",
        "https://[::ffff:invalid:ip]/path",
    ):
        data = clean_en_ad.model_dump()
        data["final_url"] = bad_url
        ad = AdInput.model_validate(data)

        issues = check_d11(ad)
        assert len(issues) == 1
        assert issues[0].rule_id == "D11"


def test_d11_valid_https_urls(clean_en_ad: AdInput) -> None:
    """Verify various valid HTTPS URLs pass D11."""
    valid_urls = [
        "https://example.com",
        "https://sub.domain.co.uk/path/to/page?query=1#section",
        "https://clinic.example.com:8443/appointment",
    ]
    for url in valid_urls:
        data = clean_en_ad.model_dump()
        data["final_url"] = url
        ad = AdInput.model_validate(data)
        assert check_d11(ad) == []


# --- Bilingual Message Assertions ---


def test_bilingual_messages_coverage() -> None:
    """Verify all deterministic rule IDs have both 'en' and 'pt' messages."""
    for rule_id in DETERMINISTIC_RULE_IDS:
        assert rule_id in RULE_MESSAGES
        assert "en" in RULE_MESSAGES[rule_id]
        assert "pt" in RULE_MESSAGES[rule_id]
        assert len(RULE_MESSAGES[rule_id]["en"]) > 0
        assert len(RULE_MESSAGES[rule_id]["pt"]) > 0


def test_bilingual_pt_messages_returned_when_lang_is_pt(clean_pt_ad: AdInput) -> None:
    """Verify PT messages are returned for violations when lang is 'pt'."""
    data = clean_pt_ad.model_dump()
    data["headlines"] = clean_pt_ad.headlines[:2]  # Triggers D01
    data["final_url"] = "http://inseguro.com.br"  # Triggers D11
    ad = AdInput.model_validate(data)

    issues = run_rules(ad)
    d01_issues = [i for i in issues if i.rule_id == "D01"]
    d11_issues = [i for i in issues if i.rule_id == "D11"]

    assert len(d01_issues) == 1
    assert d01_issues[0].message == RULE_MESSAGES["D01"]["pt"]
    assert len(d11_issues) == 1
    assert d11_issues[0].message == RULE_MESSAGES["D11"]["pt"]


# --- Unicode NFC Normalization ---


def test_unicode_nfc_character_counting() -> None:
    """Decomposed Unicode characters should be normalized to NFC before counting."""
    # "é" can be represented as precomposed "\u00e9" (1 char)
    # or decomposed "e\u0301" (2 chars). In NFC it is 1 char.
    decomposed = "e\u0301"
    assert len(decomposed) == 2
    assert nfc_len(decomposed) == 1
    assert unicodedata.normalize("NFC", decomposed) == "\u00e9"

    # Exactly 30 NFC chars using decomposed sequences
    decomposed_headline = "e\u0301" * 30
    assert len(decomposed_headline) == 60
    assert nfc_len(decomposed_headline) == 30


def test_d04_with_decomposed_unicode(clean_en_ad: AdInput) -> None:
    """Headline with 30 NFC characters constructed from decomposed chars passes D04."""
    data = clean_en_ad.model_dump()
    data["headlines"][0] = "e\u0301" * 30
    ad = AdInput.model_validate(data)
    assert check_d04(ad) == []

    # 31 NFC chars (29 decomposed e' + 2 ascii chars = 60 chars <= schema limit) triggers D04
    data["headlines"][0] = ("e\u0301" * 29) + "ab"
    ad31 = AdInput.model_validate(data)
    issues = check_d04(ad31)
    assert len(issues) == 1
    assert issues[0].rule_id == "D04"


# --- AdInput Model Validations ---


def test_lp_context_truncation_over_1200_chars(clean_en_payload: dict[str, object]) -> None:
    """lp_context exceeding 1200 chars should be truncated to exactly 1200 chars."""
    data = dict(clean_en_payload)
    data["lp_context"] = "X" * 1500
    ad = AdInput.model_validate(data)

    assert len(ad.lp_context) == 1200
    assert ad.lp_context == "X" * 1200


def test_ad_input_headline_max_schema_length(clean_en_payload: dict[str, object]) -> None:
    """Individual headline exceeding 60 characters fails Pydantic schema validation."""
    data = dict(clean_en_payload)
    headlines = list(clean_en_payload["headlines"])  # type: ignore[arg-type]
    headlines[0] = "H" * 61
    data["headlines"] = headlines

    with pytest.raises(ValidationError) as exc_info:
        AdInput.model_validate(data)
    assert "Headline at index 0 exceeds schema limit of 60 characters." in str(exc_info.value)


def test_ad_input_description_max_schema_length(clean_en_payload: dict[str, object]) -> None:
    """Individual description exceeding 180 characters fails schema validation."""
    data = dict(clean_en_payload)
    descriptions = list(clean_en_payload["descriptions"])  # type: ignore[arg-type]
    descriptions[0] = "D" * 181
    data["descriptions"] = descriptions

    with pytest.raises(ValidationError) as exc_info:
        AdInput.model_validate(data)
    assert "Description at index 0 exceeds schema limit of 180 characters." in str(exc_info.value)


def test_allowed_acronyms_contains_expected_entries() -> None:
    """Verify ALLOWED_ACRONYMS constant contains standard tech, legal and medical terms."""
    assert "HTML" in ALLOWED_ACRONYMS
    assert "LGPD" in ALLOWED_ACRONYMS
    assert "GDPR" in ALLOWED_ACRONYMS
    assert "CBCT" in ALLOWED_ACRONYMS
    assert "CADCAM" in ALLOWED_ACRONYMS


# --- GradeResult and Model Validation ---


def test_grade_result_model_instantiation() -> None:
    """Verify GradeResult model accepts valid attributes and validates ranges."""
    result = GradeResult(
        score=85,
        grade_10=8.5,
        passed=False,
        issues=[
            Issue(
                rule_id="D02",
                severity="warning",
                message="Fewer than 15 headlines.",
                location=None,
                source="code",
            )
        ],
        suggestions=[
            Suggestion(
                location=Location(field="headline", index=0),
                original="Old Headline",
                suggested="New Headline",
                reason="Improved relevance",
            )
        ],
        discarded_suggestions_count=1,
        rules_checked=list(DETERMINISTIC_RULE_IDS),
        model="google/gemini-2.5-flash",
        degraded_reason=None,
    )
    assert result.score == 85
    assert result.grade_10 == 8.5
    assert not result.passed
    assert len(result.issues) == 1
    assert len(result.suggestions) == 1
    assert result.discarded_suggestions_count == 1
    assert result.model == "google/gemini-2.5-flash"


def test_grade_result_invalid_score_bounds() -> None:
    """Score must be between 0 and 100, and grade_10 between 0.0 and 10.0."""
    with pytest.raises(ValidationError):
        GradeResult(
            score=105,
            grade_10=10.5,
            passed=True,
            issues=[],
            rules_checked=["D01"],
        )
