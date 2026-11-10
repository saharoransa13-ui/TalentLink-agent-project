// ================= Translations =================
const TEXTS = {
  ar: {
    nav_how: "كيف يعمل",
    nav_analyze: "حلّل سيرتك",
    nav_assistant: "المساعد",
    hero_title: "اكتشف ما ينقصك للوصول إلى وظيفة أحلامك",
    hero_text: "ارفع سيرتك الذاتية، واختر الوظيفة التي تستهدفها، واحصل على تقرير واضح بالمهارات الناقصة وخطة للتعلّم.",
    hero_cta: "ابدأ التحليل",
    how_title: "كيف يعمل؟",
    step1_title: "ارفع سيرتك الذاتية",
    step1_text: "PDF أو Word أو TXT",
    step2_title: "اختر الوظيفة",
    step2_text: "الوظيفة التي تطمح إليها",
    step3_title: "احصل على خطتك",
    step3_text: "المهارات الناقصة وكيفية تعلّمها",
    step4_title: "استخدم المساعد الذكي",
    step4_text: "اسأل عن الدورات والشهادات المناسبة لك",
    analyze_title: "حلّل سيرتك الذاتية",
    dropzone_text: "اسحب سيرتك الذاتية إلى هنا أو اضغط لاختيار ملف",
    rules_title: "شروط رفع السيرة الذاتية",
    rule_language: "اللغة: الإنجليزية فقط.",
    rule_format: "صيغة الملف: PDF أو DOCX أو TXT.",
    rule_size: "الحجم الأقصى: 10 ميجابايت.",
    rule_text: "يجب أن يحتوي الملف على نص قابل للتحديد (الملفات الممسوحة ضوئيًا كصور غير مدعومة).",
    bad_file_type: "صيغة الملف غير مدعومة. يُرجى رفع ملف PDF أو DOCX أو TXT.",
    file_too_large: "حجم الملف أكبر من 10 ميجابايت. يُرجى رفع ملف أصغر.",
    // Upload errors sent by the server (detail.code)
    err_file_too_large: "حجم الملف أكبر من 10 ميجابايت. يُرجى رفع ملف أصغر.",
    err_bad_file_type: "صيغة الملف غير مدعومة. يُرجى رفع ملف PDF أو DOCX أو TXT.",
    err_pdf_unreadable: "تعذّرت قراءة ملف PDF. قد يكون الملف تالفًا أو ليس ملف PDF حقيقيًا.",
    err_docx_unreadable: "تعذّرت قراءة ملف Word. قد يكون الملف تالفًا أو ليس ملف ‎.docx‎ حقيقيًا.",
    err_no_text: "لم نتمكن من استخراج أي نص من الملف. إذا كان ملف PDF ممسوحًا ضوئيًا كصورة، فهذا النوع غير مدعوم.",
    err_cv_not_english: "يجب أن تكون السيرة الذاتية مكتوبة باللغة الإنجليزية. يُرجى رفع النسخة الإنجليزية من سيرتك الذاتية.",
    // Notices shown with the results (warning_codes)
    warn_llm_failed: "تعذّر استخدام الذكاء الاصطناعي في قراءة سيرتك الذاتية هذه المرة، لذلك اعتمد التحليل على القواعد الثابتة فقط. يمكنك المحاولة مرة أخرى.",
    warn_semantic_unavailable: "تعذّرت مطابقة المهارات بالمعنى، لذلك اعتمد التحليل على مطابقة الكلمات فقط.",
    warn_llm_privacy: "تنبيه الخصوصية: أُرسل نص سيرتك الذاتية إلى خدمة ذكاء اصطناعي خارجية لاستخراج المهارات.",
    warn_no_skills: "لم نجد مهارات معروفة في سيرتك الذاتية. تأكد أن الملف يحتوي على نص وأن المهارات مكتوبة بوضوح.",
    warn_little_pdf_text: "استُخرج نص قليل جدًا من ملف PDF، وقد يكون ملفًا ممسوحًا ضوئيًا كصورة.",
    cv_not_english: "يجب أن تكون السيرة الذاتية مكتوبة باللغة الإنجليزية. يُرجى رفع النسخة الإنجليزية من سيرتك الذاتية.",
    role_label: "الوظيفة المستهدفة",
    analyze_button: "حلّل سيرتي الذاتية",
    results_title: "النتيجة",
    assistant_title: "اسأل المساعد",
    assistant_text: "اسأل عن الدورات أو المهارات أو خطة التعلّم، وسيجيبك المساعد استنادًا إلى مصادر موثوقة.",
    ask_button: "اسأل",
    footer_text: "CV Gap — مشروع تحليل فجوات المهارات",
    question_placeholder: "مثال: ما الذي يجب أن أتعلّمه أولًا لهذه الوظيفة؟",
    file_selected: "الملف المختار: {name}",
    roles_failed: "تعذّر تحميل الوظائف. تأكّد من تشغيل الخادم ثم أعد تحميل الصفحة.",
    switch_to: "English",
    upload_first: "يُرجى رفع سيرتك الذاتية أولًا.",
    analyzing: "جارٍ قراءة سيرتك الذاتية ومقارنتها بمتطلبات الوظيفة...",
    analysis_failed: "تعذّر إكمال التحليل: {reason}",
    connection_failed: "تعذّر الاتصال بخدمة التحليل. حاول مرة أخرى.",
    match_score: "نسبة التطابق",
    summary_counts: "{missing} ناقصة · {partial} جزئية · {matched} متوفرة",
    status_missing: "مهارات ناقصة",
    status_partial: "مهارات متوفرة جزئيًا",
    status_matched: "مهارات تمتلكها",
    importance_core: "أساسية للوظيفة",
    importance_important: "مهمة",
    importance_nice: "إضافية",
    evidence: "وردت في سيرتك:",
    none: "لا يوجد",
    recs_title: "مصادر تعلّم مقترحة",
    no_recs: "لم نعثر على توصيات للمهارات الناقصة.",
    helps_with: "تساعدك في: {skills}",
    duration_level: "المدة: {duration} · المستوى: {level}",
    not_specified: "غير محدد",
    all_levels: "جميع المستويات",
    type_course: "دورة تدريبية",
    type_project: "مشروع",
    type_certification: "شهادة",
    type_workshop: "ورشة عمل",
    roadmap_title: "خطة التعلّم المقترحة",
    week: "الأسبوع",
    no_roadmap: "تعذّر إنشاء خطة تعلّم.",
    empty_question: "اكتب سؤالك أولًا.",
    asking: "يبحث المساعد في المصادر ويُعِدّ الإجابة...",
    ask_failed: "تعذّر الحصول على إجابة: {reason}",
    ask_timeout: "استغرق المساعد وقتًا أطول من المتوقع. حاول مرة أخرى.",
    sources_title: "المصادر",
  },
  en: {
    nav_how: "How it works",
    nav_analyze: "Analyze your CV",
    nav_assistant: "Assistant",
    hero_title: "Find out what you're missing to land your target job",
    hero_text: "Upload your CV, choose the role you're aiming for, and get a clear report of your skill gaps with a learning plan.",
    hero_cta: "Start analysis",
    how_title: "How does it work?",
    step1_title: "Upload your CV",
    step1_text: "PDF, Word, or TXT",
    step2_title: "Choose a role",
    step2_text: "The job you want to reach",
    step3_title: "Get your plan",
    step3_text: "Your skill gaps and how to close them",
    step4_title: "Use the smart assistant",
    step4_text: "Ask about courses and certifications that fit you",
    analyze_title: "Analyze your CV",
    dropzone_text: "Drag your CV here or click to choose a file",
    rules_title: "CV upload requirements",
    rule_language: "Language: English only.",
    rule_format: "File format: PDF, DOCX or TXT.",
    rule_size: "Maximum size: 10 MB.",
    rule_text: "The file must contain selectable text (scanned image-only files are not supported).",
    bad_file_type: "Unsupported file type. Please upload a PDF, DOCX or TXT file.",
    file_too_large: "The file is larger than 10 MB. Please upload a smaller file.",
    // Upload errors sent by the server (detail.code)
    err_file_too_large: "The file is larger than 10 MB. Please upload a smaller file.",
    err_bad_file_type: "Unsupported file type. Please upload a PDF, DOCX or TXT file.",
    err_pdf_unreadable: "This PDF could not be read. It may be damaged or not a real PDF file.",
    err_docx_unreadable: "This Word file could not be read. It may be damaged or not a real .docx file.",
    err_no_text: "No text could be extracted from the file. Scanned image-only PDFs are not supported.",
    err_cv_not_english: "Your CV must be written in English. Please upload the English version of your CV.",
    // Notices shown with the results (warning_codes)
    warn_llm_failed: "The AI could not read your CV this time, so the analysis used the fixed rules only. You can try again.",
    warn_semantic_unavailable: "Meaning-based skill matching was unavailable, so only keyword matching was used.",
    warn_llm_privacy: "Privacy notice: your CV text was sent to an external AI service to extract skills.",
    warn_no_skills: "We found no known skills in your CV. Make sure the file contains text and your skills are written clearly.",
    warn_little_pdf_text: "Very little text was extracted from the PDF; it may be a scanned image.",
    cv_not_english: "Your CV must be written in English. Please upload the English version of your CV.",
    role_label: "Target role",
    analyze_button: "Analyze my CV",
    results_title: "Your results",
    assistant_title: "Ask the assistant",
    assistant_text: "Ask about courses, skills, or a learning plan, and get answers grounded in trusted sources.",
    ask_button: "Ask",
    footer_text: "CV Gap — Skill gap analysis project",
    question_placeholder: "For example: What should I learn first for this role?",
    file_selected: "Selected file: {name}",
    roles_failed: "Couldn't load the roles. Make sure the server is running and refresh the page.",
    switch_to: "العربية",
    upload_first: "Please upload your CV first.",
    analyzing: "Reading your CV and comparing it with the role requirements...",
    analysis_failed: "The analysis couldn't be completed: {reason}",
    connection_failed: "Couldn't connect to the analysis service. Try again.",
    match_score: "Match score",
    summary_counts: "{missing} missing · {partial} partial · {matched} covered",
    status_missing: "Missing skills",
    status_partial: "Partially covered",
    status_matched: "Skills you have",
    importance_core: "Core for this role",
    importance_important: "Important",
    importance_nice: "Nice to have",
    evidence: "Found in your CV:",
    none: "None",
    recs_title: "Recommended learning",
    no_recs: "No recommendations were found for your skill gaps.",
    helps_with: "Helps with: {skills}",
    duration_level: "Duration: {duration} · Level: {level}",
    not_specified: "Not specified",
    all_levels: "All levels",
    type_course: "Course",
    type_project: "Project",
    type_certification: "Certification",
    type_workshop: "Workshop",
    roadmap_title: "Suggested learning plan",
    week: "Week",
    no_roadmap: "No learning plan could be generated.",
    empty_question: "Type your question first.",
    asking: "Searching the sources and preparing an answer...",
    ask_failed: "Couldn't get an answer: {reason}",
    ask_timeout: "The assistant took too long. Try again.",
    sources_title: "Sources",
  },
};

