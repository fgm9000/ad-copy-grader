/**
 * Ad Copy Grader — Interactive Architecture Showcase
 *
 * Demonstrates the hybrid grading architecture:
 * 1. Pure Python Deterministic Rules (D01-D11)
 * 2. Bilingual Semantic LLM Audit (A01-A03)
 * 3. Server Code Authority Filter & Validated Rewrites
 * 4. Live Cloud Run FastAPI Backend Integration
 */

const CLOUD_RUN_API_URL = "https://ad-copy-grader-316736391681.us-central1.run.app/v1/grade";

// Full Bilingual UI Translations
const TRANSLATIONS = {
  en: {
    appTitle: "Ad Copy Grader",
    appSubtitle: "Hybrid Deterministic & LLM Google Ads RSA Auditor",
    swaggerNavLink: "Live Swagger API (/docs) ↗",
    showcaseBadge: "Interactive Architecture Showcase",
    onboardingTitle: "How to explore this project in 30 seconds",
    onboardingPill: "Quick 30–60s Reviewer Walkthrough",
    step1Title: "1. See Highlighted Errors & LP Numbers",
    step1Desc:
      "Notice how Landing Page prices (left, e.g. <strong>$899</strong>) are highlighted and cross-checked against RSA Headlines (center), flagging unverified claims (<strong>[A01]</strong>) and length overflows (<strong>[D04]</strong>) in red.",
    step2Title: "2. Click 'Apply All Fixes (1-Click)'",
    step2Desc:
      "Click <strong>'✨ Apply All Validated Fixes'</strong> on the right (or individual 'Apply Rewrite' buttons) to fix every issue in 1 click and watch the score jump from <strong>6.5 REJECTED</strong> to <strong>10.0 PASSED</strong>!",
    step3Title: "3. Test Scenario #2 & Live Cloud Run API",
    step3Desc:
      "Switch to <strong>Scenario 2</strong> to see the <strong>Code Authority Filter</strong> block an LLM false positive, or click <strong>'☁️ Verify on Cloud Run API'</strong> to inspect the live FastAPI JSON response.",
    scenariosLabel: "Pre-Loaded Scenarios:",
    scenarioDetailLabel: "Active Scenario:",
    lpCardTitle: "Landing Page Context",
    ruleA01Badge: "Rule A01 & Authority Filter",
    primaryServiceLabel: "Primary Service (Rule D07)",
    finalUrlLabel: "Final URL (Rule D11)",
    lpContextLabel: "Landing Page Copy (Beginning, Middle & End)",
    editLpBtn: "✏️ Edit LP Text",
    viewLpBtn: "👁️ Scanner View",
    detectedLpTokensLabel: "Extracted Numbers & Prices Checked by LLM / Filter:",
    rsaEditorTitle: "RSA Asset Editor",
    rulesEngineBadge: "Rules D01–D11 + A01–A03",
    path1Label: "Path 1",
    path2Label: "Path 2",
    headlinesHeader: "Headlines (3–15)",
    descriptionsHeader: "Descriptions (2–4)",
    showAllHeadlinesBtn: "Show all 15 (9 hidden)",
    collapseHeadlinesBtn: "Collapse to top 6 headlines",
    resetScenarioBtn: "Reset Scenario",
    gradeAdBtn: "Re-evaluate Ad Copy",
    auditReportTitle: "Hybrid Audit Report",
    qualityScaleLabel: "Google Ads Quality",
    scoreLabel: "Score",
    fixAllBtnText: "✨ Apply All Validated Fixes (1-Click → 10.0 Score)",
    fixAllAppliedText: "✅ All Fixes Applied! Score: 10.0 PASSED",
    rulesCheckedBadge: "11 Code Rules (D01-D11) + 3 LLM (A01-A03)",
    authorityFilterTitle: "Code Authority Filter Active",
    falsePositiveStrippedBadge: "False Positive Intercepted",
    authorityFilterDescription:
      "The raw LLM review flagged an offer or price claim, but the deterministic server filter verified that the claim matches the Landing Page context and automatically stripped the false positive before calculating the final score!",
    detectedIssuesTitle: "Detected Issues",
    rewriteSuggestionsTitle: "Validated Rewrites",
    rewriteSuggestionsSubtitle: "Guaranteed ≤30 chars (headlines) / ≤90 chars (descriptions)",
    applyRewriteBtn: "Apply Rewrite",
    rewriteApplied: "Applied!",
    cloudRunCardTitle: "Cloud Run FastAPI Backend",
    callCloudRunBtn: "☁️ Verify on Cloud Run API",
    callingCloudRunBtn: "⏳ Calling Cloud Run...",
    toggleJsonBtn: "{ } JSON",
    architectureSectionTitle: "How the Repository Code Works Under the Hood",
    architectureSectionSubtitle:
      "Engineering architecture: strict separation of deterministic code rules and semantic LLM judgment.",
    archCard1Title: "Deterministic Engine (D01–D11)",
    archCard1Body:
      "LLMs notoriously miscount characters due to BPE tokenization. Exact hard limits (30 chars per headline D04, 90 per description D05, 15 per path D06) are enforced 100% by pure Python functions with Unicode NFC normalization. Also handles recommended 15-headline coverage (D02), 2–4 descriptions (D03), primary service in top headlines (D07), duplicates (D08), repeated punctuation (D09), ALL CAPS (D10), and valid HTTPS final URLs (D11).",
    archCard2Title: "Bilingual LLM Audit & Self-Correction",
    archCard2Body:
      "Semantic rules evaluate unverified pricing vs. LP context (A01), missing CTA in descriptions (A02), and clinical/financial guarantees (A03). Uses native Portuguese (PROMPT_PT) and English (PROMPT_EN) system prompts with <ad_payload> XML fencing against prompt injection, parsed by Pydantic with 1 automatic self-correction retry on malformed outputs.",
    archCard3Title: "Server Code Authority Filter",
    archCard3Body:
      "The server never blindly trusts LLM outputs. filter_llm_issues() acts as an automated boundary: strips any deterministic D* rule hallucinated by the model, drops out-of-bounds asset index hallucination, and suppresses A01 false positives whenever the flagged price or offer actually exists in lp_context (as proven in Scenario 2).",
    archCard4Title: "Validated Rewrites & 3-Column Evals",
    archCard4Body:
      "validate_suggestions() re-audits every LLM rewrite against rules D04/D05/D08/D09/D10; non-compliant rewrites are discarded before reaching the user. Validated with a 3-column Promptfoo evaluation suite (raw vs. pipeline vs. degraded) and CI gates: ruff, mypy --strict, pytest (100% coverage), Semgrep OWASP Top 10, and CodeQL.",
    footerText: "Ad Copy Grader — Deterministic Google Ads rules engine & LLM semantic audit.",
    perfectScoreText: "🎉 Perfect 10.0 score! All 14 deterministic and semantic rules passed.",
    codeProvenance: "Code Verified (Deterministic)",
    llmProvenance: "LLM Judged (Semantic)",
    severityError: "ERROR",
    severityWarning: "WARNING",
    discardedBadge: "Discarded by Server Authority Filter",
    headlinePlaceholder: "Headline",
    descriptionPlaceholder: "Description",
    noTokensDetected: "No price or numeric tokens detected in LP context.",
  },
  pt: {
    appTitle: "Ad Copy Grader",
    appSubtitle: "Auditor Híbrido Determinístico e LLM para Google Ads RSA",
    swaggerNavLink: "Swagger API ao Vivo (/docs) ↗",
    showcaseBadge: "Demonstração Interativa da Arquitetura",
    onboardingTitle: "Como explorar este projeto em 30 segundos",
    onboardingPill: "Roteiro Rápido de Avaliação em 30–60s",
    step1Title: "1. Veja os Erros e Números da LP Grifados",
    step1Desc:
      "Repare como os preços da Landing Page (à esquerda, ex.: <strong>R$ 390</strong>) ficam destacados e são cruzados contra os Títulos RSA (centro), marcando preços divergentes (<strong>[A01]</strong>) e limites estourados (<strong>[D04]</strong>) em vermelho.",
    step2Title: "2. Clique em 'Aplicar Todas as Correções'",
    step2Desc:
      "Clique em <strong>'✨ Aplicar Todas as Correções (1 Clique)'</strong> à direita (ou nos botões individuais) para corrigir tudo instantaneamente e ver a nota saltar de <strong>6.5 REJECTED</strong> para <strong>10.0 PASSED</strong>!",
    step3Title: "3. Teste o Cenário #2 e a API Cloud Run",
    step3Desc:
      "Mude para o <strong>Cenário 2</strong> para ver o <strong>Filtro de Autoridade</strong> bloquear um falso positivo do LLM, ou clique em <strong>'☁️ Validar na API Cloud Run'</strong> para inspecionar o JSON real do FastAPI.",
    scenariosLabel: "Cenários Pré-Carregados:",
    scenarioDetailLabel: "Cenário Ativo:",
    lpCardTitle: "Contexto da Landing Page",
    ruleA01Badge: "Regra A01 & Filtro de Autoridade",
    primaryServiceLabel: "Serviço Principal (Regra D07)",
    finalUrlLabel: "URL Final (Regra D11)",
    lpContextLabel: "Texto da Landing Page (Começo, Meio e Fim)",
    editLpBtn: "✏️ Editar Texto da LP",
    viewLpBtn: "👁️ Visão com Grifos",
    detectedLpTokensLabel: "Números e Preços Extraídos e Checados pelo LLM / Filtro:",
    rsaEditorTitle: "Editor de Recursos RSA",
    rulesEngineBadge: "Regras D01–D11 + A01–A03",
    path1Label: "Caminho 1",
    path2Label: "Caminho 2",
    headlinesHeader: "Títulos (3–15)",
    descriptionsHeader: "Descrições (2–4)",
    showAllHeadlinesBtn: "Mostrar todos os 15 (9 ocultos)",
    collapseHeadlinesBtn: "Recolher para os 6 primeiros",
    resetScenarioBtn: "Restaurar Cenário",
    gradeAdBtn: "Reavaliar Anúncio",
    auditReportTitle: "Relatório de Auditoria Híbrida",
    qualityScaleLabel: "Qualidade Google Ads",
    scoreLabel: "Pontuação",
    fixAllBtnText: "✨ Aplicar Todas as Correções (1 Clique → Nota 10.0)",
    fixAllAppliedText: "✅ Correções Aplicadas! Nota: 10.0 PASSED",
    rulesCheckedBadge: "11 Regras de Código (D01-D11) + 3 LLM (A01-A03)",
    authorityFilterTitle: "Filtro de Autoridade Ativo",
    falsePositiveStrippedBadge: "Falso Positivo Interceptado",
    authorityFilterDescription:
      "A revisão bruta do LLM apontou erro em um preço/oferta, mas o filtro determinístico do servidor comprovou que o número consta no texto da Landing Page e descartou o falso positivo antes de calcular a nota final!",
    detectedIssuesTitle: "Problemas Detectados",
    rewriteSuggestionsTitle: "Sugestões de Reescrita Validadas",
    rewriteSuggestionsSubtitle: "Garantidas ≤30 caracteres (títulos) / ≤90 caracteres (descrições)",
    applyRewriteBtn: "Aplicar Sugestão",
    rewriteApplied: "Aplicado!",
    cloudRunCardTitle: "Backend FastAPI no Cloud Run",
    callCloudRunBtn: "☁️ Validar na API Cloud Run",
    callingCloudRunBtn: "⏳ Consultando Cloud Run...",
    toggleJsonBtn: "{ } JSON",
    architectureSectionTitle: "Como o Código do Repositório Funciona nos Bastidores",
    architectureSectionSubtitle:
      "Arquitetura de engenharia: separação estrita entre regras determinísticas de código e julgamento semântico do LLM.",
    archCard1Title: "Motor Determinístico (D01–D11)",
    archCard1Body:
      "LLMs erram contagens de caracteres devido à tokenização BPE. Limites exatos (30 caracteres por título D04, 90 por descrição D05, 15 por caminho D06) são validados 100% por funções puras em Python com normalização Unicode NFC. Também valida cobertura recomendada de 15 títulos (D02), 2–4 descrições (D03), presença do serviço nos títulos iniciais (D07), duplicidades (D08), pontuação repetida (D09), CAIXA ALTA (D10) e URL HTTPS (D11).",
    archCard2Title: "Auditoria Bilíngue LLM & Autocorreção",
    archCard2Body:
      "Regras semânticas avaliam preços não verificados na LP (A01), ausência de CTA nas descrições (A02) e garantias absolutas (A03). Usa prompts nativos em Português (PROMPT_PT) e Inglês (PROMPT_EN) com isolamento XML <ad_payload> contra prompt injection, validados via Pydantic com 1 retry automático de autocorreção.",
    archCard3Title: "Filtro de Autoridade do Código",
    archCard3Body:
      "O servidor nunca confia cegamente no LLM. filter_llm_issues() atua como fronteira: descarta qualquer regra D* alucinada pelo modelo, remove índices fora dos limites e suprime falsos positivos de A01 sempre que o preço ou oferta existir em lp_context (como demonstrado no Cenário 2).",
    archCard4Title: "Reescritas Validadas & Evals em 3 Colunas",
    archCard4Body:
      "validate_suggestions() re-audita cada sugestão do LLM contra as regras D04/D05/D08/D09/D10; sugestões fora do limite são descartadas. Validado com suíte Promptfoo em 3 colunas (raw vs. pipeline vs. degraded) e gates de CI: ruff, mypy --strict, pytest (100% cobertura), Semgrep OWASP Top 10 e CodeQL.",
    footerText: "Ad Copy Grader — Motor de regras determinísticas Google Ads e auditoria semântica LLM.",
    perfectScoreText: "🎉 Nota 10.0 perfeita! Todas as 14 regras determinísticas e semânticas foram aprovadas.",
    codeProvenance: "Verificado via Código",
    llmProvenance: "Julgado via LLM (Semântico)",
    severityError: "ERRO",
    severityWarning: "AVISO",
    discardedBadge: "Descartado pelo Filtro de Autoridade",
    headlinePlaceholder: "Título",
    descriptionPlaceholder: "Descrição",
    noTokensDetected: "Nenhum token numérico ou de preço detectado na LP.",
  },
};

