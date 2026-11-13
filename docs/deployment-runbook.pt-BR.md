# Runbook de Deploy no Cloud Run e Troubleshooting de CI/CD

🇧🇷 **Português** | 🇺🇸 [Read in English](deployment-runbook.md)

Este runbook documenta a configuração ponta a ponta da infraestrutura no Google Cloud Run, autenticação OIDC sem chaves estáticas no GitHub Actions (Workload Identity Federation), papéis IAM de menor privilégio, integração com o Secret Manager e o post-mortem técnico de todos os problemas enfrentados e resolvidos durante o deploy inicial.

---

## 1. Decisão de Arquitetura no GCP: Projeto Único de Portfólio com Múltiplos Serviços Cloud Run

Em vez de criar um projeto GCP isolado para cada repositório de demonstração, este serviço é publicado dentro de um projeto consolidado de portfólio (`fgm9000-portfolio`, Região: `us-central1`):

- **Consolidação de Custos e Free Tier:** Todos os serviços Cloud Run configurados com `--min-instances=0` escalam a zero quando ociosos (custo base `R$ 0,00`), compartilhando a franquia gratuita regional (2 milhões de requisições/mês em `us-central1`) e alertas centralizados de orçamento.
- **Isolamento por Serviço:** Cada aplicação roda como um serviço Cloud Run independente com seu próprio endpoint HTTPS, seu próprio repositório no Artifact Registry e sua própria Service Account dedicada de runtime com privilégio mínimo.
- **Pool Único de Federação OIDC:** Um único Workload Identity Pool (`github-pool`) e Provider OIDC (`github-provider`) autenticam workflows do GitHub Actions via bindings IAM restritos por repositório — nenhuma chave JSON de longa duração existe.

---

## 2. Provisionamento Passo a Passo via CLI (`gcloud` e `gh`)

### 2.1 Criação do Projeto e Vinculação de Faturamento
```bash
gcloud projects create fgm9000-portfolio --name="Portfolio"
gcloud billing projects link fgm9000-portfolio --billing-account=<BILLING_ACCOUNT_ID>
```

### 2.2 Habilitação das APIs
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  --project=fgm9000-portfolio
```

### 2.3 Repositório no Artifact Registry
```bash
gcloud artifacts repositories create ad-copy-grader \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker images for ad-copy-grader" \
  --project=fgm9000-portfolio
```

### 2.4 Configuração do Secret Manager
Mesmo executando a demonstração pública com `FAKE_MODEL=true` (custo zero de inferência externa), o container monta `OPENROUTER_API_KEY` a partir do Google Cloud Secret Manager para exercitar continuamente a injeção de segredos de produção:
```bash
printf "sk-or-v1-placeholder-fake-model-enabled" | gcloud secrets create openrouter-api-key \
  --data-file=- \
  --replication-policy=automatic \
  --project=fgm9000-portfolio