// ================= Language =================
let currentLang = "ar";

try {
  currentLang = localStorage.getItem("lang") || "ar";
} catch (e) {
  // localStorage can be blocked in some browsers; keep the default.
}

function t(key, vars = {}) {
  let text = TEXTS[currentLang][key] || TEXTS.en[key] || key;
  for (const [name, value] of Object.entries(vars)) {
    text = text.replace(`{${name}}`, value);
  }
  return text;
}

function applyLanguage() {
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === "ar" ? "rtl" : "ltr";

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });

  document.getElementById("lang-toggle").textContent = t("switch_to");
  document.getElementById("question").placeholder = t("question_placeholder");
  updateFileLabel();
  if (lastReport) renderResults(lastReport);
  if (lastAnswer) renderAnswer(lastAnswer);
}

document.getElementById("lang-toggle").addEventListener("click", () => {
  currentLang = currentLang === "ar" ? "en" : "ar";
  try {
    localStorage.setItem("lang", currentLang);
  } catch (e) {}
  applyLanguage();
});

// ================= File selection =================
const fileInput = document.getElementById("cv-file");
const dropzone = document.querySelector(".dropzone");

function updateFileLabel() {
  const label = document.getElementById("file-label");
  const file = fileInput.files[0];
  label.textContent = file ? t("file_selected", { name: file.name }) : t("dropzone_text");
}