// Application State
const state = {
  lang: "en",
  scenarios: [],
  activeScenarioIndex: 0,
  headlinesExpanded: false,
  lpEditMode: false,
  lastResult: null,
  lastSuggestions: [],
};

// DOM Elements Cache
const elements = {
  langEnBtn: document.getElementById("langEnBtn"),
  langPtBtn: document.getElementById("langPtBtn"),
  scenarioPills: document.getElementById("scenarioPills"),
  scenarioDescription: document.getElementById("scenarioDescription"),
  lpCrossCheckBanner: document.getElementById("lpCrossCheckBanner"),
  primaryServiceInput: document.getElementById("primaryServiceInput"),
  finalUrlInput: document.getElementById("finalUrlInput"),
  toggleLpEditBtn: document.getElementById("toggleLpEditBtn"),
  lpHighlightedView: document.getElementById("lpHighlightedView"),
  lpContextInput: document.getElementById("lpContextInput"),
  lpTokenCountBadge: document.getElementById("lpTokenCountBadge"),
  detectedLpTokensList: document.getElementById("detectedLpTokensList"),
  path1Input: document.getElementById("path1Input"),
  path2Input: document.getElementById("path2Input"),
  path1Counter: document.getElementById("path1Counter"),
  path2Counter: document.getElementById("path2Counter"),
  headlinesCountBadge: document.getElementById("headlinesCountBadge"),
  toggleHeadlinesBtn: document.getElementById("toggleHeadlinesBtn"),
  headlinesContainer: document.getElementById("headlinesContainer"),
  descriptionsCountBadge: document.getElementById("descriptionsCountBadge"),
  descriptionsContainer: document.getElementById("descriptionsContainer"),
  resetScenarioBtn: document.getElementById("resetScenarioBtn"),
  gradeAdBtn: document.getElementById("gradeAdBtn"),
  gradeBtnText: document.getElementById("gradeBtnText"),
  statusPassBadge: document.getElementById("statusPassBadge"),
  heroGrade10: document.getElementById("heroGrade10"),
  heroScore: document.getElementById("heroScore"),
  heroFixAllContainer: document.getElementById("heroFixAllContainer"),
  fixAllHeroBtn: document.getElementById("fixAllHeroBtn"),
  activeModelBadge: document.getElementById("activeModelBadge"),
  authorityFilterCallout: document.getElementById("authorityFilterCallout"),
  droppedIssuesList: document.getElementById("droppedIssuesList"),
  issuesList: document.getElementById("issuesList"),
  issuesCountBadge: document.getElementById("issuesCountBadge"),
  suggestionsCard: document.getElementById("suggestionsCard"),
  suggestionsList: document.getElementById("suggestionsList"),
  suggestionsCountBadge: document.getElementById("suggestionsCountBadge"),
  apiStatusBadge: document.getElementById("apiStatusBadge"),
  callCloudRunBtn: document.getElementById("callCloudRunBtn"),
  toggleJsonDrawerBtn: document.getElementById("toggleJsonDrawerBtn"),
  jsonInspectorDrawer: document.getElementById("jsonInspectorDrawer"),
  jsonInspectorPre: document.getElementById("jsonInspectorPre"),
};

