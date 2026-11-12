# ADR-005: Playground Estático com Tailwind CSS Pré-Compilado

> **[🇺🇸 English](005-zero-runtime-tailwind-static-demo.md) | [🇧🇷 Português](005-zero-runtime-tailwind-static-demo.pt-BR.md)**

- **Status:** Aceito
- **Data:** 2026-11-12

## Contexto

O projeto inclui um playground web interativo bilíngue (`web/`) hospedado no GitHub Pages para que avaliadores possam testar lado a lado o **Card de Contexto da Landing Page** e o **Editor RSA do Google Ads** imediatamente — tanto em modo offline com cenários pré-computados (`examples.json`) quanto ao vivo contra o endpoint FastAPI (`/v1/grade`).

## Alternativas Consideradas

1. **Framework SPA (React / Next.js / Vite) em `web/`:**
   - *Prós:* Ecossistema de componentes.
   - *Contras:* Introduz `package.json`, `node_modules`, bundler e manutenção contínua de dependências Node dentro de um repositório Python para uma única tela de demonstração.
2. **Tailwind Play CDN (`<script src="https://cdn.tailwindcss.com"></script>`):**
   - *Prós:* Sem etapa de compilação.
   - *Contras:* Emite alerta visível no console do DevTools (`cdn.tailwindcss.com should not be used in production`) e compila CSS em tempo de execução no navegador.
3. **HTML5/JS Puro + Tailwind CSS Estático Pré-Compilado via `@tailwindcss/cli` (Escolhida):**
   - *Prós:* `npx @tailwindcss/cli -i ./web/input.css -o ./web/styles.css --minify` gera um único arquivo estático minificado `web/styles.css` (~26 KB) com zero avisos no DevTools, zero sobrecarga de JS em runtime e sem `node_modules` ou `package.json` commitados no repositório Python.

## Decisão

Construir `web/` com **HTML5 semântico, JavaScript ES6 puro (`web/app.js`) e Tailwind CSS pré-compilado e minificado (`web/styles.css`)**, exibindo lado a lado o **Card de Contexto da Landing Page**, o **Editor de Anúncio RSA** e o **Relatório Híbrido de Auditoria**, com seletor instantâneo de idioma `🇺🇸 EN | 🇧🇷 PT`.

## Consequências

- **Positivas:** Carregamento instantâneo no GitHub Pages, zero avisos no console, fallback offline automático via `web/examples.json` e zero manutenção de dependências frontend no repositório.
- **Negativas / Trade-offs:** Caso novas classes utilitárias sejam adicionadas a `web/index.html` ou `web/app.js`, basta rodar novamente `npx @tailwindcss/cli -i ./web/input.css -o ./web/styles.css --minify`.