fileInput.addEventListener("change", updateFileLabel);

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  if (event.dataTransfer.files.length) {
    fileInput.files = event.dataTransfer.files;
    updateFileLabel();
  }
});

// ================= Roles =================
async function loadRoles() {
  const select = document.getElementById("role-select");
  try {
    const response = await fetch("/roles");
    if (!response.ok) throw new Error(response.status);
    const roles = await response.json();
    select.innerHTML = "";
    roles.forEach((role) => {
      const option = document.createElement("option");
      option.value = role.role_id;
      option.textContent = role.title;
      select.appendChild(option);
    });
  } catch (error) {
    const status = document.getElementById("analyze-status");
    status.textContent = t("roles_failed");
    status.classList.add("error");
  }
}
// ================= Helpers =================
function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function safeUrl(url) {
  return /^https?:\/\//i.test(url || "") ? escapeHtml(url) : "#";
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

// ================= Analyze =================
let lastReport = null;
const analyzeForm = document.getElementById("analyze-form");
const analyzeStatus = document.getElementById("analyze-status");

analyzeForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    setStatus(analyzeStatus, t("upload_first"), true);
    return;
  }

  // Check the file before sending it, so the user gets a fast, clear message.
  const allowedTypes = [".pdf", ".docx", ".txt"];
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  if (!allowedTypes.includes(extension)) {
    setStatus(analyzeStatus, t("bad_file_type"), true);
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    setStatus(analyzeStatus, t("file_too_large"), true);
    return;
  }

  const button = analyzeForm.querySelector("button[type=submit]");
  button.disabled = true;
  setStatus(analyzeStatus, t("analyzing"));

  const formData = new FormData();
  formData.append("file", file);
  formData.append("role_id", document.getElementById("role-select").value);

  try {
    const response = await fetch("/analyze", { method: "POST", body: formData });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const code = data.detail && data.detail.code;
      if (code && TEXTS[currentLang]["err_" + code]) {
        setStatus(analyzeStatus, t("err_" + code), true);
        return;
      }
      const reason = typeof data.detail === "string" ? data.detail : response.status;
      setStatus(analyzeStatus, t("analysis_failed", { reason }), true);
      return;
    }

    lastReport = data;
    setStatus(analyzeStatus, "");
    renderResults(data);
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    setStatus(analyzeStatus, t("connection_failed"), true);
  } finally {
    button.disabled = false;
  }
});