// Regular Expressions & Constants matching Python pipeline
const NUMERIC_TOKEN_PATTERN =
  /(?:r\$\s*\d[\d.,]*|\$\s*\d[\d.,]*|\b\d+(?:[.,]\d+)?%|\b\d{1,2}x\b|\b\d{1,2}\/\d{1,2}\b|\b\d[\d.,]*\+?\b)/gi;

const PRICE_CLAIM_PATTERN =
  /(?:r\$\s*\d[\d.,]*|\$\s*\d[\d.,]*|\b\d{1,2}%\s*(?:off|de\s+desconto)\b|\b\d{1,2}x\s+sem\s+juros\b)/i;

const CTA_PATTERN =
  /\b(?:book|schedule|call|contact|request|claim|get|start|visit|learn\s+more|agende|marque|ligue|fale|solicite|peça|peca|garanta|saiba\s+mais|confira|clique)\b/i;

const GUARANTEE_PATTERN =
  /(?:100%\s*garant\w*|garant\w*\s*(?:total|absolut\w*|100%)|garantia\s*de\s*resultado|resultado\s*100%\s*garantido|resultado\s*garantido|guaranteed\s*results?|100%\s*guaranteed)/i;

const REPEATED_PUNCTUATION_PATTERN = /!{2,}|\?{2,}|\.{3,}|…+/;
const UPPERCASE_WORD_PATTERN = /\b[A-ZÀ-ÖØ-Þ]{4,}\b/g;

const ALLOWED_ACRONYMS = new Set([
  "HTML", "HTTP", "HTTPS", "JSON", "REST", "SAAS", "GDPR", "LGPD",
  "CNPJ", "INSS", "FGTS", "OAB", "CRM", "CRO", "CREA", "CREFITO",
  "CRP", "ANVISA", "ABNT", "CPAP", "LASIK", "CBCT", "CADCAM",
]);

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// Initialize Application
async function init() {
  bindEvents();
  loadStoredSettings();
  await loadScenarios();
  updateI18nLabels();
}

// Bind Event Listeners
function bindEvents() {
  elements.langEnBtn.addEventListener("click", () => setLanguage("en"));
  elements.langPtBtn.addEventListener("click", () => setLanguage("pt"));

  elements.toggleLpEditBtn.addEventListener("click", toggleLpEditMode);
  elements.toggleHeadlinesBtn.addEventListener("click", toggleHeadlinesExpanded);
  elements.resetScenarioBtn.addEventListener("click", resetCurrentScenario);
  elements.gradeAdBtn.addEventListener("click", () => runLiveEvaluation(true));
  elements.fixAllHeroBtn.addEventListener("click", applyAllSuggestions);
  elements.callCloudRunBtn.addEventListener("click", callCloudRunApi);
  elements.toggleJsonDrawerBtn.addEventListener("click", () => {
    elements.jsonInspectorDrawer.classList.toggle("hidden");
  });

  elements.primaryServiceInput.addEventListener("input", () => runLiveEvaluation(false));
  elements.finalUrlInput.addEventListener("input", () => runLiveEvaluation(false));

  elements.path1Input.addEventListener("input", () => {
    updatePathCounters();
    runLiveEvaluation(false);
  });
  elements.path2Input.addEventListener("input", () => {
    updatePathCounters();
    runLiveEvaluation(false);
  });

  elements.lpContextInput.addEventListener("input", () => {
    runLiveEvaluation(false);
  });
}

function toggleLpEditMode() {
  state.lpEditMode = !state.lpEditMode;
  const dict = TRANSLATIONS[state.lang];
  if (state.lpEditMode) {
    elements.lpHighlightedView.classList.add("hidden");
    elements.lpContextInput.classList.remove("hidden");
    elements.lpContextInput.focus();
    elements.toggleLpEditBtn.textContent = dict.viewLpBtn;
  } else {
    elements.lpContextInput.classList.add("hidden");
    elements.lpHighlightedView.classList.remove("hidden");
    elements.toggleLpEditBtn.textContent = dict.editLpBtn;
  }
}

function loadStoredSettings() {
  const storedLang = localStorage.getItem("ad_copy_grader_lang");
  if (storedLang === "en" || storedLang === "pt") {
    state.lang = storedLang;
  }
}

// Switch Language
function setLanguage(newLang) {
  if (state.lang === newLang) return;
  state.lang = newLang;
  localStorage.setItem("ad_copy_grader_lang", newLang);

  if (newLang === "en") {
    elements.langEnBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition shadow-xs bg-white text-slate-900";
    elements.langPtBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition text-slate-600 hover:text-slate-900";
  } else {
    elements.langPtBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition shadow-xs bg-white text-slate-900";
    elements.langEnBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition text-slate-600 hover:text-slate-900";
  }

  updateI18nLabels();
  renderScenarioPills();
  loadScenario(state.activeScenarioIndex);
}

// Update text across all data-i18n elements
function updateI18nLabels() {
  const dict = TRANSLATIONS[state.lang];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerHTML = dict[key];
    }
  });

  elements.toggleHeadlinesBtn.textContent = state.headlinesExpanded
    ? dict.collapseHeadlinesBtn
    : dict.showAllHeadlinesBtn;
  elements.toggleLpEditBtn.textContent = state.lpEditMode ? dict.viewLpBtn : dict.editLpBtn;
}

// Load scenarios from examples.json
async function loadScenarios() {
  try {
    const resp = await fetch("./examples.json");
    if (!resp.ok) throw new Error("Failed to load examples.json");
    state.scenarios = await resp.json();
    renderScenarioPills();
    loadScenario(0);
  } catch (err) {
    console.error("Error loading examples.json:", err);
    elements.scenarioDescription.textContent =
      "Failed to load synthetic benchmark scenarios. Please verify examples.json.";
  }
}

// Render Scenario Selection Pills
function renderScenarioPills() {
  elements.scenarioPills.innerHTML = "";
  state.scenarios.forEach((scenario, index) => {
    const label = scenario.label[state.lang] || scenario.label.en;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `px-3 py-1.5 rounded-full text-xs font-semibold transition shadow-xs ${
      index === state.activeScenarioIndex
        ? "bg-indigo-600 text-white shadow-indigo-200 ring-2 ring-indigo-500 ring-offset-1"
        : "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200"
    }`;
    btn.textContent = label;
    btn.addEventListener("click", () => loadScenario(index));
    elements.scenarioPills.appendChild(btn);
  });
}

// Load Scenario into UI
function loadScenario(index) {
  state.activeScenarioIndex = index;
  renderScenarioPills();

  const scenario = state.scenarios[index];
  if (!scenario) return;

  const desc = scenario.description[state.lang] || scenario.description.en;
  elements.scenarioDescription.textContent = desc;

  const inputData = scenario.input[state.lang] || scenario.input.en;

  elements.primaryServiceInput.value = inputData.primary_service || "";
  elements.finalUrlInput.value = inputData.final_url || "";
  elements.lpContextInput.value = inputData.lp_context || "";
  elements.path1Input.value = inputData.path1 || "";
  elements.path2Input.value = inputData.path2 || "";

  renderHeadlinesInputs(inputData.headlines || []);
  renderDescriptionsInputs(inputData.descriptions || []);

  updatePathCounters();
  runLiveEvaluation(false);
}

