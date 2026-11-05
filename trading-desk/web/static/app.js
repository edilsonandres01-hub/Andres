const skillsEl = document.getElementById("skills");
const statsEl = document.getElementById("stats");
const ticketEl = document.getElementById("ticket");
const reloadBtn = document.getElementById("reload");

function pct(x) {
  if (x == null) return "—";
  return `${(100 * Number(x)).toFixed(1)}%`;
}

function findStep(summary, id) {
  return (summary.steps || []).find((s) => s.skill === id)?.result;
}

async function loadSkills() {
  const res = await fetch("/api/skills");
  const data = await res.json();
  skillsEl.innerHTML = "";
  data.skills.forEach((skill, i) => {
    const el = document.createElement("article");
    el.className = "skill";
    el.style.animationDelay = `${80 + i * 40}ms`;
    el.innerHTML = `
      <div class="idx">${String(i + 1).padStart(2, "0")}</div>
      <h3>${skill.name}</h3>
      <div class="cmd">${skill.cmd}</div>
      <p>${skill.job}</p>
    `;
    skillsEl.appendChild(el);
  });
}

async function loadSummary() {
  ticketEl.textContent = "Cargando…";
  statsEl.innerHTML = "";
  const res = await fetch("/api/summary");
  if (!res.ok) {
    ticketEl.textContent =
      "Sin resumen todavía.\nEjecuta:\n  python3 trading-desk/scripts/demo_reel.py";
    return;
  }
  const { summary } = await res.json();
  const entry = findStep(summary, "trader-entry") || {};
  const plan = findStep(summary, "trader-exit") || {};
  const tm = findStep(summary, "trader-timemachine") || {};
  const orders = findStep(summary, "trader-budget") || {};
  const risk = findStep(summary, "trader-risk") || {};
  const ticket = findStep(summary, "trader-broker") || [];
  const mc = tm.mc || {};
  const order = (orders.orders || [])[0] || {};
  const riskRow = (risk.results || [])[0] || {};
  const ticketRow = Array.isArray(ticket) ? ticket[0] : ticket;

  const stats = [
    { k: "Entrada", v: entry.price != null ? `$${entry.price}` : "—", cls: "" },
    { k: "Stop", v: plan.stop != null ? `$${plan.stop}` : "—", cls: "" },
    { k: "Target", v: plan.target != null ? `$${plan.target}` : "—", cls: "" },
    { k: "TM target", v: pct(mc.p_target), cls: "" },
    { k: "TM stop", v: pct(mc.p_stop), cls: "warn" },
    {
      k: "Riesgo",
      v: riskRow.verdict || "—",
      cls: riskRow.verdict === "PASS" ? "pass" : "warn",
    },
  ];

  statsEl.innerHTML = stats
    .map(
      (s) => `<div class="stat"><div class="k">${s.k}</div><div class="v ${s.cls}">${s.v}</div></div>`
    )
    .join("");

  const lines = [
    `TSLA · ${summary.session || "—"} · paper=${summary.paper}`,
    `Entry: ${entry.status} @ ${entry.price} (${entry.time})`,
    `Plan: stop ${plan.stop} · target ${plan.target} · risk/share ${plan.risk_per_share}`,
    `Time Machine: ${tm.verdict || ""}`,
    `          target ${pct(mc.p_target)} · stop ${pct(mc.p_stop)} · neither ${pct(mc.p_neither)}`,
    `Order: ${order.side || ""} ${order.qty || ""} ${order.symbol || ""} limit ${order.limit_price || ""}`,
    `Risk: ${riskRow.verdict || "—"} · max loss $${riskRow.max_loss ?? "—"}`,
    `Ticket: ${ticketRow?.status || "—"}`,
    ticketRow?.plain || "",
    "",
    "Nada se envía al broker sin tu sí explícito.",
  ];
  ticketEl.textContent = lines.filter((l) => l !== undefined).join("\n");
}

reloadBtn.addEventListener("click", () => {
  loadSummary().catch((err) => {
    ticketEl.textContent = String(err);
  });
});

loadSkills().catch(console.error);
loadSummary().catch((err) => {
  ticketEl.textContent = String(err);
});