// ================= Results =================
function importanceLabel(weight) {
  if (weight >= 0.75) return t("importance_core");
  if (weight >= 0.45) return t("importance_important");
  return t("importance_nice");
}

function renderResults(report) {
  const gaps = report.gaps || [];
  const score = Math.round(report.match_score || 0);
  const skillNames = Object.fromEntries(gaps.map((g) => [g.skill_id, g.skill_name]));
  const count = (status) => gaps.filter((g) => g.status === status).length;

  // Warnings from the server (privacy notice etc.), without the technical method line.
  // Use the translated text when the server sent a warning code we know.
  const warningTexts = report.warning_codes
    ? report.warning_codes.map((code) => (TEXTS[currentLang]["warn_" + code] ? t("warn_" + code) : null))
        .map((text, i) => text || report.warnings.filter((w) => !w.startsWith("Skill extraction method"))[i])
    : (report.warnings || []).filter((w) => !w.startsWith("Skill extraction method"));
  const warnings = warningTexts
    .filter(Boolean)
    .map((w) => `<p class="notice">${escapeHtml(w)}</p>`)
    .join("");

  // Skill groups: missing first, then partial, then matched.
  const groups = [["missing", "❌"], ["partial", "🟡"], ["matched", "✅"]]
    .map(([status, icon]) => {
      const items = gaps
        .filter((g) => g.status === status)
        .sort((a, b) => b.weight - a.weight);

      const list = items.length
        ? items.map((g) => `
            <li class="skill-item">
              <strong>${escapeHtml(g.skill_name)}</strong>
              <span class="badge badge-${status}">${importanceLabel(g.weight)}</span>
              ${g.evidence && g.evidence.length
                ? `<p class="evidence">${t("evidence")} ${escapeHtml(g.evidence.join(" | "))}</p>`
                : ""}
            </li>`).join("")
        : `<li class="skill-item muted">${t("none")}</li>`;

      return `
        <div class="card gap-group">
          <h3>${icon} ${t("status_" + status)} (${items.length})</h3>
          <ul class="skill-list">${list}</ul>
        </div>`;
    })
    .join("");

  // Recommendations as cards.
  const recs = (report.recommendations || [])
    .map((item) => {
      const related = (item.skill_ids || [])
        .filter((id) => skillNames[id])
        .map((id) => skillNames[id]);
      return `
        <div class="card rec-card">
          <span class="badge badge-type">${t("type_" + item.item_type)}</span>
          <h4><a href="${safeUrl(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a></h4>
          <p class="muted">${escapeHtml(item.provider)}</p>
          ${related.length ? `<p>${t("helps_with", { skills: escapeHtml(related.join(", ")) })}</p>` : ""}
          <p class="muted">${t("duration_level", {
            duration: escapeHtml(item.duration || t("not_specified")),
            level: escapeHtml(item.level || t("all_levels")),
          })}</p>
        </div>`;
    })
    .join("");

  // Roadmap as a numbered list.
  const roadmap = (report.roadmap || [])
    .map((item) => `
      <li>
        <span class="phase">${escapeHtml(item.phase.replace("Week", t("week")))}</span>
        <strong>${escapeHtml(item.skill_name)}</strong> — ${escapeHtml(item.recommendation.title)}
      </li>`)
    .join("");

  document.getElementById("results-content").innerHTML = `
    <div class="card summary">
      <div class="score-ring" style="--score: ${score}"><span>${score}%</span></div>
      <div>
        <p class="muted">${t("match_score")} · ${escapeHtml(report.role_title)}</p>
        <p>${t("summary_counts", {
          missing: count("missing"),
          partial: count("partial"),
          matched: count("matched"),
        })}</p>
      </div>
    </div>
    ${warnings}
    <div class="gap-groups">${groups}</div>

    <h3 class="sub-title">${t("recs_title")}</h3>
    ${recs ? `<div class="rec-grid">${recs}</div>` : `<p class="muted">${t("no_recs")}</p>`}

    <h3 class="sub-title">${t("roadmap_title")}</h3>
    ${roadmap ? `<ol class="card roadmap">${roadmap}</ol>` : `<p class="muted">${t("no_roadmap")}</p>`}
  `;

  document.getElementById("results").hidden = false;
}
// ================= Assistant =================
let lastAnswer = null;
const assistantForm = document.getElementById("assistant-form");
const assistantStatus = document.getElementById("assistant-status");
const answerBox = document.getElementById("answer");

