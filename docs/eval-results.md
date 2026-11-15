# Live Eval Results (Promptfoo, 3 columns)

🇧🇷 [Leia em Português](eval-results.pt-BR.md) | 🇺🇸 **English**

- **Date:** 2026-11-15 · **Model:** `google/gemini-2.5-flash` via OpenRouter, reasoning disabled
- **Code:** commit `31e0ef2` (branch `feat/a03-signal-veto`) · **Workflow:** `eval-live.yml`
- **Runs:** [43724236026](https://github.com/fgm9000/ad-copy-grader/actions/runs/43724236026), [43724246287](https://github.com/fgm9000/ad-copy-grader/actions/runs/43724246287), [43724256556](https://github.com/fgm9000/ad-copy-grader/actions/runs/43724256556) (same code, same model)
- **Suite:** 16 single-mutation cases (8 EN + 8 PT), `evals/cases.py`

## Summary

| Column | Run 1 | Run 2 | Run 3 | Total |
|---|---|---|---|---|
| 1. Raw LLM (before code filters) | 4/16 | 7/16 | 5/16 | 16/48 (33.3%) |
| **2. Production pipeline (code + LLM + filters)** | **16/16** | **16/16** | **16/16** | **48/48 (100%)** |
| 3. Degraded prompt (no code-authority line) | 5/16 | 6/16 | 5/16 | 16/48 (33.3%) |

The pipeline target was ≥ 90%. The raw column varies between runs (4 to 7 of 16); the pipeline does not, because code has the final word on every rule the model tends to get wrong. Column 3 had 1 provider error (case 01, run 1).

## Per case (passes out of 3 runs)

| Case | Raw | Pipeline | Degraded |
|---|---|---|---|
| 01 clean base EN | 0/3 | 3/3 | 0/3 |
| 02 clean base PT | 1/3 | 3/3 | 0/3 |
| 03 unverified price headline EN | 3/3 | 3/3 | 3/3 |
| 04 unverified price headline PT | 3/3 | 3/3 | 2/3 |
| 05 verified price in LP EN | 0/3 | 3/3 | 0/3 |
| 06 verified price in LP PT | 0/3 | 3/3 | 0/3 |
| 07 generic scheduling CTA EN | 1/3 | 3/3 | 1/3 |
| 08 unverified discount EN | 3/3 | 3/3 | 3/3 |
| 09 unverified discount PT | 1/3 | 3/3 | 2/3 |
| 10 missing CTA EN | 0/3 | 3/3 | 0/3 |
| 11 missing CTA PT | 1/3 | 3/3 | 2/3 |
| 12 absolute guarantee EN | 0/3 | 3/3 | 0/3 |
| 13 absolute guarantee PT | 0/3 | 3/3 | 0/3 |
| 14 code-only headline length | 0/3 | 3/3 | 0/3 |
| 15 code-only duplicate headline | 0/3 | 3/3 | 0/3 |
| 16 prompt injection + price | 3/3 | 3/3 | 3/3 |

## How the pipeline got here

| Step | Pipeline |
|---|---|
| First live run (`eval-live` had never run before) | 8/16 |
| Reasoning disabled, eval ground truth fixed, A01 vetoes, "only violations" prompt | 13/16, 13/16 |
| A02 decided by code (ADR-002 amendment) | 14/16, 15/16 |
| A03 vetoed on assets without absolute-promise wording | 16/16, 16/16, 16/16 |

1. **Client:** reasoning disabled (DeepSeek V4 returned empty content; thinking tokens are billed as output).
2. **Ground truth:** the "clean" ads advertised financing absent from `lp_context`, which A01 correctly flags.
3. **Code authority** (`pipeline.filter_llm_issues`, `check_a02`): A01 needs a price, `%` or offer word and is dropped when the LP backs the offer; A02 is decided by an action-verb lookup; A03 needs absolute-promise wording.
4. **Prompt:** `issues` lists only violations.

The code-side vetoes require a located asset; an issue without location is kept. Their word lists (offer, action verb, absolute promise) are the extension points.

## Other model tried

`deepseek/deepseek-v4-flash` (US$ 0.0044 per full run, reported by Promptfoo): pipeline 5/16 before the A02 and A03 changes (run [43721544696](https://github.com/fgm9000/ad-copy-grader/actions/runs/43721544696)). It reported passed rules as issues; not re-measured on the current code.

## Held-out suite (10 cases never used for tuning)

- **Code:** cases frozen in commit `14fe118` before any live run · `evals/holdout.py`, `evals/promptfooconfig.holdout.yaml`
- **Verticals:** physiotherapy (EN) and English course (PT), different from the dental cases above
- **Runs:** [43726575538](https://github.com/fgm9000/ad-copy-grader/actions/runs/43726575538), [43726584348](https://github.com/fgm9000/ad-copy-grader/actions/runs/43726584348), [43726593006](https://github.com/fgm9000/ad-copy-grader/actions/runs/43726593006) · `google/gemini-2.5-flash`

| Column | Run 1 | Run 2 | Run 3 | Total |
|---|---|---|---|---|
| 1. Raw LLM | 7/10 | 9/10 | 8/10 | 24/30 (80.0%) |
| **2. Production pipeline** | **7/10** | **8/10** | **8/10** | **23/30 (76.7%)** |
| 3. Degraded prompt | 5/10 | 5/10 | 6/10 | 16/30 (53.3%) |

**On unseen cases the pipeline scored below the raw model.** The code vetoes were designed on the dental cases and their word lists do not generalize:

| Case | Pipeline | Cause |
|---|---|---|
| H05 "Walk Pain-Free After 1 Visit" (expects A03) | 0/3 | The model flags A03; the A03 veto drops it because "pain-free" is not in the absolute-promise list |
| H09 "Inscreva-se já" (expects no issue) | 0/3 | Code-decided A02 fires because "inscrev" is not in the action-verb list (raw model: 2/3) |
| H06 "Fluência Garantida em 6 Meses" (expects A03) | 2/3 | Run 1: extra A01 on "Nivelamento Gratuito", which the LP states; "gratuit" is not among the LP-backed offer roots |

The 48/48 on the main suite therefore measures the pipeline on the cases it was tuned on. Expectations of the held-out cases are not edited after these results; fixing the word lists would require a new held-out set to measure again.
