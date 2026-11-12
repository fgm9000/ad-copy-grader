"""Deterministic rules engine (D01-D11) for Responsive Search Ads."""

import re
import unicodedata
import urllib.parse

from ad_copy_grader.models import AdInput, Issue, Language, Location

DETERMINISTIC_RULE_IDS: tuple[str, ...] = (
    "D01",
    "D02",
    "D03",
    "D04",
    "D05",
    "D06",
    "D07",
    "D08",
    "D09",
    "D10",
    "D11",
)

ALLOWED_ACRONYMS: frozenset[str] = frozenset(
    {
        "HTML",
        "HTTP",
        "HTTPS",
        "JSON",
        "REST",
        "SAAS",
        "GDPR",
        "LGPD",
        "CNPJ",
        "INSS",
        "FGTS",
        "OAB",
        "CRM",
        "CRO",
        "CREA",
        "CREFITO",
        "CRP",
        "ANVISA",
        "ABNT",
        "CPAP",
        "LASIK",
        "CBCT",
        "CADCAM",
    }
)

RULE_MESSAGES: dict[str, dict[Language, str]] = {
    "D01": {
        "en": "Responsive Search Ads must have between 3 and 15 headlines.",
        "pt": "Anúncios responsivos de pesquisa devem ter entre 3 e 15 títulos.",
    },
    "D02": {
        "en": "Fewer than 15 headlines provided; add all 15 headlines for optimal rotation.",
        "pt": "Menos de 15 títulos fornecidos; adicione todos os 15 para rotação ideal.",
    },
    "D03": {
        "en": "Responsive Search Ads must have between 2 and 4 descriptions.",
        "pt": "Anúncios responsivos de pesquisa devem ter entre 2 e 4 descrições.",
    },
    "D04": {
        "en": "Headline exceeds the 30-character limit.",
        "pt": "O título excede o limite de 30 caracteres.",
    },
    "D05": {
        "en": "Description exceeds the 90-character limit.",
        "pt": "A descrição excede o limite de 90 caracteres.",
    },
    "D06": {
        "en": "Display path exceeds the 15-character limit.",
        "pt": "O caminho de exibição excede o limite de 15 caracteres.",
    },
    "D07": {
        "en": "Fewer than 3 of the first 5 headlines mention the primary service.",
        "pt": "Menos de 3 dos primeiros 5 títulos mencionam o serviço principal.",
    },
    "D08": {
        "en": "Duplicate headline detected.",
        "pt": "Título duplicado detectado.",
    },
    "D09": {
        "en": "Repeated or excessive punctuation is not allowed.",
        "pt": "Pontuação repetida ou excessiva não é permitida.",
    },
    "D10": {
        "en": "Excessive capitalization detected; avoid ALL CAPS words unless standard acronyms.",
        "pt": "Uso excessivo de maiúsculas detectado; evite CAIXA ALTA exceto siglas padrão.",
    },
    "D11": {
        "en": "Final URL must be a valid HTTPS URL.",
        "pt": "O URL final deve ser um URL HTTPS válido.",
    },
}

REPEATED_PUNCTUATION_PATTERN = re.compile(r"!{2,}|\?{2,}|\.{3,}|…+")
UPPERCASE_WORD_PATTERN = re.compile(r"\b[A-ZÀ-ÖØ-Þ]{4,}\b")


def nfc_len(text: str) -> int:
    """Return character count after Unicode NFC normalization."""
    return len(unicodedata.normalize("NFC", text))