function resetCurrentScenario() {
  loadScenario(state.activeScenarioIndex);
}

// Render Headline Inputs
function renderHeadlinesInputs(headlines) {
  elements.headlinesContainer.innerHTML = "";

  for (let i = 0; i < 15; i++) {
    const val = headlines[i] || "";
    const row = document.createElement("div");
    row.className = `headline-row flex items-center space-x-2 ${
      i >= 6 && !state.headlinesExpanded ? "hidden" : ""
    }`;
    row.dataset.index = i;

    const label = document.createElement("span");
    label.className = "w-6 text-right text-[11px] font-mono text-slate-400 font-semibold";
    label.textContent = `#${i + 1}`;

    const inputWrapper = document.createElement("div");
    inputWrapper.className = "flex-1 relative";

    const input = document.createElement("input");
    input.type = "text";
    input.className =
      "headline-input w-full pl-2.5 pr-14 py-1.5 text-xs rounded-lg border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-sans";
    input.placeholder = `${TRANSLATIONS[state.lang].headlinePlaceholder} ${i + 1}`;
    input.value = val;

    const rightBadges = document.createElement("div");
    rightBadges.className = "absolute right-2 top-1.5 flex items-center space-x-1";

    const rulePill = document.createElement("span");
    rulePill.className = "headline-rule-pill hidden px-1 rounded text-[10px] font-mono font-bold";

    const counter = document.createElement("span");
    counter.className = "counter-badge text-[10px] font-mono font-medium text-slate-400";
    counter.textContent = `${val.length}/30`;

    rightBadges.appendChild(rulePill);
    rightBadges.appendChild(counter);

    input.addEventListener("input", () => {
      counter.textContent = `${input.value.length}/30`;
      runLiveEvaluation(false);
    });

    inputWrapper.appendChild(input);
    inputWrapper.appendChild(rightBadges);
    row.appendChild(label);
    row.appendChild(inputWrapper);
    elements.headlinesContainer.appendChild(row);
  }

  const activeCount = headlines.filter((h) => h.trim()).length;
  elements.headlinesCountBadge.textContent = `${activeCount}/15`;
}

// Render Description Inputs
function renderDescriptionsInputs(descriptions) {
  elements.descriptionsContainer.innerHTML = "";

  for (let i = 0; i < 4; i++) {
    const val = descriptions[i] || "";
    const card = document.createElement("div");
    card.className = `description-row rounded-lg border border-slate-200 p-2.5 bg-slate-50/50 ${
      i >= 2 && !val ? "hidden" : ""
    }`;
    card.dataset.index = i;

    const header = document.createElement("div");
    header.className = "flex items-center justify-between mb-1";

    const label = document.createElement("span");
    label.className = "text-[11px] font-bold text-slate-700";
    label.textContent = `${TRANSLATIONS[state.lang].descriptionPlaceholder} ${i + 1}`;

    const counter = document.createElement("span");
    counter.className = "desc-counter text-[10px] font-mono font-medium text-slate-400";
    counter.textContent = `${val.length}/90`;

    header.appendChild(label);
    header.appendChild(counter);

    const textarea = document.createElement("textarea");
    textarea.rows = 2;
    textarea.className =
      "desc-input w-full p-2 text-xs rounded-md border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500";
    textarea.placeholder = `${TRANSLATIONS[state.lang].descriptionPlaceholder} ${i + 1}`;
    textarea.value = val;

    textarea.addEventListener("input", () => {
      counter.textContent = `${textarea.value.length}/90`;
      runLiveEvaluation(false);
    });

    card.appendChild(header);
    card.appendChild(textarea);
    elements.descriptionsContainer.appendChild(card);
  }

  const activeCount = descriptions.filter((d) => d.trim()).length;
  elements.descriptionsCountBadge.textContent = `${activeCount}/4`;
}

function toggleHeadlinesExpanded() {
  state.headlinesExpanded = !state.headlinesExpanded;
  const rows = elements.headlinesContainer.querySelectorAll(".headline-row");
  rows.forEach((row, i) => {
    if (i >= 6) {
      if (state.headlinesExpanded) {
        row.classList.remove("hidden");
      } else {
        row.classList.add("hidden");
      }
    }
  });

  const dict = TRANSLATIONS[state.lang];
  elements.toggleHeadlinesBtn.textContent = state.headlinesExpanded
    ? dict.collapseHeadlinesBtn
    : dict.showAllHeadlinesBtn;
}

function updatePathCounters() {
  const p1Len = elements.path1Input.value.length;
  const p2Len = elements.path2Input.value.length;

  elements.path1Counter.textContent = `${p1Len}/15`;
  elements.path2Counter.textContent = `${p2Len}/15`;

  elements.path1Counter.className =
    p1Len > 15
      ? "text-[10px] font-mono font-bold text-rose-600"
      : "text-[10px] font-mono font-medium text-slate-400";
  elements.path2Counter.className =
    p2Len > 15
      ? "text-[10px] font-mono font-bold text-rose-600"
      : "text-[10px] font-mono font-medium text-slate-400";
}

