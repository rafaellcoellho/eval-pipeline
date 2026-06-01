lucide.createIcons();

document.querySelectorAll(".case-item").forEach((item) => {
  item.addEventListener("click", () => selectCase(item));
});

const firstCase = document.querySelector(".case-item");
if (firstCase) selectCase(firstCase);

function selectCase(item) {
  document.querySelectorAll(".case-item.selected").forEach((el) => el.classList.remove("selected"));
  item.classList.add("selected");

  document.getElementById("case-label").textContent = item.dataset.case;
  document.getElementById("empty-state").classList.add("hidden");
  document.getElementById("fields-table").classList.remove("hidden");

  const fields = JSON.parse(item.dataset.fields);
  renderFields(fields);
}

function displayValue(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

function renderFields(fields) {
  const tbody = document.getElementById("fields-body");

  tbody.innerHTML = fields
    .map((f) => {
      const isAcerto = f.status === "acerto";
      return `
        <tr class="border-t border-gray-800">
          <td class="py-3 pr-6 font-mono text-gray-300">${f.campo}</td>
          <td class="py-3 pr-6 text-gray-400 text-xs font-mono">${displayValue(f.valor_esperado)}</td>
          <td class="py-3 pr-6 text-xs font-mono ${isAcerto ? "text-green-400" : "text-red-400"}">${displayValue(f.valor_obtido)}</td>
          <td class="py-3">
            <span class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${isAcerto ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}">
              <i data-lucide="${isAcerto ? "check" : "x"}" class="w-3 h-3"></i>
              ${isAcerto ? "acerto" : "erro"}
            </span>
          </td>
        </tr>`;
    })
    .join("");

  lucide.createIcons({ nodes: Array.from(tbody.querySelectorAll("[data-lucide]")) });
}
