lucide.createIcons();

const checkboxes = document.querySelectorAll(".session-checkbox");
const compareBtn = document.getElementById("compare-btn");
const countLabel = document.getElementById("selected-count");

checkboxes.forEach((cb) => cb.addEventListener("change", updateSelection));

function updateSelection() {
  const checked = [...checkboxes].filter((cb) => cb.checked);
  const n = checked.length;

  if (n >= 2) {
    countLabel.textContent = `${n} selecionadas`;
    countLabel.classList.remove("hidden");
    compareBtn.classList.remove("hidden");
    compareBtn.disabled = false;
  } else {
    countLabel.classList.add("hidden");
    compareBtn.classList.add("hidden");
    compareBtn.disabled = true;
  }
}

compareBtn.addEventListener("click", () => {
  const ids = [...checkboxes]
    .filter((cb) => cb.checked)
    .map((cb) => cb.value);

  const params = ids.map((id) => `sessions=${encodeURIComponent(id)}`).join("&");
  window.location.href = `/analysis/compare?${params}`;
});
