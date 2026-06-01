function initNotesModal(getSessionId) {
  const modal = document.getElementById("notes-modal");
  const textarea = document.getElementById("notes-textarea");
  const saveBtn = document.getElementById("notes-save");
  const cancelBtn = document.getElementById("notes-cancel");
  const closeBtn = document.getElementById("notes-close");
  const backdrop = document.getElementById("notes-backdrop");

  let currentSessionId = null;

  function openModal(sessionId, currentNotes) {
    currentSessionId = sessionId;
    textarea.value = currentNotes || "";
    modal.classList.remove("hidden");
    textarea.focus();
  }

  async function saveNotes() {
    if (!currentSessionId) return;

    saveBtn.disabled = true;
    await fetch(`/analysis/${currentSessionId}/notes`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textarea.value }),
    });

    modal.classList.add("hidden");
    window.location.reload();
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  saveBtn.addEventListener("click", saveNotes);
  cancelBtn.addEventListener("click", closeModal);
  closeBtn.addEventListener("click", closeModal);
  backdrop.addEventListener("click", closeModal);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) saveNotes();
  });

  return { openModal };
}
