/**
 * Ad Copy Grader — Interactive Architecture Showcase
 *
 * Demonstrates the hybrid grading architecture:
 * 1. Pure Python Deterministic Rules (D01-D11)
 * 2. Bilingual Semantic LLM Audit (A01-A03)
 * 3. Server Code Authority Filter & Validated Rewrites
 */

// Full Bilingual UI Translations
const TRANSLATIONS = {
  en: {
    appTitle: "Ad Copy Grader",
    appSubtitle: "Hybrid Deterministic & LLM Google Ads RSA Auditor",
    showcaseBadge: "Interactive Architecture Showcase",
    onboardingTitle: "How to explore this project in 30 seconds",
    onboardingPill: "Quick 30–60s Reviewer Walkthrough",
    step1Title: "1. Select a Scenario",
    step1Desc: "Click one of the 4 benchmark pills below (Clean 10/10, Unverified Price A01, LP-Verified Price where Code Authority Filter intercepts an LLM false positive, or Clinical Guarantee A03 + Code Errors D04/D08).",
    step2Title: "2. Compare LP vs. RSA or Edit Live",
    step2Desc: "Cross-check Landing Page Context (left) against RSA Assets (center). Try editing a headline past 30 chars or clicking 'Apply Rewrite' on an issue to see the hybrid grader react live in 0ms.",
    step3Title: "3. Inspect Hybrid Verdict & Code",
    step3Desc: "See on the right which issues are Code Verified (D01–D11), LLM Judged (A01–A03), or intercepted by the Code Authority Filter. Scroll below to see how each Python module implements it under the hood.",
    scenariosLabel: "Pre-Loaded Scenarios:",
    scenariosSubtitle: "(Synthetic benchmarks produced by pipeline)",
    scenarioDetailLabel: "Active Scenario:",
    lpCardTitle: "Landing Page Context",
    ruleA01Badge: "Rule A01 Target",
    lpCardHelp: "The <strong>Code Authority Filter</strong> and Rule <strong>A01</strong> cross-examine every price, discount, and claim against this text.",
    primaryServiceLabel: "Primary Service",
    finalUrlLabel: "Final URL (HTTPS)",
    lpContextLabel: "LP Context Text",
    detectedLpTokensLabel: "Detected Price/Offer Tokens:",
    rsaEditorTitle: "RSA Asset Editor",
    rulesEngineBadge: "Rules D01–D11",
    path1Label: "Path 1",
    path2Label: "Path 2",
    headlinesHeader: "Headlines (3–15)",
    descriptionsHeader: "Descriptions (2–4)",
    showAllHeadlinesBtn: "Show all 15 (9 hidden)",
    collapseHeadlinesBtn: "Collapse to 6 headlines",
    resetScenarioBtn: "Reset Scenario",
    gradeAdBtn: "Re-evaluate Ad Copy",
    auditReportTitle: "Hybrid Audit Report",
    qualityScaleLabel: "Google Ads Quality",
    scoreLabel: "Score",
    rulesCheckedBadge: "11 Code Rules (D01-D11) + 3 LLM (A01-A03)",
    authorityFilterTitle: "Code Authority Filter Active",
    falsePositiveStrippedBadge: "False Positive Intercepted",
    authorityFilterDescription: "The raw LLM review flagged an offer or price claim, but the deterministic server filter verified that the claim matches the Landing Page context and automatically stripped the false positive before calculating the final score!",
    detectedIssuesTitle: "Detected Issues",
    rewriteSuggestionsTitle: "Validated Rewrites",
    rewriteSuggestionsSubtitle: "Guaranteed ≤30 chars (headlines) / ≤90 chars (descriptions)",
    applyRewriteBtn: "Apply Rewrite",
    rewriteApplied: "Applied!",
    architectureSectionTitle: "How the Repository Code Works Under the Hood",
    architectureSectionSubtitle: "Engineering architecture: strict separation of deterministic code rules and semantic LLM judgment.",
    archCard1Title: "Deterministic Engine (D01–D11)",
    archCard1Body: "LLMs notoriously miscount characters due to BPE tokenization. Exact hard limits (30 chars per headline D04, 90 per description D05, 15 per path D06) are enforced 100% by pure Python functions with Unicode NFC normalization. Also handles HTTPS validation (D07), duplicates (D08), forbidden exclamation marks (D09), ALL CAPS (D10), and primary service presence (D11).",
    archCard2Title: "Bilingual LLM Audit & Self-Correction",
    archCard2Body: "Semantic rules evaluate unverified pricing vs. LP context (A01), missing CTA in descriptions (A02), and clinical/financial guarantees (A03). Uses native Portuguese (PROMPT_PT) and English (PROMPT_EN) system prompts with <ad_payload> XML fencing against prompt injection, parsed by Pydantic with 1 automatic self-correction retry on malformed outputs.",
    archCard3Title: "Server Code Authority Filter",
    archCard3Body: "The server never blindly trusts LLM outputs. filter_llm_issues() acts as an automated boundary: strips any deterministic D* rule hallucinated by the model, drops out-of-bounds asset index hallucination, and suppresses A01 false positives whenever the flagged price or offer actually exists in lp_context (as proven in Scenario 3).",
    archCard4Title: "Validated Rewrites & 3-Column Evals",
    archCard4Body: "validate_suggestions() re-audits every LLM rewrite against rules D04/D05/D08/D09/D10; non-compliant rewrites are discarded before reaching the user. Validated with a 3-column Promptfoo evaluation suite (raw vs. pipeline vs. degraded) and CI gates: ruff, mypy --strict, pytest (99.1% coverage), Semgrep OWASP Top 10, and CodeQL.",
    footerText: "Ad Copy Grader — Deterministic Google Ads rules engine & LLM semantic audit.",
    offlineReady: "Self-Contained Client Demo",
    perfectScoreText: "🎉 Perfect 10.0 score! No deterministic or semantic issues detected.",
    codeProvenance: "Code Verified (Deterministic)",
    llmProvenance: "LLM Judged (Semantic)",
    severityError: "ERROR",
    severityWarning: "WARNING",
    discardedBadge: "Discarded by Server Authority Filter",
    headlinePlaceholder: "Headline",
    descriptionPlaceholder: "Description",
    noTokensDetected: "No price or offer tokens detected in LP context.",
  },
  pt: {
    appTitle: "Ad Copy Grader",
    appSubtitle: "Auditor Híbrido Determinístico e LLM para Google Ads RSA",
    showcaseBadge: "Demonstração Interativa da Arquitetura",
    onboardingTitle: "Como explorar este projeto em 30 segundos",
    onboardingPill: "Roteiro Rápido de Avaliação em 30–60s",
    step1Title: "1. Escolha um Cenário",
    step1Desc: "Clique em um dos 4 cenários abaixo (Conforme 10/10, Preço Não Confirmado A01, Preço Verificado onde o Filtro de Autoridade descarta falso positivo do LLM, ou Garantia Clínica A03 + Erros de Código D04/D08).",
    step2Title: "2. Compare a LP com o Anúncio ou Edite",
    step2Desc: "Compare o Contexto da LP (esquerda) com os Recursos RSA (centro). Experimente editar um título acima de 30 caracteres ou clicar em 'Aplicar Sugestão' para ver o auditor reagir ao vivo em 0ms.",
    step3Title: "3. Inspecione o Veredito Híbrido e o Código",
    step3Desc: "Veja à direita quais regras são Verificadas via Código (D01–D11), Julgadas via LLM (A01–A03) ou descartadas pelo Filtro de Autoridade. Veja abaixo como cada módulo Python opera nos bastidores.",
    scenariosLabel: "Cenários Pré-Carregados:",
    scenariosSubtitle: "(Benchmarks sintéticos produzidos pelo pipeline)",
    scenarioDetailLabel: "Cenário Ativo:",
    lpCardTitle: "Contexto da Landing Page",
    ruleA01Badge: "Alvo da Regra A01",
    lpCardHelp: "O <strong>Filtro de Autoridade</strong> e a Regra <strong>A01</strong> checam preços, descontos e promessas contra este texto.",
    primaryServiceLabel: "Serviço Principal",
    finalUrlLabel: "URL Final (HTTPS)",
    lpContextLabel: "Texto da Landing Page",
    detectedLpTokensLabel: "Tokens de Preço/Oferta Detectados:",
    rsaEditorTitle: "Editor de Recursos RSA",
    rulesEngineBadge: "Regras D01–D11",
    path1Label: "Caminho 1",
    path2Label: "Caminho 2",
    headlinesHeader: "Títulos (3–15)",
    descriptionsHeader: "Descrições (2–4)",
    showAllHeadlinesBtn: "Expandir todos os 15 (9 ocultos)",
    collapseHeadlinesBtn: "Recolher para 6 títulos",
    resetScenarioBtn: "Restaurar Cenário",
    gradeAdBtn: "Reavaliar Anúncio",
    auditReportTitle: "Relatório de Auditoria Híbrida",
    qualityScaleLabel: "Qualidade Google Ads",
    scoreLabel: "Pontuação",
    rulesCheckedBadge: "11 Regras de Código (D01-D11) + 3 LLM (A01-A03)",
    authorityFilterTitle: "Filtro de Autoridade do Código Ativo",
    falsePositiveStrippedBadge: "Falso Positivo Interceptado",
    authorityFilterDescription: "O LLM apontou uma oferta ou preço como não confirmado, mas o filtro determinístico do servidor comprovou que o dado consta na Landing Page e descartou o falso positivo automaticamente antes da nota final!",
    detectedIssuesTitle: "Problemas Detectados",
    rewriteSuggestionsTitle: "Sugestões de Reescrita Validadas",
    rewriteSuggestionsSubtitle: "Garantia de ≤30 carac. (títulos) / ≤90 carac. (descrições)",
    applyRewriteBtn: "Aplicar Sugestão",
    rewriteApplied: "Aplicado!",
    architectureSectionTitle: "Como Funciona o Código no Repositório (Arquitetura)",
    architectureSectionSubtitle: "Arquitetura de engenharia: separação estrita entre regras determinísticas e julgamento semântico LLM.",
    archCard1Title: "Motor Determinístico (D01–D11)",
    archCard1Body: "LLMs erram contagem de caracteres devido à tokenização BPE. Limites rígidos (30 caracteres no título D04, 90 na descrição D05, 15 no caminho D06) são garantidos 100% por funções puras em Python com normalização Unicode NFC. Valida também HTTPS (D07), duplicados (D08), exclamações proibidas (D09), MAIÚSCULAS (D10) e presença do serviço principal (D11).",
    archCard2Title: "Auditoria LLM Bilíngue e Autocorreção",
    archCard2Body: "Regras semânticas avaliam preços não confirmados na LP (A01), ausência de CTA (A02) e promessas de cura/resultado financeiro (A03). Utiliza prompts nativos em Português (PROMPT_PT) e Inglês (PROMPT_EN) com delimitadores XML <ad_payload> contra injeção de prompt, validados via Pydantic com 1 retry automático de autocorreção.",
    archCard3Title: "Filtro de Autoridade do Código no Servidor",
    archCard3Body: "O servidor nunca confia cegamente no modelo. filter_llm_issues() funciona como barreira de segurança: descarta qualquer regra D* alucinada pelo LLM, remove índices de ativos inexistentes e suprime falsos positivos da regra A01 sempre que o valor constar na landing page (como provado no Cenário 3).",
    archCard4Title: "Reescritas Validadas e Evals de 3 Colunas",
    archCard4Body: "validate_suggestions() reavalia cada sugestão do LLM contra as regras D04/D05/D08/D09/D10; sugestões fora do limite são descartadas antes de chegar ao usuário. Validado com suíte de 3 colunas no Promptfoo (raw vs pipeline vs degraded) e gates de CI: ruff, mypy --strict, pytest (99.1% cobertura), Semgrep OWASP Top 10 e CodeQL.",
    footerText: "Ad Copy Grader — Motor determinístico de regras para Google Ads e auditoria semântica via LLM.",
    offlineReady: "Demonstração Autocontida no Cliente",
    perfectScoreText: "🎉 Nota 10.0 perfeita! Nenhum problema determinístico ou semântico detectado.",
    codeProvenance: "Verificado via Código (Determinístico)",
    llmProvenance: "Julgado via LLM (Semântico)",
    severityError: "ERRO",
    severityWarning: "AVISO",
    discardedBadge: "Descartado pelo Filtro de Autoridade",
    headlinePlaceholder: "Título",
    descriptionPlaceholder: "Descrição",
    noTokensDetected: "Nenhum token de preço ou oferta detectado na landing page.",
  },
};

