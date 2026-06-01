require.config({
  paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.47.0/min/vs" },
});

function createMonacoEditor(elementId) {
  return monaco.editor.create(document.getElementById(elementId), {
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
    fontFamily: '"Cascadia Mono", Menlo, Monaco, "Liberation Mono", "Courier New", monospace',
    padding: { top: 12, bottom: 12 },
    renderLineHighlight: "line",
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    overviewRulerBorder: false,
    scrollbar: { vertical: "auto", horizontal: "hidden" },
  });
}
