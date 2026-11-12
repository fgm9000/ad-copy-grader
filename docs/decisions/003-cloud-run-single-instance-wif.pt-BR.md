# ADR-003: Cloud Run Single-Instance (`max-instances=1`) e Deploy Keyless via WIF

> **[🇺🇸 English](003-cloud-run-single-instance-wif.md) | [🇧🇷 Português](003-cloud-run-single-instance-wif.pt-BR.md)**

- **Status:** Aceito
- **Data:** 2026-11-12

## Contexto

Como microsserviço público de portfólio conectado a uma API paga de LLM (OpenRouter), a arquitetura de deploy precisa atender a três restrições:
1. **Custo ocioso zero** quando não há visitantes testando o serviço.
2. **Teto rígido de custo** contra abuso automatizado ou picos de tráfego, sem introduzir infraestrutura paga adicional (como Redis gerenciado / Cloud Memorystore).
3. **Zero chaves estáticas de longa duração** salvas nos Secrets do GitHub.

## Alternativas Consideradas

1. **Cloud Run Multi-Instância + Redis Gerenciado (Upstash / Memorystore) para Rate Limit:**
   - *Prós:* Rate limit distribuído escalável horizontalmente.
   - *Contras:* Adiciona latência de rede externa, complexidade de operação e custo fixo para uma carga que cabe com folga em um único processo Python assíncrono.
2. **Chave JSON Estática de Service Account nos Secrets do GitHub:**
   - *Prós:* Configuração inicial simples.
   - *Contras:* Viola boas práticas modernas de segurança em nuvem; chaves estáticas não expiram automaticamente e exigem rotação manual.
3. **Cloud Run (`min-instances=0`, `max-instances=1`, `concurrency=10`) + Rate Limiter em Memória + Workload Identity Federation (Escolhida):**
   - *Prós:* `min-instances=0` escala a zero quando ocioso (`US$ 0,00/mês`). `max-instances=1` trava o teto de computação e garante que o `StrictRateLimiter` em memória (`5 req/min/IP` e teto de `200 req/dia` UTC em `limits.py`) seja globalmente consistente para todas as requisições ativas sem depender de Redis. O Workload Identity Federation (OIDC) autentica o GitHub Actions no GCP com tokens efêmeros restritos à branch `refs/heads/main`.

## Decisão

Fazer deploy no **Google Cloud Run** (`us-central1`) com `--min-instances=0 --max-instances=1 --concurrency=10`, injetar `OPENROUTER_API_KEY` via **Google Secret Manager**, aplicar limites de taxa em memória (`limits.py`) e autenticar o CI/CD sem chaves estáticas via **Workload Identity Federation**.

## Consequências

- **Positivas:** Custo ocioso zero, proteção rígida de gasto diário com LLM e zero chaves JSON estáticas do GCP no GitHub.
- **Negativas / Trade-offs:** Um *cold start* após período de inatividade reinicia o contador diário em memória (trade-off aceitável para proteção de demo; em ambiente multi-instância bastaria trocar a implementação de `StrictRateLimiter` por Redis mantendo a mesma interface).