// Render Highlighted Landing Page View & Token Pills
function renderLpHighlightedAndTokens(lpContext, rawHeadlines) {
  const dict = TRANSLATIONS[state.lang];
  const matches = lpContext.match(NUMERIC_TOKEN_PATTERN) || [];
  const uniqueTokens = Array.from(new Set(matches.map((m) => m.trim())));

  // Collect price claims from headlines
  const headlinePriceClaims = [];
  rawHeadlines.forEach((h, idx) => {
    const m = h.match(PRICE_CLAIM_PATTERN);
    if (m) {
      const digits = (m[0].match(/\d+/g) || []).join("");
      headlinePriceClaims.push({ index: idx, raw: m[0].trim(), digits });
    }
  });

  const lpPriceMatches = lpContext.match(/(?:r\$\s*\d[\d.,]*|\$\s*\d[\d.,]*)/gi) || [];
  const lpPricesClean = Array.from(new Set(lpPriceMatches.map((p) => p.trim())));
  const lpAllDigits = new Set(
    (lpContext.match(/\d[\d.,]*/g) || []).map((m) => m.replace(/\D/g, "")).filter(Boolean)
  );

  // 1. Update Cross-Check Verdict Banner
  const unverifiedClaim = headlinePriceClaims.find(
    (c) => c.digits && !lpAllDigits.has(c.digits) && !lpContext.includes(c.digits)
  );
  const verifiedClaim = headlinePriceClaims.find(
    (c) => c.digits && (lpAllDigits.has(c.digits) || lpContext.includes(c.digits))
  );

  if (unverifiedClaim) {
    const lpPriceDisplay = lpPricesClean.length > 0 ? lpPricesClean.join(", ") : "none";
    elements.lpCrossCheckBanner.className =
      "p-2.5 rounded-lg border border-rose-200 bg-rose-50 text-xs text-rose-800 font-medium leading-snug";
    elements.lpCrossCheckBanner.innerHTML =
      state.lang === "pt"
        ? `❌ <strong>Conflito de Preço (Regra A01):</strong> O Título #${
            unverifiedClaim.index + 1
          } anuncia <span class="px-1.5 py-0.2 rounded font-mono font-bold bg-rose-100 text-rose-800">${escapeHtml(
            unverifiedClaim.raw
          )}</span>, mas a Landing Page abaixo informa <span class="px-1.5 py-0.2 rounded font-mono font-bold bg-amber-100 text-amber-800">${escapeHtml(
            lpPriceDisplay
          )}</span>.`
        : `❌ <strong>Price Conflict (Rule A01):</strong> Headline #${
            unverifiedClaim.index + 1
          } claims <span class="px-1.5 py-0.2 rounded font-mono font-bold bg-rose-100 text-rose-800">${escapeHtml(
            unverifiedClaim.raw
          )}</span>, while the Landing Page states <span class="px-1.5 py-0.2 rounded font-mono font-bold bg-amber-100 text-amber-800">${escapeHtml(
            lpPriceDisplay
          )}</span>.`;
  } else if (verifiedClaim) {
    elements.lpCrossCheckBanner.className =
      "p-2.5 rounded-lg border border-emerald-300 bg-emerald-50 text-xs text-emerald-900 font-medium leading-snug";
    elements.lpCrossCheckBanner.innerHTML =
      state.lang === "pt"
        ? `✅ <strong>Preço Confirmado na LP:</strong> O valor <span class="px-1.5 py-0.2 rounded font-mono font-bold bg-emerald-200 text-emerald-900">${escapeHtml(
            verifiedClaim.raw
          )}</span> do Título #${
            verifiedClaim.index + 1
          } consta na Landing Page (Falso positivo do LLM bloqueado!).`
        : `✅ <strong>LP Price Match Verified:</strong> <span class="px-1.5 py-0.2 rounded font-mono font-bold bg-emerald-200 text-emerald-900">${escapeHtml(
            verifiedClaim.raw
          )}</span> in Headline #${
            verifiedClaim.index + 1
          } matches the Landing Page (LLM false positive blocked!).`;
  } else {
    elements.lpCrossCheckBanner.className =
      "p-2.5 rounded-lg border border-blue-200 bg-blue-50 text-xs text-blue-700 font-medium leading-snug";
    elements.lpCrossCheckBanner.innerHTML =
      state.lang === "pt"
        ? `✓ <strong>Scanner de LP Ativo:</strong> ${uniqueTokens.length} números/ofertas indexados na página. Nenhum preço conflitante nos títulos.`
        : `✓ <strong>LP Scanner Active:</strong> ${uniqueTokens.length} numeric/offer tokens indexed. No conflicting price claims in headlines.`;
  }

  // 2. Render Highlighted Paragraphs (Beginning, Middle, End)
  const verifiedDigitsSet = new Set(
    headlinePriceClaims
      .filter((c) => c.digits && (lpAllDigits.has(c.digits) || lpContext.includes(c.digits)))
      .map((c) => c.digits)
  );

  const paragraphs = lpContext.split(/\n\s*\n/).filter(Boolean);
  const sectionLabels =
    state.lang === "pt"
      ? ["Início (Hero & Credenciais)", "Meio (Oferta & Preços)", "Fim (Horários & CTA)"]
      : ["Beginning (Hero & Credentials)", "Middle (Pricing & Offer)", "End (Hours & CTA)"];

  elements.lpHighlightedView.innerHTML = paragraphs
    .map((para, pIdx) => {
      const escapedPara = escapeHtml(para);
      const highlightedPara = escapedPara.replace(NUMERIC_TOKEN_PATTERN, (match) => {
        const cleanDigits = match.replace(/\D/g, "");
        const isCurrency = /\$|r\$/i.test(match);
        if (cleanDigits && verifiedDigitsSet.has(cleanDigits)) {
          return `<span class="px-1.5 py-0.2 rounded font-mono font-bold bg-emerald-200 text-emerald-900 border border-emerald-300">${match} ✓</span>`;
        }
        if (isCurrency) {
          return `<span class="px-1.5 py-0.2 rounded font-mono font-bold bg-amber-100 text-amber-800 border border-amber-200">${match}</span>`;
        }
        return `<span class="px-1 rounded font-mono font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">${match}</span>`;
      });

      const sectionLabel = sectionLabels[pIdx] || `Section ${pIdx + 1}`;
      return `
        <div class="space-y-0.5">
          <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400">${sectionLabel}</span>
          <p class="text-xs text-slate-700 leading-relaxed">${highlightedPara}</p>
        </div>
      `;
    })
    .join("");

  // 3. Render Token Badges below LP
  elements.lpTokenCountBadge.textContent = `${uniqueTokens.length} token${
    uniqueTokens.length === 1 ? "" : "s"
  }`;
  elements.detectedLpTokensList.innerHTML = "";

  if (uniqueTokens.length === 0) {
    const empty = document.createElement("span");
    empty.className = "text-[11px] text-slate-400 italic";
    empty.textContent = dict.noTokensDetected;
    elements.detectedLpTokensList.appendChild(empty);
    return;
  }

  uniqueTokens.forEach((token) => {
    const cleanDigits = token.replace(/\D/g, "");
    const isCurrency = /\$|r\$/i.test(token);
    const isVerifiedMatch = cleanDigits && verifiedDigitsSet.has(cleanDigits);

    const badge = document.createElement("span");
    if (isVerifiedMatch) {
      badge.className =
        "inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-2xs";
      badge.textContent = `${token} ✓`;
    } else if (isCurrency) {
      badge.className =
        "inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-amber-100 text-amber-800 border border-amber-200 shadow-2xs";
      badge.textContent = token;
    } else {
      badge.className =
        "inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200";
      badge.textContent = token;
    }
    elements.detectedLpTokensList.appendChild(badge);
  });
}

// Highlight problematic input fields directly in the RSA Editor
function highlightEditorIssues(issues, rawHeadlines, rawDescriptions) {
  const headlineIssuesByIndex = new Map();
  const descIssuesByIndex = new Map();

  issues.forEach((issue) => {
    if (issue.location && issue.location.field === "headline" && issue.location.index !== null) {
      const existing = headlineIssuesByIndex.get(issue.location.index) || [];
      existing.push(issue);
      headlineIssuesByIndex.set(issue.location.index, existing);
    } else if (
      issue.location &&
      issue.location.field === "description" &&
      issue.location.index !== null
    ) {
      const existing = descIssuesByIndex.get(issue.location.index) || [];
      existing.push(issue);
      descIssuesByIndex.set(issue.location.index, existing);
    }
  });

  const headlineRows = elements.headlinesContainer.querySelectorAll(".headline-row");
  headlineRows.forEach((row, idx) => {
    const input = row.querySelector(".headline-input");
    const counter = row.querySelector(".counter-badge");
    const rulePill = row.querySelector(".headline-rule-pill");
    const rowIssues = headlineIssuesByIndex.get(idx) || [];
    const valLen = (rawHeadlines[idx] || "").length;

    if (rowIssues.length > 0) {
      const hasError = rowIssues.some((i) => i.severity === "error");
      const ruleIds = rowIssues.map((i) => i.rule_id).join(",");
      input.className = hasError
        ? "headline-input w-full pl-2.5 pr-14 py-1.5 text-xs rounded-lg border border-rose-200 bg-rose-50 text-slate-900 font-medium focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-sans"
        : "headline-input w-full pl-2.5 pr-14 py-1.5 text-xs rounded-lg border border-amber-200 bg-amber-50 text-slate-900 font-medium focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-sans";
      rulePill.textContent = ruleIds;
      rulePill.className = hasError
        ? "headline-rule-pill px-1 rounded text-[10px] font-mono font-bold bg-rose-100 text-rose-800 border border-rose-200"
        : "headline-rule-pill px-1 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-800 border border-amber-200";
    } else {
      input.className =
        "headline-input w-full pl-2.5 pr-14 py-1.5 text-xs rounded-lg border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-sans";
      rulePill.className = "headline-rule-pill hidden";
    }

    counter.textContent = `${valLen}/30`;
    counter.className =
      valLen > 30
        ? "counter-badge text-[10px] font-mono font-bold text-rose-600"
        : "counter-badge text-[10px] font-mono font-medium text-slate-400";
  });

  const descRows = elements.descriptionsContainer.querySelectorAll(".description-row");
  descRows.forEach((row, idx) => {
    const textarea = row.querySelector(".desc-input");
    const counter = row.querySelector(".desc-counter");
    const rowIssues = descIssuesByIndex.get(idx) || [];
    const valLen = (rawDescriptions[idx] || "").length;

    if (rowIssues.length > 0) {
      textarea.className =
        "desc-input w-full p-2 text-xs rounded-md border border-rose-200 bg-rose-50 focus:outline-hidden focus:ring-2 focus:ring-indigo-500";
    } else {
      textarea.className =
        "desc-input w-full p-2 text-xs rounded-md border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500";
    }

    counter.textContent = `${valLen}/90`;
    counter.className =
      valLen > 90
        ? "desc-counter text-[10px] font-mono font-bold text-rose-600"
        : "desc-counter text-[10px] font-mono font-medium text-slate-400";
  });
}

