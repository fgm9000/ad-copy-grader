# ADR-001: Python 3.12, FastAPI, Pydantic v2, and `uv`

> **[🇺🇸 English](001-python-fastapi-pydantic-v2.md) | [🇧🇷 Português](001-python-fastapi-pydantic-v2.pt-BR.md)**

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

We need a backend stack for `ad-copy-grader` that provides strict request/response schema validation, structured LLM output parsing with self-correction retries, low cold-start latency on serverless containers, and reproducible dependency locking.

## Alternatives Considered

1. **TypeScript / Deno or Node.js (Hono / Express + Zod):**
   - *Pros:* Fast startup, familiar ecosystem for web applications.
   - *Cons:* Less alignment with standard Python AI/LLM evaluation and data engineering ecosystems (`pytest`, `pydantic`, `mypy --strict`).
2. **Python + Django / Django Ninja:**
   - *Pros:* Batteries-included ORM and admin.
   - *Cons:* Heavyweight for a 100% stateless microservice with no relational database.
3. **Python 3.12 + FastAPI + Pydantic v2 + `uv` (Selected):**
   - *Pros:* Pydantic v2 (`pydantic-core` in Rust) delivers fast JSON validation and detailed field-level error messages that can be fed directly back into LLM self-correction retries (`parser.py`). FastAPI automatically generates OpenAPI 3.1 schemas. `uv` provides deterministic lockfiles (`uv.lock`) and sub-second virtual environment builds in CI and Docker multi-stage builds.

## Decision

Adopt **Python 3.12**, **FastAPI**, **Pydantic v2**, and **`uv`**, enforced by **`ruff`** (`E,F,I,B,UP,S,N,SIM`) and **`mypy --strict`**.

## Consequences

- **Positive:** Single source of truth for HTTP contracts (`AdInput`, `GradeResult`), LLM parser validation (`LlmReview`), and OpenAPI documentation.
- **Positive:** Fast container builds (`uv sync --frozen --no-dev`) and strict static typing with zero `# type: ignore` suppressions.
- **Negative / Trade-off:** Requires Python 3.12+ in local development and CI environments.
