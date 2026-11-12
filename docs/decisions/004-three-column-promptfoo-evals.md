# ADR-004: Three-Column Promptfoo Evaluation Design

> **[🇺🇸 English](004-three-column-promptfoo-evals.md) | [🇧🇷 Português](004-three-column-promptfoo-evals.pt-BR.md)**

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

In a hybrid AI system where deterministic code filters and augments LLM output, evaluating only the final pipeline output hides whether the prompt itself is degrading or whether the server-side filters are masking prompt regressions. Conversely, evaluating only the raw LLM output ignores the protective value of the deterministic rules and server authority filters.

## Alternatives Considered

1. **Single-Column End-to-End Evaluation:**
   - *Pros:* Simple configuration.
   - *Cons:* Does not isolate the contribution of the prompt guardrail versus the server-side Code Authority Filter.
2. **Pytest-Only Unit Tests with Mocked Responses:**
   - *Pros:* Fast and deterministic in CI.
   - *Cons:* Cannot benchmark live model upgrades (e.g., comparing `google/gemini-2.5-flash` vs. other models on OpenRouter) with token/cost tracking and side-by-side matrix visualization.
3. **Three-Column Promptfoo Evaluation (`raw`, `pipeline`, `degraded`) with Shared Call Caching (Selected):**
   - *Pros:* Compares three columns simultaneously across 16 bilingual (`en` and `pt`) single-mutation scenarios:
     - **Column 1 (`raw`):** Raw LLM output before deterministic rules or server filters.
     - **Column 2 (`pipeline`):** Complete hybrid production output (`D01–D11` + `A01–A03` + Code Authority Filter).
     - **Column 3 (`degraded`):** Real ablation of `PROMPT_EN` / `PROMPT_PT` with the anti-`D*` authority instruction programmatically removed (`build_degraded_system_prompt`), proving the guardrail's impact.
   - *Efficiency:* Columns 1 (`raw`) and 2 (`pipeline`) share a single `grade()` execution per test case via SHA-256 caching in `evals/provider.py`, cutting live evaluation token cost by 33%.

## Decision

Adopt a **3-column Promptfoo evaluation architecture** in `evals/` supporting both offline deterministic CI (`FAKE_MODEL=1` in `.github/workflows/ci.yml`) and on-demand live model benchmarking (`.github/workflows/eval-live.yml`).

## Consequences

- **Positive:** Proves quantitatively how each layer (prompt guardrail + server authority filter + deterministic engine) contributes to accuracy across English and Portuguese.
- **Negative / Trade-off:** Requires Node.js (`npx promptfoo@0.109.0`) in the CI `eval-fake` job alongside `uv`.
