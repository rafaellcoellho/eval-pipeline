lucide.createIcons();

const container = document.querySelector("[data-case]");
const caseName = container.dataset.case;
const initialJson = JSON.stringify(JSON.parse(container.dataset.resultado), null, 2);

const saveBtn = document.getElementById("save-btn");
const unsavedBadge = document.getElementById("unsaved-badge");
const copyJsonBtn = document.getElementById("copy-json-btn");
const copyOcrBtn = document.getElementById("copy-ocr-btn");

let editor = null;

require(["vs/editor/editor.main"], function () {
  editor = monaco.editor.create(document.getElementById("json-editor"), {
    value: initialJson,
    language: "json",
    theme: "vs-dark",
    readOnly: false,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    folding: false,
    lineNumbers: "on",
    fontSize: 13,
    fontFamily: '"Cascadia Mono", Menlo, Monaco, "Liberation Mono", "Courier New", monospace',
    padding: { top: 12, bottom: 12 },
    renderLineHighlight: "line",
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    overviewRulerBorder: false,
    scrollbar: { vertical: "auto", horizontal: "hidden" },
  });

  editor.onDidChangeModelContent(() => {
    const isDirty = editor.getValue() !== initialJson;
    saveBtn.disabled = !isDirty;
    unsavedBadge.classList.toggle("hidden", !isDirty);
  });
});

copyJsonBtn.addEventListener("click", () => {
  const value = editor ? editor.getValue() : initialJson;
  navigator.clipboard.writeText(value);
  copyJsonBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Copiado!';
  lucide.createIcons({ nodes: [copyJsonBtn] });
  setTimeout(() => {
    copyJsonBtn.innerHTML = '<i data-lucide="braces" class="w-3.5 h-3.5"></i> Copiar JSON';
    lucide.createIcons({ nodes: [copyJsonBtn] });
  }, 1500);
});

if (copyOcrBtn) {
  copyOcrBtn.addEventListener("click", async () => {
    const res = await fetch(`/cases/${caseName}/ocr`);
    if (!res.ok) return;
    const { text } = await res.json();
    navigator.clipboard.writeText(text);
    copyOcrBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Copiado!';
    lucide.createIcons({ nodes: [copyOcrBtn] });
    setTimeout(() => {
      copyOcrBtn.innerHTML = '<i data-lucide="clipboard-copy" class="w-3.5 h-3.5"></i> Copiar OCR';
      lucide.createIcons({ nodes: [copyOcrBtn] });
    }, 1500);
  });
}

saveBtn.addEventListener("click", async () => {
  if (!editor) return;

  let parsed;
  try {
    parsed = JSON.parse(editor.getValue());
  } catch {
    alert("JSON inválido. Corrija antes de salvar.");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Salvando...';
  lucide.createIcons({ nodes: [saveBtn] });

  await fetch(`/cases/${caseName}/resultado`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(parsed),
  });

  unsavedBadge.classList.add("hidden");
  saveBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i> Salvo!';
  lucide.createIcons({ nodes: [saveBtn] });

  setTimeout(() => {
    saveBtn.innerHTML = '<i data-lucide="save" class="w-3.5 h-3.5"></i> Salvar';
    lucide.createIcons({ nodes: [saveBtn] });
    saveBtn.disabled = true;
  }, 1500);
});
