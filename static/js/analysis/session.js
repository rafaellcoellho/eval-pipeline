lucide.createIcons();

const TRUNCATE_AT = 80;
const _entries = [];

const modal = document.getElementById("value-modal");
const modalTitle = document.getElementById("modal-title");
const modalContentArea = document.getElementById("modal-content-area");
const modalCopy = document.getElementById("modal-copy");
const modalClose = document.getElementById("modal-close");
const modalBackdrop = document.getElementById("modal-backdrop");

modalClose.addEventListener("click", closeModal);
modalBackdrop.addEventListener("click", closeModal);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

modalCopy.addEventListener("click", () => {
  const idx = parseInt(modal.dataset.entryIdx);
  navigator.clipboard.writeText(entryToText(_entries[idx]));
  modalCopy.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Copiado!';
  lucide.createIcons({ nodes: [modalCopy] });
  setTimeout(() => {
    modalCopy.innerHTML = '<i data-lucide="copy" class="w-3.5 h-3.5"></i> Copiar';
    lucide.createIcons({ nodes: [modalCopy] });
  }, 1500);
});

function entryToText(entry) {
  if (entry.type === "text") return entry.value;
  return JSON.stringify(entry.value, null, 2);
}

function openModal(idx) {
  const entry = _entries[idx];
  modal.dataset.entryIdx = idx;
  modalTitle.textContent = entry.label;
  modalContentArea.innerHTML = renderModalContent(entry);
  modal.classList.remove("hidden");
  lucide.createIcons({ nodes: Array.from(modalContentArea.querySelectorAll("[data-lucide]")) });
}

function closeModal() {
  modal.classList.add("hidden");
}

function copyValue(idx) {
  navigator.clipboard.writeText(entryToText(_entries[idx]));
}