// Application State
const state = {
  lang: "en",
  scenarios: [],
  activeScenarioIndex: 0,
  headlinesExpanded: false,
};

// Cached DOM References
const elements = {
  langEnBtn: document.getElementById("langEnBtn"),
  langPtBtn: document.getElementById("langPtBtn"),
  scenarioPills: document.getElementById("scenarioPills"),
  scenarioDescription: document.getElementById("scenarioDescription"),
  primaryServiceInput: document.getElementById("primaryServiceInput"),
  finalUrlInput: document.getElementById("finalUrlInput"),
  lpContextInput: document.getElementById("lpContextInput"),
  lpTokenCountBadge: document.getElementById("lpTokenCountBadge"),
  detectedLpTokensList: document.getElementById("detectedLpTokensList"),
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
  statusPassBadge: document.getElementById("statusPassBadge"),
  heroGrade10: document.getElementById("heroGrade10"),
  heroScore: document.getElementById("heroScore"),
  activeModelBadge: document.getElementById("activeModelBadge"),
  authorityFilterCallout: document.getElementById("authorityFilterCallout"),
  droppedIssuesList: document.getElementById("droppedIssuesList"),
  issuesList: document.getElementById("issuesList"),
  issuesCountBadge: document.getElementById("issuesCountBadge"),
  suggestionsCard: document.getElementById("suggestionsCard"),
  suggestionsList: document.getElementById("suggestionsList"),
  suggestionsCountBadge: document.getElementById("suggestionsCountBadge"),
};

