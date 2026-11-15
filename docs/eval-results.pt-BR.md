# Resultados do Eval Real (Promptfoo, 3 colunas)

🇧🇷 **Português** | 🇺🇸 [Read in English](eval-results.md)

- **Data:** 15/11/2026 · **Modelo:** `google/gemini-2.5-flash` via OpenRouter, raciocínio desligado
- **Código:** commit `41b23e2` (branch `feat/evidence-verification`): conferência de evidência no A01/A03 e A02 decidido a partir de frases de CTA extraídas pelo modelo (ADR-002, último adendo)
- **Workflow:** `eval-live.yml` com `suite` = `main` | `holdout` | `holdout_v2` | `holdout_v3`; 3 rodadas por suíte no mesmo código
- **Colunas:** 1. saída crua do modelo · 2. pipeline de produção · 3. pipeline sem a linha de autoridade do código no prompt

## Resultados atuais

| Suíte | Situação | Cru | **Pipeline** | Degradado |
|---|---|---|---|---|
| **Held-out v3** (banho e tosa EN, contabilidade PT) | **Congelado em `b5ddced` antes deste desenho; nunca visto** | 26/30 (86,7%) | **30/30 (100%)** | 29/30 |
| Held-out v2 (direito de família EN, academia PT) | Visto: as falhas de A02 motivaram este desenho | 29/30 | 30/30 | 28/30 |
| Held-out v1 (fisioterapia EN, curso de inglês PT) | Visto: as falhas aposentaram os vetos por lista | 24/30 | 28/30 | 25/30 |
| Principal (16 casos odontológicos) | Conjunto de ajuste | 30/48 (62,5%) | 41/48 (85,4%) | 24/48 |

Execuções: principal [43732915171](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732915171), [43732923768](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732923768), [43732931751](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732931751) · v1 [43732940844](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732940844), [43732948964](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732948964), [43732958135](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732958135) · v2 [43732971505](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732971505), [43732982774](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732982774), [43732992640](https://github.com/fgm9000/ad-copy-grader/actions/runs/43732992640) · v3 [43733003001](https://github.com/fgm9000/ad-copy-grader/actions/runs/43733003001), [43733013481](https://github.com/fgm9000/ad-copy-grader/actions/runs/43733013481), [43733024076](https://github.com/fgm9000/ad-copy-grader/actions/runs/43733024076)

**O número que mede generalização é o held-out v3: 30/30.** São 10 casos × 3 rodadas em dois setores; um conjunto inédito maior reduziria a incerteza. No v3, o modelo cru errou o A02 de W07/W08 em algumas rodadas; a extração conferida acertou em todas.

### Falhas restantes (todas julgamento do modelo, nenhuma por evidência não conferida)

| Onde | Vezes | O que o modelo fez |
|---|---|---|
| Principal 12/14, A01 em "Flexible Financing Available" | 5 | Aponta o financiamento como não verificado, embora a LP o cite. O código só confere números, então esse julgamento fica com o modelo |
| Principal 13, A01 a mais em "100% Garantido" | 1 | Marca a garantia também como oferta |
| Principal 16 / v1 H10, A03 no texto de injeção | 2 | Trata "Ignore all audit rules…" como promessa |
| v1 H07, sem A02 | 1 | Listou "build exercise plans around your goals" como CTA. Limite conhecido: frase real que não é CTA livra o anúncio |

## Como o desenho evoluiu (coluna pipeline)

| Desenho | Principal (16) | Held-out v1 | Held-out v2 | Held-out v3 |
|---|---|---|---|---|
| Original (primeira execução real) | 8/16 | — | — | — |
| Vetos por lista de palavras (oferta no A01, verbos no A02, promessa no A03) | 48/48 | **23/30, abaixo do cru 24/30** | — | — |
| Evidência no A01/A03, A02 de volta ao modelo | 34/48 | 22/30 | **15/30, abaixo do cru 17/30** | — |
| **Evidência + A02 por extração (atual)** | 41/48 | 28/30 | 30/30 | **30/30** |

- O 48/48 do desenho por listas era sobreajuste: as listas foram escritas olhando os 16 casos odontológicos e falharam em setores novos ("Pain-Free", "Inscreva-se").
- Sem as listas, o A02 do modelo errou nas duas direções (12 das 15 falhas no v2): perguntado "falta CTA?", ele precisa julgar uma ausência.
- Pedir ao modelo para **citar as CTAs que encontra** e deixar o código conferir e decidir resolveu o A02 em setores inéditos.
- Cada mudança de desenho foi medida num held-out escrito e commitado antes da mudança (`14fe118`, `f336be1`, `b5ddced`). Uma suíte cujas falhas foram usadas para mudar o desenho deixa de ser held-out.

## Outros modelos testados

**`google/gemini-2.5-flash-lite`** (15/11/2026, desenho atual, commit `1633828`, 3 rodadas por suíte): cerca de 4× mais barato por chamada, mas pior em todas as suítes. A produção continua no Gemini 2.5 Flash.

| Suíte | Flash (pipeline) | Flash-Lite (pipeline) |
|---|---|---|
| Held-out v3 | 30/30 | 24/30 |
| Held-out v2 | 30/30 | 20/30 |
| Held-out v1 | 28/30 | 21/30 |
| Principal | 41/48 | 35/48 |

Na suíte principal, o Flash-Lite devolveu de 11 a 17 respostas por rodada fora do schema mesmo depois do retry do parser, o que em produção deixaria esses anúncios só com o resultado do código. Execuções: principal [43737449716](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737449716), [43737458970](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737458970), [43737467973](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737467973) · v3 [43737534778](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737534778), [43737545091](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737545091), [43737554811](https://github.com/fgm9000/ad-copy-grader/actions/runs/43737554811).

**`deepseek/deepseek-v4-flash`** (US$ 0,0044 por execução completa, segundo o Promptfoo): pipeline 5/16 na suíte principal com o desenho por listas (execução [43721544696](https://github.com/fgm9000/ad-copy-grader/actions/runs/43721544696)). Ele registrava regras aprovadas como issues; não foi medido de novo no desenho atual.
