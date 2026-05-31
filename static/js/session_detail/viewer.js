document.querySelectorAll(".case-item").forEach((item) => {
  item.querySelector("span").addEventListener("click", () => selectCase(item));
  item.querySelector(".pdf-btn").addEventListener("click", (e) => {
    e.stopPropagation();
    openPdfModal(item.dataset.caseName);
  });
});

document.getElementById("pdf-modal-close").addEventListener("click", closePdfModal);
document.getElementById("pdf-modal-backdrop").addEventListener("click", closePdfModal);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closePdfModal();
});

const firstCase = document.querySelector(".case-item");
if (firstCase) selectCase(firstCase);

function selectCase(item) {
  document.querySelectorAll(".case-item.selected").forEach((el) => el.classList.remove("selected"));
  item.classList.add("selected");

  document.getElementById("actual-label").textContent = item.dataset.filename;

  window.App.editorsReady.then(() => {
    window.App.expectedEditor.setValue(JSON.stringify(JSON.parse(item.dataset.expected), null, 2));
    window.App.actualEditor.setValue(JSON.stringify(JSON.parse(item.dataset.actual), null, 2));
  });
}

function openPdfModal(caseName) {
  document.getElementById("pdf-modal-frame").src = `/cases/${caseName}/pdf`;
  document.getElementById("pdf-modal-label").textContent = caseName;
  document.getElementById("pdf-modal").classList.remove("hidden");
}

function closePdfModal() {
  document.getElementById("pdf-modal").classList.add("hidden");
  document.getElementById("pdf-modal-frame").src = "";
}
