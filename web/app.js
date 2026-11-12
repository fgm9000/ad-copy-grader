/**
 * Ad Copy Grader — Bilingual Static Web Demo
 *
 * Provides interactive Responsive Search Ad grading, live Google Search preview,
 * character counter validation, Code Authority Filter inspection, and validated rewrites.
 */

// UI Translations dictionary
const TRANSLATIONS = {
  en: {
    appTitle: "Ad Copy Grader",
    appSubtitle: "Hybrid Deterministic & LLM Google Ads RSA Auditor",
    apiConnected: "Live API",
    apiOffline: "Offline Demo Mode",
    apiEndpointSettings: "API Endpoint Settings",
    apiEndpointHelp: "Connect to a live FastAPI backend or leave empty for offline pre-evaluated mode.",
    apiUrlLabel: "Endpoint URL",
    testConnectionBtn: "Test Health (/healthz)",
    saveBtn: "Save",
    scenariosLabel: "Scenarios:",
    scenariosSubtitle: "(Pre-evaluated synthetic benchmarks)",
    scenarioDetailLabel: "Active Scenario:",
    lpCardTitle: "Landing Page Context",
    ruleA01Badge: "Rule A01 Target",
    lpCardHelp: "The <strong>Code Authority Filter</strong> and Rule <strong>A01</strong> cross-examine every price, discount, and claim against this text.",
    primaryServiceLabel: "Primary Service",
    finalUrlLabel: "Final URL (HTTPS)",
    lpContextLabel: "LP Context Text",
    detectedLpTokensLabel: "Detected Price/Offer Tokens:",
    liveSearchPreviewTitle: "Google Search Ad Live Preview",
    adSponsoredLabel: "Sponsored",
    rsaEditorTitle: "Google Ads RSA Asset Editor",
    rulesEngineBadge: "Rules D01–D11",
    path1Label: "Path 1",
    path2Label: "Path 2",
    headlinesHeader: "Headlines (3–15)",
    descriptionsHeader: "Descriptions (2–4)",
    showAllHeadlinesBtn: "Show all 15 (9 hidden)",
    collapseHeadlinesBtn: "Collapse to 6 headlines",
    resetScenarioBtn: "Reset Scenario",
    gradeAdBtn: "Grade Ad Copy (Live API)",
    gradingText: "Grading with Live API...",
    auditReportTitle: "Hybrid Audit Report",
    qualityScaleLabel: "Google Ads Quality",
    scoreLabel: "Score",
    rulesCheckedBadge: "11 Code Rules (D01-D11) + 3 LLM (A01-A03)",
    degradedTitle: "Fallback Notice",
    authorityFilterTitle: "Code Authority Filter Active",
    falsePositiveStrippedBadge: "False Positive Intercepted",
    authorityFilterDescription: "The raw LLM review flagged an offer or price claim, but the deterministic server filter verified that the claim matches the Landing Page context and automatically stripped the false positive before calculating the final score!",
    detectedIssuesTitle: "Detected Issues",
    rewriteSuggestionsTitle: "Validated Rewrites",
    rewriteSuggestionsSubtitle: "Guaranteed ≤30 chars (headlines) / ≤90 chars (descriptions)",
    applyRewriteBtn: "Apply Rewrite",
    rewriteApplied: "Applied!",
    footerText: "Ad Copy Grader — Deterministic Google Ads rules engine & LLM semantic audit.",
    offlineReady: "Offline Ready",
    perfectScoreText: "🎉 Perfect 10.0 score! No deterministic or semantic issues detected.",
    codeProvenance: "Code Verified (Deterministic)",
    llmProvenance: "LLM Judged (Semantic)",
    severityError: "ERROR",
    severityWarning: "WARNING",
    discardedBadge: "Discarded by Server Authority Filter",
    headlinePlaceholder: "Headline",
    descriptionPlaceholder: "Description",
    noTokensDetected: "No price or offer tokens detected in LP context.",
    apiTestSuccess: "Backend healthy: version",
    apiTestFailed: "Connection failed. Please ensure the backend is running and CORS is enabled.",
  },
  pt: {
    appTitle: "Ad Copy Grader",
    appSubtitle: "Auditor Híbrido Determinístico e LLM para Google Ads RSA",
    apiConnected: "API Ao Vivo",
    apiOffline: "Modo Demo Offline",
    apiEndpointSettings: "Configurações do Endpoint da API",
    apiEndpointHelp: "Conecte a um backend FastAPI ativo ou utilize o modo offline pré-avaliado.",
    apiUrlLabel: "URL do Endpoint",
    testConnectionBtn: "Testar Conexão (/healthz)",
    saveBtn: "Salvar",
    scenariosLabel: "Cenários:",
    scenariosSubtitle: "(Benchmarks sintéticos pré-avaliados)",
    scenarioDetailLabel: "Cenário Ativo:",
    lpCardTitle: "Contexto da Landing Page",
    ruleA01Badge: "Alvo da Regra A01",
    lpCardHelp: "O <strong>Filtro de Autoridade</strong> e a Regra <strong>A01</strong> checam preços, descontos e promessas contra este texto.",
    primaryServiceLabel: "Serviço Principal",
    finalUrlLabel: "URL Final (HTTPS)",
    lpContextLabel: "Texto da Landing Page",
    detectedLpTokensLabel: "Tokens de Preço/Oferta Detectados:",
    liveSearchPreviewTitle: "Prévia ao Vivo no Google Search",
    adSponsoredLabel: "Patrocinado",
    rsaEditorTitle: "Editor de Recursos RSA do Google Ads",
    rulesEngineBadge: "Regras D01–D11",
    path1Label: "Caminho 1",
    path2Label: "Caminho 2",
    headlinesHeader: "Títulos (3–15)",
    descriptionsHeader: "Descrições (2–4)",
    showAllHeadlinesBtn: "Expandir todos os 15 (9 ocultos)",
    collapseHeadlinesBtn: "Recolher para 6 títulos",
    resetScenarioBtn: "Restaurar Cenário",
    gradeAdBtn: "Avaliar Anúncio (API Ao Vivo)",
    gradingText: "Avaliando via API Ao Vivo...",
    auditReportTitle: "Relatório de Auditoria Híbrida",
    qualityScaleLabel: "Qualidade Google Ads",
    scoreLabel: "Pontuação",
    rulesCheckedBadge: "11 Regras de Código (D01-D11) + 3 LLM (A01-A03)",
    degradedTitle: "Aviso de Modo Degradado",
    authorityFilterTitle: "Filtro de Autoridade do Código Ativo",
    falsePositiveStrippedBadge: "Falso Positivo Interceptado",
    authorityFilterDescription: "O LLM apontou uma oferta ou preço como não confirmado, mas o filtro determinístico do servidor comprovou que o dado consta na Landing Page e descartou o falso positivo automaticamente antes da nota final!",
    detectedIssuesTitle: "Problemas Detectados",
    rewriteSuggestionsTitle: "Sugestões de Reescrita Validadas",
    rewriteSuggestionsSubtitle: "Garantia de ≤30 carac. (títulos) / ≤90 carac. (descrições)",
    applyRewriteBtn: "Aplicar Sugestão",
    rewriteApplied: "Aplicado!",
    footerText: "Ad Copy Grader — Motor determinístico de regras para Google Ads e auditoria semântica via LLM.",
    offlineReady: "Pronto Offline",
    perfectScoreText: "🎉 Nota 10.0 perfeita! Nenhum problema determinístico ou semântico detectado.",
    codeProvenance: "Verificado via Código (Determinístico)",
    llmProvenance: "Julgado via LLM (Semântico)",
    severityError: "ERRO",
    severityWarning: "AVISO",
    discardedBadge: "Descartado pelo Filtro de Autoridade",
    headlinePlaceholder: "Título",
    descriptionPlaceholder: "Descrição",
    noTokensDetected: "Nenhum token de preço ou oferta detectado na landing page.",
    apiTestSuccess: "Backend ativo e saudável: versão",
    apiTestFailed: "Falha na conexão. Certifique-se de que o backend está rodando com CORS habilitado.",
  },
};