```

### 2.5 Service Accounts de Menor Privilégio (Separação entre Runtime e Deployer)
Duas Service Accounts distintas garantem separação de responsabilidades entre o container em execução e o pipeline de CI/CD:

1. **Runtime SA (`ad-copy-grader-runtime`):** Anexada à revisão do Cloud Run. Possui **apenas** `roles/secretmanager.secretAccessor` no segredo `openrouter-api-key`.
2. **Deployer SA (`ad-copy-grader-deployer`):** Assumida pelo GitHub Actions via OIDC. Possui `roles/run.admin`, `roles/artifactregistry.writer` e `roles/iam.serviceAccountUser` sobre a Runtime SA.

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

### 2.6 Autenticação Keyless no GitHub Actions via OIDC (Workload Identity Federation)
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

### 2.7 Variáveis de Repositório no GitHub Actions
```bash
gh variable set GCP_PROJECT_ID --body "fgm9000-portfolio" -R fgm9000/ad-copy-grader
gh variable set GCP_WIF_PROVIDER --body "projects/316736391681/locations/global/workloadIdentityPools/github-pool/providers/github-provider" -R fgm9000/ad-copy-grader
gh variable set GCP_SERVICE_ACCOUNT --body "ad-copy-grader-deployer@fgm9000-portfolio.iam.gserviceaccount.com" -R fgm9000/ad-copy-grader
gh variable set FAKE_MODEL --body "true" -R fgm9000/ad-copy-grader
gh variable set ALLOWED_ORIGINS --body "https://fgm9000.github.io" -R fgm9000/ad-copy-grader
```

---

## 3. Troubleshooting e Post-Mortem dos Problemas Enfrentados

Todos os problemas técnicos encontrados durante a ativação inicial do CI/CD e deploy no Cloud Run estão documentados abaixo com sua causa-raiz e correção definitiva.

### Problema 1 — Divergência de Arredondamento de Cobertura entre Sistemas Operacionais (`99.1%` Windows vs `99.0%` Linux)
- **Sintoma:** A primeira execução do CI no GitHub Actions falhou no `scripts/quality_check.py` com:
  `coverage_percent: baseline 99.1 -> current 99.0 [WORSENED]`.
- **Causa-Raiz:** 7 linhas defensivas em `src/ad_copy_grader/llm.py` (`_extract_ad_payload` e `_price_digits_in_lp`) não estavam cobertas, resultando em `731 / 738 = 99.051%` de cobertura. No Windows local o valor arredondou para `99.1%`, enquanto no Linux (`ubuntu-latest`) avaliou para `99.0%`.
- **Solução:** Adicionado `test_llm_helper_edge_cases` em `tests/test_evals.py` cobrindo todas as branches defensivas de `llm.py`, elevando a cobertura de linhas para **`100.0%` (`738/738` statements, `0 missed`)** em qualquer sistema operacional.

### Problema 2 — Falha de Chave Estrangeira SQLite no Promptfoo em Runners Efêmeros (`SQLITE_CONSTRAINT_FOREIGNKEY`)
- **Sintoma:** `npx promptfoo@0.109.0 eval -c evals/promptfooconfig.yaml --no-cache` aprovou todas as 48 asserções (`100%`) no CI, mas encerrou com código 1 devido a `SqliteError: FOREIGN KEY constraint failed` ao gravar metadados em `~/.promptfoo/promptfoo.db`.
- **Causa-Raiz:** O Promptfoo tenta persistir o resumo da execução em um banco SQLite local ao finalizar o processo, sofrendo condição de corrida de inicialização em runners efêmeros quando `--no-cache` está ativo.
- **Solução:** Adicionada a flag `--no-write` (`npx --yes promptfoo@0.109.0 eval -c evals/promptfooconfig.yaml --no-cache --no-write`) no `.github/workflows/ci.yml`, gravando os resultados exclusivamente no artefato JSON (`--output eval-results-fake.json`).

### Problema 3 — Falha do `gitleaks-action@v2` no Commit Raiz (`unknown revision ^`)
- **Sintoma:** No push inicial para `main`, o `gitleaks/gitleaks-action@v2` falhou com `fatal: ambiguous argument '4cd32f5^..5e686a0': unknown revision`.
- **Causa-Raiz:** `4cd32f5` é o commit raiz do repositório, portanto a referência ao seu pai (`4cd32f5^`) não existe no grafo do Git.
- **Solução:** Substituído o wrapper no `.github/workflows/ci.yml` pelo container oficial `docker://zricethezav/gitleaks:v8.24.3` executando `git config --global --add safe.directory "$GITHUB_WORKSPACE" && gitleaks detect --source . --verbose --redact`.

### Problema 4 — `PERMISSION_DENIED` no Artifact Registry Imediatamente Após Habilitar a API
- **Sintoma:** Executar `gcloud artifacts repositories create` 2 segundos após `gcloud services enable artifactregistry.googleapis.com` em um projeto GCP recém-criado retornou `PERMISSION_DENIED`.
- **Causa-Raiz:** A propagação de Service Usage e políticas IAM entre endpoints regionais leva de 10 a 20 segundos em projetos recém-provisionados.
- **Solução:** Aguardados ~15 segundos para propagação do Service Usage antes de criar o repositório Docker.

