# Cloud Run Deployment & CI/CD Troubleshooting Runbook

🇧🇷 [Leia em Português](deployment-runbook.pt-BR.md) | 🇺🇸 **English**

This runbook documents the end-to-end setup of the Google Cloud Run infrastructure, Keyless GitHub Actions OIDC authentication (Workload Identity Federation), least-privilege IAM roles, Secret Manager bindings, and a post-mortem of every infrastructure and CI/CD issue encountered and resolved during initial deployment.

---

## 1. GCP Architecture Decision: Single Portfolio Project, Multiple Cloud Run Services

Rather than provisioning a separate GCP project for every demo repository, this service is deployed inside a consolidated portfolio project (`fgm9000-portfolio`, Region: `us-central1`):

- **Cost & Quota Consolidation:** All Cloud Run services configured with `--min-instances=0` scale to zero when idle (`$0.00` baseline cost) while sharing the regional free tier (2 million requests/month in `us-central1`) and centralized billing alerts.
- **Per-Service Isolation:** Each project runs as an isolated Cloud Run service with its own HTTPS endpoint, its own Artifact Registry repository, and its own dedicated least-privilege Runtime Service Account.
- **Shared OIDC Federation Pool:** A single Workload Identity Pool (`github-pool`) and OIDC Provider (`github-provider`) authenticate GitHub Actions workflows across repositories via repository-scoped IAM bindings—zero long-lived service account JSON keys exist anywhere.

---

## 2. Step-by-Step Provisioning via `gcloud` and `gh` CLI

### 2.1 Project Creation & Billing Link
```bash
gcloud projects create fgm9000-portfolio --name="Portfolio"
gcloud billing projects link fgm9000-portfolio --billing-account=<BILLING_ACCOUNT_ID>
```

### 2.2 API Enablement
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  --project=fgm9000-portfolio
```

### 2.3 Artifact Registry Repository
```bash
gcloud artifacts repositories create ad-copy-grader \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker images for ad-copy-grader" \
  --project=fgm9000-portfolio
```

### 2.4 Secret Manager Configuration
Even when running the public demo with `FAKE_MODEL=true` (zero external LLM spend), the container mounts `OPENROUTER_API_KEY` from Google Cloud Secret Manager so the production secret-injection path is continuously exercised:
```bash
printf "sk-or-v1-placeholder-fake-model-enabled" | gcloud secrets create openrouter-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=fgm9000-portfolio
```

### 2.5 Least-Privilege Service Accounts (Runtime vs. Deployer Separation)
Two distinct service accounts enforce separation of duties between the running container and the CI/CD deployment pipeline:

1. **Runtime SA (`ad-copy-grader-runtime`):** Attached to the Cloud Run revision. Granted **only** `roles/secretmanager.secretAccessor` on the `openrouter-api-key` secret.
2. **Deployer SA (`ad-copy-grader-deployer`):** Assumed by GitHub Actions via OIDC. Granted `roles/run.admin`, `roles/artifactregistry.writer`, and `roles/iam.serviceAccountUser` on the Runtime SA.

```bash
gcloud iam service-accounts create ad-copy-grader-runtime \
  --display-name="ad-copy-grader Cloud Run runtime SA" \
  --project=fgm9000-portfolio

gcloud iam service-accounts create ad-copy-grader-deployer \
  --display-name="ad-copy-grader GitHub Actions deployer SA" \
  --project=fgm9000-portfolio

gcloud secrets add-iam-policy-binding openrouter-api-key \
  --member="serviceAccount:ad-copy-grader-runtime@fgm9000-portfolio.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=fgm9000-portfolio

gcloud projects add-iam-policy-binding fgm9000-portfolio \
  --member="serviceAccount:ad-copy-grader-deployer@fgm9000-portfolio.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding fgm9000-portfolio \
  --member="serviceAccount:ad-copy-grader-deployer@fgm9000-portfolio.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud iam service-accounts add-iam-policy-binding \
  ad-copy-grader-runtime@fgm9000-portfolio.iam.gserviceaccount.com \
  --member="serviceAccount:ad-copy-grader-deployer@fgm9000-portfolio.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --project=fgm9000-portfolio