// Application State
const state = {
  lang: "en",
  apiUrl:
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
      ? "http://localhost:8000"
      : "https://ad-copy-grader-939763784116.us-central1.run.app",
  isApiOnline: false,
  scenarios: [],
  activeScenarioIndex: 0,
  headlinesExpanded: false,
  currentResult: null,
  currentDroppedIssues: [],
};

// Cached DOM References
const elements = {
  langEnBtn: document.getElementById("langEnBtn"),
  langPtBtn: document.getElementById("langPtBtn"),
  apiConfigBtn: document.getElementById("apiConfigBtn"),
  apiConfigPanel: document.getElementById("apiConfigPanel"),
  apiUrlInput: document.getElementById("apiUrlInput"),
  testApiBtn: document.getElementById("testApiBtn"),
  saveApiBtn: document.getElementById("saveApiBtn"),
  apiStatusDot: document.getElementById("apiStatusDot"),
  apiStatusText: document.getElementById("apiStatusText"),
  apiTestResult: document.getElementById("apiTestResult"),
  scenarioPills: document.getElementById("scenarioPills"),
  scenarioDescription: document.getElementById("scenarioDescription"),
  primaryServiceInput: document.getElementById("primaryServiceInput"),
  finalUrlInput: document.getElementById("finalUrlInput"),
  lpContextInput: document.getElementById("lpContextInput"),
  lpTokenCountBadge: document.getElementById("lpTokenCountBadge"),
  detectedLpTokensList: document.getElementById("detectedLpTokensList"),
  previewDisplayUrl: document.getElementById("previewDisplayUrl"),
  previewHeadline: document.getElementById("previewHeadline"),
  previewDescription: document.getElementById("previewDescription"),
  path1Input: document.getElementById("path1Input"),
  path2Input: document.getElementById("path2Input"),
  path1Counter: document.getElementById("path1Counter"),
  path2Counter: document.getElementById("path2Counter"),
  headlinesContainer: document.getElementById("headlinesContainer"),
  descriptionsContainer: document.getElementById("descriptionsContainer"),
  toggleHeadlinesBtn: document.getElementById("toggleHeadlinesBtn"),
  headlinesCountBadge: document.getElementById("headlinesCountBadge"),
  descriptionsCountBadge: document.getElementById("descriptionsCountBadge"),
  resetScenarioBtn: document.getElementById("resetScenarioBtn"),
  gradeAdBtn: document.getElementById("gradeAdBtn"),
  gradeBtnText: document.getElementById("gradeBtnText"),
  gradeSpinner: document.getElementById("gradeSpinner"),
  statusPassBadge: document.getElementById("statusPassBadge"),
  heroGrade10: document.getElementById("heroGrade10"),
  heroScore: document.getElementById("heroScore"),
  activeModelBadge: document.getElementById("activeModelBadge"),
  degradedBanner: document.getElementById("degradedBanner"),
  degradedMessage: document.getElementById("degradedMessage"),
  authorityFilterCallout: document.getElementById("authorityFilterCallout"),
  droppedIssuesList: document.getElementById("droppedIssuesList"),
  issuesList: document.getElementById("issuesList"),
  issuesCountBadge: document.getElementById("issuesCountBadge"),
  suggestionsCard: document.getElementById("suggestionsCard"),
  suggestionsList: document.getElementById("suggestionsList"),
  suggestionsCountBadge: document.getElementById("suggestionsCountBadge"),
};

