# ADR-003: Single-Instance Cloud Run (`max-instances=1`) & Keyless OIDC WIF

> **[🇺🇸 English](003-cloud-run-single-instance-wif.md) | [🇧🇷 Português](003-cloud-run-single-instance-wif.pt-BR.md)**

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

As a public portfolio microservice that calls a paid LLM API (OpenRouter), the deployment architecture must satisfy three constraints:
1. **Zero idle cost** when no visitors are testing the service.
2. **Hard cost ceiling** against automated abuse or traffic spikes without introducing paid stateful infrastructure (such as managed Redis / Cloud Memorystore).
3. **Zero long-lived cloud credentials** stored in GitHub Secrets.

## Alternatives Considered

1. **Multi-Instance Cloud Run + Managed Redis (Upstash / Memorystore) for Rate Limiting:**
   - *Pros:* Horizontally scalable distributed rate limiting.
   - *Cons:* Adds external network hops, configuration overhead, and potential monthly cost for a portfolio service whose traffic easily fits within a single async Python process.
2. **Static Service Account JSON Key in GitHub Secrets:**
   - *Pros:* Quick initial setup.
   - *Cons:* Violates modern cloud security best practices; long-lived keys can be leaked and require manual rotation.
3. **Cloud Run (`min-instances=0`, `max-instances=1`, `concurrency=10`) + In-Memory Rate Limiter + Workload Identity Federation (Selected):**
   - *Pros:* `min-instances=0` scales to zero when idle (`$0.00/month`). `max-instances=1` caps both compute spend and ensures that the in-memory `StrictRateLimiter` (`5 req/min/IP` and `200 req/day` UTC cap in `limits.py`) is globally authoritative across all live requests without needing Redis. Workload Identity Federation (OIDC) authenticates GitHub Actions to GCP using short-lived tokens restricted to `refs/heads/main`.

## Decision

Deploy to **Google Cloud Run** (`us-central1`) with `--min-instances=0 --max-instances=1 --concurrency=10`, store `OPENROUTER_API_KEY` in **Google Secret Manager**, enforce rate limits in memory (`limits.py`), and authenticate CI/CD via keyless **Workload Identity Federation**.

## Consequences

- **Positive:** Zero idle cost, hard daily LLM spend protection, and zero static GCP keys in GitHub.
- **Negative / Trade-off:** A cold start after inactivity resets the in-memory daily counter (acceptable for low-cost demo protection; a production multi-tenant deployment would swap `StrictRateLimiter` for Redis while keeping the same interface).