function renderModalContent(entry) {
  if (entry.type === "text") {
    return `<pre class="text-xs text-gray-300 font-mono whitespace-pre-wrap break-all leading-relaxed">${escapeHtml(entry.value)}</pre>`;
  }

  if (entry.type === "string-list") {
    const items = entry.value
      .map((v, i) => `
        <li class="flex items-start gap-3 py-1.5 border-b border-gray-800/50 last:border-0">
          <span class="font-mono text-xs text-gray-600 w-6 shrink-0 text-right">${i + 1}</span>
          <span class="font-mono text-xs text-gray-300 break-all">${escapeHtml(String(v))}</span>
        </li>`)
      .join("");
    return `<ol>${items}</ol>`;
  }

  if (entry.type === "item-compare") {
    const { exp, obt, allKeys } = entry.value;
    const rows = allKeys
      .map((k) => {
        const expVal = exp && exp[k] !== undefined ? displayValue(exp[k]) : "—";
        const obtVal = obt && obt[k] !== undefined ? displayValue(obt[k]) : "—";
        const diff = JSON.stringify(exp?.[k]) !== JSON.stringify(obt?.[k]);
        return `
          <tr class="${diff ? "bg-red-500/5" : ""}">
            <td class="px-3 py-1.5 font-mono text-xs ${diff ? "text-gray-400" : "text-gray-600"} align-top w-44">${escapeHtml(k)}</td>
            <td class="px-3 py-1.5 font-mono text-xs ${diff ? "text-gray-300" : "text-gray-500"} align-top">${escapeHtml(expVal)}</td>
            <td class="px-3 py-1.5 font-mono text-xs ${diff ? "text-red-400" : "text-gray-500"} align-top">${escapeHtml(obtVal)}</td>
          </tr>`;
      })
      .join("");
    return `
      <table class="w-full border border-gray-800 rounded overflow-hidden">
        <thead>
          <tr class="bg-gray-800/50 text-xs text-gray-600">
            <th class="text-left font-normal px-3 py-2 w-44">campo</th>
            <th class="text-left font-normal px-3 py-2">esperado</th>
            <th class="text-left font-normal px-3 py-2">obtido</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-800/60">${rows}</tbody>
      </table>`;
  }

  const cards = entry.value
    .map((obj, i) => {
      const rows = Object.entries(obj)
        .map(([k, v]) => `
          <div class="flex gap-3 py-1.5 border-b border-gray-800/40 last:border-0">
            <span class="font-mono text-xs text-gray-500 w-44 shrink-0">${escapeHtml(k)}</span>
            <span class="font-mono text-xs text-gray-300 break-all">${escapeHtml(displayValue(v))}</span>
          </div>`)
        .join("");
      return `
        <div class="rounded-lg border border-gray-700/50 overflow-hidden mb-3 last:mb-0">
          <div class="px-4 py-2 bg-gray-800/50 border-b border-gray-700/50">
            <span class="text-xs font-medium text-gray-400">Item ${i + 1}</span>
          </div>
          <div class="px-4 py-1">${rows}</div>
        </div>`;
    })
    .join("");
  return `<div>${cards}</div>`;
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

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function storeEntry(type, value, label) {
  return _entries.push({ type, value, label }) - 1;
}

function viewBtn(idx) {
  return `<button onclick="openModal(${idx})" class="text-gray-600 hover:text-gray-300 transition-colors" title="Ver completo"><i data-lucide="eye" class="w-3 h-3"></i></button>`;
}

function copyBtn(idx) {
  return `<button onclick="copyValue(${idx})" class="text-gray-600 hover:text-gray-300 transition-colors" title="Copiar"><i data-lucide="copy" class="w-3 h-3"></i></button>`;
}

function valueCell(raw, colorClass) {
  if (raw === null || raw === undefined) {
    return `<span class="text-xs text-gray-600">—</span>`;
  }

  const compact = displayValue(raw);
  const needsTrunc = compact.length > TRUNCATE_AT;
  const shown = needsTrunc ? compact.slice(0, TRUNCATE_AT) + "…" : compact;
  const idx = storeEntry("text", JSON.stringify(raw, null, 2), "Valor completo");

  return `
    <div class="flex items-start gap-1.5">
      <span class="font-mono text-xs ${colorClass} break-all leading-relaxed">${escapeHtml(shown)}</span>
      <div class="flex items-center gap-1 shrink-0 mt-0.5">
        ${needsTrunc ? viewBtn(idx) : ""}
        ${copyBtn(idx)}
      </div>
    </div>`;
}

function compareItems(exp, obt) {
  if (typeof exp === "object" && exp !== null && typeof obt === "object" && obt !== null) {
    const allKeys = new Set([...Object.keys(exp), ...Object.keys(obt)]);
    const diffs = [];
    for (const key of allKeys) {
      if (JSON.stringify(exp[key]) !== JSON.stringify(obt[key])) diffs.push(key);
    }
    return { match: diffs.length === 0, diffs };
  }
  return { match: JSON.stringify(exp) === JSON.stringify(obt), diffs: [] };
}

function listComparisonCell(expected, obtained, sortKey) {
  const isObjects = expected.length > 0 && typeof expected[0] === "object" && expected[0] !== null;
  const obtainedIsArray = Array.isArray(obtained);
  const expIdx = storeEntry("object-list", expected, `Esperado — lista de ${expected.length} objetos`);
  const obtIdx = storeEntry(isObjects ? "object-list" : "string-list", obtainedIsArray ? obtained : [], `Obtido — lista de ${obtainedIsArray ? obtained.length : 0} objetos`);

  if (!obtainedIsArray) {
    return `
      <div class="flex items-center gap-2">
        <span class="text-xs text-red-400 font-mono">obtido não é uma lista</span>
        ${copyBtn(expIdx)}
      </div>`;
  }

  if (isObjects) {
    return renderObjectListDiff(expected, obtained, sortKey, expIdx, obtIdx);
  }

  return renderStringListDiff(expected, obtained, expIdx, obtIdx);
}

function itemLabel(item, sortKey, index) {
  const keyVal = sortKey && item && item[sortKey] ? escapeHtml(String(item[sortKey])) : null;
  const num = `<span class="font-mono text-xs text-gray-600 shrink-0">item ${index + 1}</span>`;
  const label = keyVal ? `<span class="font-mono text-xs text-gray-400">${keyVal}</span>` : "";
  return `<div class="flex items-center gap-2">${num}${label}</div>`;
}

function itemFullCompareEntry(exp, obt, sortKey, index) {
  const ref = exp || obt;
  const keyVal = sortKey && ref ? (ref[sortKey] || `item ${index + 1}`) : `item ${index + 1}`;
  const allKeys = [...new Set([...Object.keys(exp || {}), ...Object.keys(obt || {})])];
  return storeEntry("item-compare", { exp, obt, allKeys }, String(keyVal));
}

function mergeJoinByKey(expected, obtained, key) {
  const expMap = new Map(expected.map((item) => [String(item[key]), item]));
  const obtMap = new Map(obtained.map((item) => [String(item[key]), item]));
  const allKeys = [...new Set([...expMap.keys(), ...obtMap.keys()])].sort();
  return allKeys.map((k) => ({ keyVal: k, exp: expMap.get(k) || null, obt: obtMap.get(k) || null }));
}

function renderObjectListDiff(expected, obtained, sortKey, expIdx, obtIdx) {
  const pairs = sortKey
    ? mergeJoinByKey(expected, obtained, sortKey)
    : Array.from({ length: Math.max(expected.length, obtained.length) }, (_, i) => ({
        keyVal: null,
        exp: expected[i] || null,
        obt: obtained[i] || null,
      }));

  const blocks = [];

  for (const [i, { exp, obt }] of pairs.entries()) {

    if (exp === null) {
      const itemIdx = itemFullCompareEntry(null, obt, sortKey, i);
      blocks.push(`
        <div class="flex items-center gap-2 py-0.5">
          ${itemLabel(obt, sortKey, i)}
          <span class="text-xs text-yellow-400 flex items-center gap-1"><i data-lucide="plus" class="w-3 h-3 shrink-0"></i> extra no obtido</span>
          ${viewBtn(itemIdx)}
        </div>`);
      continue;
    }

    if (obt === null) {
      const itemIdx = itemFullCompareEntry(exp, null, sortKey, i);
      blocks.push(`
        <div class="flex items-center gap-2 py-0.5">
          ${itemLabel(exp, sortKey, i)}
          <span class="text-xs text-red-400 flex items-center gap-1"><i data-lucide="minus" class="w-3 h-3 shrink-0"></i> ausente no obtido</span>
          ${viewBtn(itemIdx)}
        </div>`);
      continue;
    }

    const allKeys = [...new Set([...Object.keys(exp), ...Object.keys(obt)])];
    const diffKeys = allKeys.filter((k) => JSON.stringify(exp[k]) !== JSON.stringify(obt[k]));
    const itemIdx = itemFullCompareEntry(exp, obt, sortKey, i);

    if (diffKeys.length === 0) {
      blocks.push(`
        <div class="flex items-center gap-2 py-0.5">
          ${itemLabel(exp, sortKey, i)}
          <span class="text-xs text-green-400 flex items-center gap-1"><i data-lucide="check" class="w-3 h-3 shrink-0"></i> todos campos iguais</span>
          ${viewBtn(itemIdx)}
        </div>`);
      continue;
    }

    const fieldRows = diffKeys
      .map((k) => {
        const expVal = exp[k] !== undefined ? displayValue(exp[k]) : "—";
        const obtVal = obt[k] !== undefined ? displayValue(obt[k]) : "—";
        return `
          <tr>
            <td class="px-3 py-1.5 font-mono text-xs text-gray-500 align-top w-40">${escapeHtml(k)}</td>
            <td class="px-3 py-1.5 font-mono text-xs text-gray-400 align-top">${escapeHtml(expVal)}</td>
            <td class="px-3 py-1.5 font-mono text-xs text-red-400 align-top">${escapeHtml(obtVal)}</td>
          </tr>`;
      })
      .join("");

    blocks.push(`
      <div class="mb-3">
        <div class="flex items-center gap-2 mb-1">
          ${itemLabel(exp, sortKey, i)}
          <span class="text-xs text-red-400 flex items-center gap-1"><i data-lucide="x" class="w-3 h-3 shrink-0"></i> ${diffKeys.length} campo(s) diferente(s)</span>
          ${viewBtn(itemIdx)}
        </div>
        <div class="ml-4 border border-gray-800 rounded overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-800/40 text-xs text-gray-600">
                <th class="text-left font-normal px-3 py-1.5 w-40">campo</th>
                <th class="text-left font-normal px-3 py-1.5">esperado</th>
                <th class="text-left font-normal px-3 py-1.5">obtido</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/60">${fieldRows}</tbody>
          </table>
        </div>
      </div>`);
  }

  return `
    <div class="space-y-0.5">
      ${blocks.join("")}
    </div>
    <div class="flex items-center gap-1.5 mt-3 pt-2 border-t border-gray-800/60">
      <span class="text-xs text-gray-600">esperado</span>${viewBtn(expIdx)}${copyBtn(expIdx)}
      <span class="text-xs text-gray-600 ml-3">obtido</span>${viewBtn(obtIdx)}${copyBtn(obtIdx)}
    </div>`;
}

function renderStringListDiff(expected, obtained, expIdx, obtIdx) {
  const obtainedSet = new Set(obtained.map((v) => JSON.stringify(v)));
  const expectedSet = new Set(expected.map((v) => JSON.stringify(v)));

  const expItems = expected
    .map((v) => {
      const match = obtainedSet.has(JSON.stringify(v));
      return `<li class="flex items-center gap-1 text-xs font-mono py-0.5 ${match ? "text-gray-400" : "text-red-400"}">
        <i data-lucide="${match ? "check" : "x"}" class="w-3 h-3 shrink-0"></i>
        ${escapeHtml(String(v))}
      </li>`;
    })
    .join("");

  const obtItems = obtained
    .map((v) => {
      const match = expectedSet.has(JSON.stringify(v));
      return `<li class="flex items-center gap-1 text-xs font-mono py-0.5 ${match ? "text-gray-400" : "text-red-400"}">
        <i data-lucide="${match ? "check" : "x"}" class="w-3 h-3 shrink-0"></i>
        ${escapeHtml(String(v))}
      </li>`;
    })
    .join("");

  return `
    <div class="grid grid-cols-2 gap-6">
      <div>
        <div class="text-xs text-gray-600 mb-1">esperado</div>
        <ol class="space-y-0">${expItems}</ol>
        <div class="flex items-center gap-1 mt-1.5">${copyBtn(expIdx)}</div>
      </div>
      <div>
        <div class="text-xs text-gray-600 mb-1">obtido</div>
        <ol class="space-y-0">${obtItems}</ol>
        <div class="flex items-center gap-1 mt-1.5">${copyBtn(obtIdx)}</div>
      </div>
    </div>`;
}

function renderFields(fields) {
  _entries.length = 0;
  const tbody = document.getElementById("fields-body");

  tbody.innerHTML = fields
    .map((f) => {
      const isAcerto = f.status === "acerto";
      const statusBadge = `
        <span class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${isAcerto ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}">
          <i data-lucide="${isAcerto ? "check" : "x"}" class="w-3 h-3"></i>
          ${isAcerto ? "acerto" : "erro"}
        </span>`;

      if (Array.isArray(f.valor_esperado)) {
        return `
          <tr class="border-t border-gray-800">
            <td class="py-3 pr-6 font-mono text-gray-300 text-xs align-top">${escapeHtml(f.campo)}</td>
            <td class="py-3 pr-6 align-top" colspan="2">${listComparisonCell(f.valor_esperado, f.valor_obtido, f.list_sort_key || null)}</td>
            <td class="py-3 align-top">${statusBadge}</td>
          </tr>`;
      }

      const obtidoColor = isAcerto ? "text-green-400" : "text-red-400";
      return `
        <tr class="border-t border-gray-800">
          <td class="py-3 pr-6 font-mono text-gray-300 text-xs align-top">${escapeHtml(f.campo)}</td>
          <td class="py-3 pr-6 align-top">${valueCell(f.valor_esperado, "text-gray-400")}</td>
          <td class="py-3 pr-6 align-top">${valueCell(f.valor_obtido, obtidoColor)}</td>
          <td class="py-3 align-top">${statusBadge}</td>
        </tr>`;
    })
    .join("");

  lucide.createIcons({ nodes: Array.from(tbody.querySelectorAll("[data-lucide]")) });
}