// Regular Expressions & Constants matching Python pipeline
const NUMERIC_TOKEN_PATTERN =
  /(?:r\$\s*[\d.,]+|\$\s*[\d.,]+|\b\d+(?:[.,]\d+)?%|\b\d{1,2}x\b|\b\d{2,6}\b)/gi;

const PRICE_CLAIM_PATTERN =
  /(?:r\$\s*\d[\d.,]*|\$\s*\d[\d.,]*|\b\d{1,2}%\s*(?:off|de\s+desconto)\b|\b\d{1,2}x\s+sem\s+juros\b)/i;

const CTA_PATTERN =
  /\b(?:book|schedule|call|contact|request|claim|get|start|visit|learn\s+more|agende|marque|ligue|fale|solicite|peça|peca|garanta|saiba\s+mais|confira|clique)\b/i;

const GUARANTEE_PATTERN =
  /(?:100%\s*garant\w*|garant\w*\s*(?:total|absolut\w*|100%)|garantia\s*de\s*resultado|resultado\s*garantido|guaranteed\s*results?|100%\s*guaranteed)/i;

const REPEATED_PUNCTUATION_PATTERN = /!{2,}|\?{2,}|\.{3,}|…+/;
const UPPERCASE_WORD_PATTERN = /\b[A-ZÀ-ÖØ-Þ]{4,}\b/g;

