# Resultados do Eval Real (Promptfoo, 3 colunas)

🇧🇷 **Português** | 🇺🇸 [Read in English](eval-results.md)

- **Data:** 15/11/2026 · **Modelo:** `google/gemini-2.5-flash` via OpenRouter, raciocínio desligado
- **Código:** commit `31e0ef2` (branch `feat/a03-signal-veto`) · **Workflow:** `eval-live.yml`
- **Execuções:** [43724236026](https://github.com/fgm9000/ad-copy-grader/actions/runs/43724236026), [43724246287](https://github.com/fgm9000/ad-copy-grader/actions/runs/43724246287), [43724256556](https://github.com/fgm9000/ad-copy-grader/actions/runs/43724256556) (mesmo código, mesmo modelo)
- **Suíte:** 16 casos de mutação única (8 EN + 8 PT), `evals/cases.py`

## Resumo

| Coluna | Rodada 1 | Rodada 2 | Rodada 3 | Total |
|---|---|---|---|---|
| 1. LLM cru (antes dos filtros de código) | 4/16 | 7/16 | 5/16 | 16/48 (33,3%) |
| **2. Pipeline de produção (código + LLM + filtros)** | **16/16** | **16/16** | **16/16** | **48/48 (100%)** |
| 3. Prompt degradado (sem a linha de autoridade do código) | 5/16 | 6/16 | 5/16 | 16/48 (33,3%) |

A meta do pipeline era ≥ 90%. A coluna crua varia entre rodadas (de 4 a 7 de 16); o pipeline não varia, porque o código tem a palavra final em cada regra que o modelo costuma errar. A coluna 3 teve 1 erro do provedor (caso 01, rodada 1).

## Por caso (acertos em 3 rodadas)

| Caso | Cru | Pipeline | Degradado |
|---|---|---|---|
| 01 base limpa EN | 0/3 | 3/3 | 0/3 |
| 02 base limpa PT | 1/3 | 3/3 | 0/3 |
| 03 preço não verificado no título EN | 3/3 | 3/3 | 3/3 |
| 04 preço não verificado no título PT | 3/3 | 3/3 | 2/3 |
| 05 preço confirmado na LP EN | 0/3 | 3/3 | 0/3 |
| 06 preço confirmado na LP PT | 0/3 | 3/3 | 0/3 |
| 07 CTA genérica de agendamento EN | 1/3 | 3/3 | 1/3 |
| 08 desconto não verificado EN | 3/3 | 3/3 | 3/3 |
| 09 desconto não verificado PT | 1/3 | 3/3 | 2/3 |
| 10 sem CTA EN | 0/3 | 3/3 | 0/3 |
| 11 sem CTA PT | 1/3 | 3/3 | 2/3 |
| 12 garantia absoluta EN | 0/3 | 3/3 | 0/3 |
| 13 garantia absoluta PT | 0/3 | 3/3 | 0/3 |
| 14 só código: tamanho de título | 0/3 | 3/3 | 0/3 |
| 15 só código: título duplicado | 0/3 | 3/3 | 0/3 |
| 16 injeção de prompt + preço | 3/3 | 3/3 | 3/3 |

## Como o pipeline chegou aqui

| Etapa | Pipeline |
|---|---|
| Primeira execução real (o `eval-live` nunca tinha rodado) | 8/16 |
| Raciocínio desligado, gabarito corrigido, vetos do A01, prompt "só violações" | 13/16, 13/16 |
| A02 decidido por código (adendo ao ADR-002) | 14/16, 15/16 |
| A03 vetado em itens sem palavra de promessa absoluta | 16/16, 16/16, 16/16 |

1. **Cliente:** raciocínio desligado (o DeepSeek V4 devolvia conteúdo vazio; tokens de raciocínio são cobrados como saída).
2. **Gabarito:** os anúncios "limpos" anunciavam financiamento ausente do `lp_context`, que o A01 aponta corretamente.
3. **Autoridade do código** (`pipeline.filter_llm_issues`, `check_a02`): o A01 exige preço, `%` ou palavra de oferta e cai quando a LP confirma a oferta; o A02 é decidido por busca de verbo de ação; o A03 exige palavra de promessa absoluta.
4. **Prompt:** `issues` lista só violações.

Os vetos do código exigem um item localizado; issue sem localização é mantido. As listas de palavras (oferta, verbo de ação, promessa absoluta) são os pontos de extensão.

## Outro modelo testado

`deepseek/deepseek-v4-flash` (US$ 0,0044 por execução completa, segundo o Promptfoo): pipeline 5/16 antes das mudanças do A02 e do A03 (execução [43721544696](https://github.com/fgm9000/ad-copy-grader/actions/runs/43721544696)). Ele registrava regras aprovadas como issues; não foi medido de novo no código atual.
