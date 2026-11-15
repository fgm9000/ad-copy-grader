# Live Eval Results (Promptfoo, 3 columns)

🇧🇷 [Leia em Português](eval-results.pt-BR.md) | 🇺🇸 **English**

- **Date:** 2026-11-15 · **Model:** `google/gemini-2.5-flash` via OpenRouter, reasoning disabled
- **Code:** commit `2416f71` (branch `feat/a02-code-authority`) · **Workflow:** `eval-live.yml`
- **Runs:** [43722588891](https://github.com/fgm9000/ad-copy-grader/actions/runs/43722588891) and [43722597568](https://github.com/fgm9000/ad-copy-grader/actions/runs/43722597568) (same code, same model)
- **Suite:** 16 single-mutation cases (8 EN + 8 PT), `evals/cases.py`

## Summary

| Column | Run 1 | Run 2 | Total |
|---|---|---|---|
| 1. Raw LLM (before code filters) | 4/16 | 5/16 | 9/32 (28.1%) |
| **2. Production pipeline (code + LLM + filters)** | **14/16** | **15/16** | **29/32 (90.6%)** |
| 3. Degraded prompt (no code-authority line) | 6/16 | 5/16 | 11/32 (34.4%) |

The pipeline target was ≥ 90%. The two runs combined reach 90.6%; individually, run 1 is below (87.5%) and run 2 above (93.8%). The gap between columns 1 and 2 is the effect of code authority over the same model output.

## Per case (P = pass, F = fail; run 1 / run 2)

| Case | Raw | Pipeline | Degraded |
|---|---|---|---|
| 01 clean base EN | F / F | P / P | F / F |
| 02 clean base PT | F / P | P / P | F / F |
| 03 unverified price headline EN | P / P | P / P | P / P |
| 04 unverified price headline PT | P / P | P / P | P / P |
| 05 verified price in LP EN | F / F | P / P | F / F |
| 06 verified price in LP PT | F / F | P / P | F / F |
| 07 generic scheduling CTA EN | F / F | P / P | P / F |
| 08 unverified discount EN | P / P | P / P | P / P |
| 09 unverified discount PT | F / F | **F / F** | P / P |
| 10 missing CTA EN | F / F | P / P | F / F |
| 11 missing CTA PT | F / F | P / P | P / P |
| 12 absolute guarantee EN | F / F | P / P | F / F |
| 13 absolute guarantee PT | F / F | **F** / P | F / F |
| 14 code-only headline length | F / F | P / P | F / F |
| 15 code-only duplicate headline | F / F | P / P | F / F |
| 16 prompt injection + price | P / P | P / P | F / F |

## Residual failures

- **09 (both runs):** the model adds A03 to soft PT phrases ("Recupere Seu Sorriso", "cirurgia guiada de alta precisão"). A03 is still decided by the LLM.
- **13 (run 1):** an extra A01 on an asset the model itself describes as present in the landing page.

## What changed to get here (from 8/16 on the first run)

1. Reasoning disabled in the OpenRouter client (DeepSeek V4 returned empty content; thinking tokens are billed as output).
2. Eval ground truth fixed: the "clean" ads advertised financing absent from `lp_context`.
3. Code authority: A01 vetoed on assets without price/offer signal or with LP-backed offers; A02 decided by code (ADR-002 amendment).
4. Prompt: `issues` lists only violations.

## Other model tried

`deepseek/deepseek-v4-flash` (US$ 0.0044 per full run, reported by Promptfoo): pipeline 5/16 on the closest comparable code (run [43721544696](https://github.com/fgm9000/ad-copy-grader/actions/runs/43721544696)). It reports passed rules as issues and over-flags A03; not adopted.
