window.App = {
  resultadoEditor: null,
  editorsReady: null,
};

lucide.createIcons();

window.App.editorsReady = new Promise((resolve) => {
  require(["vs/editor/editor.main"], function () {
    window.App.resultadoEditor = createMonacoEditor("json-editor");
    resolve();
  });
});
