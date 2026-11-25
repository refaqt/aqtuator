// SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
// SPDX-License-Identifier: GPL-3.0-or-later
//
// Forcer cooling results page. Plain script (no module), so the page also works
// when it is opened straight from disk. Data: thermal_data.js and thermal_fields.js.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const statusEl = $("status");
  function fail(e) {
    statusEl.textContent = "The page stopped: " + (e && e.message ? e.message : e) +
      ". Reload the page. If that does not help, clear the browser cache.";
    statusEl.className = "status bad";
    if (window.console) console.error(e);
  }
  window.addEventListener("error", (ev) => fail(ev.error || ev.message));

  const D = window.THERMAL_DATA;
  const F = window.THERMAL_FIELDS;
  if (!D) { fail(new Error("thermal_data.js did not load")); return; }
  const R = D.results;
  const M = R.main;
  const cfg = D.inputs;
  const G = R.mech_main || null;
  const GC = R.mech_clamped || null;

  // ---------------------------------------------------------------- helpers
  const fmt = (v, d = 0) => (v === null || v === undefined || !isFinite(v)) ? "—" :
    Number(v).toLocaleString("en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const C = (v, d = 1) => fmt(v, d) + " °C";
  function badge(cls, text) { return `<span class="badge ${cls}">${esc(text)}</span>`; }
  function decode(q) {
    const bin = atob(q.b64);
    const n = bin.length / 2;
    const out = new Float32Array(n);
    const span = q.hi - q.lo;
    for (let i = 0; i < n; i++) {
      const v = bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8);
      out[i] = q.lo + (v / 65535) * span;
    }
    return out;
  }
  function decodeBytes(b64, Type) {
    const bin = atob(b64);
    const buf = new ArrayBuffer(bin.length);
    const u8 = new Uint8Array(buf);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    return new Type(buf);
  }
  function table(id, head, rows, numCols = []) {
    const th = head.map((h, i) => `<th${numCols.includes(i) ? ' class="num"' : ""}>${h}</th>`).join("");
    const tr = rows.map((r) => "<tr>" + r.map((c, i) => `<td${numCols.includes(i) ? ' class="num"' : ""}>${c}</td>`).join("") + "</tr>").join("");
    $(id).innerHTML = `<thead><tr>${th}</tr></thead><tbody>${tr}</tbody>`;
  }
  function layout(extra) {
    const ink = css("--ink"), grid = css("--grid"), muted = css("--muted");
    return Object.assign({
      margin: { l: 60, r: 16, t: 30, b: 48 }, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: css("--sans") || "sans-serif", size: 12, color: ink },
      xaxis: { gridcolor: grid, zerolinecolor: grid, linecolor: muted },
      yaxis: { gridcolor: grid, zerolinecolor: grid, linecolor: muted },
      legend: { orientation: "h", y: -0.22 },
    }, extra || {});
  }
  const hasPlotly = () => typeof window.Plotly !== "undefined";
  function plot(id, traces, lay) {
    if (!hasPlotly()) { $(id).innerHTML = '<p class="muted">The chart library did not load. Charts need an internet connection.</p>'; return; }
    Plotly.newPlot(id, traces, layout(lay), { displayModeBar: false, responsive: true });
  }
  const S = (k) => css(k);
  const NAME = {
    base: "base", carriage_bottom: "carriage-bottom", carriage_top: "carriage-top", cooling_block: "cooling block (printed)",
    forcer: "forcer (MK21 coil unit)", track: "magnet track (2 × MK2-180)", rail_1: "rail at y = 36", rail_2: "rail at y = 174",
    block_1: "guide block 1", block_2: "guide block 2", block_3: "guide block 3", block_4: "guide block 4", water: "water",
  };
  const B = M.bodies;
  const blocks = ["block_1", "block_2", "block_3", "block_4"];
  const maxOf = (names, key) => Math.max(...names.map((n) => B[n][key]));
  const meanOf = (names) => names.reduce((a, n) => a + B[n].mean, 0) / names.length;
  const mainMat = D.materials.find((m) => m.name.startsWith("Formlabs Grey V5 (standard resin)") && !m.name.includes("not")) || D.materials[0];
  const recPump = D.hydraulics.pumps.find((p) => p.recommended) || D.hydraulics.pumps[0];
  const tIn = M.params.t_in, tAir = M.params.t_air;
  const tMax = cfg.motor.t_max;

  // ---------------------------------------------------------------- short answers
  function tile(cls, name, val, verdict, lim) {
    return `<div class="tile ${cls}"><div class="name">${name}</div><div class="val">${val}</div>` +
      (verdict ? `<div class="verdict">${verdict}</div>` : "") + `<div class="lim">${lim}</div></div>`;
  }
  function answers() {
    const coilMargin = tMax - M.coil_max;
    const coilCls = coilMargin >= 15 ? "ok" : coilMargin >= 5 ? "warn" : "bad";
    const bm = mainMat.hdt_045 - D.block_max_worst;
    const blkCls = bm >= 20 ? "ok" : bm >= 5 ? "warn" : "bad";
    const t = [];
    t.push(tile(coilCls, "Coil, hottest point", C(M.coil_max), `${fmt(coilMargin, 0)} K below the limit`,
      `Limit ${tMax} °C: highest coil temperature, MAXWELL MK2 data sheet. The PTC sensor trips near 120 °C.`));
    t.push(tile("", "Coil above the water inlet", fmt(M.coil_minus_water_in, 1) + " K", "",
      `Water in at ${C(tIn, 0)}. Of this, ${fmt(cfg.motor.rth * M.P_loss_W, 1)} K is inside the motor (data sheet 0.87 K/W × ${fmt(M.P_loss_W, 0)} W).`));
    t.push(tile("", "Water in → out", fmt(M.water_rise, 2) + " K", `out at ${C(M.water_out, 2)}`,
      `${fmt(R.flow_main, 2)} l/min per axis. ${fmt(M.balance.water, 0)} W go into the water.`));
    t.push(tile("", "Forcer mounting face", C(M.forcer_face_mean), `hottest ${C(M.forcer_face_max)}`,
      "Mean over the face that touches carriage-bottom."));
    for (const [k, lim] of [["carriage_bottom", "7075-T651. Strength drops above about 100 °C (no limit near these values)."],
      ["carriage_top", "Mounting face for the tool or the next stage."], ["base", "Sits on the machine table at the air temperature."]]) {
      t.push(tile("", NAME[k], C(B[k].max), `mean ${C(B[k].mean)}`, lim));
    }
    const railMax = maxOf(["rail_1", "rail_2"], "max"), blkMax = maxOf(blocks, "max");
    t.push(tile(blkMax < 70 ? "ok" : "warn", "Rails and guide blocks", C(Math.max(railMax, blkMax)),
      `blocks up to ${C(blkMax)}`, "HIWIN: QE blocks with plastic parts up to 80 °C; above that, steel-only blocks (catalogue GW-13-1)."));
    t.push(tile(blkCls, "Printed cooling block", C(M.bodies.cooling_block.max), `${fmt(bm, 0)} K below the HDT of ${esc(mainMat.name.replace(" (standard resin)", ""))}`,
      `Worst case of the unknown inputs: ${C(D.block_max_worst)}. Limit: heat deflection temperature at 0.45 MPa, ${mainMat.hdt_045} °C (Formlabs data sheet). See all materials below.`));
    const op = recPump.op;
    t.push(tile("", "Flow per axis", fmt(op.q_axes[0], 2) + " l/min", `manifold ${fmt(op.dp_manifold_bar, 1)} bar`,
      `${esc(recPump.name)}, six axes and a spindle in parallel. Pump curve shape assumed between two maker points.`));
    if (G) {
      const tilt = Math.max(Math.abs(G.top_pitch_urad), Math.abs(G.top_roll_urad));
      t.push(tile("", "Carriage-top lift and tilt", fmt(G.top_lift_um, 1) + " µm", `tilt up to ${fmt(tilt, 1)} µrad`,
        `Flatness change ${fmt(G.top_flatness_um, 1)} µm over the top face.`));
      t.push(tile("", "Table centre against read head", fmt(G.table_centre_minus_read_head_ux_um, 1) + " µm", "along the travel",
        `Heat moves the top face centre against the encoder read head. The scale on the base moves ${fmt(G.scale_ux_um, 1)} µm.`));
    }
    $("tiles").innerHTML = t.join("");
    $("answers-sub").innerHTML = `Motor at its rated current, ${cfg.motor.current} A rms (181 N), without a stop. Water at
      ${C(tIn, 0)} in, ${fmt(R.flow_main, 2)} l/min per axis (from the recommended pump). Still air at ${C(tAir, 0)}.
      Copper loss at the steady coil temperature: <b>${fmt(M.P_loss_W, 1)} W</b>.`;
    const forcerShare = 100 * M.balance.water / M.P_loss_W;
    $("answers-text").innerHTML = `<div class="note"><p><b>What this means.</b> With 20 °C water, the coil settles at
      <b>${C(M.coil_max)}</b>, ${fmt(coilMargin, 0)} K under its 120 °C limit. The water takes ${fmt(forcerShare, 0)} % of the
      heat; the rest goes to the air and through the base into the table. Most of the temperature difference sits
      inside the motor itself (${fmt(cfg.motor.rth * M.P_loss_W, 0)} K over the data sheet thermal resistance), so better
      cooling cannot bring the coil much closer to the water temperature. The printed cooling block stays at
      ${C(M.bodies.cooling_block.max)}, far below the heat limit of a standard resin.</p></div>`;
  }

  // ---------------------------------------------------------------- model text and tables
  function modelText() {
    const mesh = R.mesh;
    const nodes = Object.values(mesh).reduce((a, m) => a + m.nodes, 0);
    const els = Object.values(mesh).reduce((a, m) => a + m.elements, 0);
    $("model-text").innerHTML = `
      <p><b>One model for heat and for growth.</b> Each part is meshed on its own with second-order tetrahedra
      (Gmsh): ${fmt(nodes)} nodes, ${fmt(els)} elements in all. The parts are joined in the solver at the faces where they
      touch. Each joint has its own contact conductance (heat) and is tied (growth). The water itself is not meshed for the
      heat: it is a film on the wetted walls, with a water temperature that rises along its path.</p>
      <p><b>Geometry from the CAD.</b> Base, carriage-bottom, carriage-top and the printed cooling block are the real solids
      from their part files, on the positions in the assembly <code>compact-stage.FCStd</code>. Screw holes and threads
      are filled. The water is the exact volume that the channel, port and passage features cut. The bought parts
      (forcer, magnet track, rails, guide blocks) are blocks with the sizes from the parts library and the maker
      data sheets, placed on their assembly positions.</p>
      <p><b>Heat in the forcer.</b> The copper loss is P = 1.5 · R<sub>LL</sub>(T) · I², with R<sub>LL</sub> from
      13.8 Ω at 25 °C to 19.0 Ω at 120 °C. It is spread evenly over the forcer block. The conductivity of the block,
      ${fmt(R.k_forcer, 2)} W/(m K), is set so that its hottest point is 0.87 K/W above its mounting face when that face
      is held at one temperature: this is the data sheet thermal resistance.</p>
      <p><b>Water.</b> Film coefficient from the flow: Gnielinski, with his blend between laminar and turbulent
      flow between Re 2 300 and 10 000. Channel: ${fmt(M.params.h_channel, 0)} W/(m² K) at Re ${fmt(M.params.re_channel, 0)};
      2 mm passages: ${fmt(M.params.h_passage, 0)} W/(m² K) at Re ${fmt(M.params.re_passage, 0)}. The water temperature along
      the ${fmt(R.water_path_mm, 0)} mm path follows from the heat it takes up: dT<sub>w</sub>/ds = q'(s) / (ṁ c).</p>
      <p><b>Solve.</b> Steady heat conduction, then repeat: new water temperatures and new copper loss, until nothing
      changes by more than 0.002 K (${M.iterations} rounds). The thermal growth is a linear elastic solve on the same
      mesh with the steady temperatures, relative to 20 °C.</p>`;
    const g = D.geometry;
    const rows = g.bodies.filter((b) => b.name !== "water").map((b) => {
      const src = ["base", "carriage_bottom", "carriage_top", "cooling_block"].includes(b.name) ? "CAD part file" : "block from catalogue sizes";
      const m = mesh[b.name] || { nodes: 0, elements: 0 };
      return [NAME[b.name] || b.name, src, b.material, fmt(b.volume / 1000, 1), fmt(m.nodes), fmt(m.elements)];
    });
    table("parts-table", ["Part", "Geometry", "Material", "Volume cm³", "Nodes", "Elements"], rows, [3, 4, 5]);
    const fa = R.face_area_mm2;
    const kinds = ["water", "contact", "gap", "air", "table", "table_gap"];
    table("bc-table", ["Part", "Wetted", "Contact (joint)", "Thin air gap", "Open air", "On the table", "Air gap to table"],
      Object.keys(fa).map((n) => [NAME[n] || n, ...kinds.map((k) => fa[n][k] ? fmt(fa[n][k], 0) : "—")]), [1, 2, 3, 4, 5, 6]);
    const c = cfg.contact, a = cfg.air;
    $("bc-text").innerHTML = `<p class="muted">Areas in mm². Each outer face of each part gets exactly one condition:</p><ul>
      <li><b>Wetted:</b> film to the local water temperature (channel walls, the forcer face under the channel, ports, block passages).</li>
      <li><b>Contact:</b> faces that touch another part: forcer on carriage-bottom ${fmt(c.forcer_face, 0)} W/(m² K), bolted
        metal joints ${fmt(c.metal_bolted, 0)}, printed block on its pocket floor ${fmt(c.resin_block, 0)}, rail to guide block through
        the balls ${fmt(c.balls, 0)}. None is measured; each is swept.</li>
      <li><b>Thin air gap:</b> faces that face another part across less than 1 mm: air conduction k/gap (the 0.6 mm motor air gap,
        the 0.15 mm gaps around the printed block, the small gaps between carriage and base).</li>
      <li><b>On the table:</b> the two bottom strips of the base, ${fmt(c.table, 0)} W/(m² K) to the table at the air temperature;
        the 0.5 mm recess between them: air conduction.</li>
      <li><b>Open air:</b> still-air convection ${a.h_up} (faces up), ${a.h_side} (sides), ${a.h_down} (faces down),
        ${a.h_cavity} W/(m² K) in the space under the carriage, plus radiation with emissivity ${a.emissivity_bare} (bare metal).</li></ul>`;
  }

  function inputs() {
    const m = cfg.motor, w = cfg.water, h = cfg.hydraulics, mat = cfg.materials;
    const rows = [
      ["Motor current", `${m.current} A rms`, "MK21 continuous current, MAXWELL MK2 data sheet"],
      ["Resistance line to line", `${m.r_ll_25} Ω at 25 °C, ${m.r_ll_120} Ω at 120 °C`, "MAXWELL MK2 data sheet"],
      ["Thermal resistance coil to mounting face", `${m.rth} K/W`, "MAXWELL MK2 data sheet (R<sub>TH</sub>); what it is measured to is assumed"],
      ["Highest coil temperature", `${m.t_max} °C`, "MAXWELL MK2 data sheet"],
      ["Thermal time constant", `${m.tau_th} s`, "MAXWELL MK2 data sheet (t<sub>TH</sub>), used only as a comparison"],
      ["Forcer size", `${m.length} × ${m.width} × ${m.height} mm, air gap ${m.air_gap} mm, mass ${m.mass} kg`, "MK21 drawing in the data sheet"],
      ["Forcer heat capacity", `${m.c_specific} J/(kg K)`, "Estimate: copper, iron and resin"],
      ["Water at the inlet", `${w.t_in} °C`, "Given (chiller set point)"],
      ["Water flow per axis", `${fmt(R.flow_main, 3)} l/min`, "Operating point of the recommended pump (section Pump and flow)"],
      ["Water properties", `ρ ${w.rho} kg/m³, c ${w.cp} J/(kg K), k ${w.k} W/(m K), μ ${w.mu * 1000} mPa s, Pr ${w.pr}`, "VDI Heat Atlas, 20 to 30 °C"],
      ["Channel", `${h.channel_w} × ${h.channel_d} mm, ${h.channel_length} mm long, ${h.channel_turns} turns`, "CAD (Sketch019 / Pocket008)"],
      ["Block passages", `Ø${h.passage_d} mm, ${h.passage_length} mm together`, "CAD (cooling_passage_d, feature volumes)"],
      ["Hoses", `PUN-H 4 × ${h.hose_id} mm, ${h.hose_length / 1000} m supply + ${h.hose_length / 1000} m return per axis`, "Festo; length is an estimate"],
      ["Air", `${cfg.air.t_air} °C, still`, "Given; swept 15 to 30 °C"],
      ["EN AW-7075-T651", `k ${mat.al7075.k} W/(m K), E ${mat.al7075.E / 1000} GPa, α ${mat.al7075.alpha * 1e6} µm/(m K)`, "Typical values (ASM, Alcoa); k swept −10 %"],
      ["Rail and block steel", `k ${mat.steel.k} W/(m K), E ${mat.steel.E / 1000} GPa, α ${mat.steel.alpha * 1e6} µm/(m K)`, "Typical bearing steel"],
      ["Magnet track", `k ${mat.track.k} W/(m K), α ${mat.track.alpha * 1e6} µm/(m K)`, "Estimate: steel plate with NdFeB magnets"],
      ["Printed block (for heat)", `k ${mat.resin.k} W/(m K), E ${mat.resin.E} MPa, α ${mat.resin.alpha * 1e6} µm/(m K)`, "Typical cured photopolymer; E from Formlabs Grey V5"],
      ["Guide block ball stiffness", `${cfg.contact.ball_stiffness_n_per_um} N/µm per block`, "HIWIN QE15, ZA preload (as in the crash study)"],
    ];
    table("inputs-table", ["Input", "Value", "Source"], rows);
    const A = [
      "Rated current all the time, at standstill or slow motion. The three phases share the loss evenly (true when the forcer moves; at a standstill one phase can carry more).",
      "The data sheet thermal resistance 0.87 K/W is taken from the hottest coil point to the mounting face. It fits the data sheet exactly: (120 − 25) K / 0.87 K/W = 109 W, the loss at 181 N with a 120 °C coil.",
      "The forcer is one block of uniform material with the heat spread evenly. Its inside is not modelled; only the 0.87 K/W from coil to face is.",
      "The carriage stands still in the middle of the stroke. Moving would add a little air cooling.",
      "No payload and nothing mounted on carriage-top. A payload adds mass to heat and area to cool.",
      "The machine table stays at the air temperature.",
      "The water enters every axis at 20 °C: the chiller holds the tank at 20 °C.",
      "Screw holes and threads are filled. Screws are not modelled; each bolted joint is a contact conductance over the touching faces.",
      "The sealing strip, rollers, read head, cable clamps and cables are left out. They carry little heat.",
      "The rail and the guide block touch over the full rail top and both rail sides. The real balls touch on four lines; the contact conductance stands for that.",
      "Material values do not change with temperature over 20 to 60 °C.",
    ];
    $("assumptions").innerHTML = A.map((x) => `<li>${x}</li>`).join("");
  }

  // ---------------------------------------------------------------- temperatures
  function temps() {
    const order = ["forcer", "cooling_block", "carriage_bottom", "carriage_top", "base", "track", "rail_1", "rail_2", ...blocks];
    table("temp-table", ["Part", "Lowest", "Mean", "Highest"],
      order.map((n) => [NAME[n], C(B[n].min), C(B[n].mean), C(B[n].max)]), [1, 2, 3]);
    const b = M.balance;
    plot("plot-heat", [{
      type: "bar", x: ["into the water", "air: convection", "air: radiation", "table: strips", "table: air gap"],
      y: [b.water, b.conv, b.rad, b.table, b.table_gap], marker: { color: [S("--s1"), S("--s3"), S("--s4"), S("--s2"), S("--ref")] },
      text: [b.water, b.conv, b.rad, b.table, b.table_gap].map((v) => fmt(v, 1) + " W"), textposition: "outside",
    }], { title: { text: `Where the ${fmt(b.source, 1)} W go`, font: { size: 14 } }, yaxis: { title: "W", gridcolor: S("--grid") }, showlegend: false });
    const wp = M.water_profile;
    plot("plot-water", [{ x: wp.s, y: wp.T, mode: "lines", line: { color: S("--s1"), width: 2.5 }, name: "water" }],
      { xaxis: { title: "distance along the water path from the inlet fitting (mm)", gridcolor: S("--grid") },
        yaxis: { title: "water temperature (°C)", gridcolor: S("--grid") }, showlegend: false });
    $("water-text").textContent = `The water passes the supply passage of the block, the port, the eight passes of the channel, the second port
      and the return passage. It warms by ${fmt(M.water_rise, 2)} K. A hand check from the heat balance: ${fmt(M.balance.water, 1)} W /
      (ṁ c) = ${fmt(D.checks.water_rise_hand, 2)} K.`;
  }

  // ---------------------------------------------------------------- cooling block
  function block() {
    const mats = D.materials.slice().sort((a, b) => (a.process === b.process ? a.hdt_045 - b.hdt_045 : a.process < b.process ? 1 : -1));
    const names = mats.map((m) => m.name);
    plot("plot-mat", [
      { type: "bar", orientation: "h", y: names, x: mats.map((m) => m.hdt_045), name: "HDT at 0.45 MPa", marker: { color: S("--s1") } },
      { type: "bar", orientation: "h", y: names, x: mats.map((m) => m.hdt_18 > 0 ? m.hdt_18 : null), name: "HDT at 1.8 MPa", marker: { color: S("--s4") } },
      { type: "scatter", mode: "lines", x: [M.bodies.cooling_block.max, M.bodies.cooling_block.max], y: [names[0], names[names.length - 1]],
        name: "block, main case", line: { color: S("--bad"), width: 3 } },
      { type: "scatter", mode: "lines", x: [D.block_max_worst, D.block_max_worst], y: [names[0], names[names.length - 1]],
        name: "block, worst unknown input", line: { color: S("--warn"), width: 2, dash: "dash" } },
    ], { barmode: "group", margin: { l: 280, r: 16, t: 10, b: 48 }, xaxis: { title: "°C", gridcolor: S("--grid") },
      yaxis: { automargin: true }, height: 520 });
    table("mat-table", ["Material", "Process", "HDT 0.45 MPa", "HDT 1.8 MPa", "Tg", "Margin to HDT 0.45 (main / worst)", "Verdict", "Data sheet"],
      mats.map((m) => [esc(m.name), m.process, m.hdt_045 + " °C", m.hdt_18 > 0 ? m.hdt_18 + " °C" : "—", m.tg > 0 ? m.tg + " °C" : "—",
        `${fmt(m.margin, 0)} / ${fmt(m.margin_worst, 0)} K`, badge(m.verdict, m.verdict === "ok" ? "fits" : m.verdict === "warn" ? "little margin" : "too hot"),
        `<a href="${m.source}">link</a>${m.note ? "<br><small>" + esc(m.note) + "</small>" : ""}`]), [2, 3, 4, 5]);
    const vm = G ? G.cooling_block_vm_MPa : null;
    $("block-text").innerHTML = `<p><b>No.</b> The block sits on a carriage that runs ${fmt(B.carriage_bottom.max - tIn, 0)} K above the
      water at most, and water runs through it. Its hottest point is <b>${C(M.bodies.cooling_block.max)}</b> (99 % of its volume is below
      ${C(M.cooling_block_p99)}). With every unknown input at its worst it reaches ${C(D.block_max_worst)}. All materials below,
      even PLA, stay well under their heat deflection temperature (HDT). The HDT is the temperature where a test bar bends
      a set amount under 0.45 MPa; the block sees much less stress than that from the heat alone${vm ? ` (thermal stress ${fmt(vm.p99, 2)} MPa at 99 % of the volume, highest ${fmt(vm.max, 2)} MPa)` : ""}.</p>
      <p><b>What still matters for the material:</b> the water pressure (up to ${fmt(recPump.op.p_pump_bar, 1)} bar at the pump), the
      screw clamp force on the O-rings, and long-term creep. Resins creep more as they get warmer, even below the HDT. A tough
      resin (Tough 2000) or PETG, ABS, ASA keeps more margin over years. Water uptake of some resins also lowers the stiffness; ask
      the resin maker for long-term water contact data.</p>`;
  }

  // ---------------------------------------------------------------- pump
  function pump() {
    const H = D.hydraulics;
    const sysQ = H.system.map((s) => s.q_total), sysP = H.system.map((s) => s.p_pump_bar);
    const tr = [{ x: sysQ, y: sysP, mode: "lines", name: "the 7 branches (system)", line: { color: S("--ink"), width: 3 } }];
    const cols = [S("--s1"), S("--s2"), S("--s3"), S("--s4"), S("--ref")];
    H.pumps.forEach((p, i) => {
      tr.push({ x: p.curve.map((c) => c.q), y: p.curve.map((c) => c.p_bar), mode: "lines", name: p.name, line: { color: cols[i % 5], dash: p.kind === "fixed" ? "dot" : "solid" } });
      tr.push({ x: [p.op.q_total], y: [p.op.p_pump_bar], mode: "markers", marker: { size: 10, color: cols[i % 5] }, showlegend: false });
    });
    plot("plot-pump", tr, { xaxis: { title: "total flow (l/min)", range: [0, 16], gridcolor: S("--grid") },
      yaxis: { title: "pressure (bar)", range: [0, 4.5], gridcolor: S("--grid") }, legend: { orientation: "h", y: -0.35 } });
    const br = H.branch;
    plot("plot-branch", [
      { x: br.map((b) => b.q), y: br.map((b) => b.dp_bar), mode: "lines", name: "pressure loss of one axis", line: { color: S("--s2"), width: 2.5 } },
      { x: br.map((b) => b.q), y: br.map((b) => b.h_channel / 1000), mode: "lines", name: "film in the channel (kW/(m² K))", yaxis: "y2", line: { color: S("--s1"), dash: "dash" } },
    ], { xaxis: { title: "flow through one axis (l/min)", gridcolor: S("--grid") }, yaxis: { title: "bar", gridcolor: S("--grid") },
      yaxis2: { title: "kW/(m² K)", overlaying: "y", side: "right", showgrid: false } });
    const heat = recPump.heat_w;
    table("pump-table", ["Pump", "Max pressure", "Flow per axis", "Total flow", "Manifold", "Without spindle valve", "One axis with 2 × 3 m hose", "Price", "Source"],
      H.pumps.map((p) => [esc(p.name) + (p.recommended ? " " + badge("ok", "recommended") : ""),
        p.kind === "fixed" ? `relief ${p.relief_bar} bar` : `${p.p_max_bar} bar`,
        fmt(p.op.q_axes[0], 2) + " l/min", fmt(p.op.q_total, 1) + " l/min", fmt(p.op.dp_manifold_bar, 2) + " bar",
        `axis ${fmt(p.op_no_valve.q_axes[0], 2)}, spindle ${fmt(p.op_no_valve.q_spindle, 1)} l/min`,
        `${fmt(p.op_one_long_hose.q_axes[p.op_one_long_hose.q_axes.length - 1], 2)} l/min`,
        esc(p.price_eur), `<a href="${p.source}">link</a>`]), [2, 3, 4]);
    table("dp-table", ["Part of the path", "Pressure loss", "Speed", "Reynolds number"],
      H.main_parts.map((x) => [esc(x.part), fmt(x.dp_bar, 3) + " bar", fmt(x.v, 2) + " m/s", fmt(x.re, 0)]).concat(
        [["<b>Total, one axis</b>", `<b>${fmt(H.main_dp_bar, 2)} bar</b>`, "", ""]]), [1, 2, 3]);
    const sweepPumps = (R.sweeps || []).filter((s) => s.group === "pump");
    const dRows = sweepPumps.map((s) => `${esc(s.label.replace("pump: ", ""))}: coil ${C(s.coil_max)}`).join("; ");
    $("pump-text").innerHTML = `<div class="note"><p><b>What this means.</b> Each axis is a narrow path: 2.6 mm hoses, 2 mm
      passages and a 3 × 1 mm channel. It needs pressure more than flow. A common PC cooling pump (D5) gives only 0.38 bar
      and too little flow. A small spindle chiller with the 4 bar pump option, the <b>${esc(recPump.name)}</b>, gives
      ${fmt(recPump.op.q_axes[0], 2)} l/min to each axis at ${fmt(recPump.op.dp_manifold_bar, 1)} bar, keeps the water at
      20 °C, and has ${fmt(recPump.cooling_w, 0)} W of cooling for about ${fmt(heat, 0)} W of heat (six axes and about
      ${cfg.hydraulics.spindle_heat_w} W from the spindle).</p>
      <p><b>The rule:</b> every branch sees the same manifold pressure. The pump curve meets the system curve of the seven
      parallel branches. The spindle branch has a low loss, so it needs a needle valve set to ${cfg.hydraulics.spindle_q_lpm} l/min;
      without it, the spindle takes most of the flow. Pump coil temperatures: ${dRows || "see Unknown inputs"}.</p>
      <p><b>What to do next:</b> ask TEYU for the pump curve and the exact model code of the 4 bar option, and check that the
      printed block holds the pressure (leak test at 2 × the manifold pressure). Only the maximum pressure and maximum flow of each
      pump come from the maker; the curve between is assumed. Prices are from shop pages and are not confirmed.</p></div>`;
  }

  // ---------------------------------------------------------------- warm-up
  function warm() {
    const h = R.transient;
    if (!h) { $("warm-sub").textContent = "Not computed in this run."; return; }
    const t = h.map((x) => x.t / 60);
    const tr = [
      ["forcer_max", "coil, hottest point", S("--bad")], ["carriage_bottom_mean", "carriage-bottom, mean", S("--s1")],
      ["carriage_top_mean", "carriage-top, mean", S("--s3")], ["base_mean", "base, mean", S("--s4")],
      ["cooling_block_max", "cooling block, hottest", S("--s2")], ["water_out", "water out", S("--ref")]]
      .map(([k, n, c]) => ({ x: t, y: h.map((x) => x[k]), mode: "lines", name: n, line: { color: c, width: 2 } }));
    plot("plot-warm", tr, { xaxis: { title: "time after switch-on (min)", gridcolor: S("--grid") }, yaxis: { title: "°C", gridcolor: S("--grid") } });
    const end = h[h.length - 1];
    const c63 = h[0].forcer_max + 0.632 * (M.coil_max - h[0].forcer_max);
    const i63 = h.findIndex((x) => x.forcer_max >= c63);
    const base95 = h[0].base_mean + 0.95 * (B.base.mean - h[0].base_mean);
    const i95 = h.findIndex((x) => x.base_mean >= base95);
    $("warm-sub").innerHTML = `Everything starts at 20 °C, then the full rated current switches on. The coil reaches 63 % of its rise after
      about <b>${i63 >= 0 ? fmt(h[i63].t / 60, 1) : "—"} min</b> (data sheet thermal time constant: ${fmt(cfg.motor.tau_th / 60, 0)} min,
      probably measured on a large heat sink). The base, which is heavy and cooled only by air and the table, needs
      ${i95 >= 0 ? "about " + fmt(h[i95].t / 60, 0) + " min" : "more than " + fmt(end.t / 60, 0) + " min"} to reach 95 % of its rise.`;
  }

  // ---------------------------------------------------------------- growth
  function growth() {
    if (!G) { $("growth-text").textContent = "Not computed in this run."; return; }
    const rows = [
      ["Lift of the carriage-top face (mean)", fmt(G.top_lift_um, 2), fmt(GC.top_lift_um, 2), "µm"],
      ["Tilt along the travel (pitch)", fmt(G.top_pitch_urad, 1), fmt(GC.top_pitch_urad, 1), "µrad"],
      ["Tilt across the travel (roll)", fmt(G.top_roll_urad, 1), fmt(GC.top_roll_urad, 1), "µrad"],
      ["Flatness change of the top face", fmt(G.top_flatness_um, 2), fmt(GC.top_flatness_um, 2), "µm"],
      ["Top face centre, along x", fmt(G.top_centre_u_um[0], 2), fmt(GC.top_centre_u_um[0], 2), "µm"],
      ["Top face centre, across (y)", fmt(G.top_centre_u_um[1], 2), fmt(GC.top_centre_u_um[1], 2), "µm"],
      ["Read head mount, along x", fmt(G.read_head_ux_um, 2), fmt(GC.read_head_ux_um, 2), "µm"],
      ["Scale on the base, along x", fmt(G.scale_ux_um, 2), fmt(GC.scale_ux_um, 2), "µm"],
      ["Read head against the scale", fmt(G.read_head_minus_scale_um, 2), fmt(GC.read_head_minus_scale_um, 2), "µm"],
      ["Top face centre against the read head", fmt(G.table_centre_minus_read_head_ux_um, 2), fmt(GC.table_centre_minus_read_head_ux_um, 2), "µm"],
      ["Motor air gap change (mean, min, max)", `${fmt(G.air_gap_change_um.mean, 2)} (${fmt(G.air_gap_change_um.min, 2)} to ${fmt(G.air_gap_change_um.max, 2)})`,
        `${fmt(GC.air_gap_change_um.mean, 2)}`, "µm"],
      ["Largest movement anywhere", fmt(G.u_max_um, 1), fmt(GC.u_max_um, 1), "µm"],
      ["Printed block, thermal stress (highest / 99 %)", `${fmt(G.cooling_block_vm_MPa.max, 2)} / ${fmt(G.cooling_block_vm_MPa.p99, 2)}`,
        `${fmt(GC.cooling_block_vm_MPa.max, 2)}`, "MPa"],
    ];
    table("growth-table", ["Result", "Base free to grow", "Base bottom clamped", "Unit"], rows, [1, 2]);
    const L = G.block_loads_N || {};
    const bl = Object.keys(L).sort().map((k) => `${NAME[k]}: ${fmt(L[k].Fz, 0)} N up/down, ${fmt(L[k].Fy_pos, 0)} / ${fmt(L[k].Fy_neg, 0)} N sideways`).join("; ");
    $("growth-text").innerHTML = `<p><b>What this means.</b> The aluminium carriage grows more than the steel rails under it
      (23.4 against 11.5 µm/(m K)). The guide blocks roll freely along the rail, so that mismatch along the travel costs nothing.
      Across the travel the two rails are ${fmt(D.geometry.rails[1].y - D.geometry.rails[0].y, 0)} mm apart, and the warm carriage
      pushes them apart a little. Extra load on the guide blocks from the heat: ${bl || "—"}. HIWIN rates each QEH15SA block
      at C0 = 8 790 N. The heat moves the top face centre ${fmt(G.table_centre_minus_read_head_ux_um, 1)} µm against the encoder
      read head along the travel: this is a position error the encoder does not see.</p>
      <p class="muted">"Base free to grow": the base slides on the table in its plane, held at one point (main case).
      "Bottom clamped": the whole base bottom is held; a stiff, cold table and very tight clamps.</p>`;
  }

  // ---------------------------------------------------------------- sweeps
  function sweeps() {
    const sw = R.sweeps || [];
    if (!sw.length) return;
    const groups = sw.filter((s) => ["contact", "air", "surface", "water film", "alloy"].includes(s.group));
    const lab = groups.map((s) => s.label);
    plot("plot-tornado", [{ type: "bar", orientation: "h", y: lab, x: groups.map((s) => s.coil_max - M.coil_max), marker: { color: S("--s1") } }],
      { title: { text: `Coil: change from ${C(M.coil_max)}`, font: { size: 14 } }, margin: { l: 230, r: 16, t: 30, b: 48 },
        xaxis: { title: "K", gridcolor: S("--grid") }, yaxis: { automargin: true }, showlegend: false });
    plot("plot-tornado-b", [{ type: "bar", orientation: "h", y: lab, x: groups.map((s) => s.bodies.cooling_block.max - M.bodies.cooling_block.max), marker: { color: S("--s2") } }],
      { title: { text: `Cooling block: change from ${C(M.bodies.cooling_block.max)}`, font: { size: 14 } }, margin: { l: 230, r: 16, t: 30, b: 48 },
        xaxis: { title: "K", gridcolor: S("--grid") }, yaxis: { automargin: true }, showlegend: false });
    const fl = sw.filter((s) => s.group === "flow");
    plot("plot-flow", [
      { x: fl.map((s) => s.params.flow), y: fl.map((s) => s.coil_max), mode: "lines+markers", name: "coil, hottest", line: { color: S("--bad") } },
      { x: fl.map((s) => s.params.flow), y: fl.map((s) => s.forcer_face_mean), mode: "lines+markers", name: "forcer face, mean", line: { color: S("--s1") } },
      { x: fl.map((s) => s.params.flow), y: fl.map((s) => s.bodies.carriage_bottom.max), mode: "lines+markers", name: "carriage-bottom, hottest", line: { color: S("--s3") } },
      { x: fl.map((s) => s.params.flow), y: fl.map((s) => s.water_out), mode: "lines+markers", name: "water out", line: { color: S("--ref") } },
    ], { title: { text: "Effect of the flow per axis", font: { size: 14 } }, xaxis: { title: "l/min per axis", gridcolor: S("--grid") }, yaxis: { title: "°C", gridcolor: S("--grid") } });
    table("sweep-table", ["Case", "Loss", "Coil", "Forcer face", "Water out", "Carriage-bottom", "Carriage-top", "Base", "Block (printed)"],
      sw.map((s) => [esc(s.label), fmt(s.P_loss_W, 1) + " W", C(s.coil_max), C(s.forcer_face_mean), C(s.water_out, 2),
        C(s.bodies.carriage_bottom.max), C(s.bodies.carriage_top.max), C(s.bodies.base.max), C(s.bodies.cooling_block.max)]), [1, 2, 3, 4, 5, 6, 7, 8]);
  }

  // ---------------------------------------------------------------- proof
  function proof() {
    const k = D.checks;
    const items = [];
    function add(ok, title, text) {
      const cls = ok === true ? "ok" : ok === false ? "bad" : "warn";
      items.push(`<div class="check"><span class="mark ${cls}">${ok === true ? "✓" : ok === false ? "✗" : "!"}</span><div><b>${title}</b><br>${text}</div></div>`);
    }
    add(Math.abs(k.balance_pct) < 0.5, "Energy balance", `Heat out (water ${fmt(M.balance.water, 2)} W + air ${fmt(M.balance.conv + M.balance.rad, 2)} W + table
      ${fmt(M.balance.table + M.balance.table_gap, 2)} W) against the copper loss ${fmt(M.balance.source, 2)} W: difference ${fmt(k.balance_pct, 3)} %.`);
    add(Math.abs(k.water_rise_hand - k.water_rise_model) < 0.02, "Water warm-up", `Heat into the water / (ṁ c) = ${fmt(k.water_rise_hand, 3)} K;
      the model water profile ends ${fmt(k.water_rise_model, 3)} K above the inlet.`);
    add(Math.abs(k.loss_hand - k.loss_model) < 0.05, "Copper loss", `1.5 · R(T) · I² with the coil at ${C(M.coil_max)}: ${fmt(k.loss_hand, 2)} W; model ${fmt(k.loss_model, 2)} W.`);
    add(Math.abs(k.coil_face_model / k.coil_face_hand - 1) < 0.12, "Coil above its mounting face", `Data sheet: 0.87 K/W × ${fmt(M.P_loss_W, 1)} W =
      ${fmt(k.coil_face_hand, 1)} K, for a face at one temperature. Model: hottest coil point minus the mean face temperature = ${fmt(k.coil_face_model, 1)} K.
      The model is a little higher because the real face is not at one temperature, and some heat leaves through other faces.`);
    add(null, "Water film, hand check", `Heat into the water / (h × wetted channel area) = ${fmt(k.film_dT_hand, 1)} K: the mean step from the
      channel wall to the water. The rest of the coil rise is in the motor and in the aluminium.`);
    if (k.mesh) {
      const d = k.mesh.coil_fine - k.mesh.coil_coarse, db = k.mesh.block_fine - k.mesh.block_coarse;
      add(Math.abs(d) < 1 && Math.abs(db) < 1, "Mesh check", `Coarser mesh (${fmt(k.mesh.nodes_coarse)} nodes) against the main mesh (${fmt(k.mesh.nodes_fine)} nodes):
        coil ${C(k.mesh.coil_coarse, 2)} against ${C(k.mesh.coil_fine, 2)}, block ${C(k.mesh.block_coarse, 2)} against ${C(k.mesh.block_fine, 2)}.`);
    } else add(null, "Mesh check", "Not run for this page.");
    add(true, "Solver tests", `The element code gives the exact answer on a test block: heated slab (q L² / 2k), uniform heating of a free
      block (growth α ΔT L, no stress), and a block cooled by a film (P / hA). See <code>fem.py</code> and the case README.`);
    add(true, "Face sorting", `Wetted area of the channel in the model ${fmt(R.wetted_area_mm2.channel, 0)} mm²; by hand: channel ceiling 2 312 mm² + two
      1 mm walls over 771 mm + the forcer face under the channel 2 312 mm² ≈ 6 170 mm². Base on the table: ${fmt(R.face_area_mm2.base.table, 0)} mm²; two
      440 × 40 mm strips = 35 200 mm².`);
    if (R.removed_faces && Object.keys(R.removed_faces).length) {
      const t = Object.entries(R.removed_faces).map(([b, l]) => `${NAME[b]}: ${l.map((f) => `${f.type} face of ${fmt(f.area, 1)} mm²`).join(", ")}`).join("; ");
      add(null, "Faces removed for meshing", `Gmsh could not mesh these small faces, so they were removed (the faces next to them grow over the gap): ${t}.`);
    }
    $("proof-list").innerHTML = items.join("");
  }

  function doubt() {
    const L = [
      "<b>The motor inside is a block.</b> The real coil has hot spots near the end turns. The model only matches the data sheet value of 0.87 K/W. Ask MAXWELL what R<sub>TH</sub> is measured to (coil to mounting face is assumed).",
      "<b>Contact conductances are not measured.</b> The forcer face joint matters most for the coil; see Unknown inputs.",
      "<b>The flow depends on the pump curve.</b> Only the maximum pressure and flow of each pump are from the maker. Hose length, fittings and turns in the channel are estimates.",
      "<b>The film coefficient in the channel</b> is in the change from laminar to turbulent flow (Re about 4 000), where correlations spread by ±30 % or more. The sweep with the film × 0.5 and × 2 covers this.",
      "<b>Still air.</b> A running machine moves air, and a spindle or coolant changes the room. More air flow cools the base and carriage a little.",
      "<b>Bought parts are blocks.</b> Rails, guide blocks, forcer and magnet track are simple solids with catalogue sizes, because their STEP files were not available in this session.",
      "<b>Growth is linear and the joints do not slip.</b> Bolted joints are tied. A joint that slips would release some of the stress and change the tilt a little.",
      "<b>The table stays at the air temperature.</b> A machine table that warms up moves the whole stage.",
    ];
    $("doubt-list").innerHTML = L.map((x) => `<li>${x}</li>`).join("");
  }

  // ---------------------------------------------------------------- 3D view
  const V = { mode: "T", support: "free" };
  function colourmap(t) {
    // blue - cyan - green - yellow - red
    const stops = [[0.18, 0.35, 0.85], [0.1, 0.7, 0.85], [0.3, 0.75, 0.35], [0.95, 0.8, 0.2], [0.85, 0.2, 0.15]];
    t = Math.max(0, Math.min(1, t)) * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(t)), f = t - i;
    return stops[i].map((v, k) => v + (stops[i + 1][k] - v) * f);
  }
  const PART_COL = [[0.62, 0.66, 0.7], [0.36, 0.56, 0.8], [0.5, 0.72, 0.85], [0.95, 0.55, 0.25], [0.75, 0.35, 0.35],
    [0.45, 0.45, 0.5], [0.3, 0.3, 0.33], [0.3, 0.3, 0.33], [0.55, 0.45, 0.75], [0.55, 0.45, 0.75], [0.55, 0.45, 0.75], [0.55, 0.45, 0.75], [0.2, 0.5, 0.95]];
  const KIND_COL = { air: [0.82, 0.84, 0.86], contact: [0.95, 0.6, 0.15], gap: [0.65, 0.45, 0.85], water: [0.15, 0.45, 0.95],
    table: [0.25, 0.65, 0.3], table_gap: [0.55, 0.8, 0.5], cavity: [0.65, 0.7, 0.74] };
  const KIND_LABEL = { air: "open air", contact: "contact with another part", gap: "thin air gap", water: "wetted by water",
    table: "on the machine table", table_gap: "air gap to the table", cavity: "air under the carriage" };
  function init3d() {
    const el = $("viewer");
    if (!F) { el.innerHTML += '<div class="nolib">The 3D data (thermal_fields.js) did not load.</div>'; return; }
    if (typeof window.THREE === "undefined" || !THREE.OrbitControls) {
      el.innerHTML += '<div class="nolib">The 3D library did not load. This view needs an internet connection.</div>'; return;
    }
    const x = decode(F.x), y = decode(F.y), z = decode(F.z);
    const n = F.n;
    V.n = n; V.T = decode(F.T);
    V.u = { free: [decode(F.ux), decode(F.uy), decode(F.uz)], clamped: [decode(F.cux), decode(F.cuy), decode(F.cuz)] };
    V.kind = decodeBytes(F.kind, Uint8Array); V.body = decodeBytes(F.body, Uint8Array);
    V.p0 = new Float32Array(3 * n);
    for (let i = 0; i < n; i++) { V.p0[3 * i] = x[i]; V.p0[3 * i + 1] = y[i]; V.p0[3 * i + 2] = z[i]; }
    const tris = decodeBytes(F.tris, Uint32Array);
    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(new THREE.Color(css("--digital") || "#eef4f5"));
    el.insertBefore(renderer.domElement, el.firstChild);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 1, 8000);
    camera.up.set(0, 0, 1);
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    function resetView() { camera.position.set(560, -380, 420); controls.target.set(220, 105, 25); controls.update(); }
    resetView();
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.8));
    const dl = new THREE.DirectionalLight(0xffffff, 0.5); dl.position.set(300, -400, 600); scene.add(dl);
    // one mesh per body, so parts can be hidden
    V.meshes = F.bodies.map((b, bi) => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(V.p0), 3));
      geo.setAttribute("color", new THREE.BufferAttribute(new Float32Array(3 * n), 3));
      let cnt = 0, start = -1;
      for (let t = 0; t < tris.length / 3; t++) if (V.body[tris[3 * t]] === bi) { if (start < 0) start = t; cnt++; }
      geo.setIndex(new THREE.BufferAttribute(tris.subarray(3 * start, 3 * (start + cnt)), 1));
      const mesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide }));
      mesh.userData.body = bi;
      scene.add(mesh);
      return mesh;
    });
    // toggles
    const tg = $("toggles");
    tg.innerHTML = F.bodies.map((b, i) => `<label><input type="checkbox" data-b="${i}" ${b.name === "water" ? "" : "checked"}> ${esc(NAME[b.name] || b.name)}</label>`).join("");
    tg.querySelectorAll("input").forEach((cb) => {
      V.meshes[+cb.dataset.b].visible = cb.checked;
      cb.addEventListener("change", () => { V.meshes[+cb.dataset.b].visible = cb.checked; });
    });
    Object.assign(V, { renderer, scene, camera, controls, resetView });
    function resize() { const w = el.clientWidth, h = el.clientHeight; renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
    window.addEventListener("resize", resize); resize();
    (function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
    const ray = new THREE.Raycaster();
    renderer.domElement.addEventListener("click", (ev) => {
      const r = renderer.domElement.getBoundingClientRect();
      const m = new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(m, camera);
      const hit = ray.intersectObjects(V.meshes.filter((q) => q.visible))[0];
      if (!hit) return;
      const ids = [hit.face.a, hit.face.b, hit.face.c];
      let best = ids[0], bd = Infinity;
      ids.forEach((i) => { const d = (V.p0[3 * i] - hit.point.x) ** 2 + (V.p0[3 * i + 1] - hit.point.y) ** 2 + (V.p0[3 * i + 2] - hit.point.z) ** 2; if (d < bd) { bd = d; best = i; } });
      const i = best, u = V.u[V.support];
      const bname = F.bodies[V.body[i]].name;
      $("probe").innerHTML = `${esc(NAME[bname] || bname)} · x ${fmt(V.p0[3 * i], 1)} y ${fmt(V.p0[3 * i + 1], 1)} z ${fmt(V.p0[3 * i + 2], 1)} mm<br>` +
        (bname === "water" ? "water" : `${C(V.T[i], 2)} · growth x ${fmt(u[0][i], 2)} y ${fmt(u[1][i], 2)} z ${fmt(u[2][i], 2)} µm`) +
        `<br>${esc(KIND_LABEL[F.kinds[V.kind[i]]] || "")}`;
    });
    $("reset").addEventListener("click", resetView);
    $("mode").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      $("mode").querySelectorAll("button").forEach((q) => q.setAttribute("aria-pressed", q === b ? "true" : "false"));
      V.mode = b.dataset.m; update3d();
    }));
    $("support").addEventListener("change", () => { V.support = $("support").value; update3d(); });
    $("scale").addEventListener("input", update3d);
    V.ready = true;
    update3d();
  }
  function update3d() {
    if (!V.ready) return;
    const n = V.n, mode = V.mode, u = V.u[V.support];
    let lo = Infinity, hi = -Infinity, vals = null;
    if (mode === "T") { vals = V.T; for (let i = 0; i < n; i++) if (F.bodies[V.body[i]].name !== "water") { lo = Math.min(lo, vals[i]); hi = Math.max(hi, vals[i]); } }
    if (mode === "u") { vals = new Float32Array(n); for (let i = 0; i < n; i++) { vals[i] = Math.hypot(u[0][i], u[1][i], u[2][i]); hi = Math.max(hi, vals[i]); } lo = 0; }
    const scale = mode === "u" ? Math.round(Math.pow(10, parseFloat($("scale").value))) : 0;
    $("scale-v").textContent = mode === "u" ? fmt(scale) : "1 (only in Thermal growth)";
    for (const mesh of V.meshes) {
      const col = mesh.geometry.attributes.color.array, pos = mesh.geometry.attributes.position.array;
      const bi = mesh.userData.body, isWater = F.bodies[bi].name === "water";
      for (let i = 0; i < n; i++) {
        if (V.body[i] !== bi) continue;
        let c;
        if (isWater) c = [0.15, 0.45, 0.95];
        else if (mode === "parts") c = PART_COL[bi % PART_COL.length];
        else if (mode === "bc") c = KIND_COL[F.kinds[V.kind[i]]] || [0.5, 0.5, 0.5];
        else c = colourmap((vals[i] - lo) / Math.max(hi - lo, 1e-9));
        col[3 * i] = c[0]; col[3 * i + 1] = c[1]; col[3 * i + 2] = c[2];
        const s = scale / 1000;
        pos[3 * i] = V.p0[3 * i] + s * u[0][i]; pos[3 * i + 1] = V.p0[3 * i + 1] + s * u[1][i]; pos[3 * i + 2] = V.p0[3 * i + 2] + s * u[2][i];
      }
      mesh.geometry.attributes.color.needsUpdate = true;
      mesh.geometry.attributes.position.needsUpdate = true;
      mesh.geometry.computeVertexNormals();
      mesh.geometry.computeBoundingSphere();
    }
    // legend
    const cv = $("legend"), ctx = cv.getContext("2d");
    ctx.clearRect(0, 0, cv.width, cv.height);
    if (mode === "T" || mode === "u") {
      for (let xx = 0; xx < cv.width; xx++) { const c = colourmap(xx / (cv.width - 1)); ctx.fillStyle = `rgb(${c.map((q) => Math.round(q * 255)).join(",")})`; ctx.fillRect(xx, 0, 1, cv.height); }
      $("legend-text").textContent = mode === "T" ? `${C(lo)} to ${C(hi)}` : `0 to ${fmt(hi, 1)} µm movement, drawn ${fmt(scale)} × larger`;
      cv.style.display = "";
    } else {
      cv.style.display = "none";
      const m = mode === "parts" ? F.bodies.map((b, i) => [NAME[b.name] || b.name, PART_COL[i % PART_COL.length]]) :
        Object.keys(KIND_COL).map((k) => [KIND_LABEL[k], KIND_COL[k]]);
      $("legend-text").innerHTML = m.map(([t, c]) => `<span><span class="swatch" style="background:rgb(${c.map((q) => Math.round(q * 255)).join(",")})"></span>${esc(t)}</span>`).join(" &nbsp; ");
    }
    $("overlay").innerHTML = mode === "T" ? "Temperature at rated current, steady state" : mode === "u" ? `Thermal growth, base ${V.support === "free" ? "free to grow" : "clamped"}` :
      mode === "bc" ? "Boundary condition of each face" : "Parts of the model";
  }

  // ---------------------------------------------------------------- run
  try {
    answers(); modelText(); inputs(); temps(); block(); pump(); warm(); growth(); sweeps(); proof(); doubt();
    init3d();
    statusEl.textContent = "Ready";
  } catch (e) { fail(e); }
})();