// Extra information sent with the question so the answer is personal.
function buildContext() {
  const parts = [];
  if (lastReport) {
    const gaps = (lastReport.gaps || [])
      .filter((g) => g.status !== "matched")
      .sort((a, b) => b.weight - a.weight);
    parts.push(`Candidate target role: ${lastReport.role_title}.`);
    parts.push(`Match score: ${Math.round(lastReport.match_score)}%.`);
    if (gaps.length) {
      parts.push("Skill gaps: " + gaps.map((g) => `${g.skill_name} (${g.status})`).join(", ") + ".");
    }
    const recs = (lastReport.recommendations || [])
      .slice(0, 6)
      .map((r) => `${r.title} (${r.provider}, ${r.url})`);
    if (recs.length) {
      parts.push("Catalog recommendations: " + recs.join("; ") + ".");
    }
  }
  if (currentLang === "ar") {
    parts.push("Write the answer in Modern Standard Arabic (فصحى). Keep course names, certifications and technical terms in English. Write citations exactly like [S1].");
  }
  return parts.join("\n").slice(0, 5800);
}

assistantForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = document.getElementById("question").value.trim();
  if (!question) {
    setStatus(assistantStatus, t("empty_question"), true);
    return;
  }

  const button = assistantForm.querySelector("button[type=submit]");
  button.disabled = true;
  setStatus(assistantStatus, t("asking"));

  // Stop waiting after 90 seconds.
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 90000);

  try {
    const response = await fetch("/rag/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context: buildContext(), top_k: 4 }),
      signal: controller.signal,
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const reason = typeof data.detail === "string" ? data.detail : response.status;
      setStatus(assistantStatus, t("ask_failed", { reason }), true);
      return;
    }

    lastAnswer = data;
    setStatus(assistantStatus, "");
    renderAnswer(data);
  } catch (error) {
    const message = error.name === "AbortError" ? t("ask_timeout") : t("connection_failed");
    setStatus(assistantStatus, message, true);
  } finally {
    clearTimeout(timer);
    button.disabled = false;
  }
});

