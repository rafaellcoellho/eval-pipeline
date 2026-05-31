document.querySelectorAll("#cases-body tr").forEach((row) => {
  row.querySelector(".eye-btn").addEventListener("click", () => {
    const caseName = row.dataset.caseName;

    if (window.App.selectedCaseName === caseName) {
      deselectCase(row);
    } else {
      selectCase(row, caseName);
    }
  });
});

document.getElementById("pdf-fullscreen-btn").addEventListener("click", () => {
  toggleFullscreen(document.getElementById("pdf-fullscreen-btn").closest(".panel"));
});

document.getElementById("json-fullscreen-btn").addEventListener("click", () => {
  toggleFullscreen(document.getElementById("json-fullscreen-btn").closest(".panel"));
});

document.addEventListener("fullscreenchange", () => {
  const isFullscreen = !!document.fullscreenElement;
  document.querySelectorAll(".fullscreen-btn").forEach((btn) => {
    const isThisPanel = btn.closest(".panel") === document.fullscreenElement;
    btn.querySelector(".icon-expand").classList.toggle("hidden", isFullscreen && isThisPanel);
    btn.querySelector(".icon-compress").classList.toggle("hidden", !isFullscreen || !isThisPanel);
  });
});

function deselectCase(row) {
  window.App.selectedCaseName = null;
  row.classList.remove("selected");
  setEyeActive(row, false);
  document.getElementById("viewer").classList.add("hidden");
  document.getElementById("pdf-frame").src = "";
}

function selectCase(row, caseName) {
  const previousRow = document.querySelector("#cases-body tr.selected");
  if (previousRow) {
    previousRow.classList.remove("selected");
    setEyeActive(previousRow, false);
  }

  window.App.selectedCaseName = caseName;
  row.classList.add("selected");
  setEyeActive(row, true);

  document.getElementById("viewer").classList.remove("hidden");
  document.getElementById("pdf-frame").src = `/cases/${caseName}/pdf`;
  document.getElementById("viewer-case-label").textContent = caseName;
  document.getElementById("pdf-filename-label").textContent = row.dataset.pdfFilename;
  document.getElementById("resultado-filename-label").textContent = row.dataset.resultadoFilename;
  document.getElementById("viewer-json-case-label").textContent = caseName;

  const json = JSON.stringify(JSON.parse(row.dataset.resultado), null, 2);
  window.App.editorsReady.then(() => window.App.resultadoEditor.setValue(json));
}

function setEyeActive(row, active) {
  const btn = row.querySelector(".eye-btn");
  btn.classList.toggle("text-blue-400", active);
  btn.classList.toggle("bg-blue-500/10", active);
  btn.classList.toggle("text-gray-500", !active);
}

function toggleFullscreen(panel) {
  if (document.fullscreenElement === panel) {
    document.exitFullscreen();
  } else {
    panel.requestFullscreen();
  }
}