// In-Browser Instant Hybrid Evaluation Engine (0ms feedback)
function runLiveEvaluation(highlightAnimation = false) {
  const lang = state.lang;
  const headlineInputs = elements.headlinesContainer.querySelectorAll(".headline-input");
  const rawHeadlines = Array.from(headlineInputs).map((i) => i.value);
  const activeHeadlines = rawHeadlines.map((h) => h.trim()).filter(Boolean);

  const descInputs = elements.descriptionsContainer.querySelectorAll(".desc-input");
  const rawDescriptions = Array.from(descInputs).map((d) => d.value);
  const activeDescriptions = rawDescriptions.map((d) => d.trim()).filter(Boolean);

  const primaryService = elements.primaryServiceInput.value.trim();
  const finalUrl = elements.finalUrlInput.value.trim();
  const path1 = elements.path1Input.value.trim();
  const path2 = elements.path2Input.value.trim();
  const lpContext = elements.lpContextInput.value.trim();

  renderLpHighlightedAndTokens(lpContext, rawHeadlines);

  const lpDigits = new Set(
    (lpContext.match(/\d[\d.,]*/g) || []).map((m) => m.replace(/\D/g, "")).filter(Boolean)
  );

  const deterministicIssues = [];
  const llmIssues = [];
  const droppedIssues = [];
  const suggestions = [];

  // 1. DETERMINISTIC RULES D01–D11

  if (activeHeadlines.length < 3 || activeHeadlines.length > 15) {
    deterministicIssues.push({
      rule_id: "D01",
      severity: "error",
      message:
        lang === "pt"
          ? "Anúncios responsivos de pesquisa devem ter entre 3 e 15 títulos."
          : "Responsive Search Ads must have between 3 and 15 headlines.",
      location: null,
      source: "code",
    });
  }

  // D02: Recommended headline coverage (3 to 14 headlines)
  if (activeHeadlines.length >= 3 && activeHeadlines.length < 15) {
    deterministicIssues.push({
      rule_id: "D02",
      severity: "warning",
      message:
        lang === "pt"
          ? "Menos de 15 títulos fornecidos; adicione todos os 15 para rotação ideal."
          : "Fewer than 15 headlines provided; add all 15 headlines for optimal rotation.",
      location: null,
      source: "code",
    });
  }

  // D03: Description count bounds (2 to 4)
  if (activeDescriptions.length < 2 || activeDescriptions.length > 4) {
    deterministicIssues.push({
      rule_id: "D03",
      severity: "error",
      message:
        lang === "pt"
          ? "Anúncios responsivos de pesquisa devem ter entre 2 e 4 descrições."
          : "Responsive Search Ads must have between 2 and 4 descriptions.",
      location: null,
      source: "code",
    });
  }

  // D04: Headline max 30 chars (+ validated rewrite so 1-Click Fix resolves D04 too!)
  rawHeadlines.forEach((h, idx) => {
    if (h.trim() && h.length > 30) {
      deterministicIssues.push({
        rule_id: "D04",
        severity: "error",
        message:
          lang === "pt"
            ? `O título excede o limite de 30 caracteres (${h.length}/30).`
            : `Headline exceeds the 30-character limit (${h.length}/30).`,
        location: { field: "headline", index: idx },
        source: "code",
      });

      const cleanService = (primaryService || "Dental Implants").slice(0, 21);
      const shortRewrite =
        lang === "pt" ? `${cleanService} Avançado`.slice(0, 30) : `Advanced ${cleanService}`.slice(0, 30);
      suggestions.push({
        location: { field: "headline", index: idx },
        original: h,
        suggested: shortRewrite,
        reason:
          lang === "pt"
            ? "Reduz título para dentro do limite de 30 caracteres (D04)."
            : "Shortens headline to comply with the 30-char limit (D04).",
      });
    }
  });

  // D05: Description max 90 chars
  rawDescriptions.forEach((d, idx) => {
    if (d.trim() && d.length > 90) {
      deterministicIssues.push({
        rule_id: "D05",
        severity: "error",
        message:
          lang === "pt"
            ? "A descrição excede o limite de 90 caracteres."
            : "Description exceeds the 90-character limit.",
        location: { field: "description", index: idx },
        source: "code",
      });
    }
  });

  // D06: Display paths max 15 chars
  if (path1.length > 15) {
    deterministicIssues.push({
      rule_id: "D06",
      severity: "error",
      message:
        lang === "pt"
          ? "O caminho de exibição excede o limite de 15 caracteres."
          : "Display path exceeds the 15-character limit.",
      location: { field: "path1", index: null },
      source: "code",
    });
  }
  if (path2.length > 15) {
    deterministicIssues.push({
      rule_id: "D06",
      severity: "error",
      message:
        lang === "pt"
          ? "O caminho de exibição excede o limite de 15 caracteres."
          : "Display path exceeds the 15-character limit.",
      location: { field: "path2", index: null },
      source: "code",
    });
  }

  // D11: Final URL HTTPS
  if (!finalUrl.startsWith("https://") || /\s/.test(finalUrl)) {
    deterministicIssues.push({
      rule_id: "D11",
      severity: "error",
      message:
        lang === "pt"
          ? "O URL final deve ser um URL HTTPS válido."
          : "Final URL must be a valid HTTPS URL.",
      location: { field: "final_url", index: null },
      source: "code",
    });
  }

  // D08: Duplicate headlines (+ validated rewrite)
  const seenHeadlines = new Set();
  rawHeadlines.forEach((h, idx) => {
    const trimmed = h.trim();
    if (!trimmed) return;
    const norm = trimmed.toLowerCase();
    if (seenHeadlines.has(norm)) {
      deterministicIssues.push({
        rule_id: "D08",
        severity: "error",
        message:
          lang === "pt" ? "Título duplicado detectado." : "Duplicate headline detected.",
        location: { field: "headline", index: idx },
        source: "code",
      });

      const cleanService = (primaryService || "Service").slice(0, 20);
      const uniqueRewrite =
        lang === "pt" ? `Equipe de ${cleanService}`.slice(0, 30) : `Certified ${cleanService}`.slice(0, 30);
      suggestions.push({
        location: { field: "headline", index: idx },
        original: h,
        suggested: uniqueRewrite,
        reason:
          lang === "pt"
            ? "Substitui título duplicado por variação única (D08)."
            : "Replaces duplicate headline with unique asset (D08).",
      });
    } else {
      seenHeadlines.add(norm);
    }
  });

  // D09: Repeated punctuation / exclamation in headlines
  rawHeadlines.forEach((h, idx) => {
    if (h.includes("!") || REPEATED_PUNCTUATION_PATTERN.test(h)) {
      deterministicIssues.push({
        rule_id: "D09",
        severity: "error",
        message:
          lang === "pt"
            ? "Ponto de exclamação ou pontuação repetida não permitida no título."
            : "Exclamation mark or repeated punctuation is not allowed in headlines.",
        location: { field: "headline", index: idx },
        source: "code",
      });
    }
  });

  // D10: ALL CAPS words
  rawHeadlines.forEach((h, idx) => {
    const caps = h.match(UPPERCASE_WORD_PATTERN) || [];
    if (caps.some((w) => !ALLOWED_ACRONYMS.has(w))) {
      deterministicIssues.push({
        rule_id: "D10",
        severity: "warning",
        message:
          lang === "pt"
            ? "Uso excessivo de maiúsculas detectado; evite CAIXA ALTA."
            : "Excessive capitalization detected; avoid ALL CAPS words.",
        location: { field: "headline", index: idx },
        source: "code",
      });
    }
  });

  // D07: Primary service mention in top 5 headlines
  if (primaryService && activeHeadlines.length >= 5) {
    const normService = primaryService.toLowerCase();
    const serviceWords = normService.split(/\s+/).filter((w) => w.length >= 3);
    const top5 = activeHeadlines.slice(0, 5);

    let matchCount = 0;
    top5.forEach((h) => {
      const normH = h.toLowerCase();
      if (normH.includes(normService)) {
        matchCount++;
      } else if (serviceWords.length > 0) {
        const matchesWord = serviceWords.filter(
          (w) => normH.includes(w) || normH.includes(w.substring(0, 5))
        ).length;
        if (matchesWord >= Math.min(2, serviceWords.length)) {
          matchCount++;
        }
      }
    });

    if (matchCount < 3) {
      deterministicIssues.push({
        rule_id: "D07",
        severity: "warning",
        message:
          lang === "pt"
            ? "Menos de 3 dos primeiros 5 títulos mencionam o serviço principal."
            : "Fewer than 3 of the first 5 headlines mention the primary service.",
        location: null,
        source: "code",
      });
    }
  }

  // 2. SEMANTIC RULES A01–A03 & SERVER CODE AUTHORITY FILTER

  // A01: Unverified price or offer claim in headline
  rawHeadlines.forEach((h, idx) => {
    const match = h.match(PRICE_CLAIM_PATTERN);
    if (match) {
      const offerStr = match[0];
      const offerDigits = (offerStr.match(/\d+/g) || []).join("");
      const isVerifiedInLp =
        offerDigits && (lpDigits.has(offerDigits) || lpContext.includes(offerDigits));

      const rawA01Issue = {
        rule_id: "A01",
        severity: "error",
        message:
          lang === "pt"
            ? `Preço ou oferta '${offerStr}' no título não confirmado na landing page.`
            : `Price or offer '${offerStr}' in headline not verified in landing page.`,
        location: { field: "headline", index: idx },
        source: "llm",
      };

      if (!isVerifiedInLp) {
        llmIssues.push(rawA01Issue);

        const cleanService = (primaryService || "Service").slice(0, 22);
        const rewrite = lang === "pt" ? `${cleanService} Hoje` : `${cleanService} Today`;
        suggestions.push({
          location: { field: "headline", index: idx },
          original: h,
          suggested: rewrite.slice(0, 30),
          reason:
            lang === "pt"
              ? "Remove preço não verificado na página (A01)."
              : "Removes unverified price claim (A01).",
        });
      } else {
        droppedIssues.push(rawA01Issue);
      }
    }
  });

  // A02: Missing Call-to-Action in descriptions
  if (activeDescriptions.length > 0 && !activeDescriptions.some((d) => CTA_PATTERN.test(d))) {
    llmIssues.push({
      rule_id: "A02",
      severity: "warning",
      message:
        lang === "pt"
          ? "Nenhuma descrição possui uma chamada para ação (CTA) clara."
          : "None of the descriptions contain a clear Call-to-Action (CTA).",
      location: { field: "description", index: 0 },
      source: "llm",
    });

    const cleanService = (primaryService || "service").toLowerCase();
    const ctaRewrite =
      lang === "pt"
        ? `Agende sua avaliação de ${cleanService} com nossa equipe hoje.`
        : `Book your ${cleanService} consultation with our team today.`;
    suggestions.push({
      location: { field: "description", index: 0 },
      original: activeDescriptions[0] || "",
      suggested: ctaRewrite.slice(0, 90),
      reason:
        lang === "pt"
          ? "Adiciona chamada para ação clara (A02)."
          : "Adds a clear call to action (A02).",
    });
  }

  // A03: Absolute outcome guarantee
  rawHeadlines.forEach((h, idx) => {
    if (GUARANTEE_PATTERN.test(h)) {
      llmIssues.push({
        rule_id: "A03",
        severity: "warning",
        message:
          lang === "pt"
            ? "Promessa absoluta ou garantia de resultado no título."
            : "Absolute outcome guarantee or regulated promise in headline.",
        location: { field: "headline", index: idx },
        source: "llm",
      });

      const cleanService = primaryService || "Care";
      const rewrite =
        lang === "pt"
          ? `Especialistas em ${cleanService}`.slice(0, 30)
          : `Trusted ${cleanService} Care`.slice(0, 30);
      suggestions.push({
        location: { field: "headline", index: idx },
        original: h,
        suggested: rewrite,
        reason:
          lang === "pt"
            ? "Substitui garantia absoluta por afirmação adequada (A03)."
            : "Replaces absolute guarantee with compliant phrasing (A03).",
      });
    }
  });

  const allIssues = [...deterministicIssues, ...llmIssues];
  const errors = allIssues.filter((i) => i.severity === "error").length;
  const warnings = allIssues.filter((i) => i.severity === "warning").length;
  const score = Math.max(0, 100 - 15 * errors - 5 * warnings);
  const grade10 = Number((score / 10).toFixed(1));
  const passed = score >= 75 && errors === 0;

  const result = {
    score: score,
    grade_10: grade10,
    passed: passed,
    issues: allIssues,
    suggestions: suggestions,
    discarded_suggestions_count: 0,
    rules_checked: [
      "D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11",
      "A01", "A02", "A03",
    ],
    model: "Hybrid Pipeline: Deterministic + LLM",
    degraded_reason: null,
  };

  state.lastResult = result;
  state.lastSuggestions = suggestions;

  highlightEditorIssues(allIssues, rawHeadlines, rawDescriptions);
  renderAuditReport(result, droppedIssues);
  elements.jsonInspectorPre.textContent = JSON.stringify(result, null, 2);

  if (highlightAnimation) {
    elements.heroScore.classList.add("scale-110", "transition-transform");
    setTimeout(() => {
      elements.heroScore.classList.remove("scale-110");
    }, 200);
  }
}