// "aruba-ansf.md" -> "aruba ansf"
function sourceLabel(name) {
  return String(name || "")
    .replace(/\.(md|txt|pdf|docx)$/i, "")
    .replace(/[-_]+/g, " ");
}

function renderAnswer(data) {
  const answer = data.answer || "";

  // Markdown -> safe HTML. If the libraries didn't load, show plain text.
  const html = window.marked && window.DOMPurify
    ? DOMPurify.sanitize(marked.parse(answer))
    : escapeHtml(answer).replace(/\n/g, "<br>");

  // Group the citations by file, so each file is listed once with all its numbers (S1, S2 ...).
  const groups = new Map();
  for (const c of data.citations || []) {
    if (!groups.has(c.source)) groups.set(c.source, []);
    groups.get(c.source).push(c.id);
  }
  const knownIds = new Set((data.citations || []).map((c) => c.id));

  const sources = [...groups.entries()].map(([source, ids]) => {
    const badges = ids.map((id) => `<span class="badge badge-type">${escapeHtml(id)}</span>`).join(" ");
    return `<li class="source-item" data-ids="${escapeHtml(ids.join(" "))}">${badges} ${escapeHtml(sourceLabel(source))}</li>`;
  });

  answerBox.innerHTML = `
    <div class="answer-body" dir="auto">${html}</div>
    ${sources.length ? `<h4>${t("sources_title")}</h4><ul class="sources">${sources.join("")}</ul>` : ""}
  `;
  linkCitations(answerBox.querySelector(".answer-body"), knownIds);
  answerBox.hidden = false;
}
// Turn [S1] or [S1, S2] in the answer text into buttons that point to the source list.
function linkCitations(container, knownIds) {
  if (!container || !knownIds.size) return;
  const pattern = /\[(S\d+(?:\s*[,،]\s*S\d+)*)\]/g;
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) {
    if (pattern.test(walker.currentNode.nodeValue)) textNodes.push(walker.currentNode);
    pattern.lastIndex = 0;
  }

  for (const node of textNodes) {
    const fragment = document.createDocumentFragment();
    const text = node.nodeValue;
    let last = 0;
    for (const match of text.matchAll(pattern)) {
      fragment.append(text.slice(last, match.index));
      fragment.append("[");
      match[1].split(/\s*[,،]\s*/).forEach((id, i) => {
        if (i > 0) fragment.append(", ");
        if (knownIds.has(id)) {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "cite";
          button.textContent = id;
          button.addEventListener("click", () => highlightSource(id));
          fragment.append(button);
        } else {
          fragment.append(id);
        }
      });
      fragment.append("]");
      last = match.index + match[0].length;
    }
    fragment.append(text.slice(last));
    node.replaceWith(fragment);
  }
}

// Scroll to the source that has this id and highlight it for a moment.
function highlightSource(id) {
  const item = [...document.querySelectorAll("#answer .source-item")]
    .find((li) => li.dataset.ids.split(" ").includes(id));
  if (!item) return;
  item.scrollIntoView({ behavior: "smooth", block: "center" });
  item.classList.remove("source-highlight");
  void item.offsetWidth; // restart the animation
  item.classList.add("source-highlight");
}
// ================= Start =================
applyLanguage();
loadRoles();