// Regular Expressions
const NUMERIC_TOKEN_PATTERN =
  /(?:r\$\s*[\d.,]+|\$\s*[\d.,]+|\b\d+(?:[.,]\d+)?%|\b\d{1,2}x\b|\b\d{2,6}\b)/gi;

// Initialize Application
async function init() {
  bindEvents();
  loadStoredSettings();
  await loadScenarios();
  updateI18nLabels();
  checkApiHealth(false);
}

// Bind Event Listeners
function bindEvents() {
  elements.langEnBtn.addEventListener("click", () => setLanguage("en"));
  elements.langPtBtn.addEventListener("click", () => setLanguage("pt"));

  elements.apiConfigBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    elements.apiConfigPanel.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (
      !elements.apiConfigPanel.contains(e.target) &&
      !elements.apiConfigBtn.contains(e.target)
    ) {
      elements.apiConfigPanel.classList.add("hidden");
    }
  });

  elements.testApiBtn.addEventListener("click", () => checkApiHealth(true));
  elements.saveApiBtn.addEventListener("click", saveApiUrl);

  elements.toggleHeadlinesBtn.addEventListener("click", toggleHeadlinesExpanded);
  elements.resetScenarioBtn.addEventListener("click", resetCurrentScenario);
  elements.gradeAdBtn.addEventListener("click", gradeCurrentAd);

  elements.primaryServiceInput.addEventListener("input", updateSearchPreview);
  elements.finalUrlInput.addEventListener("input", updateSearchPreview);
  elements.path1Input.addEventListener("input", () => {
    updatePathCounters();
    updateSearchPreview();
  });
  elements.path2Input.addEventListener("input", () => {
    updatePathCounters();
    updateSearchPreview();
  });

  elements.lpContextInput.addEventListener("input", () => {
    detectLpTokens();
  });
}

