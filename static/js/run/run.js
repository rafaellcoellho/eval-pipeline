lucide.createIcons();

const isMonitoring = !!document.querySelector("[data-session-id]");

if (isMonitoring) {
  startPolling();
} else {
  initSelection();
}

function initSelection() {
  const checkboxes = document.querySelectorAll(".case-checkbox");
  const runBtn = document.getElementById("run-btn");
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

  runBtn.addEventListener("click", async () => {
    const caseNames = [...checkboxes]
      .filter((cb) => cb.checked)
      .map((cb) => cb.value);

    runBtn.disabled = true;

    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_names: caseNames }),
    });

    const { session_id } = await res.json();
    window.location.href = `/run/${session_id}`;
  });
}

function startPolling() {
  const card = document.querySelector("[data-session-id]");
  const sessionId = card.dataset.sessionId;
  const total = document.querySelectorAll(".case-row").length;

  const interval = setInterval(async () => {
    const res = await fetch(`/run/${sessionId}/status`);
    const data = await res.json();

    updateCaseStatuses(data.cases, total);

    if (data.overall === "done" || data.overall === "error") {
      clearInterval(interval);
      showOverallDone(data.overall);
    }
  }, 2000);
}

function updateCaseStatuses(cases, total) {
  let doneCount = 0;

  for (const [caseName, status] of Object.entries(cases)) {
    const row = document.querySelector(`.case-row[data-case="${caseName}"]`);
    if (!row) continue;

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

  if (overall === "done") {
    document.getElementById("overall-check").classList.remove("hidden");
    document.getElementById("done-banner").classList.remove("hidden");
  } else {
    document.getElementById("overall-error").classList.remove("hidden");
  }
}

function badgeClass(status) {
  if (status === "done") return "bg-green-500/10 text-green-400";
  if (status === "error") return "bg-red-500/10 text-red-400";
  return "bg-gray-800 text-gray-500";
}

function badgeContent(status) {
  if (status === "done") return `<i data-lucide="check" class="w-3 h-3"></i> Concluído`;
  if (status === "error") return `<i data-lucide="x" class="w-3 h-3"></i> Erro`;
  return `<i data-lucide="clock" class="w-3 h-3"></i> Pendente`;
}
