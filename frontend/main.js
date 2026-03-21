const API = "http://localhost:7070";
const grid = document.getElementById("gallery-grid");
const newBtn = document.getElementById("new-btn");
const picker = document.getElementById("type-picker");
const pickerClose = document.getElementById("picker-close");

const TYPE_LABELS = { slime: "Slime Mold", boids: "Boids", cells: "Cells" };

function formatDate(ts) {
  return new Date(ts * 1000).toLocaleDateString(undefined, {
    month: "short", day: "numeric", year: "numeric",
  });
}

function createCard(sim) {
  const card = document.createElement("div");
  card.className = "slime-card";
  card.innerHTML = `
    <div class="card-preview"></div>
    <div class="card-info">
      <div class="card-top-row">
        <span class="card-name">${sim.name}</span>
        <span class="type-badge type-badge--${sim.type}">${TYPE_LABELS[sim.type] ?? sim.type}</span>
      </div>
      <span class="card-meta">${sim.author} &middot; ${formatDate(sim.created_at)}</span>
    </div>
  `;
  card.addEventListener("click", () => {
    window.location.href = `simulation.html?id=${sim.id}`;
  });
  return card;
}

async function createSim(type) {
  const res = await fetch(`${API}/api/slimes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, name: `New ${TYPE_LABELS[type]}`, author: "Anonymous" }),
  });
  if (!res.ok) throw new Error("Failed to create");
  return res.json();
}

async function loadGallery() {
  try {
    const res = await fetch(`${API}/api/slimes`);
    if (!res.ok) throw new Error();
    const sims = await res.json();
    grid.innerHTML = "";
    sims.forEach((s) => grid.appendChild(createCard(s)));
    if (sims.length === 0) {
      const empty = document.createElement("div");
      empty.className = "gallery-empty";
      empty.textContent = "No simulations yet. Hit + New to get started.";
      grid.appendChild(empty);
    }
  } catch {
    grid.innerHTML = `<div class="gallery-empty">Could not reach backend.</div>`;
  }
}

// Type picker
newBtn.addEventListener("click", () => picker.classList.remove("hidden"));
pickerClose.addEventListener("click", () => picker.classList.add("hidden"));
picker.addEventListener("click", (e) => { if (e.target === picker) picker.classList.add("hidden"); });

document.querySelectorAll(".type-option").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const type = btn.dataset.type;
    btn.disabled = true;
    try {
      const sim = await createSim(type);
      window.location.href = `simulation.html?id=${sim.id}`;
    } catch {
      btn.disabled = false;
      alert("Could not reach backend.");
    }
  });
});

loadGallery();