const ALLOWED_ACRONYMS = new Set([
  "HTML", "HTTP", "HTTPS", "JSON", "REST", "SAAS", "GDPR", "LGPD",
  "CNPJ", "INSS", "FGTS", "OAB", "CRM", "CRO", "CREA", "CREFITO",
  "CRP", "ANVISA", "ABNT", "CPAP", "LASIK", "CBCT", "CADCAM",
]);

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

  elements.toggleHeadlinesBtn.addEventListener("click", toggleHeadlinesExpanded);
  elements.resetScenarioBtn.addEventListener("click", resetCurrentScenario);
  elements.gradeAdBtn.addEventListener("click", () => runLiveEvaluation(true));

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
    detectLpTokens();
    runLiveEvaluation(false);
  });
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
    btn.className = `px-3 py-1 rounded-full text-xs font-semibold transition shadow-xs ${
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

  // Update counters & tokens
  updatePathCounters();
  detectLpTokens();

  // Run initial hybrid evaluation
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
      "headline-input w-full pl-3 pr-14 py-1.5 text-xs rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-sans";
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
      runLiveEvaluation(false);
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
      "desc-input w-full p-2 text-xs rounded-md border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500";
    textarea.placeholder = `${TRANSLATIONS[state.lang].descriptionPlaceholder} ${i + 1}`;
    textarea.value = val;

    textarea.addEventListener("input", () => {
      counter.textContent = `${textarea.value.length}/90`;
      updateCharCounterStyle(counter, textarea.value.length, 90);
      runLiveEvaluation(false);
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

  // Extract LP digits for authority verification
  const lpDigits = new Set(
    (lpContext.match(/\d[\d.,]*/g) || []).map((m) => m.replace(/\D/g, "")).filter(Boolean)
  );

  const deterministicIssues = [];
  const llmIssues = [];
  const droppedIssues = [];
  const suggestions = [];

  // 1. DETERMINISTIC RULES D01–D11

  // D01: Headline count (3 to 15)
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

  // D02: Fewer than 15 headlines recommendation
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

  // D03: Description count (2 to 4)
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

  // D04: Headline max 30 chars
  rawHeadlines.forEach((h, idx) => {
    if (h.trim() && h.length > 30) {
      deterministicIssues.push({
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

  // D07: Primary service mention in first 5 headlines
  if (primaryService && activeHeadlines.length >= 3) {
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

    if (matchCount < Math.min(3, top5.length)) {
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

  // D08: Duplicate headlines
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
    } else {
      seenHeadlines.add(norm);
    }
  });

  // D09: Repeated punctuation
  rawHeadlines.forEach((h, idx) => {
    if (REPEATED_PUNCTUATION_PATTERN.test(h)) {
      deterministicIssues.push({
        rule_id: "D09",
        severity: "error",
        message:
          lang === "pt"
            ? "Pontuação repetida ou excessiva não é permitida."
            : "Repeated or excessive punctuation is not allowed.",
        location: { field: "headline", index: idx },
        source: "code",
      });
    }
  });
  rawDescriptions.forEach((d, idx) => {
    if (REPEATED_PUNCTUATION_PATTERN.test(d)) {
      deterministicIssues.push({
        rule_id: "D09",
        severity: "error",
        message:
          lang === "pt"
            ? "Pontuação repetida ou excessiva não é permitida."
            : "Repeated or excessive punctuation is not allowed.",
        location: { field: "description", index: idx },
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
            ? "Uso excessivo de maiúsculas detectado; evite CAIXA ALTA exceto siglas padrão."
            : "Excessive capitalization detected; avoid ALL CAPS words unless standard acronyms.",
        location: { field: "headline", index: idx },
        source: "code",
      });
    }
  });

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
        // Unverified: LLM flags it and server accepts it
        llmIssues.push(rawA01Issue);

        const cleanService = (primaryService || "Service").slice(0, 22);
        const rewrite = lang === "pt" ? `${cleanService} Hoje` : `${cleanService} Today`;
        suggestions.push({
          location: { field: "headline", index: idx },
          original: h,
          suggested: rewrite.slice(0, 30),
          reason:
            lang === "pt"
              ? "Remove preço não verificado na página."
              : "Removes unverified price claim.",
        });
      } else {
        // Verified in LP!
        // In Scenario 3, the simulated LLM emitted an A01 false positive, but the Code Authority Filter stripped it!
        if (state.activeScenarioIndex === 2) {
          droppedIssues.push(rawA01Issue);
        }
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
          ? "Adiciona chamada para ação clara."
          : "Adds a clear call to action.",
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
            ? "Substitui garantia absoluta por afirmação adequada."
            : "Replaces absolute guarantee with compliant phrasing.",
      });
    }
  });

  // Merge issues
  const allIssues = [...deterministicIssues, ...llmIssues];

  // Calculate scores
  const errors = allIssues.filter((i) => i.severity === "error").length;
  const warnings = allIssues.filter((i) => i.severity === "warning").length;
  const score = Math.max(0, 100 - 15 * errors - 5 * warnings);
  const grade10 = Number((score / 10).toFixed(1));
  const passed = errors === 0;

  const result = {
    score: score,
    grade_10: grade10,
    passed: passed,
    issues: allIssues,
    suggestions: suggestions,
    rules_checked: ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11", "A01", "A02", "A03"],
    model: "Hybrid Pipeline: Deterministic + LLM",
  };

  renderAuditReport(result, droppedIssues);

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
    perfectCard.className = "p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium";
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
      card.className = "p-3 rounded-lg border border-indigo-100 bg-indigo-50/40 space-y-2 shadow-2xs";

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

// Apply Rewrite Suggestion to Editor and re-evaluate
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

  // Trigger immediate live re-evaluation
  runLiveEvaluation(true);
}

// Start application on DOM ready
document.addEventListener("DOMContentLoaded", init);
