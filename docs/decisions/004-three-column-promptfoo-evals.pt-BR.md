# ADR-004: Avaliação em 3 Colunas com Promptfoo

> **[🇺🇸 English](004-three-column-promptfoo-evals.md) | [🇧🇷 Português](004-three-column-promptfoo-evals.pt-BR.md)**

- **Status:** Aceito
- **Data:** 2026-11-12

## Contexto

Em um sistema de IA híbrido onde o código determinístico filtra e complementa a saída do LLM, avaliar apenas o resultado final do pipeline esconde regressões do prompt que estejam sendo mascaradas pelos filtros do servidor. Por outro lado, avaliar apenas a saída crua do LLM ignora o valor protetor das regras determinísticas e do filtro de autoridade.

## Alternativas Consideradas

1. **Avaliação Ponta a Ponta de Coluna Única:**
   - *Prós:* Configuração simples.
   - *Contras:* Não isola a contribuição do guardrail do prompt em relação ao Filtro de Autoridade do Código no servidor.
2. **Apenas Testes Unitários no Pytest com Respostas Mockadas:**
   - *Prós:* Rápido e determinístico na CI.
   - *Contras:* Não permite comparar trocas de modelos reais (ex.: `google/gemini-2.5-flash` vs. outros modelos no OpenRouter) com rastreamento de tokens/custo e visualização matricial lado a lado.
3. **Avaliação Promptfoo em 3 Colunas (`raw`, `pipeline`, `degraded`) com Cache Compartilhado (Escolhida):**
   - *Prós:* Compara três colunas simultaneamente em 16 cenários bilíngues (`en` e `pt`) de mutação única:
     - **Coluna 1 (`raw`):** Saída crua do LLM antes das regras de código e filtros do servidor.
     - **Coluna 2 (`pipeline`):** Saída híbrida completa de produção (`D01–D11` + `A01–A03` + Filtro de Autoridade).
     - **Coluna 3 (`degraded`):** Ablação real de `PROMPT_EN` / `PROMPT_PT` removendo programaticamente a instrução que proíbe o modelo de reportar regras `D*` (`build_degraded_system_prompt`), comprovando o papel do guardrail.
   - *Eficiência:* As colunas 1 (`raw`) e 2 (`pipeline`) compartilham uma única chamada `grade()` por caso via cache SHA-256 em `evals/provider.py`, reduzindo o custo de tokens em 33%.

## Decisão

Adotar uma **arquitetura de avaliação de 3 colunas no Promptfoo** em `evals/`, suportando tanto execução determinística offline na CI (`FAKE_MODEL=1` em `.github/workflows/ci.yml`) quanto *benchmark* sob demanda com modelo real (`.github/workflows/eval-live.yml`).

## Consequências

- **Positivas:** Demonstra quantitativamente como cada camada (guardrail de prompt + filtro de autoridade do servidor + motor determinístico) contribui para a precisão em inglês e português.
- **Negativas / Trade-offs:** Exige Node.js (`npx promptfoo@0.109.0`) no job `eval-fake` da CI junto com o `uv`.