// Render the Audit Report Card
function renderAuditReport(result, droppedIssues = []) {
  const dict = TRANSLATIONS[state.lang];

  elements.heroGrade10.textContent = (result.grade_10 !== undefined ? result.grade_10 : 0.0).toFixed(1);
  elements.heroScore.textContent = result.score !== undefined ? result.score : 0;

  if (result.passed) {
    elements.statusPassBadge.className =
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800";
    elements.statusPassBadge.textContent = "PASSED";
    elements.heroScore.className = "text-2xl sm:text-3xl font-extrabold text-emerald-600";
  } else {
    elements.statusPassBadge.className =
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800";
    elements.statusPassBadge.textContent = "REJECTED";
    elements.heroScore.className = "text-2xl sm:text-3xl font-extrabold text-rose-600";
  }

  // Show/hide 1-Click Fix All Hero Button
  if (result.suggestions && result.suggestions.length > 0) {
    elements.heroFixAllContainer.classList.remove("hidden");
    elements.fixAllHeroBtn.textContent = dict.fixAllBtnText;
  } else {
    elements.heroFixAllContainer.classList.add("hidden");
  }

  elements.activeModelBadge.textContent = result.model || "Hybrid Pipeline: Deterministic + LLM";

  // Code Authority Filter Callout (Stripped False Positives)
  if (droppedIssues && droppedIssues.length > 0) {
    elements.authorityFilterCallout.classList.remove("hidden");
    elements.droppedIssuesList.innerHTML = "";
    droppedIssues.forEach((issue) => {
      const item = document.createElement("div");
      item.className =
        "flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded-lg bg-white border border-emerald-200 text-xs gap-1.5 shadow-2xs";
      item.innerHTML = `
        <div class="flex items-center space-x-2">
          <span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-100 text-rose-700">${issue.rule_id}</span>
          <span class="text-slate-700 font-medium line-through text-slate-400">${escapeHtml(issue.message)}</span>
        </div>
        <span class="self-start sm:self-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800 shrink-0">
          ${dict.discardedBadge}
        </span>
      `;
      elements.droppedIssuesList.appendChild(item);
    });
  } else {
    elements.authorityFilterCallout.classList.add("hidden");
  }

  // Issues List
  elements.issuesList.innerHTML = "";
  const issues = result.issues || [];
  elements.issuesCountBadge.textContent = `${issues.length} issue${issues.length === 1 ? "" : "s"}`;

  if (issues.length === 0) {
    const perfectCard = document.createElement("div");
    perfectCard.className =
      "p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium";
    perfectCard.textContent = dict.perfectScoreText;
    elements.issuesList.appendChild(perfectCard);
  } else {
    issues.forEach((issue) => {
      const item = document.createElement("div");
      item.className = "p-3 rounded-lg border border-slate-200 bg-white space-y-1.5 shadow-2xs";

      const topRow = document.createElement("div");
      topRow.className = "flex items-center justify-between";

      const leftBadges = document.createElement("div");
      leftBadges.className = "flex items-center space-x-1.5";

      const ruleBadge = document.createElement("span");
      ruleBadge.className =
        issue.severity === "error"
          ? "px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-100 text-rose-800"
          : "px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-800";
      ruleBadge.textContent = issue.rule_id;
      leftBadges.appendChild(ruleBadge);

      const sevBadge = document.createElement("span");
      sevBadge.className =
        issue.severity === "error"
          ? "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200"
          : "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200";
      sevBadge.textContent =
        issue.severity === "error" ? dict.severityError : dict.severityWarning;
      leftBadges.appendChild(sevBadge);

      if (issue.location && issue.location.field) {
        const locBadge = document.createElement("span");
        locBadge.className =
          "px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-700 font-semibold";
        locBadge.textContent =
          issue.location.index !== null && issue.location.index !== undefined
            ? `${issue.location.field} #${issue.location.index + 1}`
            : issue.location.field;
        leftBadges.appendChild(locBadge);
      }

      const provBadge = document.createElement("span");
      if (issue.source === "code") {
        provBadge.className =
          "px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200";
        provBadge.textContent = dict.codeProvenance;
      } else {
        provBadge.className =
          "px-2 py-0.5 rounded-full text-[10px] font-semibold bg-purple-50 text-purple-700 border border-purple-200";
        provBadge.textContent = dict.llmProvenance;
      }

      topRow.appendChild(leftBadges);
      topRow.appendChild(provBadge);

      const msg = document.createElement("p");
      msg.className = "text-xs text-slate-700 leading-normal";
      msg.textContent = issue.message;

      item.appendChild(topRow);
      item.appendChild(msg);
      elements.issuesList.appendChild(item);
    });
  }

  // Suggestions Card
  const suggestions = result.suggestions || [];
  elements.suggestionsCountBadge.textContent = `${suggestions.length} rewrite${
    suggestions.length === 1 ? "" : "s"
  }`;

  if (suggestions.length === 0) {
    elements.suggestionsCard.classList.add("hidden");
  } else {
    elements.suggestionsCard.classList.remove("hidden");
    elements.suggestionsList.innerHTML = "";

    suggestions.forEach((sugg) => {
      const card = document.createElement("div");
      card.className = "p-3 rounded-lg border border-indigo-100 bg-indigo-50/40 space-y-2 shadow-2xs";

      const locText =
        sugg.location && sugg.location.field
          ? `${sugg.location.field} #${(sugg.location.index ?? 0) + 1}`
          : "Asset";

      const locHeader = document.createElement("div");
      locHeader.className = "flex items-center justify-between text-[11px] text-slate-600 font-semibold";
      locHeader.innerHTML = `
        <span class="font-mono text-indigo-700 bg-indigo-100 px-1.5 py-0.2 rounded">${locText}</span>
        <span class="text-slate-400 font-mono text-[10px]">Max: ${
          sugg.location?.field === "description" ? "90" : "30"
        } chars</span>
      `;

      const diffBox = document.createElement("div");
      diffBox.className = "text-xs space-y-1";
      diffBox.innerHTML = `
        <div class="flex items-start space-x-1.5 text-rose-700">
          <span class="text-[10px] font-mono font-bold bg-rose-100 px-1 rounded shrink-0">-</span>
          <span class="line-through">${escapeHtml(sugg.original)}</span>
        </div>
        <div class="flex items-start space-x-1.5 text-emerald-800 font-medium">
          <span class="text-[10px] font-mono font-bold bg-emerald-100 px-1 rounded shrink-0">+</span>
          <span>${escapeHtml(sugg.suggested)}</span>
          <span class="ml-auto text-[10px] font-mono text-emerald-700 font-bold bg-emerald-100/80 px-1.5 py-0.2 rounded">
            ${sugg.suggested.length} chars
          </span>
        </div>
      `;

      const bottomRow = document.createElement("div");
      bottomRow.className = "pt-1 flex items-center justify-between gap-2";

      const reason = document.createElement("span");
      reason.className = "text-[11px] text-slate-500 italic";
      reason.textContent = sugg.reason || "";

      const applyBtn = document.createElement("button");
      applyBtn.type = "button";
      applyBtn.className =
        "px-2.5 py-1 rounded text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-2xs transition shrink-0";
      applyBtn.textContent = dict.applyRewriteBtn;

      applyBtn.addEventListener("click", () => {
        applySuggestion(sugg, applyBtn);
      });

      bottomRow.appendChild(reason);
      bottomRow.appendChild(applyBtn);

      card.appendChild(locHeader);
      card.appendChild(diffBox);
      card.appendChild(bottomRow);
      elements.suggestionsList.appendChild(card);
    });
  }
}

