# ADR-002: Pipeline Híbrido com Autoridade Determinística sobre o LLM

> **[🇺🇸 English](002-hybrid-deterministic-llm-authority.md) | [🇧🇷 Português](002-hybrid-deterministic-llm-authority.pt-BR.md)**

- **Status:** Aceito
- **Data:** 2026-11-12

## Contexto

Anúncios Responsivos de Pesquisa (RSAs) do Google Ads precisam respeitar tanto **regras mecânicas exatas** (máx. 30 caracteres por título, máx. 90 por descrição, máx. 15 por path, esquema `https://`, ausência de duplicatas, proibição de pontuação repetida como `!!`, `??` ou `...`) quanto **regras semânticas** (ausência de preços/ofertas não confirmados na Landing Page, presença de CTA claro e ausência de garantias clínicas/financeiras absolutas).

Modelos de linguagem erram contagens de caracteres devido à tokenização por subpalavras, ocasionalmente alucinam regras determinísticas e frequentemente sugerem reescritas que estouram o limite de 30 caracteres.

## Alternativas Consideradas

1. **Auditoria 100% via LLM:**
   - *Prós:* Prompt único, menos código de aplicação.
   - *Contras:* Alta taxa de falsos positivos em limites de caracteres (`D04`, `D05`, `D06`), pontuação não-determinística e sugestões de reescrita inválidas para upload no Google Ads.
2. **Auditoria 100% via Regex / Código:**
   - *Prós:* Rápida, custo zero de tokens e 100% determinística.
   - *Contras:* Incapaz de cruzar semanticamente ofertas e condições entre o anúncio e o texto livre da Landing Page (`A01`) ou julgar nuances de CTA (`A02`).
3. **Pipeline Híbrido com Filtro de Autoridade do Código e Validador de Reescrita (Escolhida):**
   - *Prós:* O código Python (`rules.py`) é a única autoridade para `D01–D11`. O LLM avalia apenas `A01–A03`. O filtro de autoridade no servidor (`filter_llm_issues` em `pipeline.py`) remove qualquer regra `D*` emitida pelo LLM e bloqueia falsos positivos de `A01` quando o preço consta no `lp_context`. Por fim, `validate_suggestions` (`rewrite.py`) aplica `D04/D05/D08/D09/D10` em cada sugestão de reescrita antes de devolvê-la.

## Decisão

Implementar um **Pipeline Híbrido Determinístico + LLM** com separação estrita de autoridade:
1. Regras de código (`D01–D11`) rodam primeiro sobre strings normalizadas em NFC.
2. O LLM avalia regras semânticas (`A01–A03`) com prompts bilíngues nativos (`PROMPT_EN` / `PROMPT_PT`).
3. O **Filtro de Autoridade do Código** descarta invasões em `D*`, índices fora de faixa e falsos positivos de `A01` confirmados na LP.
4. O **Validador de Reescrita** descarta sugestões do LLM que violem limites determinísticos.
5. Em falha dupla do LLM, a API degrada de forma elegante para as regras determinísticas (`D01–D11`).

## Consequências

- **Positivas:** Zero alucinações de contagem de caracteres, sugestões de reescrita garantidamente válidas e resiliência contra indisponibilidade do provedor de LLM.
- **Negativas / Trade-offs:** Exige manter regras determinísticas e prompts sincronizados, validados continuamente pela suíte de 3 colunas no Promptfoo.

## Adendo (15/11/2026): A02 passa para a autoridade do código

As primeiras execuções reais do Promptfoo mostraram os modelos inventando A02 em anúncios com CTA clara ("Agende sua avaliação hoje") e omitindo A02 em anúncios sem nenhuma CTA, em rodadas diferentes do mesmo caso. Detectar CTA é uma busca de verbo de ação que o código faz com exatidão; por isso o A02 segue o princípio deste ADR: **o código decide, o LLM sugere**.

- `pipeline.check_a02` aponta A02 (`source: "code"`) quando nenhuma descrição contém verbo de ação em EN/PT (regex com limite de palavra); issues A02 do LLM são sempre descartados.
- O código da regra continua `A02` (contrato da API inalterado) e o LLM continua propondo reescritas com CTA, validadas por `rewrite.py`.
- O A02 também vale no modo degradado, já que não depende mais do modelo.
- Trade-off: uma CTA escrita sem nenhum verbo da lista passa despercebida; a lista de verbos é o ponto de extensão.

## Adendo (15/11/2026): veto do código no A03

O A03 continua decidido pelo LLM, mas os evals reais mostraram o modelo apontando frases suaves de benefício em PT ("Recupere Seu Sorriso", "cirurgia guiada de alta precisão") como garantia absoluta. Uma violação de A03 exige palavra de promessa absoluta; por isso `filter_llm_issues` descarta o A03 cujo item localizado não contém nenhuma (garantia, 100%, cura, sem dor, imediato, permanente, definitivo, risco zero, certeza; EN/PT). A03 sem localização é mantido. Trade-off: uma promessa absoluta escrita sem nenhuma palavra da lista passa despercebida; a lista é o ponto de extensão. Resultado: pipeline 48/48 em três rodadas reais (`docs/eval-results.pt-BR.md`).
