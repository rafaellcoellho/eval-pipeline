lucide.createIcons();

const isMonitoring = !!document.querySelector("[data-session-id]");

if (isMonitoring) {
  startPolling();
} else {
  initSelection();
}

async function startRun(caseNames) {
  const res = await fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_names: caseNames }),
  });
  const { session_id } = await res.json();
  window.location.href = `/run/${session_id}`;
}

function initSelection() {
  const checkboxes = document.querySelectorAll(".case-checkbox");
  const runBtn = document.getElementById("run-btn");
  const runAllBtn = document.getElementById("run-all-btn");
  const countLabel = document.getElementById("selected-count");
  const toggleBtn = document.getElementById("toggle-all");

  function updateCount() {
    const checked = [...checkboxes].filter((cb) => cb.checked);
    const n = checked.length;
    countLabel.textContent = `${n} selecionado${n !== 1 ? "s" : ""}`;
    runBtn.disabled = n === 0;
    toggleBtn.textContent = n === checkboxes.length ? "Desmarcar todos" : "Selecionar todos";
  }

  checkboxes.forEach((cb) => cb.addEventListener("change", updateCount));
  updateCount();

  toggleBtn.addEventListener("click", () => {
    const allChecked = [...checkboxes].every((cb) => cb.checked);
    checkboxes.forEach((cb) => (cb.checked = !allChecked));
    updateCount();
  });

  runBtn.addEventListener("click", () => {
    const caseNames = [...checkboxes].filter((cb) => cb.checked).map((cb) => cb.value);
    runBtn.disabled = true;
    startRun(caseNames);
  });

  runAllBtn.addEventListener("click", () => {
    runAllBtn.disabled = true;
    startRun([...checkboxes].map((cb) => cb.value));
  });

  document.querySelectorAll(".run-single-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.disabled = true;
      startRun([btn.dataset.case]);
    });
  });

}

function startPolling() {
  const card = document.querySelector("[data-session-id]");
  const sessionId = card.dataset.sessionId;
  const total = document.querySelectorAll(".case-row").length;

  const stopAllBtn = document.getElementById("stop-all-btn");
  const stopAndAnalyzeBtn = document.getElementById("stop-and-analyze-btn");

  stopAllBtn.addEventListener("click", async () => {
    stopAllBtn.disabled = true;
    stopAndAnalyzeBtn.disabled = true;
    await fetch(`/run/${sessionId}/stop`, { method: "POST" });
  });

  stopAndAnalyzeBtn.addEventListener("click", async () => {
    stopAllBtn.disabled = true;
    stopAndAnalyzeBtn.disabled = true;
    await fetch(`/run/${sessionId}/stop-and-analyze`, { method: "POST" });
  });

  const caseStartTimes = {};
  const caseEndTimes = {};

  const sessionStart = Date.now();
  let sessionEnd = null;
  const totalTimerEl = document.getElementById("total-timer");

  setInterval(() => {
    if (!totalTimerEl) return;
    const elapsed = Math.floor(((sessionEnd ?? Date.now()) - sessionStart) / 1000);
    const m = Math.floor(elapsed / 60);
    const s = elapsed % 60;
    totalTimerEl.innerHTML = `<i data-lucide="timer" class="w-3 h-3"></i> ${m}:${s.toString().padStart(2, "0")}`;
    lucide.createIcons({ nodes: [totalTimerEl] });
  }, 1000);

  setInterval(() => {
    for (const [caseName, startTime] of Object.entries(caseStartTimes)) {
      const row = document.querySelector(`.case-row[data-case="${caseName}"]`);
      if (!row) continue;
      const timerEl = row.querySelector(".case-timer");
      if (!timerEl) continue;
      const end = caseEndTimes[caseName] ?? Date.now();
      const elapsed = Math.floor((end - startTime) / 1000);
      const m = Math.floor(elapsed / 60);
      const s = elapsed % 60;
      timerEl.textContent = `${m}:${s.toString().padStart(2, "0")}`;
    }
  }, 1000);

  const ACTIVE_STATUSES = new Set(["Na fila", "Pendente", "Iniciado", "Adiado", "Aguardando nova tentativa", "started"]);
  const TERMINAL_STATUSES_JS = new Set(["done", "error", "Finalizado", "Falhou", "Cancelado"]);

  function trackCaseTime(caseName, status) {
    if (ACTIVE_STATUSES.has(status) && !caseStartTimes[caseName]) {
      caseStartTimes[caseName] = Date.now();
    }
    if (TERMINAL_STATUSES_JS.has(status) && !caseEndTimes[caseName] && caseStartTimes[caseName]) {
      caseEndTimes[caseName] = Date.now();
    }
  }

  const interval = setInterval(async () => {
    const res = await fetch(`/run/${sessionId}/status`);
    const data = await res.json();

    updateCaseStatuses(data.cases, total, trackCaseTime);

    if (data.overall === "done" || data.overall === "error" || data.overall === "cancelled") {
      clearInterval(interval);
      sessionEnd = Date.now();
      showOverallDone(data.overall);
    }
  }, 2000);
}

