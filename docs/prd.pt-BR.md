# Documento de Requisitos de Produto (PRD) — Ad Copy Grader API

> 🌐 **Idioma / Language:** [🇺🇸 Read in English](prd.md) | **🇧🇷 Português (pt-BR)**

| Metadado | Valor |
| --- | --- |
| **Produto** | Ad Copy Grader (`ad-copy-grader`) |
| **Versão do Documento** | 1.0 · 12/11/2026 |
| **Status** | Aprovado para Implementação |
| **Licença** | PolyForm Noncommercial License 1.0.0 (Proibido uso comercial) |
| **Stack Principal** | Python 3.12 · FastAPI · Pydantic v2 · `uv` · OpenRouter (`google/gemini-2.5-flash`) · Google Cloud Run · GitHub Pages (HTML5 + Tailwind CLI + Vanilla JS) |
| **Política de Idioma** | **100% Bilíngue (`en` e `pt-BR`)** em Prompts, Regras da API, Interface Web, Exemplos, README, PRD, Arquitetura e ADRs (código-fonte e commits em inglês) |

---

## 1. Visão Geral e Problema (Problem Statement)

Anúncios Responsivos de Pesquisa (**RSA — Responsive Search Ads**) do Google Ads exigem conformidade simultânea com regras estruturais rígidas (quantidade de títulos e descrições, limites exatos de caracteres Unicode `NFC`, pontuação, capitalização e URL final `https://`) e políticas semânticas/regulatórias (coerência de preços e promoções com a Landing Page, presença de Call-to-Action e proibição de promessas absolutas de resultado em setores regulados como saúde e direito).

**Por que abordagens de paradigma único falham:**
1. **Avaliação apenas por LLM (Zero-Shot Prompting):** LLMs erram contagens exatas de caracteres, alucinam violações de tamanho inexistentes e deixam passar duplicidades sutis. Pior: ao sugerir reescritas, frequentemente geram novos títulos que estouram o limite de 30 caracteres.
2. **Avaliação apenas Determinística (Regex / Código Estático):** O código valida limites de caracteres e sintaxe com 100% de precisão, mas é incapaz de julgar se um preço promocional no anúncio contradiz o resumo da Landing Page ou se o texto faz uma promessa clínica indevida (ex.: *"cura 100% garantida"*, *"tratamento sem dor"*).

**A Solução (Tese Arquitetural Central):**
Uma API e playground web interativo de auditoria híbrida construídos sobre o princípio: **"O código tem autoridade sobre o que é verificável; o LLM julga apenas o que é semântico."**
- Um motor determinístico em Python puro avalia todas as regras estruturais e sintáticas (`D01–D11`).
- Um LLM com saída JSON estruturada avalia exclusivamente regras semânticas (`A01–A03`), operando com prompts nativos em inglês (`PROMPT_EN`) ou português (`PROMPT_PT`) conforme o parâmetro `lang`.
- Uma **Camada de Filtros de Autoridade** descarta qualquer alucinação do LLM que tente apontar regras determinísticas (`D*`) ou que acuse falso positivo de preço quando o valor numérico existe literalmente no contexto da Landing Page.
- Toda **sugestão de reescrita** proposta pelo LLM é revalidada contra o motor determinístico antes de ser devolvida ao usuário.

---

## 2. Personas e Casos de Uso

1. **Gestor de Tráfego / Copywriter (Demo Web Interativa — Layout Lado a Lado Bilíngue `EN | PT`):**
   - Alterna entre **Inglês (`EN`)** e **Português (`PT`)** no topo da interface.
   - Visualiza **lado a lado** o **Card da Landing Page de Exemplo** (`lp_context`, `primary_service` e `final_url`) e o **Card do Anúncio RSA** (títulos e descrições com contadores `N/30` e `N/90` em tempo real), tornando imediata a compreensão de como o motor cruza as promessas do anúncio com o conteúdo da página sem fazer scraping externo.
   - Recebe uma **nota de 0.0 a 10.0 (`grade_10`)** (alinhada ao modelo mental do *Quality Score* de 1 a 10 do Google Ads) junto ao `score` de 0 a 100, destaques por campo, selos explícitos de autoridade (`Verificado pelo Código` vs. `Julgado pelo LLM`) e sugestões de substituição já revalidadas.
