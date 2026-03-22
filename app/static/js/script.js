function toggleAddForm() {
    const form = document.getElementById("addForm");
    form.style.display = (form.style.display === "block") ? "none" : "block";
}

function toggleRemoveForm() {
    const form = document.getElementById("removeForm");
    form.style.display = (form.style.display === "block") ? "none" : "block";
}

const labels = document.getElementById("dayLabels");
const today = new Date();
if (labels) {
    labels.innerHTML = "<div></div>";
}
for (let i = 0; i < 7; i++) {
    const d = new Date();
    d.setDate(today.getDate() + i);

    const label = document.createElement("div");
    label.textContent = d.toLocaleDateString(undefined, {
        weekday: "short",
        month: "numeric",
        day: "numeric"
    });

    labels.appendChild(label);
}