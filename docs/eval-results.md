# Live Eval Results (Promptfoo, 3 columns)

🇧🇷 [Leia em Português](eval-results.pt-BR.md) | 🇺🇸 **English**

- **Date:** 2026-11-15 · **Model:** `google/gemini-2.5-flash` via OpenRouter, reasoning disabled
- **Code:** commit `41b23e2` (branch `feat/evidence-verification`): evidence verification for A01/A03, A02 decided from model-extracted CTA phrases (ADR-002, last amendment)
- **Workflow:** `eval-live.yml` with `suite` = `main` | `holdout` | `holdout_v2` | `holdout_v3`; 3 runs per suite on the same code
- **Columns:** 1. raw model output · 2. production pipeline · 3. pipeline with the code-authority line removed from the prompt

## Current results

| Suite | Status | Raw | **Pipeline** | Degraded |
|---|---|---|---|---|
| **Held-out v3** (dog grooming EN, accounting PT) | **Frozen in `b5ddced` before this design; never seen** | 26/30 (86.7%) | **30/30 (100%)** | 29/30 |
| Held-out v2 (family law EN, gym PT) | Seen: its A02 failures motivated this design | 29/30 | 30/30 | 28/30 |
| Held-out v1 (physiotherapy EN, English course PT) | Seen: its failures retired the word-list vetoes | 24/30 | 28/30 | 25/30 |
| Main (16 dental cases) | Tuning set | 30/48 (62.5%) | 41/48 (85.4%) | 24/48 |

Runs: main [43732915171](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732915171), [43732923768](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732923768), [43732931751](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732931751) · v1 [43732940844](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732940844), [43732948964](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732948964), [43732958135](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732958135) · v2 [43732971505](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732971505), [43732982774](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732982774), [43732992640](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732992640) · v3 [43733003001](https://github.com/fgm9000/ad-copy-grader/actions/runs/43733003001), [43733013481](https://github.com/fgm9000/ad-copy-grader/actions/runs/43733013481), [43733024076](https://github.com/fgm9000/ad-copy-grader/actions/runs/43733024076)

**The number that measures generalization is held-out v3: 30/30.** It is 10 cases × 3 runs on two verticals; a larger unseen set would narrow the uncertainty. In v3 the raw model missed A02 on W07/W08 in some runs; the verified extraction got them right in all runs.

### Remaining failures (all model judgements, none from unverified evidence)

| Where | Count | What the model did |
|---|---|---|
| Main 12/14, A01 on "Flexible Financing Available" | 5 | Flags financing as unverified although the LP states it. Code checks only numbers, so this judgement stays with the model |
| Main 13, extra A01 on "100% Garantido" | 1 | Tags the guarantee as an offer too |
| Main 16 / v1 H10, A03 on the injection text | 2 | Treats "Ignore all audit rules…" as a promise |
| v1 H07, no A02 | 1 | Listed "build exercise plans around your goals" as a CTA. Known limit: a real phrase that is not a CTA still clears the ad |

## How the design evolved (pipeline column)

| Design | Main (16) | Held-out v1 | Held-out v2 | Held-out v3 |
|---|---|---|---|---|
| Original (first live run) | 8/16 | — | — | — |
| Word-list vetoes (A01 offer words, A02 action verbs, A03 promise words) | 48/48 | **23/30, below raw 24/30** | — | — |
| Evidence for A01/A03, A02 back to the model | 34/48 | 22/30 | **15/30, below raw 17/30** | — |
| **Evidence + A02 by extraction (current)** | 41/48 | 28/30 | 30/30 | **30/30** |

- The 48/48 of the word-list design was overfitting: the lists were written while looking at the 16 dental cases and failed on new verticals ("Pain-Free", "Inscreva-se").
- Without the lists, the model's A02 failed in both directions (12 of 15 failures on v2): asked "is a CTA missing?", it has to judge an absence.
- Asking the model to **quote the CTAs it finds** and letting code verify them and decide fixed A02 on unseen verticals.
- Each design change was measured on a held-out suite written and committed before the change (`14fe118`, `f336be1`, `b5ddced`). A suite whose failures were used to change the design is no longer held-out.

## Other models tried

**`google/gemini-2.5-flash-lite`** (2026-11-15, current design, commit `1633828`, 3 runs per suite): about 4× cheaper per call, but worse on every suite. Production stays on Gemini 2.5 Flash.

| Suite | Flash (pipeline) | Flash-Lite (pipeline) |
|---|---|---|
| Held-out v3 | 30/30 | 24/30 |
| Held-out v2 | 30/30 | 20/30 |
| Held-out v1 | 28/30 | 21/30 |
| Main | 41/48 | 35/48 |

On the main suite Flash-Lite returned 11–17 responses per run that failed schema validation even after the parser retry, which would degrade those ads to code-only results in production. Runs: main [43737449716](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737449716), [43737458970](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737458970), [43737467973](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737467973) · v3 [43737534778](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737534778), [43737545091](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737545091), [43737554811](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737554811).

**`deepseek/deepseek-v4-flash`** (US$ 0.0044 per full run, reported by Promptfoo): pipeline 5/16 on the main suite with the word-list design (run [43721544696](https://github.com/fgm9000/ad-copy-grader/actions/runs/43721544696)). It reported passed rules as issues. Not re-measured on the current design.
