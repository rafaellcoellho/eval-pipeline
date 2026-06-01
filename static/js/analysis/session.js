lucide.createIcons();

const TRUNCATE_AT = 80;
const _fullValues = [];

const modal = document.getElementById("value-modal");
const modalContent = document.getElementById("modal-content");
const modalCopy = document.getElementById("modal-copy");
const modalClose = document.getElementById("modal-close");
const modalBackdrop = document.getElementById("modal-backdrop");

modalClose.addEventListener("click", closeModal);
modalBackdrop.addEventListener("click", closeModal);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

modalCopy.addEventListener("click", () => {
  navigator.clipboard.writeText(modalContent.textContent);
  modalCopy.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Copiado!';
  lucide.createIcons({ nodes: [modalCopy] });
  setTimeout(() => {
    modalCopy.innerHTML = '<i data-lucide="copy" class="w-3.5 h-3.5"></i> Copiar';
    lucide.createIcons({ nodes: [modalCopy] });
  }, 1500);
});

function openModal(idx) {
  modalContent.textContent = _fullValues[idx];
  modal.classList.remove("hidden");
}

function closeModal() {
  modal.classList.add("hidden");
}

function copyValue(idx) {
  navigator.clipboard.writeText(_fullValues[idx]);
}

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

function displayValueFull(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return JSON.stringify(v, null, 2);
  return String(v);
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function valueCell(raw, colorClass) {
  const compact = displayValue(raw);

  if (compact === "—") {
    return `<span class="text-xs text-gray-600">—</span>`;
  }

  const full = displayValueFull(raw);
  const needsTrunc = compact.length > TRUNCATE_AT;
  const shown = needsTrunc ? compact.slice(0, TRUNCATE_AT) + "…" : compact;
  const idx = _fullValues.push(full) - 1;

  return `
    <div class="flex items-start gap-1.5">
      <span class="font-mono text-xs ${colorClass} break-all leading-relaxed">${escapeHtml(shown)}</span>
      <div class="flex items-center gap-1 shrink-0 mt-0.5">
        ${needsTrunc ? `<button onclick="openModal(${idx})" class="text-gray-600 hover:text-gray-300 transition-colors" title="Ver completo"><i data-lucide="eye" class="w-3 h-3"></i></button>` : ""}
        <button onclick="copyValue(${idx})" class="text-gray-600 hover:text-gray-300 transition-colors" title="Copiar"><i data-lucide="copy" class="w-3 h-3"></i></button>
      </div>
    </div>`;
}

function renderFields(fields) {
  _fullValues.length = 0;
  const tbody = document.getElementById("fields-body");

  tbody.innerHTML = fields
    .map((f) => {
      const isAcerto = f.status === "acerto";
      const obtidoColor = isAcerto ? "text-green-400" : "text-red-400";

      return `
        <tr class="border-t border-gray-800">
          <td class="py-3 pr-6 font-mono text-gray-300 text-xs align-top">${escapeHtml(f.campo)}</td>
          <td class="py-3 pr-6 align-top">${valueCell(f.valor_esperado, "text-gray-400")}</td>
          <td class="py-3 pr-6 align-top">${valueCell(f.valor_obtido, obtidoColor)}</td>
          <td class="py-3 align-top">
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