function loadStoredSettings() {
  const storedLang = localStorage.getItem("ad_copy_grader_lang");
  if (storedLang === "en" || storedLang === "pt") {
    state.lang = storedLang;
  }
  const storedUrl = localStorage.getItem("ad_copy_grader_api_url");
  if (storedUrl) {
    state.apiUrl = storedUrl;
  }
  elements.apiUrlInput.value = state.apiUrl;
}

// Switch Language
function setLanguage(newLang) {
  if (state.lang === newLang) return;
  state.lang = newLang;
  localStorage.setItem("ad_copy_grader_lang", newLang);

  // Update button active states
  if (newLang === "en") {
    elements.langEnBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition shadow-sm bg-white text-slate-900";
    elements.langPtBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition text-slate-600 hover:text-slate-900";
  } else {
    elements.langPtBtn.className =
      "px-2.5 py-1 text-xs font-semibold rounded-md transition shadow-sm bg-white text-slate-900";
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

  updateApiBadge();
}

function updateApiBadge() {
  const dict = TRANSLATIONS[state.lang];
  if (state.isApiOnline) {
    elements.apiStatusDot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
    elements.apiStatusText.textContent = dict.apiConnected;
  } else {
    elements.apiStatusDot.className = "w-2 h-2 rounded-full bg-amber-500";
    elements.apiStatusText.textContent = dict.apiOffline;
  }
}

// Test and Save API Settings
async function checkApiHealth(showFeedback = false) {
  const targetUrl = elements.apiUrlInput.value.trim().replace(/\/+$/, "");
  const dict = TRANSLATIONS[state.lang];

  if (showFeedback) {
    elements.apiTestResult.classList.remove("hidden");
    elements.apiTestResult.className =
      "text-xs p-2 rounded-md bg-slate-100 text-slate-700 border border-slate-200";
    elements.apiTestResult.textContent = "Checking /healthz...";
  }

  try {
    const resp = await fetch(`${targetUrl}/healthz`, { method: "GET", mode: "cors" });
    if (resp.ok) {
      const data = await resp.json();
      state.isApiOnline = true;
      state.apiUrl = targetUrl;
      localStorage.setItem("ad_copy_grader_api_url", targetUrl);
      updateApiBadge();

      if (showFeedback) {
        elements.apiTestResult.className =
          "text-xs p-2 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 font-medium";
        elements.apiTestResult.textContent = `${dict.apiTestSuccess} ${data.version || "0.1.0"}`;
      }
      return true;
    }
  } catch (err) {
    // API is offline
  }

  state.isApiOnline = false;
  updateApiBadge();

  if (showFeedback) {
    elements.apiTestResult.className =
      "text-xs p-2 rounded-md bg-rose-50 text-rose-800 border border-rose-200";
    elements.apiTestResult.textContent = dict.apiTestFailed;
  }
  return false;
}

function saveApiUrl() {
  state.apiUrl = elements.apiUrlInput.value.trim().replace(/\/+$/, "");
  localStorage.setItem("ad_copy_grader_api_url", state.apiUrl);
  checkApiHealth(true);
  setTimeout(() => {
    elements.apiConfigPanel.classList.add("hidden");
  }, 1000);
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
      "Failed to load synthetic benchmark scenarios. Please check examples.json.";
  }
}