function updateCaseStatuses(cases, total, onCaseStatus) {
  let doneCount = 0;

  for (const [caseName, status] of Object.entries(cases)) {
    const row = document.querySelector(`.case-row[data-case="${caseName}"]`);
    if (!row) continue;

    if (onCaseStatus) onCaseStatus(caseName, status);
    if (status === "done") doneCount++;

    const badge = row.querySelector(".status-badge");
    badge.className = `status-badge inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-full ${badgeClass(status)}`;
    badge.innerHTML = badgeContent(status);
    lucide.createIcons({ nodes: [badge] });
  }

  document.getElementById("progress-label").textContent =
    `${doneCount} / ${total} concluídos`;
}

function showOverallDone(overall) {
  document.getElementById("overall-spinner").classList.add("hidden");
  document.getElementById("stop-all-btn").classList.add("hidden");
  document.getElementById("stop-and-analyze-btn").classList.add("hidden");

  if (overall === "done") {
    document.getElementById("overall-check").classList.remove("hidden");
    const banner = document.getElementById("done-banner");
    banner.classList.remove("hidden");
    lucide.createIcons({ nodes: Array.from(banner.querySelectorAll("[data-lucide]")) });
  } else if (overall === "cancelled") {
    document.getElementById("overall-error").classList.remove("hidden");
    const banner = document.getElementById("cancelled-banner");
    banner.classList.remove("hidden");
    lucide.createIcons({ nodes: Array.from(banner.querySelectorAll("[data-lucide]")) });
  } else {
    document.getElementById("overall-error").classList.remove("hidden");
  }
}

function badgeClass(status) {
  if (status === "done" || status === "Finalizado") return "bg-green-500/10 text-green-400";
  if (status === "started" || status === "Iniciado") return "bg-blue-500/10 text-blue-400";
  if (status === "Aguardando nova tentativa" || status === "Adiado") return "bg-orange-500/10 text-orange-400";
  if (status === "error" || status === "Falhou" || status === "Cancelado") return "bg-red-500/10 text-red-400";
  return "bg-gray-800 text-gray-500";
}

function badgeContent(status) {
  if (status === "done") return `<i data-lucide="check" class="w-3 h-3"></i> Concluído`;
  if (status === "Finalizado") return `<i data-lucide="check" class="w-3 h-3"></i> Finalizado`;
  if (status === "started" || status === "Iniciado") return `<i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i> Iniciado`;
  if (status === "Na fila" || status === "pending") return `<i data-lucide="clock" class="w-3 h-3"></i> Na fila`;
  if (status === "Pendente") return `<i data-lucide="clock" class="w-3 h-3"></i> Pendente`;
  if (status === "Aguardando nova tentativa") return `<i data-lucide="refresh-cw" class="w-3 h-3"></i> Aguardando nova tentativa`;
  if (status === "Adiado") return `<i data-lucide="pause-circle" class="w-3 h-3"></i> Adiado`;
  if (status === "error" || status === "Falhou") return `<i data-lucide="x" class="w-3 h-3"></i> Falhou`;
  if (status === "Cancelado") return `<i data-lucide="ban" class="w-3 h-3"></i> Cancelado`;
  return `<i data-lucide="clock" class="w-3 h-3"></i> ${status}`;
}
