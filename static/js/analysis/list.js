lucide.createIcons();

const { openModal: openNotesModal } = initNotesModal();

document.querySelectorAll(".notes-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    openNotesModal(btn.dataset.session, btn.dataset.notes);
  });
});
