window.App = {
  expectedEditor: null,
  actualEditor: null,
  editorsReady: null,
};

lucide.createIcons();

window.App.editorsReady = new Promise((resolve) => {
  require(["vs/editor/editor.main"], function () {
    window.App.expectedEditor = createMonacoEditor("expected-editor");
    window.App.actualEditor = createMonacoEditor("actual-editor");
    resolve();
  });
});
