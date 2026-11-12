# ADR-001: Python 3.12, FastAPI, Pydantic v2 e `uv`

> **[🇺🇸 English](001-python-fastapi-pydantic-v2.md) | [🇧🇷 Português](001-python-fastapi-pydantic-v2.pt-BR.md)**

- **Status:** Aceito
- **Data:** 2026-11-12

## Contexto

Precisávamos de uma stack de backend para o `ad-copy-grader` que oferecesse validação estrita de contratos de entrada/saída, *parsing* estruturado de respostas de LLM com *retry* de autocorreção, baixo *cold start* em containers serverless e travamento reprodutível de dependências.

## Alternativas Consideradas

1. **TypeScript / Deno ou Node.js (Hono / Express + Zod):**
   - *Prós:* Inicialização rápida e ecossistema comum para aplicações web.
   - *Contras:* Menor aderência ao ecossistema padrão de engenharia de IA/LLM em Python (`pytest`, `pydantic`, `mypy --strict`).
2. **Python + Django / Django Ninja:**
   - *Prós:* ORM e painel administrativo integrados.
   - *Contras:* Sobrecarga desnecessária para um microsserviço 100% *stateless* sem banco de dados relacional.
3. **Python 3.12 + FastAPI + Pydantic v2 + `uv` (Escolhida):**
   - *Prós:* O Pydantic v2 (`pydantic-core` em Rust) entrega validação JSON rápida e mensagens de erro detalhadas por campo que alimentam diretamente o *retry* de autocorreção do LLM (`parser.py`). O FastAPI gera documentação OpenAPI 3.1 automaticamente, e o `uv` garante lockfile determinístico (`uv.lock`) e builds rápidos em CI e Docker multi-stage.

## Decisão

Adotar **Python 3.12**, **FastAPI**, **Pydantic v2** e **`uv`**, com verificação estrita via **`ruff`** (`E,F,I,B,UP,S,N,SIM`) e **`mypy --strict`**.

## Consequências

- **Positivas:** Fonte única de verdade para contratos HTTP (`AdInput`, `GradeResult`), validação de saída do LLM (`LlmReview`) e documentação OpenAPI.
- **Positivas:** Builds de container rápidos (`uv sync --frozen --no-dev`) e tipagem estática estrita com zero supressões `# type: ignore`.
- **Negativas / Trade-offs:** Exige Python 3.12+ no ambiente local e na CI.
