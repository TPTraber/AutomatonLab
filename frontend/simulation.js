const API = "http://localhost:7070";

const urlParams = new URLSearchParams(window.location.search);
const simId = urlParams.get("id");
if (!simId) window.location.href = "index.html";

const form = document.getElementById("params-form");
const statusEl = document.getElementById("status");
const runBtn = document.getElementById("run-btn");
const saveBtn = document.getElementById("save-btn");
const nameInput = document.getElementById("slime-name");
const authorEl = document.getElementById("slime-author");
const typeBadge = document.getElementById("type-badge");

const TYPE_LABELS = { slime: "Slime Mold", boids: "Boids", cells: "Cells" };

const SCHEMAS = {
  slime: [
    { group: "Agents", fields: [
      { name: "num_agents",    label: "Agent Count",       min: 1,    max: 100000, step: 1    },
      { name: "step_size",     label: "Step Size",         min: 0.1,  max: 10,     step: 0.1  },
    ]},
    { group: "Sensors", fields: [
      { name: "sensor_angle",    label: "Sensor Angle (°)",  min: 1,  max: 180, step: 1   },
      { name: "sensor_distance", label: "Sensor Distance",   min: 1,  max: 50,  step: 1   },
      { name: "rotation_angle",  label: "Rotation Angle (°)",min: 1,  max: 180, step: 1   },
    ]},
    { group: "Trail", fields: [
      { name: "deposit_amount", label: "Deposit Amount", min: 0.1, max: 50, step: 0.1 },
      { name: "decay_rate",     label: "Decay Rate",     min: 0.01, max: 1, step: 0.01 },
      { name: "diffuse_rate",   label: "Diffuse Rate",   min: 0.01, max: 1, step: 0.01 },
    ]},
    { group: "Canvas", fields: [
      { name: "width",  label: "Width",  min: 100, max: 2000, step: 10 },
      { name: "height", label: "Height", min: 100, max: 2000, step: 10 },
    ]},
  ],

  boids: [
    { group: "Flock", fields: [
      { name: "num_boids",  label: "Boid Count", min: 1,   max: 10000, step: 1   },
      { name: "max_speed",  label: "Max Speed",  min: 0.1, max: 20,    step: 0.1 },
      { name: "min_speed",  label: "Min Speed",  min: 0.1, max: 20,    step: 0.1 },
    ]},
    { group: "Perception", fields: [
      { name: "perception_radius",  label: "Perception Radius",  min: 1, max: 300, step: 1 },
      { name: "separation_radius",  label: "Separation Radius",  min: 1, max: 150, step: 1 },
    ]},
    { group: "Weights", fields: [
      { name: "alignment_weight",   label: "Alignment",   min: 0, max: 5, step: 0.1 },
      { name: "cohesion_weight",    label: "Cohesion",    min: 0, max: 5, step: 0.1 },
      { name: "separation_weight",  label: "Separation",  min: 0, max: 5, step: 0.1 },
    ]},
    { group: "Canvas", fields: [
      { name: "width",  label: "Width",  min: 100, max: 2000, step: 10 },
      { name: "height", label: "Height", min: 100, max: 2000, step: 10 },
    ]},
  ],

  cells: [
    { group: "Grid", fields: [
      { name: "grid_width",  label: "Grid Width",  min: 10, max: 500, step: 1 },
      { name: "grid_height", label: "Grid Height", min: 10, max: 500, step: 1 },
    ]},
    { group: "Birth Rule", fields: [
      { name: "birth_min", label: "Min Neighbors", min: 0, max: 8, step: 1 },
      { name: "birth_max", label: "Max Neighbors", min: 0, max: 8, step: 1 },
    ]},
    { group: "Survival Rule", fields: [
      { name: "survival_min", label: "Min Neighbors", min: 0, max: 8, step: 1 },
      { name: "survival_max", label: "Max Neighbors", min: 0, max: 8, step: 1 },
    ]},
    { group: "Initial State", fields: [
      { name: "initial_density", label: "Density (0–1)", min: 0, max: 1, step: 0.01 },
    ]},
  ],
};

function buildForm(type) {
  const schema = SCHEMAS[type] ?? SCHEMAS.slime;
  form.innerHTML = "";
  schema.forEach(({ group, fields }) => {
    const groupEl = document.createElement("div");
    groupEl.className = "param-group";
    groupEl.innerHTML = `<h2>${group}</h2>`;
    fields.forEach(({ name, label, min, max, step }) => {
      const lbl = document.createElement("label");
      lbl.innerHTML = `${label}<input type="number" name="${name}" min="${min}" max="${max}" step="${step}" />`;
      groupEl.appendChild(lbl);
    });
    form.appendChild(groupEl);
  });
}

function fillForm(params) {
  for (const [key, val] of Object.entries(params)) {
    const input = form.elements[key];
    if (input) input.value = val;
  }
}

function getFormParams() {
  return Object.fromEntries(
    Array.from(form.elements)
      .filter((el) => el.name)
      .map((el) => [el.name, Number(el.value)])
  );
}

function setStatus(msg, type = "") {
  statusEl.textContent = msg;
  statusEl.className = type;
}

async function load() {
  try {
    const res = await fetch(`${API}/api/slimes/${simId}`);
    if (!res.ok) throw new Error("Not found");
    const sim = await res.json();
    nameInput.value = sim.name;
    authorEl.textContent = `by ${sim.author}`;
    typeBadge.textContent = TYPE_LABELS[sim.type] ?? sim.type;
    typeBadge.className = `type-badge type-badge--${sim.type}`;
    document.title = `${sim.name} | Cellular Simulations`;
    buildForm(sim.type);
    fillForm(sim.params);
  } catch (err) {
    setStatus(`Error: ${err.message}`, "error");
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  runBtn.disabled = true;
  setStatus("Running...");
  try {
    const res = await fetch(`${API}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ params: getFormParams() }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    setStatus("Running", "ok");
  } catch (err) {
    setStatus(`Error: ${err.message}`, "error");
  } finally {
    runBtn.disabled = false;
  }
});

saveBtn.addEventListener("click", async () => {
  saveBtn.disabled = true;
  setStatus("Saving...");
  try {
    const res = await fetch(`${API}/api/slimes/${simId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: nameInput.value.trim() || "Unnamed", params: getFormParams() }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    setStatus("Saved", "ok");
  } catch (err) {
    setStatus(`Error: ${err.message}`, "error");
  } finally {
    saveBtn.disabled = false;
  }
});

load();