### Problema 5 — Falha no Build Multi-Stage do Docker por Metadados do `hatchling` (`License file does not exist: LICENSE`)
- **Sintoma:** No `.github/workflows/deploy.yml`, o `docker build` falhou durante `RUN uv sync --frozen --no-dev --no-editable` com `OSError: License file does not exist: LICENSE`.
- **Causa-Raiz:** O `pyproject.toml` declara `readme = "README.md"` e `license = { file = "LICENSE" }`. A construção do wheel não-editável no estágio builder exige ambos os arquivos, mas o `.dockerignore` ignorava `*.md` e o `Dockerfile` copiava apenas `pyproject.toml uv.lock`.
- **Solução:** Adicionada a regra `!README.md` no `.dockerignore` e atualizado o `Dockerfile` para `COPY pyproject.toml uv.lock LICENSE README.md ./`.

### Problema 6 — Crash de Inicialização no Cloud Run ao Parsear `ALLOWED_ORIGINS` (`pydantic-settings` `JSONDecodeError`)
- **Sintoma:** A primeira revisão publicada no Cloud Run encerrou com código 1 na inicialização. O Cloud Logging registrou:
  `pydantic_settings.exceptions.SettingsError: error parsing value for field "allowed_origins" from source "EnvSettingsSource" -> JSONDecodeError`.
- **Causa-Raiz:** No `pydantic-settings` v2, campos compostos tipados como `list[str]` são pré-decodificados via `json.loads()` pela `EnvSettingsSource` *antes* da execução dos validadores `mode="before"`. Passar uma URL simples (`ALLOWED_ORIGINS=https://fgm9000.github.io`) falhava na decodificação JSON antes de chegar ao validador.
- **Solução:** Anotado o campo como `allowed_origins: Annotated[list[str], NoDecode]` em `src/ad_copy_grader/settings.py`, instruindo o `pydantic-settings` a repassar a string bruta diretamente ao `@field_validator("allowed_origins", mode="before")`.

### Problema 7 — Caminho `/healthz` Reservado pelo Google Frontend (GFE) (`404 Not Found`) e Redirecionamento da Raiz (`GET /`)
- **Sintoma:**
  1. Requisições externas para `https://ad-copy-grader-*.run.app/healthz` (incluindo o smoke test pós-deploy do GitHub Actions) recebiam uma página HTML `Error 404 (Not Found)!!1` do próprio Google sem que nenhuma requisição aparecesse nos logs `run.googleapis.com/requests` do container.
  2. Ao abrir a URL raiz do Cloud Run (`https://ad-copy-grader-316736391681.us-central1.run.app/`) no navegador, o FastAPI respondia `HTTP 404` (`{"detail":"Not Found"}`).
- **Causa-Raiz:**
  1. **Caminhos `*z` Reservados no GFE:** Nos domínios `*.run.app`, o Google Frontend (GFE) reserva rotas terminadas em `z` (`/healthz`, `/statusz`, `/varz`) para diagnóstico interno da infraestrutura do Google e intercepta chamadas HTTP externas na borda antes de chegarem ao container Cloud Run.
  2. **Ausência de Handler na Raiz:** O FastAPI registrava apenas `/healthz`, `/v1/grade` e `/docs`, sem rota para `GET /`.
- **Solução:**
  1. Adicionado `@app.get("/health")` junto ao `@app.get("/healthz", include_in_schema=False)` em `src/ad_copy_grader/api.py` e atualizado o smoke test externo no `.github/workflows/deploy.yml` para consultar `/health`.
  2. Adicionada a rota `@app.get("/", include_in_schema=False)` retornando `RedirectResponse(url="/docs")`, fazendo com que a URL pública raiz redirecione (`HTTP 307`) diretamente para o Swagger UI interativo.
