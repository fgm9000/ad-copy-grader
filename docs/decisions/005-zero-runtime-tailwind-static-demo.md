# ADR-005: Pre-Compiled Tailwind CSS Static Web Playground

> **[🇺🇸 English](005-zero-runtime-tailwind-static-demo.md) | [🇧🇷 Português](005-zero-runtime-tailwind-static-demo.pt-BR.md)**

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

The project includes an interactive bilingual web playground (`web/`) hosted on GitHub Pages so reviewers can test the side-by-side **Landing Page Context Card** and **Google Ads RSA Editor** immediately—either offline with pre-computed benchmark scenarios (`examples.json`) or live against the FastAPI endpoint (`/v1/grade`).

## Alternatives Considered

1. **SPA Framework (React / Next.js / Vite) in `web/`:**
   - *Pros:* Component ecosystem.
   - *Cons:* Introduces a permanent `package.json`, `node_modules`, bundler configuration, and weekly Node dependency churn in a Python repository for a single-screen playground.
2. **Tailwind Play CDN (`<script src="https://cdn.tailwindcss.com"></script>`):**
   - *Pros:* Zero build step.
   - *Cons:* Emits a prominent console warning in browser DevTools (`cdn.tailwindcss.com should not be used in production`) and compiles CSS at runtime in the user's browser.
3. **Vanilla HTML5/JS + Pre-Compiled Static Tailwind CSS via `@tailwindcss/cli` (Selected):**
   - *Pros:* `npx @tailwindcss/cli -i ./web/input.css -o ./web/styles.css --minify` produces a single static minified `web/styles.css` (~26 KB) with zero DevTools warnings, zero runtime JS overhead, and zero `node_modules` or `package.json` committed to the Python repository.

## Decision

Build `web/` using **semantic HTML5, Vanilla ES6 JavaScript (`web/app.js`), and pre-compiled minified Tailwind CSS (`web/styles.css`)**, with a side-by-side layout displaying the **Landing Page Context Card** next to the **RSA Ad Copy Card** and a `🇺🇸 EN | 🇧🇷 PT` language toggle.

## Consequences

- **Positive:** Instant page load on GitHub Pages, zero console warnings, offline fallback via `web/examples.json`, and zero frontend dependency maintenance in the repository.
- **Negative / Trade-off:** Modifying utility classes in `web/index.html` or `web/app.js` requires re-running `npx @tailwindcss/cli -i ./web/input.css -o ./web/styles.css --minify`.