def _strip_accents(text: str) -> str:
    """Strip diacritical marks using Unicode NFD decomposition."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def _normalize_for_matching(text: str) -> str:
    """Normalize text for case- and accent-insensitive matching."""
    return _strip_accents(text).lower()


def _headline_matches_service(norm_headline: str, norm_service: str) -> bool:
    """Check if a normalized headline references the normalized primary service."""
    if norm_service in norm_headline:
        return True

    service_words = [w for w in re.findall(r"\w+", norm_service) if len(w) >= 3]
    if not service_words:
        return False

    threshold = min(2, len(service_words))
    matched_count = 0
    for word in service_words:
        stem = word[:5] if len(word) >= 5 else word
        if word in norm_headline or stem in norm_headline:
            matched_count += 1

    return matched_count >= threshold


def check_d01(ad: AdInput) -> list[Issue]:
    """Flag error if headline count is less than 3 or greater than 15."""
    count = len(ad.headlines)
    if count < 3 or count > 15:
        return [
            Issue(
                rule_id="D01",
                severity="error",
                message=RULE_MESSAGES["D01"][ad.lang],
                location=None,
                source="code",
            )
        ]
    return []


def check_d02(ad: AdInput) -> list[Issue]:
    """Flag warning if headline count is between 3 and 14."""
    count = len(ad.headlines)
    if 3 <= count < 15:
        return [
            Issue(
                rule_id="D02",
                severity="warning",
                message=RULE_MESSAGES["D02"][ad.lang],
                location=None,
                source="code",
            )
        ]
    return []


def check_d03(ad: AdInput) -> list[Issue]:
    """Flag error if description count is less than 2 or greater than 4."""
    count = len(ad.descriptions)
    if count < 2 or count > 4:
        return [
            Issue(
                rule_id="D03",
                severity="error",
                message=RULE_MESSAGES["D03"][ad.lang],
                location=None,
                source="code",
            )
        ]
    return []


def check_d04(ad: AdInput) -> list[Issue]:
    """Flag error for each headline exceeding 30 Unicode NFC characters."""
    issues: list[Issue] = []
    for idx, headline in enumerate(ad.headlines):
        if nfc_len(headline) > 30:
            issues.append(
                Issue(
                    rule_id="D04",
                    severity="error",
                    message=RULE_MESSAGES["D04"][ad.lang],
                    location=Location(field="headline", index=idx),
                    source="code",
                )
            )
    return issues


def check_d05(ad: AdInput) -> list[Issue]:
    """Flag error for each description exceeding 90 Unicode NFC characters."""
    issues: list[Issue] = []
    for idx, desc in enumerate(ad.descriptions):
        if nfc_len(desc) > 90:
            issues.append(
                Issue(
                    rule_id="D05",
                    severity="error",
                    message=RULE_MESSAGES["D05"][ad.lang],
                    location=Location(field="description", index=idx),
                    source="code",
                )
            )
    return issues


def check_d06(ad: AdInput) -> list[Issue]:
    """Flag error if path1 or path2 exceeds 15 Unicode NFC characters."""
    issues: list[Issue] = []
    if ad.path1 is not None and nfc_len(ad.path1) > 15:
        issues.append(
            Issue(
                rule_id="D06",
                severity="error",
                message=RULE_MESSAGES["D06"][ad.lang],
                location=Location(field="path1", index=None),
                source="code",
            )
        )
    if ad.path2 is not None and nfc_len(ad.path2) > 15:
        issues.append(
            Issue(
                rule_id="D06",
                severity="error",
                message=RULE_MESSAGES["D06"][ad.lang],
                location=Location(field="path2", index=None),
                source="code",
            )
        )
    return issues


def check_d07(ad: AdInput) -> list[Issue]:
    """Flag warning if fewer than 3 of top 5 headlines reference primary_service."""
    if len(ad.headlines) < 5:
        return []

    norm_service = _normalize_for_matching(ad.primary_service)
    top_5 = ad.headlines[:5]
    match_count = sum(
        1 for h in top_5 if _headline_matches_service(_normalize_for_matching(h), norm_service)
    )

    if match_count < 3:
        return [
            Issue(
                rule_id="D07",
                severity="warning",
                message=RULE_MESSAGES["D07"][ad.lang],
                location=None,
                source="code",
            )
        ]
    return []


def check_d08(ad: AdInput) -> list[Issue]:
    """Flag error for duplicate headlines after NFC normalization, strip, and casefold."""
    issues: list[Issue] = []
    seen: set[str] = set()
    for idx, headline in enumerate(ad.headlines):
        norm = unicodedata.normalize("NFC", headline).strip().casefold()
        if norm in seen:
            issues.append(
                Issue(
                    rule_id="D08",
                    severity="error",
                    message=RULE_MESSAGES["D08"][ad.lang],
                    location=Location(field="headline", index=idx),
                    source="code",
                )
            )
        else:
            seen.add(norm)
    return issues


def check_d09(ad: AdInput) -> list[Issue]:
    """Flag error if repeated or excessive punctuation is found."""
    issues: list[Issue] = []
    for idx, headline in enumerate(ad.headlines):
        if REPEATED_PUNCTUATION_PATTERN.search(headline):
            issues.append(
                Issue(
                    rule_id="D09",
                    severity="error",
                    message=RULE_MESSAGES["D09"][ad.lang],
                    location=Location(field="headline", index=idx),
                    source="code",
                )
            )
    for idx, desc in enumerate(ad.descriptions):
        if REPEATED_PUNCTUATION_PATTERN.search(desc):
            issues.append(
                Issue(
                    rule_id="D09",
                    severity="error",
                    message=RULE_MESSAGES["D09"][ad.lang],
                    location=Location(field="description", index=idx),
                    source="code",
                )
            )
    return issues


def check_d10(ad: AdInput) -> list[Issue]:
    """Flag warning if excessive capitalization (ALL CAPS >= 4 chars) is found."""
    issues: list[Issue] = []
    for idx, headline in enumerate(ad.headlines):
        norm = unicodedata.normalize("NFC", headline)
        caps = UPPERCASE_WORD_PATTERN.findall(norm)
        if any(word not in ALLOWED_ACRONYMS for word in caps):
            issues.append(
                Issue(
                    rule_id="D10",
                    severity="warning",
                    message=RULE_MESSAGES["D10"][ad.lang],
                    location=Location(field="headline", index=idx),
                    source="code",
                )
            )
    for idx, desc in enumerate(ad.descriptions):
        norm = unicodedata.normalize("NFC", desc)
        caps = UPPERCASE_WORD_PATTERN.findall(norm)
        if any(word not in ALLOWED_ACRONYMS for word in caps):
            issues.append(
                Issue(
                    rule_id="D10",
                    severity="warning",
                    message=RULE_MESSAGES["D10"][ad.lang],
                    location=Location(field="description", index=idx),
                    source="code",
                )
            )
    return issues


def check_d11(ad: AdInput) -> list[Issue]:
    """Flag error if final_url is not a valid HTTPS URL."""
    url = ad.final_url
    is_invalid = False
    if not url.startswith("https://") or any(c.isspace() for c in url):
        is_invalid = True
    else:
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc
            if not netloc or "." not in netloc:
                is_invalid = True
            else:
                host = parsed.hostname or netloc
                parts = host.split(".")
                if not parts[0] or not parts[-1]:
                    is_invalid = True
        except Exception:
            is_invalid = True

    if is_invalid:
        return [
            Issue(
                rule_id="D11",
                severity="error",
                message=RULE_MESSAGES["D11"][ad.lang],
                location=Location(field="final_url", index=None),
                source="code",
            )
        ]
    return []


def run_rules(ad: AdInput) -> list[Issue]:
    """Execute all deterministic rules D01 through D11 in order."""
    issues: list[Issue] = []
    issues.extend(check_d01(ad))
    issues.extend(check_d02(ad))
    issues.extend(check_d03(ad))
    issues.extend(check_d04(ad))
    issues.extend(check_d05(ad))
    issues.extend(check_d06(ad))
    issues.extend(check_d07(ad))
    issues.extend(check_d08(ad))
    issues.extend(check_d09(ad))
    issues.extend(check_d10(ad))
    issues.extend(check_d11(ad))
    return issues


__all__ = [
    "ALLOWED_ACRONYMS",
    "DETERMINISTIC_RULE_IDS",
    "RULE_MESSAGES",
    "check_d01",
    "check_d02",
    "check_d03",
    "check_d04",
    "check_d05",
    "check_d06",
    "check_d07",
    "check_d08",
    "check_d09",
    "check_d10",
    "check_d11",
    "nfc_len",
    "run_rules",
]