```

### 2.6 Keyless GitHub Actions OIDC (Workload Identity Federation)
```bash
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --project=fgm9000-portfolio

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository_owner == 'fgm9000' && assertion.repository == 'fgm9000/ad-copy-grader' && assertion.ref == 'refs/heads/main'" \
  --project=fgm9000-portfolio

gcloud iam service-accounts add-iam-policy-binding \
  ad-copy-grader-deployer@fgm9000-portfolio.iam.gserviceaccount.com \
  --project=fgm9000-portfolio \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/316736391681/locations/global/workloadIdentityPools/github-pool/attribute.repository/fgm9000/ad-copy-grader"
```

### 2.7 GitHub Actions Repository Variables
```bash
gh variable set GCP_PROJECT_ID --body "fgm9000-portfolio" -R fgm9000/ad-copy-grader
gh variable set GCP_WIF_PROVIDER --body "projects/316736391681/locations/global/workloadIdentityPools/github-pool/providers/github-provider" -R fgm9000/ad-copy-grader
gh variable set GCP_SERVICE_ACCOUNT --body "ad-copy-grader-deployer@fgm9000-portfolio.iam.gserviceaccount.com" -R fgm9000/ad-copy-grader
gh variable set FAKE_MODEL --body "true" -R fgm9000/ad-copy-grader
gh variable set ALLOWED_ORIGINS --body "https://fgm9000.github.io" -R fgm9000/ad-copy-grader
```

---

## 3. Troubleshooting & Incident Post-Mortems

Every issue encountered during initial CI/CD activation and Cloud Run deployment is documented below along with its root cause and permanent fix.

### Issue 1 — Quality Ratchet Coverage Rounding Discrepancy Across OS (`99.1%` Windows vs `99.0%` Linux)
- **Symptom:** The first GitHub Actions CI run failed on `scripts/quality_check.py` with:
  `coverage_percent: baseline 99.1 -> current 99.0 [WORSENED]`.
- **Root Cause:** 7 defensive lines in `src/ad_copy_grader/llm.py` (`_extract_ad_payload` and `_price_digits_in_lp`) were uncovered, yielding `731 / 738 = 99.051%` coverage. Local Windows rounded to `99.1%`, while Linux (`ubuntu-latest`) evaluated to `99.0%`.
- **Resolution:** Added `test_llm_helper_edge_cases` in `tests/test_evals.py` to cover every remaining defensive branch in `llm.py`, bringing line coverage to **`100.0%` (`738/738` statements, `0 missed`)** across all operating systems.

### Issue 2 — Promptfoo SQLite Foreign Key Crash on Ephemeral Runners (`SQLITE_CONSTRAINT_FOREIGNKEY`)
- **Symptom:** `npx promptfoo@0.109.0 eval -c evals/promptfooconfig.yaml --no-cache` passed all 48 assertions (`100%`) in CI, but exited with code 1 on process teardown due to `SqliteError: FOREIGN KEY constraint failed` when writing summary rows to `~/.promptfoo/promptfoo.db`.
- **Root Cause:** Promptfoo attempts to persist evaluation metadata into a local SQLite database on shutdown, which can hit an initialization race on fresh ephemeral runners when `--no-cache` is active.
- **Resolution:** Added `--no-write` (`npx --yes promptfoo@0.109.0 eval -c evals/promptfooconfig.yaml --no-cache --no-write`) in `.github/workflows/ci.yml` so results are written exclusively to the JSON artifact (`--output eval-results-fake.json`).

### Issue 3 — `gitleaks-action@v2` Failing on Root-Commit Range (`unknown revision ^`)
- **Symptom:** On the initial push to `main`, `gitleaks/gitleaks-action@v2` failed with `fatal: ambiguous argument '4cd32f5^..5e686a0': unknown revision`.
- **Root Cause:** `4cd32f5` is the repository's root commit, so `4cd32f5^` (its parent reference) does not exist in Git's commit graph.
- **Resolution:** Replaced the action wrapper in `.github/workflows/ci.yml` with the official container `docker://zricethezav/gitleaks:v8.24.3` executing `git config --global --add safe.directory "$GITHUB_WORKSPACE" && gitleaks detect --source . --verbose --redact`.

