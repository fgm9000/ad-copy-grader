# Product Requirements Document (PRD) — Ad Copy Grader API

> 🌐 **Language / Idioma:** **🇺🇸 English** | [🇧🇷 Leia em Português](prd.pt-BR.md)

| Metadata | Value |
| --- | --- |
| **Product** | Ad Copy Grader (`ad-copy-grader`) |
| **Document Version** | 1.0 · 2026-11-12 |
| **Status** | Approved for Implementation |
| **License** | PolyForm Noncommercial License 1.0.0 (Non-commercial use only) |
| **Core Stack** | Python 3.12 · FastAPI · Pydantic v2 · `uv` · OpenRouter (`google/gemini-2.5-flash`) · Google Cloud Run · GitHub Pages (HTML5 + Tailwind CLI + Vanilla JS) |
| **Language Policy** | **Full Bilingual (`en` & `pt-BR`)** across Prompts, API Rule Messages, Web UI, Scenarios, README, PRD, Architecture Docs, and ADRs (source code & Git commits in English) |

---

## 1. Executive Summary & Problem Statement

Google Ads **Responsive Search Ads (RSAs)** enforce strict structural and editorial constraints (headline and description counts, Unicode `NFC` character limits, punctuation rules, capitalization policies, and HTTPS destination URLs) alongside nuanced semantic and regulatory policies (offer/price consistency with the landing page, clear Call-to-Action presence, and prohibition of absolute outcome guarantees in regulated industries such as healthcare and legal services).

**Why single-paradigm approaches fail:**
1. **Pure LLM Grading (Zero-Shot Prompting):** LLMs routinely miscount exact character lengths, hallucinate formatting violations, and miss subtle case-insensitive duplicates. Worse, when asked to rewrite a failing headline, LLMs frequently suggest replacements that exceed the 30-character limit.
2. **Pure Deterministic Rules (Regex / Static Code):** Code enforces exact character limits and syntax with 100% precision, but cannot evaluate whether a promotional price in an ad contradicts the landing page summary or whether phrasing implies an unsubstantiated clinical guarantee (e.g., *"100% guaranteed cure"*, *"painless procedure"*).

**The Solution (Core Architectural Thesis):**
A hybrid auditing API and interactive web playground built on the principle: **"Code has authority over what is verifiable; the LLM judges only what is semantic."**
- A pure-Python deterministic engine evaluates all structural and syntactic rules (`D01–D11`).
- A structured-output LLM evaluates strictly semantic rules (`A01–A03`).
- An **Authority Filter Layer** strips any LLM hallucination that attempts to flag deterministic (`D*`) rules or raises false-positive price mismatches when the exact price string is verifiably present in the landing page context.
- Every **rewrite suggestion** proposed by the LLM is re-validated against the deterministic engine before being returned to the caller.

---

## 2. Target Users & Use Cases