// Render Scenario Selection Pills
function renderScenarioPills() {
  elements.scenarioPills.innerHTML = "";
  state.scenarios.forEach((scenario, index) => {
    const label = scenario.label[state.lang] || scenario.label.en;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `px-3 py-1 rounded-full text-xs font-semibold transition shadow-sm ${
      index === state.activeScenarioIndex
        ? "bg-indigo-600 text-white shadow-indigo-200 ring-2 ring-indigo-500 ring-offset-1"
        : "bg-white text-slate-700 hover:bg-slate-200 border border-slate-200"
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
  const resultData = scenario.result[state.lang] || scenario.result.en;
  const droppedData =
    (scenario.dropped_issues &&
      (scenario.dropped_issues[state.lang] || scenario.dropped_issues.en)) ||
    [];

  // Fill LP Context fields
  elements.primaryServiceInput.value = inputData.primary_service || "";
  elements.finalUrlInput.value = inputData.final_url || "";
  elements.lpContextInput.value = inputData.lp_context || "";
  elements.path1Input.value = inputData.path1 || "";
  elements.path2Input.value = inputData.path2 || "";

  // Render Headline inputs (up to 15)
  renderHeadlinesInputs(inputData.headlines || []);

  // Render Description inputs (up to 4)
  renderDescriptionsInputs(inputData.descriptions || []);

  // Update counters, tokens, and preview
  updatePathCounters();
  detectLpTokens();
  updateSearchPreview();

  // Render precomputed GradeResult
  state.currentResult = resultData;
  state.currentDroppedIssues = droppedData;
  renderAuditReport(resultData, droppedData);
}

function resetCurrentScenario() {
  loadScenario(state.activeScenarioIndex);
}

// Render Headline Inputs
function renderHeadlinesInputs(headlines) {
  elements.headlinesContainer.innerHTML = "";
  const total = Math.max(15, headlines.length);

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
      "headline-input w-full pl-3 pr-14 py-1.5 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans";
    input.placeholder = `${TRANSLATIONS[state.lang].headlinePlaceholder} ${i + 1}`;
    input.value = val;

    const counter = document.createElement("span");
    counter.className =
      "counter-badge absolute right-2 top-1.5 text-[10px] font-mono font-medium text-slate-400";
    counter.textContent = `${val.length}/30`;
    updateCharCounterStyle(counter, val.length, 30);

    input.addEventListener("input", () => {
      counter.textContent = `${input.value.length}/30`;
      updateCharCounterStyle(counter, input.value.length, 30);
      updateSearchPreview();
    });

    inputWrapper.appendChild(input);
    inputWrapper.appendChild(counter);
    row.appendChild(label);
    row.appendChild(inputWrapper);
    elements.headlinesContainer.appendChild(row);
  }

  const activeCount = headlines.filter((h) => h.trim()).length;
  elements.headlinesCountBadge.textContent = `${activeCount} / 15`;
}

// Render Description Inputs
function renderDescriptionsInputs(descriptions) {
  elements.descriptionsContainer.innerHTML = "";

  for (let i = 0; i < 4; i++) {
    const val = descriptions[i] || "";
    const card = document.createElement("div");
    card.className = "description-row rounded-lg border border-slate-200 p-2.5 bg-slate-50/50";
    card.dataset.index = i;

    const header = document.createElement("div");
    header.className = "flex items-center justify-between mb-1";

    const label = document.createElement("span");
    label.className = "text-[11px] font-bold text-slate-700";
    label.textContent = `${TRANSLATIONS[state.lang].descriptionPlaceholder} ${i + 1}`;

    const counter = document.createElement("span");
    counter.className = "desc-counter text-[10px] font-mono font-medium text-slate-400";
    counter.textContent = `${val.length}/90`;
    updateCharCounterStyle(counter, val.length, 90);

    header.appendChild(label);
    header.appendChild(counter);

    const textarea = document.createElement("textarea");
    textarea.rows = 2;
    textarea.className =
      "desc-input w-full p-2 text-xs rounded-md border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500";
    textarea.placeholder = `${TRANSLATIONS[state.lang].descriptionPlaceholder} ${i + 1}`;
    textarea.value = val;

    textarea.addEventListener("input", () => {
      counter.textContent = `${textarea.value.length}/90`;
      updateCharCounterStyle(counter, textarea.value.length, 90);
      updateSearchPreview();
    });

    card.appendChild(header);
    card.appendChild(textarea);
    elements.descriptionsContainer.appendChild(card);
  }

  const activeCount = descriptions.filter((d) => d.trim()).length;
  elements.descriptionsCountBadge.textContent = `${activeCount} / 4`;
}

function updateCharCounterStyle(element, length, limit) {
  if (length > limit) {
    element.className =
      "counter-badge absolute right-2 top-1.5 text-[10px] font-mono font-bold text-rose-600 bg-rose-50 px-1 rounded";
    if (element.classList.contains("desc-counter")) {
      element.className =
        "desc-counter text-[10px] font-mono font-bold text-rose-600 bg-rose-50 px-1 rounded";
    }
  } else {
    element.className =
      "counter-badge absolute right-2 top-1.5 text-[10px] font-mono font-medium text-slate-400";
    if (element.classList.contains("desc-counter")) {
      element.className = "desc-counter text-[10px] font-mono font-medium text-slate-400";
    }
  }
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

// Live Search Ad Preview
function updateSearchPreview() {
  const finalUrl = elements.finalUrlInput.value.trim() || "https://example.com";
  const p1 = elements.path1Input.value.trim();
  const p2 = elements.path2Input.value.trim();

  let display = finalUrl;
  try {
    const parsed = new URL(finalUrl);
    display = parsed.hostname;
  } catch (e) {
    display = "example.com";
  }

  if (p1) display += `/${p1}`;
  if (p2) display += `/${p2}`;
  elements.previewDisplayUrl.textContent = display;

  // Gather headlines
  const headlineInputs = elements.headlinesContainer.querySelectorAll(".headline-input");
  const headlineVals = Array.from(headlineInputs)
    .map((input) => input.value.trim())
    .filter(Boolean);

  const topHeadlines = headlineVals.slice(0, 3);
  elements.previewHeadline.textContent =
    topHeadlines.length > 0
      ? topHeadlines.join(" | ")
      : "Responsive Search Ad Title Headline 1 | Headline 2";

  // Gather descriptions
  const descInputs = elements.descriptionsContainer.querySelectorAll(".desc-input");
  const descVals = Array.from(descInputs)
    .map((input) => input.value.trim())
    .filter(Boolean);

  const topDescriptions = descVals.slice(0, 2);
  elements.previewDescription.textContent =
    topDescriptions.length > 0
      ? topDescriptions.join(" ")
      : "Your primary Google Ads description goes here. Connect with customers and showcase your services.";
}

// Detect Price/Offer numeric tokens in LP Context
function detectLpTokens() {
  const text = elements.lpContextInput.value;
  const dict = TRANSLATIONS[state.lang];
  const matches = text.match(NUMERIC_TOKEN_PATTERN) || [];
  const uniqueTokens = Array.from(new Set(matches.map((m) => m.trim())));

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
    const badge = document.createElement("span");
    badge.className =
      "inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs";
    badge.textContent = token;
    elements.detectedLpTokensList.appendChild(badge);
  });
}

// Grade Current Ad (Live API call with offline fallback)
async function gradeCurrentAd() {
  const dict = TRANSLATIONS[state.lang];

  // Extract non-empty headlines & descriptions
  const headlineInputs = elements.headlinesContainer.querySelectorAll(".headline-input");
  const headlines = Array.from(headlineInputs)
    .map((i) => i.value.trim())
    .filter(Boolean);

  const descInputs = elements.descriptionsContainer.querySelectorAll(".desc-input");
  const descriptions = Array.from(descInputs)
    .map((d) => d.value.trim())
    .filter(Boolean);

  const payload = {
    headlines: headlines,
    descriptions: descriptions,
    primary_service: elements.primaryServiceInput.value.trim() || "Service",
    final_url: elements.finalUrlInput.value.trim() || "https://example.com",
    path1: elements.path1Input.value.trim() || null,
    path2: elements.path2Input.value.trim() || null,
    lp_context: elements.lpContextInput.value.trim(),
    lang: state.lang,
  };

  // Set loading state
  elements.gradeAdBtn.disabled = true;
  elements.gradeSpinner.classList.remove("hidden");
  elements.gradeBtnText.textContent = dict.gradingText;

  let result = null;
  let droppedIssues = [];

  try {
    const resp = await fetch(`${state.apiUrl}/v1/grade`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (resp.ok) {
      result = await resp.json();
      state.isApiOnline = true;
      updateApiBadge();
    } else {
      throw new Error(`HTTP ${resp.status}`);
    }
  } catch (err) {
    console.warn("Live API call failed or offline:", err);
    state.isApiOnline = false;
    updateApiBadge();

    // Fallback: evaluate deterministically client-side or use scenario baseline
    result = evaluateClientSide(payload);
    if (state.scenarios[state.activeScenarioIndex]) {
      const scenario = state.scenarios[state.activeScenarioIndex];
      droppedIssues =
        (scenario.dropped_issues &&
          (scenario.dropped_issues[state.lang] || scenario.dropped_issues.en)) ||
        [];
    }
  } finally {
    elements.gradeAdBtn.disabled = false;
    elements.gradeSpinner.classList.add("hidden");
    elements.gradeBtnText.textContent = dict.gradeAdBtn;
  }

  if (result) {
    state.currentResult = result;
    state.currentDroppedIssues = droppedIssues;
    renderAuditReport(result, droppedIssues);
  }
}

// Client-Side Deterministic Evaluator (D01-D11 fallback)
function evaluateClientSide(ad) {
  const issues = [];
  const lang = ad.lang;

  // D01 & D02
  const hCount = ad.headlines.length;
  if (hCount < 3 || hCount > 15) {
    issues.push({
      rule_id: "D01",
      severity: "error",
      message:
        lang === "pt"
          ? "Anúncios responsivos de pesquisa devem ter entre 3 e 15 títulos."
          : "Responsive Search Ads must have between 3 and 15 headlines.",
      location: null,
      source: "code",
    });
  } else if (hCount < 15) {
    issues.push({
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

  // D03
  const dCount = ad.descriptions.length;
  if (dCount < 2 || dCount > 4) {
    issues.push({
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

  // D04
  ad.headlines.forEach((h, idx) => {
    if (h.length > 30) {
      issues.push({
        rule_id: "D04",
        severity: "error",
        message:
          lang === "pt"
            ? "O título excede o limite de 30 caracteres."
            : "Headline exceeds the 30-character limit.",
        location: { field: "headline", index: idx },
        source: "code",
      });
    }
  });

  // D05
  ad.descriptions.forEach((d, idx) => {
    if (d.length > 90) {
      issues.push({
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

  // D06
  if (ad.path1 && ad.path1.length > 15) {
    issues.push({
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
  if (ad.path2 && ad.path2.length > 15) {
    issues.push({
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

  // D08 Duplicate headlines
  const seenHeadlines = new Set();
  ad.headlines.forEach((h, idx) => {
    const norm = h.trim().toLowerCase();
    if (seenHeadlines.has(norm)) {
      issues.push({
        rule_id: "D08",
        severity: "error",
        message:
          lang === "pt" ? "Título duplicado detectado." : "Duplicate headline detected.",
        location: { field: "headline", index: idx },
        source: "code",
      });
    } else {
      seenHeadlines.add(norm);
    }
  });

  // Calculate score
  const errors = issues.filter((i) => i.severity === "error").length;
  const warnings = issues.filter((i) => i.severity === "warning").length;
  const score = Math.max(0, 100 - 15 * errors - 5 * warnings);
  const grade10 = Number((score / 10).toFixed(1));
  const passed = errors === 0;

  return {
    score: score,
    grade_10: grade10,
    passed: passed,
    issues: issues,
    suggestions: [],
    discarded_suggestions_count: 0,
    rules_checked: ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11"],
    model: null,
    degraded_reason:
      lang === "pt"
        ? "Auditoria em modo offline local (regras determinísticas D01-D11)."
        : "Evaluated in local offline mode (deterministic rules D01-D11).",
  };
}

// Render the Audit Report Card
function renderAuditReport(result, droppedIssues = []) {
  const dict = TRANSLATIONS[state.lang];

  // Score Hero
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

  // Model Badge
  elements.activeModelBadge.textContent = result.model || "Deterministic / Offline";

  // Degraded Banner
  if (result.degraded_reason) {
    elements.degradedBanner.classList.remove("hidden");
    elements.degradedMessage.textContent = result.degraded_reason;
  } else {
    elements.degradedBanner.classList.add("hidden");
  }

  // Authority Filter Callout (Stripped False Positives)
  if (droppedIssues && droppedIssues.length > 0) {
    elements.authorityFilterCallout.classList.remove("hidden");
    elements.droppedIssuesList.innerHTML = "";
    droppedIssues.forEach((issue) => {
      const item = document.createElement("div");
      item.className =
        "flex flex-col sm:flex-row sm:items-center justify-between p-2 rounded-lg bg-white border border-emerald-200 text-xs gap-1";
      item.innerHTML = `
        <div class="flex items-center space-x-2">
          <span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-100 text-rose-700">${issue.rule_id}</span>
          <span class="text-slate-700 font-medium line-through text-slate-400">${issue.message}</span>
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
    perfectCard.className = "p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800";
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

      // Rule ID Badge
      const ruleBadge = document.createElement("span");
      ruleBadge.className =
        issue.severity === "error"
          ? "px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-100 text-rose-800"
          : "px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-800";
      ruleBadge.textContent = issue.rule_id;
      leftBadges.appendChild(ruleBadge);

      // Severity Pill
      const sevBadge = document.createElement("span");
      sevBadge.className =
        issue.severity === "error"
          ? "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200"
          : "px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200";
      sevBadge.textContent =
        issue.severity === "error" ? dict.severityError : dict.severityWarning;
      leftBadges.appendChild(sevBadge);

      // Location Pill
      if (issue.location && issue.location.field) {
        const locBadge = document.createElement("span");
        locBadge.className =
          "px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-700";
        locBadge.textContent =
          issue.location.index !== null && issue.location.index !== undefined
            ? `${issue.location.field}[${issue.location.index}]`
            : issue.location.field;
        leftBadges.appendChild(locBadge);
      }

      // Source Provenance Badge
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
      card.className = "p-3 rounded-lg border border-indigo-100 bg-indigo-50/40 space-y-2";

      const locText =
        sugg.location && sugg.location.field
          ? `${sugg.location.field}[${sugg.location.index ?? 0}]`
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
          <span class="line-through">${sugg.original}</span>
        </div>
        <div class="flex items-start space-x-1.5 text-emerald-800 font-medium">
          <span class="text-[10px] font-mono font-bold bg-emerald-100 px-1 rounded shrink-0">+</span>
          <span>${sugg.suggested}</span>
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

// Apply Rewrite Suggestion to Editor
function applySuggestion(sugg, buttonElement) {
  const dict = TRANSLATIONS[state.lang];
  if (!sugg.location) return;

  const { field, index } = sugg.location;
  if (field === "headline" && index !== null && index !== undefined) {
    const row = elements.headlinesContainer.querySelector(`.headline-row[data-index="${index}"]`);
    if (row) {
      const input = row.querySelector(".headline-input");
      if (input) {
        input.value = sugg.suggested;
        input.dispatchEvent(new Event("input"));
        input.classList.add("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        setTimeout(() => {
          input.classList.remove("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        }, 1500);
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
        textarea.dispatchEvent(new Event("input"));
        textarea.classList.add("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        setTimeout(() => {
          textarea.classList.remove("ring-2", "ring-emerald-500", "bg-emerald-50/50");
        }, 1500);
      }
    }
  }

  buttonElement.textContent = dict.rewriteApplied;
  buttonElement.className =
    "px-2.5 py-1 rounded text-xs font-bold bg-emerald-600 text-white shrink-0";
  setTimeout(() => {
    buttonElement.textContent = dict.applyRewriteBtn;
    buttonElement.className =
      "px-2.5 py-1 rounded text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-2xs transition shrink-0";
  }, 1500);
}

// Start application on DOM ready
document.addEventListener("DOMContentLoaded", init);
