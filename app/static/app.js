const $ = (id) => document.getElementById(id);

let selectedTargetId = null;

function setMsg(text, ok = true) {
  const el = $("msg");
  if (!el) return;
  el.textContent = text;
  el.style.color = ok ? "#0a7a0a" : "#b10000";
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${txt}`);
  }
  return res.json();
}

async function refreshTargets() {
  const tbody = $("targetsBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const targets = await api("/targets");

  for (const t of targets) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.id}</td>
      <td>${t.name}</td>
      <td><code>${t.type}</code></td>
      <td>${t.target}</td>
      <td>${t.port ?? ""}</td>
      <td style="display:flex; gap:8px;">
        <button class="secondary" data-action="select" data-id="${t.id}">Select</button>
        <button data-action="delete" data-id="${t.id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  }

  // Wire up row actions (select/delete)
  tbody.querySelectorAll("button[data-action][data-id]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = parseInt(btn.dataset.id, 10);
      const action = btn.dataset.action;

      if (action === "select") {
        selectTarget(id);
        return;
      }

      if (action === "delete") {
        const ok = confirm(`Delete target #${id}? This will also delete its checks.`);
        if (!ok) return;

        try {
          await api(`/targets/${id}`, { method: "DELETE" });

          if (selectedTargetId === id) {
            selectedTargetId = null;
            const dt = $("detailTitle");
            const out = $("detailOut");
            if (dt) dt.textContent = "—";
            if (out) out.textContent = "";
          }

          setMsg(`Deleted target #${id}`, true);
          await refreshTargets();
        } catch (e) {
          setMsg(e.message, false);
        }
      }
    });
  });

  if (targets.length === 0) setMsg("No targets yet. Add the first one 🙂", true);
}

async function addTarget() {
  const nameEl = $("name");
  const typeEl = $("type");
  const targetEl = $("target");
  const portEl = $("port");
  if (!nameEl || !typeEl || !targetEl || !portEl) {
    setMsg("UI is missing form fields (index.html).", false);
    return;
  }

  const name = nameEl.value.trim();
  const type = typeEl.value;
  const target = targetEl.value.trim();
  const portRaw = portEl.value.trim();

  if (!name || !type || !target) {
    setMsg("Fill in name + type + target.", false);
    return;
  }

  let port = null;
  if (type === "tcp") {
    if (!portRaw) {
      setMsg("TCP requires a port.", false);
      return;
    }
    port = parseInt(portRaw, 10);
  }

  const payload = { name, type, target, port, enabled: true };
  const created = await api("/targets", { method: "POST", body: JSON.stringify(payload) });

  setMsg(`Target created: id=${created.id}`, true);
  await refreshTargets();
}

function selectTarget(id) {
  selectedTargetId = id;
  const dt = $("detailTitle");
  const out = $("detailOut");
  if (dt) dt.textContent = `#${id}`;
  if (out) out.textContent = "Pick an action: Load checks / Load uptime.";
}

async function loadChecks() {
  if (!selectedTargetId) {
    setMsg("Select a target first.", false);
    return;
  }
  const checks = await api(`/targets/${selectedTargetId}/checks?limit=20`);
  // pretty JSON output
  const out = $("detailOut");
  if (out) out.textContent = JSON.stringify(checks, null, 2);
}

async function loadUptime() {
  if (!selectedTargetId) {
    setMsg("Select a target first.", false);
    return;
  }
  const hoursEl = $("uptimeHours");
  const hours = hoursEl ? parseInt(hoursEl.value, 10) || 24 : 24;
  const uptime = await api(`/targets/${selectedTargetId}/uptime?hours=${hours}`);
  const out = $("detailOut");
  if (out) out.textContent = JSON.stringify(uptime, null, 2);
}

window.addEventListener("load", async () => {
  const addBtn = $("addBtn");
  const refreshBtn = $("refreshBtn");
  const loadChecksBtn = $("loadChecksBtn");
  const loadUptimeBtn = $("loadUptimeBtn");

  if (addBtn) addBtn.addEventListener("click", () => addTarget().catch((e) => setMsg(e.message, false)));
  if (refreshBtn) refreshBtn.addEventListener("click", () => refreshTargets().catch((e) => setMsg(e.message, false)));
  if (loadChecksBtn) loadChecksBtn.addEventListener("click", () => loadChecks().catch((e) => setMsg(e.message, false)));
  if (loadUptimeBtn) loadUptimeBtn.addEventListener("click", () => loadUptime().catch((e) => setMsg(e.message, false)));

  try {
    await refreshTargets();
  } catch (e) {
    setMsg(e.message, false);
  }
});