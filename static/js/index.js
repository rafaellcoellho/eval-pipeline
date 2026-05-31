lucide.createIcons();

document.getElementById("pdf-fullscreen-btn").addEventListener("click", () => {
  toggleFullscreen(document.getElementById("pdf-fullscreen-btn").closest(".flex-1"));
});

document.getElementById("json-fullscreen-btn").addEventListener("click", () => {
  toggleFullscreen(document.getElementById("json-fullscreen-btn").closest(".flex-1"));
});

document.addEventListener("fullscreenchange", () => {
  const isFullscreen = !!document.fullscreenElement;
  document.querySelectorAll(".fullscreen-btn").forEach((btn) => {
    const isThisPanel = btn.closest(".flex-1") === document.fullscreenElement;
    btn.querySelector(".icon-expand").classList.toggle("hidden", isFullscreen && isThisPanel);
    btn.querySelector(".icon-compress").classList.toggle("hidden", !isFullscreen || !isThisPanel);
  });
});

function toggleFullscreen(panel) {
  if (document.fullscreenElement === panel) {
    document.exitFullscreen();
  } else {
    panel.requestFullscreen();
  }
}

require.config({
  paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.47.0/min/vs" },
});

let monacoEditor = null;
let selectedCaseName = null;

require(["vs/editor/editor.main"], function () {
  monacoEditor = monaco.editor.create(document.getElementById("json-editor"), {
    value: "",
    language: "json",
    theme: "vs-dark",
    readOnly: true,
    domReadOnly: true,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    folding: false,
    lineNumbers: "on",
    contextmenu: false,
    fontSize: 13,
    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
    padding: { top: 12, bottom: 12 },
    renderLineHighlight: "line",
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    overviewRulerBorder: false,
    scrollbar: { vertical: "auto", horizontal: "hidden" },
  });

  document.querySelectorAll("#cases-body tr").forEach((row) => {
    row.querySelector(".eye-btn").addEventListener("click", () => {
      const caseName = row.dataset.caseName;

      if (selectedCaseName === caseName) {
        deselect(row);
      } else {
        selectCase(row, caseName);
      }
    });
  });
});

function deselect(row) {
  selectedCaseName = null;
  row.classList.remove("selected");
  setEyeActive(row, false);
  hideViewer();
}

function selectCase(row, caseName) {
  const previousRow = document.querySelector("#cases-body tr.selected");
  if (previousRow) {
    previousRow.classList.remove("selected");
    setEyeActive(previousRow, false);
  }

  selectedCaseName = caseName;
  row.classList.add("selected");
  setEyeActive(row, true);
  showViewer(caseName, row.dataset.pdfFilename, row.dataset.resultadoFilename, row.dataset.resultado);
}

function setEyeActive(row, active) {
  const btn = row.querySelector(".eye-btn");
  btn.classList.toggle("text-blue-400", active);
  btn.classList.toggle("bg-blue-500/10", active);
  btn.classList.toggle("text-gray-500", !active);
}

function hideViewer() {
  document.getElementById("viewer").classList.add("hidden");
  document.getElementById("pdf-frame").src = "";
}

function showViewer(caseName, pdfFilename, resultadoFilename, resultadoEncoded) {
  document.getElementById("viewer").classList.remove("hidden");
  document.getElementById("pdf-frame").src = `/cases/${caseName}/pdf`;
  document.getElementById("viewer-case-label").textContent = caseName;
  document.getElementById("pdf-filename-label").textContent = pdfFilename;
  document.getElementById("resultado-filename-label").textContent = resultadoFilename;
  document.getElementById("viewer-json-case-label").textContent = caseName;

  const json = JSON.stringify(JSON.parse(resultadoEncoded), null, 2);
  monacoEditor.setValue(json);
}