2. **Engenheiro de Marketing / Automação de Campanhas (Consumidor da API `POST /v1/grade`):**
   - Envia o anúncio RSA com `"lang": "en"` ou `"lang": "pt"` como *Quality Gate* antes de publicar na Google Ads API.
   - Recebe JSON estritamente tipado (`passed`, `score`, `grade_10`, `issues`, `suggestions`) no idioma solicitado, com degradação graciosa caso o provedor de LLM esteja indisponível.

---

## 3. Requisitos Funcionais (Functional Requirements)

### FR-01: Motor de Regras Determinísticas (`D01–D11`) Bilíngue
Executado em Python puro sobre strings normalizadas em Unicode `NFC`, sem chamadas de rede, com mensagens de diagnóstico em `en` e `pt`:

| ID | Regra | Severidade | Critério de Disparo |
| --- | --- | --- | --- |
| `D01` | Limites de quantidade de títulos | `error` | Menos de 3 ou mais de 15 títulos |
| `D02` | Cobertura recomendada de títulos | `warning` | Entre 3 e 14 títulos (abaixo do ideal de 15 posições do RSA) |
| `D03` | Limites de quantidade de descrições | `error` | Menos de 2 ou mais de 4 descrições |
| `D04` | Limite de caracteres de título | `error` | Título com `> 30` caracteres Unicode NFC |
| `D05` | Limite de caracteres de descrição | `error` | Descrição com `> 90` caracteres Unicode NFC |
| `D06` | Limite de caracteres de `path1` / `path2` | `error` | `path1` ou `path2` presente com `> 15` caracteres Unicode NFC |
| `D07` | Relevância do serviço nos títulos iniciais | `warning` | Quando há `>= 5` títulos e menos de 3 dos 5 primeiros citam `primary_service` |
| `D08` | Títulos duplicados | `error` | Títulos idênticos após `strip()` e `casefold()` |
| `D09` | Pontuação repetida ou excessiva | `error` | Sequências repetidas como `!!`, `??` ou `...` |
| `D10` | Uso abusivo de CAIXA ALTA | `warning` | Palavra inteira com `>= 4` letras maiúsculas (exceto lista de siglas permitidas EN/PT) |
| `D11` | URL final HTTPS válida | `error` | `final_url` ausente, malformada ou sem esquema `https://` |

### FR-02: Motor Semântico via LLM (`A01–A03`) com Prompts Nativos `EN` e `PT`
Executado via OpenRouter (`google/gemini-2.5-flash` por padrão) em modo JSON, selecionando `PROMPT_EN` ou `PROMPT_PT` conforme `ad.lang`:

| ID | Regra | Severidade | Critério de Disparo |
| --- | --- | --- | --- |
| `A01` | Preço ou promoção ausente da Landing Page | `error` | Preço numérico, desconto ou oferta concreta no anúncio ausente de `lp_context` |
| `A02` | Ausência de Call-to-Action (CTA) | `warning` | Nenhuma descrição contém chamada para ação clara |
| `A03` | Promessa absoluta ou garantia de resultado | `warning` | Garantia indevida ou promessa clínica/regulada (ex.: *"garantido"*, *"100%"*, *"cura"*, *"sem dor"* / *"guaranteed"*, *"cure"*, *"painless"*) |

