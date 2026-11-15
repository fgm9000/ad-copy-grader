# Resultados do Eval Real (Promptfoo, 3 colunas)

🇧🇷 **Português** | 🇺🇸 [Read in English](eval-results.md)

- **Data:** 15/11/2026 · **Modelo:** `google/gemini-2.5-flash` via OpenRouter, raciocínio desligado
- **Código:** commit `2416f71` (branch `feat/a02-code-authority`) · **Workflow:** `eval-live.yml`
- **Execuções:** [43722588891](https://github.com/fgm9000/ad-copy-grader/actions/runs/43722588891) e [43722597568](https://github.com/fgm9000/ad-copy-grader/actions/runs/43722597568) (mesmo código, mesmo modelo)
- **Suíte:** 16 casos de mutação única (8 EN + 8 PT), `evals/cases.py`

## Resumo

| Coluna | Rodada 1 | Rodada 2 | Total |
|---|---|---|---|
| 1. LLM cru (antes dos filtros de código) | 4/16 | 5/16 | 9/32 (28,1%) |
| **2. Pipeline de produção (código + LLM + filtros)** | **14/16** | **15/16** | **29/32 (90,6%)** |
| 3. Prompt degradado (sem a linha de autoridade do código) | 6/16 | 5/16 | 11/32 (34,4%) |

A meta do pipeline era ≥ 90%. Somando as duas rodadas, 90,6%; isoladamente, a rodada 1 fica abaixo (87,5%) e a rodada 2 acima (93,8%). A diferença entre as colunas 1 e 2 é o efeito da autoridade do código sobre a mesma saída do modelo.

## Por caso (P = passou, F = falhou; rodada 1 / rodada 2)

| Caso | Cru | Pipeline | Degradado |
|---|---|---|---|
| 01 base limpa EN | F / F | P / P | F / F |
| 02 base limpa PT | F / P | P / P | F / F |
| 03 preço não verificado no título EN | P / P | P / P | P / P |
| 04 preço não verificado no título PT | P / P | P / P | P / P |
| 05 preço confirmado na LP EN | F / F | P / P | F / F |
| 06 preço confirmado na LP PT | F / F | P / P | F / F |
| 07 CTA genérica de agendamento EN | F / F | P / P | P / F |
| 08 desconto não verificado EN | P / P | P / P | P / P |
| 09 desconto não verificado PT | F / F | **F / F** | P / P |
| 10 sem CTA EN | F / F | P / P | F / F |
| 11 sem CTA PT | F / F | P / P | P / P |
| 12 garantia absoluta EN | F / F | P / P | F / F |
| 13 garantia absoluta PT | F / F | **F** / P | F / F |
| 14 só código: tamanho de título | F / F | P / P | F / F |
| 15 só código: título duplicado | F / F | P / P | F / F |
| 16 injeção de prompt + preço | P / P | P / P | F / F |

## Falhas restantes

- **09 (as duas rodadas):** o modelo acrescenta A03 em frases suaves em PT ("Recupere Seu Sorriso", "cirurgia guiada de alta precisão"). O A03 continua decidido pelo LLM.
- **13 (rodada 1):** um A01 a mais num item que o próprio modelo descreve como presente na landing page.

## O que mudou até aqui (a partir de 8/16 na primeira execução)

1. Raciocínio desligado no cliente OpenRouter (o DeepSeek V4 devolvia conteúdo vazio; tokens de raciocínio são cobrados como saída).
2. Gabarito do eval corrigido: os anúncios "limpos" anunciavam financiamento ausente do `lp_context`.
3. Autoridade do código: A01 vetado em itens sem sinal de preço/oferta ou com oferta confirmada na LP; A02 decidido por código (adendo ao ADR-002).
4. Prompt: `issues` lista só violações.

## Outro modelo testado

`deepseek/deepseek-v4-flash` (US$ 0,0044 por execução completa, segundo o Promptfoo): pipeline 5/16 no código comparável mais próximo (execução [43721544696](https://github.com/fgm9000/ad-copy-grader/actions/runs/43721544696)). Ele registra regras aprovadas como issues e aponta A03 em excesso; não foi adotado.