### Issue 4 — Artifact Registry `PERMISSION_DENIED` Immediately After Enabling API
- **Symptom:** Running `gcloud artifacts repositories create` within 2 seconds of `gcloud services enable artifactregistry.googleapis.com` on a brand-new GCP project returned `PERMISSION_DENIED`.
- **Root Cause:** Service Usage and IAM policy propagation across regional endpoints takes 10–20 seconds on newly created GCP projects.
- **Resolution:** Waited ~15 seconds for Service Usage propagation and re-ran the repository creation command, which succeeded cleanly.

### Issue 5 — Multi-Stage Docker Build Failing on `hatchling` Metadata (`License file does not exist: LICENSE`)
- **Symptom:** In `.github/workflows/deploy.yml`, `docker build` failed during `RUN uv sync --frozen --no-dev --no-editable` with `OSError: License file does not exist: LICENSE`.
- **Root Cause:** `pyproject.toml` declares `readme = "README.md"` and `license = { file = "LICENSE" }`. Building the non-editable wheel in the builder stage requires both files, but `.dockerignore` excluded `*.md` and the `Dockerfile` only copied `pyproject.toml uv.lock`.
- **Resolution:** Added `!README.md` to `.dockerignore` and updated `Dockerfile` to `COPY pyproject.toml uv.lock LICENSE README.md ./`.

### Issue 6 — Cloud Run Startup Crash on `ALLOWED_ORIGINS` (`pydantic-settings` `JSONDecodeError`)
- **Symptom:** The first Cloud Run revision exited with code 1 during startup. Cloud Logging reported:
  `pydantic_settings.exceptions.SettingsError: error parsing value for field "allowed_origins" from source "EnvSettingsSource" -> JSONDecodeError`.
- **Root Cause:** In `pydantic-settings` v2, complex fields typed as `list[str]` are pre-decoded with `json.loads()` by `EnvSettingsSource` *before* `"before"` field validators execute. Passing a plain URL (`ALLOWED_ORIGINS=https://fgm9000.github.io`) therefore failed JSON decoding before `parse_allowed_origins` could split it.
- **Resolution:** Annotated `allowed_origins: Annotated[list[str], NoDecode]` in `src/ad_copy_grader/settings.py` so `pydantic-settings` passes the raw environment string directly into `@field_validator("allowed_origins", mode="before")`.

### Issue 7 — Google Frontend (GFE) Reserved `/healthz` Path (`404 Not Found`) & Root URL Redirect (`GET /`)
- **Symptom:**
  1. External requests to `https://ad-copy-grader-*.run.app/healthz` (including the GitHub Actions post-deploy smoke test) received a Google-branded `Error 404 (Not Found)!!1` HTML page without any entry appearing in Cloud Run's `run.googleapis.com/requests` logs.
  2. Clicking the root Cloud Run URL (`https://ad-copy-grader-316736391681.us-central1.run.app/`) in a browser returned FastAPI's JSON `404` (`{"detail":"Not Found"}`).
- **Root Cause:**
  1. **GFE Reserved `*z` Paths:** On `*.run.app` domains, Google Frontend (GFE) reserves paths ending in `z` (`/healthz`, `/statusz`, `/varz`) for internal Google infrastructure and blocks external HTTP requests at the edge before they ever reach the Cloud Run container.
  2. **Missing Root Handler:** FastAPI only registered `/healthz`, `/v1/grade`, and `/docs`, with no route for `GET /`.
- **Resolution:**
  1. Added `@app.get("/health")` alongside `@app.get("/healthz", include_in_schema=False)` in `src/ad_copy_grader/api.py` and pointed the external smoke test in `.github/workflows/deploy.yml` to `/health` (`curl --fail ... "${SERVICE_URL}/health"`).
  2. Added `@app.get("/", include_in_schema=False)` returning `RedirectResponse(url="/docs")` so visiting the root Cloud Run URL in a browser redirects (`HTTP 307`) directly to the interactive Swagger UI.