1. **Paid Search Manager / Copywriter (Interactive Web Demo — Side-by-Side Layout):**
   - Views the **Landing Page Context Card** (`lp_context`, `primary_service`, and `final_url`) **side by side** with the **RSA Ad Copy Card** (headlines and descriptions with live `N/30` and `N/90` character counters). This makes it immediately clear how the engine cross-checks ad claims against landing page content without performing external web scraping.
   - Receives a **0.0 to 10.0 quality grade (`grade_10`)** (aligned with Google Ads' native 1–10 Quality Score mental model) alongside a 0–100 `score`, field-level issue highlights, explicit authority badges (`Code Verified (Deterministic)` vs. `LLM Judged (Semantic)`), and pre-validated rewrite suggestions.
2. **Marketing Engineer / Campaign Automation Pipeline (`POST /v1/grade` API Consumer):**
   - Integrates the endpoint as a pre-publish quality gate before submitting RSAs to the Google Ads API.
   - Receives a strictly typed JSON payload (`passed`, `score`, `grade_10`, `issues`, `suggestions`) with graceful degradation if the upstream LLM provider times out or fails.

---

## 3. Functional Requirements

### FR-01: Deterministic Rule Engine (`D01–D11`)
Executed in pure Python over Unicode `NFC`-normalized strings with zero external network calls:

| ID | Rule | Severity | Trigger Condition |
| --- | --- | --- | --- |
| `D01` | Headline count bounds | `error` | Fewer than 3 or more than 15 headlines |
| `D02` | Recommended headline coverage | `warning` | Between 3 and 14 headlines (below the optimal 15 RSA slots) |
| `D03` | Description count bounds | `error` | Fewer than 2 or more than 4 descriptions |
| `D04` | Headline character limit | `error` | Headline length `> 30` Unicode NFC characters |
| `D05` | Description character limit | `error` | Description length `> 90` Unicode NFC characters |
| `D06` | Display path character limit | `error` | Present `path1` or `path2` length `> 15` Unicode NFC characters |
| `D07` | Primary service relevance in top headlines | `warning` | When `>= 5` headlines exist and fewer than 3 of the first 5 mention `primary_service` |
| `D08` | Duplicate headlines | `error` | Identical headlines after `strip()` and `casefold()` |
| `D09` | Repeated / excessive punctuation | `error` | Repeated punctuation sequences such as `!!`, `??`, or `...` |
| `D10` | Excessive capitalization (ALL CAPS) | `warning` | Whole word with `>= 4` uppercase letters (excluding an allowlist of standard acronyms) |
| `D11` | Valid HTTPS final URL | `error` | Missing, malformed, or non-`https://` `final_url` |

### FR-02: Semantic Rule Engine via LLM (`A01–A03`)
Executed via OpenRouter (`google/gemini-2.5-flash` by default) in JSON mode:

| ID | Rule | Severity | Trigger Condition |
| --- | --- | --- | --- |
| `A01` | Unverified price or promotion claim | `error` | Numeric price, discount, or concrete promotional offer in the ad is absent from `lp_context` |
| `A02` | Missing Call-to-Action (CTA) | `warning` | No description contains a clear action directive |
| `A03` | Absolute outcome guarantee | `warning` | Unsubstantiated guarantee or clinical/regulated promise (e.g., *"guaranteed"*, *"100%"*, *"cure"*, *"painless"*) |

### FR-03: Resilient Output Parser with Self-Correction Retry
- Extracts JSON payloads even when wrapped in Markdown code fences (```` ```json ````).
- Validates the payload against the Pydantic v2 `LlmReview` schema and enforces that `rules_checked` includes `["A01", "A02", "A03"]`.
- On validation failure, performs **at most one self-correction retry**, appending the structured Pydantic `ValidationError` details to the prompt. Raises `LlmOutputError` if the second attempt also fails.

### FR-04: Code Authority Filters
- Strips any LLM-reported issue whose `rule_id` starts with `D`.
- Strips `A01` issues when the numeric price or figure cited in the ad copy appears literally inside `lp_context` (deterministic false-positive prevention).
- Strips any issue referencing an out-of-bounds `location.index`.

### FR-05: Deterministic Rewrite Re-Validation (`rewrite.py`)
- Every LLM rewrite suggestion is audited against `D04`, `D05`, `D08`, `D09`, and `D10`.
- Any suggestion that violates a deterministic constraint is discarded before reaching the user and counted in `discarded_suggestions_count`.

### FR-06: Scoring System (0–10 and 0–100) & Pass Criteria
- **100-Point Score (`score`):** `max(0, 100 - 15 * errors - 5 * warnings)`
- **10-Point Grade (`grade_10`):** `round(score / 10, 1)` (e.g., `8.5 / 10.0`, mirroring Google Ads' 0–10 scale).
- **Pass Flag (`passed`):** `errors == 0`.

### FR-07: Graceful Degradation
- If OpenRouter fails (network timeout, HTTP 5xx, or double schema validation failure), the API still returns all deterministic issues (`D01–D11`) with `model: null` and a descriptive English `degraded_reason`, ensuring the client and web demo never fail with a blank screen.

---

## 4. Non-Functional Requirements (NFRs)

| Category | Requirement | Enforcement Mechanism |
| --- | --- | --- |
| **FinOps / Cost Ceiling** | Total cloud + LLM spend `< US$ 5.00 / month` | Cloud Run `min-instances=0`, `max-instances=1`, in-memory per-IP sliding window (`5 req/min`), global daily cap (`200 req/day`), and offline pre-computed scenarios (`examples.json`). |
| **Latency** | P95 `< 4.0s` (live LLM) and `< 50ms` (deterministic / `FakeModel`) | Async `httpx.AsyncClient` (20s timeout), Rust-backed Pydantic v2 validation, and `google/gemini-2.5-flash`. |
| **Security** | Zero static secrets in repo/CI; prompt-injection resilience | Keyless GitHub Actions deploy via GCP Workload Identity Federation (OIDC), Google Secret Manager, `gitleaks` in pre-commit + CI, untrusted-input framing in system prompt, and strict CORS. |
| **Code Quality** | Test coverage `>= 90%`, `mypy --strict` (0 errors), active quality ratchet | CI quality ratchet (`quality_check.py`) blocking regressions or new `# noqa` / `# type: ignore` suppressions. |
| **AI Quality (Evals)** | Pass rate `>= 90%` on the `pipeline` column in Promptfoo | 3-column comparative Promptfoo suite (`raw` vs. `pipeline` vs. `degraded`) across 15+ synthetic test cases including prompt-injection attempts. |
| **Accessibility & UI** | Lighthouse Accessibility `>= 90` and Performance `>= 95` | Semantic HTML5 + static CSS compiled via `@tailwindcss/cli` + Vanilla JS with instant `EN | PT` language toggle. |

---

## 5. Non-Goals (Out of Scope)

- **No database or ad persistence:** The service is intentionally 100% stateless to minimize attack surface and keep idle cost at zero.
- **No end-user authentication:** The web demo is publicly accessible for frictionless portfolio evaluation, protected by per-IP and daily rate limits.
- **No live web scraping of `final_url`:** Landing page context is passed explicitly via `lp_context` (and visualized side by side in the demo UI) to avoid SSRF risks and scraper flakiness.

---

## 6. Engineering Governance & Release Criteria

1. **Conventional Commits & Bilingual Documentation:** All commits, branch names, and source code identifiers are written in English following Conventional Commits; all architectural documentation, PRD, ADRs, and README files are maintained in both English (`en`) and Brazilian Portuguese (`pt-BR`).
2. **Automated Quality Ratchet & CI Gates:** Every change must pass `ruff` (lint + format + `flake8-bandit` `S` rules), `mypy --strict`, `pytest` (`>= 90%` coverage), `semgrep` (`p/owasp-top-ten`, `p/python`, `p/fastapi`), `codeql` (GitHub CodeQL semantic taint analysis for Python), `gitleaks`, the 3-column Promptfoo pipeline check, and the zero-regression quality ratchet (`quality_check.py`) before merging to `main`.
