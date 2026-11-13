# Stage 1: Build virtual environment with uv
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock LICENSE README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev --no-editable

# Stage 2: Minimal non-root runtime image
FROM python:3.12-slim AS runtime

RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /sbin/nologin --no-create-home appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn ad_copy_grader.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