### FR-03: Output Parser Resiliente com Loop de Auto-Correção
- Extrai o JSON mesmo quando cercado por blocos Markdown (```` ```json ````).
- Valida contra o schema Pydantic v2 `LlmReview` e exige que `rules_checked` contenha `["A01", "A02", "A03"]`.
- Em caso de falha de validação, executa **no máximo 1 nova tentativa (retry)** anexando os detalhes estruturados do `ValidationError` do Pydantic ao prompt (no idioma correspondente). Lança `LlmOutputError` se a segunda tentativa falhar.

### FR-04: Filtros de Autoridade do Código
- Descarta qualquer issue retornada pelo LLM cujo `rule_id` comece com `D`.
- Descarta issues `A01` quando o valor numérico ou preço citado no anúncio aparece literalmente dentro de `lp_context` (prevenção determinística de falso positivo).
- Descarta qualquer issue cujo `location.index` esteja fora dos limites reais das listas enviadas.

### FR-05: Revalidação Determinística de Reescritas (`rewrite.py`)
- Toda sugestão de reescrita gerada pelo LLM é submetida às regras `D04`, `D05`, `D08`, `D09` e `D10`.
- Sugestões que violem qualquer regra determinística são descartadas antes de chegar ao usuário e contabilizadas em `discarded_suggestions_count`.

### FR-06: Sistema de Pontuação (0–10 e 0–100) e Critério de Aprovação
- **Nota Base 100 (`score`):** `max(0, 100 - 15 * errors - 5 * warnings)`
- **Nota Escala 0 a 10 (`grade_10`):** `round(score / 10, 1)` (ex.: `8.5 / 10.0`, espelhando a escala de 0 a 10 do Google Ads).
- **Flag de Aprovação (`passed`):** `errors == 0`.

### FR-07: Degradação Graciosa (Graceful Degradation)
- Se o OpenRouter falhar (timeout, HTTP 5xx ou falha dupla de schema), a API retorna todas as issues determinísticas (`D01–D11`) com `model: null` e `degraded_reason` no idioma solicitado (`en` ou `pt`), garantindo que a demo nunca exiba tela vazia.

---

## 4. Requisitos Não-Funcionais (NFRs)

| Categoria | Requisito | Mecanismo de Garantia |
| --- | --- | --- |
| **FinOps / Teto de Custo** | Gasto total nuvem + LLM `< US$ 5,00 / mês` | Cloud Run `min-instances=0`, `max-instances=1`, janela deslizante em memória por IP (`5 req/min`), teto global diário (`200 req/dia`) e cenários offline pré-computados (`examples.json` em EN e PT). |
| **Latência** | P95 `< 4,0s` (LLM ao vivo) e `< 50ms` (determinístico / `FakeModel`) | `httpx.AsyncClient` assíncrono (timeout 20s), validação em Rust via Pydantic v2 e `google/gemini-2.5-flash`. |
| **Segurança** | Zero segredos estáticos em código/CI; resistência a *Prompt Injection* | Deploy keyless via GCP Workload Identity Federation (OIDC), Google Secret Manager, `gitleaks` em pre-commit + CI, isolamento de input não-confiável no system prompt e CORS restrito. |
| **Qualidade de Código** | Cobertura `>= 90%`, `mypy --strict` (0 erros), catraca (*ratchet*) ativa | Gate de CI (`quality_check.py`) bloqueando regressões ou novas supressões (`# noqa`, `# type: ignore`). |
| **Qualidade de IA (Evals)** | Taxa de aprovação `>= 90%` na coluna `pipeline` no Promptfoo | Suíte comparativa de 3 colunas (`raw` vs. `pipeline` vs. `degraded`) cobrindo casos em inglês e português, incluindo tentativas de prompt injection. |
| **Acessibilidade & UI** | Lighthouse Acessibilidade `>= 90` e Performance `>= 95` | HTML5 semântico + CSS estático compilado via `@tailwindcss/cli` + Vanilla JS com toggle instantâneo `EN | PT`. |

---

## 5. Fora de Escopo (Non-Goals)

- **Sem banco de dados ou persistência de anúncios:** Serviço 100% *stateless* para minimizar superfície de ataque e manter custo ocioso zero.
- **Sem autenticação de usuário final:** Demo pública para avaliação imediata de portfólio, protegida por rate-limit por IP e teto diário.
- **Sem scraping ao vivo de `final_url`:** O contexto da Landing Page é enviado explicitamente via `lp_context` (e visualizado lado a lado na UI) para evitar riscos de SSRF e instabilidade de scrapers.

---

## 6. Governança de Engenharia e Critérios de Release

1. **Conventional Commits e Documentação Bilíngue:** Commits, nomes de branches e identificadores de código seguem padrão em inglês (Conventional Commits); toda a documentação arquitetural, PRD, ADRs e README é mantida em par bilíngue (`en` e `pt-BR`).
2. **Catraca de Qualidade Automatizada e Gates de CI:** Toda alteração deve passar por `ruff` (lint + format + regras `S` / `flake8-bandit`), `mypy --strict`, `pytest` (cobertura `>= 90%`), `semgrep` (`p/owasp-top-ten`, `p/python`, `p/fastapi`), `codeql` (análise semântica de fluxo de dados do GitHub CodeQL para Python), `gitleaks`, suíte de 3 colunas do Promptfoo e catraca de regressão zero (`quality_check.py`) antes do merge na `main`.
