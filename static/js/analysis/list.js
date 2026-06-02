lucide.createIcons();

const { openModal: openNotesModal } = initNotesModal();

document.querySelectorAll(".notes-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    openNotesModal(btn.dataset.session, btn.dataset.notes);
  });
});

const checkboxes = document.querySelectorAll(".session-checkbox");
const deleteSelectedBtn = document.getElementById("delete-selected-btn");
const selectedCountLabel = document.getElementById("selected-count");

checkboxes.forEach((cb) => cb.addEventListener("change", updateSelection));

function updateSelection() {
  const n = [...checkboxes].filter((cb) => cb.checked).length;

  if (n >= 1) {
    selectedCountLabel.textContent = `${n} selecionada${n > 1 ? "s" : ""}`;
    selectedCountLabel.classList.remove("hidden");
    deleteSelectedBtn.classList.remove("hidden");
    deleteSelectedBtn.disabled = false;
  } else {
    selectedCountLabel.classList.add("hidden");
    deleteSelectedBtn.classList.add("hidden");
    deleteSelectedBtn.disabled = true;
  }
}

document.querySelectorAll(".delete-single-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    await fetch(`/analysis/${btn.dataset.session}`, { method: "DELETE" });
    window.location.reload();
  });
});

deleteSelectedBtn.addEventListener("click", async () => {
  const ids = [...checkboxes].filter((cb) => cb.checked).map((cb) => cb.value);

  await Promise.all(ids.map((id) => fetch(`/analysis/${id}`, { method: "DELETE" })));
  window.location.reload();
});

document.getElementById("delete-all-btn").addEventListener("click", async () => {
  if (!confirm("Deletar todas as análises? Esta ação não pode ser desfeita.")) return;

  await fetch("/analysis", { method: "DELETE" });
  window.location.reload();
});
