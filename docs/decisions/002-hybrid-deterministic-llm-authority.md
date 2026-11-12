# ADR-002: Hybrid Deterministic Code + LLM Authority Pipeline

> **[🇺🇸 English](002-hybrid-deterministic-llm-authority.md) | [🇧🇷 Português](002-hybrid-deterministic-llm-authority.pt-BR.md)**

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

Google Ads Responsive Search Ads (RSAs) must satisfy both **exact mechanical rules** (e.g., max 30 characters per headline, max 90 per description, max 15 per path, `https://` scheme, no duplicate assets, no exclamation marks in headlines) and **semantic rules** (e.g., no unverified price or discount claims absent from the landing page, presence of a clear CTA, no absolute clinical/financial guarantees).

LLMs frequently miscount character lengths due to subword tokenization, occasionally hallucinate deterministic violations, and sometimes generate rewrite suggestions that themselves exceed the 30-character limit.

## Alternatives Considered

1. **LLM-Only Auditing:**
   - *Pros:* Single prompt, minimal application code.
   - *Cons:* High false-positive rate on character limits (`D04`, `D05`, `D06`), non-deterministic scoring, and unvalidated rewrite suggestions that fail Google Ads upload.
2. **Regex / Deterministic-Only Auditing:**
   - *Pros:* Fast, zero token cost, 100% deterministic.
   - *Cons:* Cannot reliably cross-reference semantic claims or promotional conditions between ad copy and arbitrary landing page text (`A01`) or judge nuanced CTA intent (`A02`).
3. **Hybrid Pipeline with Server Code Authority Filter & Rewrite Validator (Selected):**
   - *Pros:* Deterministic Python code (`rules.py`) is the sole authority for `D01–D11`. The LLM evaluates only semantic rules (`A01–A03`). Server-side filters (`filter_llm_issues` in `pipeline.py`) strip any `D*` rule emitted by the LLM and suppress `A01` false positives when the price/offer is present in `lp_context`. Finally, `validate_suggestions` (`rewrite.py`) runs `D04/D05/D08/D09/D10` against every LLM-suggested rewrite before returning it.

## Decision

Implement a **Hybrid Deterministic + LLM Pipeline** with strict separation of authority:
1. Code rules (`D01–D11`) run first over NFC-normalized strings.
2. LLM evaluates semantic rules (`A01–A03`) using native bilingual prompts (`PROMPT_EN` / `PROMPT_PT`).
3. Server-side **Code Authority Filter** strips `D*` overreach, out-of-bounds indices, and LP-verified `A01` false positives.
4. **Rewrite Validator** discards any LLM rewrite suggestion that violates deterministic constraints.
5. On double LLM failure, the API degrades gracefully to deterministic rules (`D01–D11`) rather than returning an empty error screen.

## Consequences

- **Positive:** Zero character-count hallucinations, guaranteed-valid rewrite suggestions, and resilience against upstream LLM outages.
- **Negative / Trade-off:** Requires maintaining both deterministic rules and semantic prompts, verified continuously via the 3-column Promptfoo suite.