// Apply a single Rewrite Suggestion
function applySuggestionToDom(sugg) {
  if (!sugg.location) return;
  const { field, index } = sugg.location;

  if (field === "headline" && index !== null && index !== undefined) {
    const row = elements.headlinesContainer.querySelector(`.headline-row[data-index="${index}"]`);
    if (row) {
      const input = row.querySelector(".headline-input");
      if (input) {
        input.value = sugg.suggested;
        input.classList.add("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        setTimeout(() => {
          input.classList.remove("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        }, 1600);
      }
    }
  } else if (field === "description" && index !== null && index !== undefined) {
    const row = elements.descriptionsContainer.querySelector(
      `.description-row[data-index="${index}"]`
    );
    if (row) {
      const textarea = row.querySelector(".desc-input");
      if (textarea) {
        textarea.value = sugg.suggested;
        textarea.classList.add("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        setTimeout(() => {
          textarea.classList.remove("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        }, 1600);
      }
    }
  }
}

function applySuggestion(sugg, buttonElement) {
  const dict = TRANSLATIONS[state.lang];
  applySuggestionToDom(sugg);

  if (buttonElement) {
    buttonElement.textContent = dict.rewriteApplied;
    buttonElement.className =
      "px-2.5 py-1 rounded text-xs font-bold bg-emerald-600 text-white shrink-0";
  }

  runLiveEvaluation(true);
}

// Apply ALL Rewrite Suggestions in 1 Click
function applyAllSuggestions() {
  const suggestions = [...state.lastSuggestions];
  suggestions.forEach((sugg) => applySuggestionToDom(sugg));
  runLiveEvaluation(true);
}

// Call Live Cloud Run FastAPI Backend (POST /v1/grade)
async function callCloudRunApi() {
  const dict = TRANSLATIONS[state.lang];
  const headlineInputs = elements.headlinesContainer.querySelectorAll(".headline-input");
  const headlines = Array.from(headlineInputs)
    .map((i) => i.value.trim())
    .filter(Boolean);

  const descInputs = elements.descriptionsContainer.querySelectorAll(".desc-input");
  const descriptions = Array.from(descInputs)
    .map((d) => d.value.trim())
    .filter(Boolean);

  const payload = {
    headlines,
    descriptions,
    path1: elements.path1Input.value.trim() || null,
    path2: elements.path2Input.value.trim() || null,
    final_url: elements.finalUrlInput.value.trim(),
    primary_service: elements.primaryServiceInput.value.trim(),
    lp_context: elements.lpContextInput.value.trim(),
    lang: state.lang,
  };

  elements.callCloudRunBtn.textContent = dict.callingCloudRunBtn;
  const t0 = performance.now();

  try {
    const resp = await fetch(CLOUD_RUN_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const latencyMs = Math.round(performance.now() - t0);
    const data = await resp.json();

    elements.apiStatusBadge.textContent = `HTTP ${resp.status} • ${latencyMs}ms`;
    elements.apiStatusBadge.className = resp.ok
      ? "text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200"
      : "text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800 border border-rose-200";

    elements.jsonInspectorPre.textContent = JSON.stringify(data, null, 2);
    elements.jsonInspectorDrawer.classList.remove("hidden");
  } catch (err) {
    elements.apiStatusBadge.textContent = "Offline Fallback Active";
    elements.jsonInspectorDrawer.classList.remove("hidden");
  } finally {
    elements.callCloudRunBtn.textContent = dict.callCloudRunBtn;
  }
}

// Start application on DOM ready
document.addEventListener("DOMContentLoaded", init);
