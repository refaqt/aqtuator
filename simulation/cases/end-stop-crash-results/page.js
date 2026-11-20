// End-stop crash results page. Plain script (no module), so the page also works
// when it is opened straight from disk. Data: crash_data.js and fem_fields.js.
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

  const D = window.CRASH_DATA;
  const F = window.FEM_FIELDS;
  if (!D) { fail(new Error("crash_data.js did not load")); return; }
  const cfg = D.inputs;
  const MAT = cfg.material_base;
  const C0 = cfg.guides.c0;
  const HEAD_LIMIT = cfg.read_head.shock_limit;
  const RP = MAT.rp02, RM = MAT.rm;
  const STRESS_AMBER = RP / 1.5;

  // ---------------------------------------------------------------- helpers
  const fmt = (v, d = 0) => (v === null || v === undefined || !isFinite(v)) ? "—" :
    Number(v).toLocaleString("en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
  const kN = (n, d = 1) => fmt(n / 1000, d) + " kN";
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
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

  // ---------------------------------------------------------------- cases
  const cases = D.cases;
  const sel = $("case");
  const groups = [
    ["named", "The named cases (2.0 m/s, motor pushing)"],
    ["motor off", "Motor switched off at the crash (2.0 m/s)"],
    ["overspeed", "At the overspeed trip, 2.2 m/s, motor pushing"],
    ["table", "Payload table (2.0 m/s, motor pushing)"],
  ];
  function niceLabel(c) {
    if (c.group === "table") return `${c.payload_kg} kg payload, centre of mass ${c.com_height_mm} mm above the carriage`;
    return c.label.replace("cross stage, upper carriage +0 mm", "second stage on top, its carriage in the middle")
      .replace("cross stage, upper carriage +108 mm", "second stage on top, its carriage at the end")
      .replace("1 kg at 50 mm", "1 kg payload, centre of mass 50 mm high")
      .replace(", motor off", "").replace(", 2.2 m/s trip", "");
  }
  groups.forEach(([g, title]) => {
    const og = document.createElement("optgroup");
    og.label = title;
    cases.forEach((c, i) => {
      if (c.group !== g) return;
      const o = document.createElement("option");
      o.value = i; o.textContent = niceLabel(c);
      og.appendChild(o);
    });
    sel.appendChild(og);
  });
  let current = 0;

  // ---------------------------------------------------------------- verdict
  function joint(c, name) { return c.summary.joints ? c.summary.joints[name] : null; }
  function tilesFor(c) {
    const s = c.summary;
    const tiles = [];
    const eIn = s.kinetic_energy + s.motor_work;
    // Bumpers
    {
      let cls = "ok", v = "Inside the stroke";
      if (s.metal_hit) { cls = "bad"; v = "Pressed flat, metal hits metal"; }
      else if (s.bumpers_fully_in) { cls = "warn"; v = "Pressed past the 7 mm stroke"; }
      tiles.push({ name: "Bumpers (2 × TA17-7)", val: `${fmt(eIn, 1)} J in`, cls, verdict: v,
        lim: `Two bumpers take 12 J in their 7 mm stroke (6 J each, ACE). ACE allows 9 J each in an emergency. Travel ${fmt(s.travel_past_first_touch_mm, 2)} mm. Change them after any crash.` });
    }
    // Base
    {
      const b = s.base;
      const pe = Math.max(b.pocket.plastic_strain_max, b.band.plastic_strain_max);
      const vm = Math.max(b.pocket.von_mises_max, b.band.von_mises_max);
      const dent = Math.max(b.pocket.lasting_dent, b.band.lasting_dent);
      const beyond = b.pocket.beyond_fem_range || b.band.beyond_fem_range;
      let cls = "ok", v = "Elastic, no lasting dent";
      if (beyond) { cls = "bad"; v = "Force beyond the FEM range"; }
      else if (pe >= 0.002) { cls = "bad"; v = `Yields: dent ${fmt(dent * 1000, 1)} µm`; }
      else if (pe > 0) { cls = "warn"; v = "Just at the yield point"; }
      else if (vm >= STRESS_AMBER) { cls = "warn"; v = "Elastic, but above 2/3 of yield"; }
      tiles.push({ name: "Base end wall (7075-T651)", val: `${fmt(vm)} MPa`, cls, verdict: v,
        lim: `Yield Rp0.2 = ${RP} MPa (EN 485-2 minimum). Amber from ${fmt(STRESS_AMBER)} MPa (safety 1.5) or any plastic strain; red from 0.2 % plastic strain. Plastic strain here ${fmt(pe * 100, 3)} %.` });
    }
    // Guide blocks
    {
      const f = s.block_fsl;
      let cls = f >= 5 ? "ok" : f >= 3 ? "warn" : "bad";
      let v = f >= 5 ? "Above the HIWIN advice" : f >= 3 ? "Inside the HIWIN range 3 to 5" : f >= 1 ? "Below the HIWIN advice" : "Over C0: balls dent the tracks";
      tiles.push({ name: "Guide blocks (HIWIN QEH15SA)", val: `C0/P = ${fmt(f, 2)}`, cls, verdict: v,
        lim: `HIWIN asks C0/P ≥ 3 to 5 under shock (catalogue Table 2.1). Below 1 the balls leave lasting dents. Worst block P = ${kN(s.block_worst_p, 2)}, C0 = ${kN(C0, 2)}.` });
    }
    if (s.upper_stage) {
      const f = s.upper_stage.block_fsl;
      tiles.push({ name: "Guide blocks of the upper stage", val: `C0/P = ${fmt(f, 2)}`,
        cls: f >= 5 ? "ok" : f >= 3 ? "warn" : "bad",
        verdict: f >= 5 ? "Above the HIWIN advice" : f >= 3 ? "Inside the HIWIN range" : f >= 1 ? "Below the HIWIN advice, no dents" : "Over C0",
        lim: `Side push on the upper carriage ${kN(s.upper_stage.lateral_force_max, 1)}. Same HIWIN rule.` });
    }
    // Read head
    {
      const a = s.read_head.accel_peak;
      tiles.push({ name: "Read head (RSF AK MC 15)", val: `${fmt(a)} m/s²`, cls: a <= HEAD_LIMIT ? "ok" : "bad",
        verdict: a <= HEAD_LIMIT ? "Inside the rating" : `${fmt(100 * (a / HEAD_LIMIT - 1))} % over the rating: ask RSF`,
        lim: `RSF rates ${HEAD_LIMIT} m/s² for 6 ms (half sine). This pulse lasts ${fmt(s.read_head.pulse_width_ms, 1)} ms, speed change ${fmt(s.read_head.velocity_change, 1)} m/s against 3.8 m/s in the test.` });
    }
    // Joints
    const jlist = [
      ["carriage-top to carriage-bottom", "Carriage halves, 6 × M4"],
      ["forcer to carriage-bottom", "Motor coil unit, 6 × M4"],
      ["payload to carriage-top", "Payload or upper stage, 6 × M5"],
      ["base to machine table", "Base on the machine table, 12 × M5"],
    ];
    jlist.forEach(([k, name]) => {
      const j = joint(c, k);
      if (!j) return;
      const u = j.slip_use_mu_low;
      tiles.push({ name, val: `slip use ${fmt(u, 2)}`, cls: u < 0.8 ? "ok" : u <= 1 ? "warn" : "bad",
        verdict: u < 0.8 ? "Holds by friction" : u <= 1 ? "Close to slipping" : (j.screw_shear_use_if_slip > 1 ? "Slides, screws shear off" : "Slides by up to the hole play"),
        lim: `Above 1 the joint slides. Amber from 0.8 (my choice: 20 % margin for the unknown torque). Friction 0.10; with 0.15: ${fmt(j.slip_use_mu_high, 2)}.${j.opens ? " The joint opens." : ""}` });
    });
    // Rail end
    {
      const v = s.block_body_to_rail_end_mm;
      tiles.push({ name: "Guide blocks at the rail end", val: `${fmt(v, 1)} mm on the rail`, cls: v <= 0 ? "bad" : s.block_end_to_rail_end_mm < 0 ? "warn" : "ok",
        verdict: v <= 0 ? "Block runs off the rail" : s.block_end_to_rail_end_mm < 0 ? "Lubrication unit runs off, balls stay on" : "Whole block stays on the rail",
        lim: "Steel block body with the balls still on the rail at the deepest point. Valid only if the E2 lubrication unit points outward (to be checked in the CAD)." });
    }
    if (s.motor_pushes) {
      tiles.push({ name: "Motor after the stop", val: "670 N for > 0.5 s", cls: "warn", verdict: "Drive must switch off",
        lim: "The MK21 may give 670 N for 0.5 s only. If the drive keeps pushing against the bumpers, the coil overheats (drive requirement DRV-13)." });
    }
    return tiles;
  }
  function renderVerdict(c) {
    const s = c.summary;
    $("verdict-sub").textContent = `${niceLabel(c)}. Moving mass ${fmt(s.moving_mass, 2)} kg, speed ${fmt(s.impact_speed, 1)} m/s, motor ${s.motor_pushes ? "pushing 670 N" : "switched off"}.`;
    $("tiles").innerHTML = tilesFor(c).map((t) => `<div class="tile ${t.cls}"><div class="name">${esc(t.name)}</div>
      <div class="val">${esc(t.val)}</div><div class="verdict">${t.cls === "ok" ? "✓" : t.cls === "warn" ? "!" : "✕"} ${esc(t.verdict)}</div>
      <div class="lim">${esc(t.lim)}</div></div>`).join("");
  }

  // ---------------------------------------------------------------- story
  function renderStory(c) {
    const s = c.summary;
    $("sch-speed").textContent = `${fmt(s.impact_speed, 1)} m/s`;
    const eIn = s.kinetic_energy + s.motor_work;
    const p = [];
    p.push(`<p>The carriage, ${fmt(s.moving_mass, 2)} kg in total, arrives at ${fmt(s.impact_speed, 1)} m/s. It carries
      ${fmt(s.kinetic_energy, 1)} J of motion energy. ${s.motor_pushes ? `The motor keeps pushing with 670 N and adds ${fmt(s.motor_work, 1)} J while the carriage stops.` : "The motor is off."}
      So the end stop must take ${fmt(eIn, 1)} J.</p>`);
    if (!s.bumpers_fully_in) p.push(`<p>The two bumpers take it all within their 7 mm stroke. They are pressed in ${fmt(s.travel_past_first_touch_mm, 2)} mm.
      The peak force of both bumpers is ${kN(s.peak_force_bumpers)}.</p>`);
    else if (!s.metal_hit) p.push(`<p>Two bumpers take 12 J in their full 7 mm stroke. That is not enough, so they are pressed past their stroke,
      to ${fmt(s.travel_past_first_touch_mm, 2)} mm. There the flat tube is very stiff, and the force rises quickly to ${kN(s.peak_force_bumpers)}.
      Metal does not hit metal: the gap is 2 mm and only ${fmt(s.travel_past_first_touch_mm - 7, 2)} mm is used.</p>`);
    else p.push(`<p>The bumpers are pressed flat. After ${fmt(cfg.bumper.stroke + cfg.metal_contact.gap_after_stroke, 0)} mm the end face of the carriage hits the end wall of the base:
      metal on metal, ${fmt(s.metal_overlap_mm, 2)} mm into the wall. The bumpers push with up to ${kN(s.peak_force_bumpers)} and the metal hit with up to ${kN(s.peak_force_metal)}.
      Together up to ${kN(s.peak_force_total)} on the end wall.</p>`);
    p.push(`<p>The peak deceleration is ${fmt(s.peak_deceleration_g)} g. The carriage then bounces back at up to ${fmt(s.rebound_speed, 2)} m/s.
      It tips forward by ${fmt(s.pitch_max_mrad, 2)} mrad and turns by ${fmt(s.yaw_max_mrad, 2)} mrad, so the guide blocks get extra load.</p>`);
    const parts = c.parts.map((x) => `${esc(x.name)} ${fmt(x.mass, 2)} kg`).join(", ");
    p.push(`<details><summary>Parts in the moving body</summary><p style="font-size:13.5px">${parts}.</p></details>`);
    $("story-text").innerHTML = p.join("");
  }

  // ---------------------------------------------------------------- inputs
  function renderInputs() {
    const b = cfg.bumper, g = cfg.guides;
    const rows = [
      ["Speed at the crash", "2.0 m/s (2.2 m/s overspeed trip)", "Speed limit chosen by the team, 2026-10-20", ""],
      ["Motor force", "670 N", "Tecnotion MK21 data sheet (limit force, 0.5 s)", ""],
      ["Magnetic pull of the motor", "963 N", "Tecnotion MK21 data sheet", ""],
      ["Moving mass, no payload", "4.24 kg", "CE assessment estimate, CAD centres of mass", "not weighed"],
      ["Bumper energy", "6 J per bumper at 7 mm (9 J emergency)", "ACE operating instructions 21_22_0019", ""],
      ["Bumper curve shape", "1 − (1 − d/s)^1.8", "Fitted to the ACE TA37-16 curve", "estimate"],
      ["Bumper force past 7 mm", `${fmt(b.solid_stiffness)} N/mm per bumper`, "Estimate: solid co-polyester ring", "not known, swept 1800 to 9000"],
      ["Bumper speed / temperature factor", "×1.0", "—", "not known, swept 0.7 to 1.3"],
      ["Bumper work turned into heat", "65 %", "ACE: 58 to 73 %", ""],
      ["Guide block C0, C", `${g.c0} N, ${g.c_dyn} N`, "HIWIN catalogue GW-13-1-EN-2606-K", ""],
      ["Guide block stiffness", "115 N/µm up/down and sideways", "HIWIN (radial); sideways assumed the same", "sideways estimated"],
      ["Read head rating", "1000 m/s², 6 ms half sine", "RSF AK MC 15 mounting instructions 2.1.1", ""],
      ["Base material", "7075-T651: E 71 GPa, Rp0.2 460, Rm 530 MPa, A 5 %", "EN 485-2 minimum values", "hardening line estimated"],
      ["Screw torques", "M3 1.2, M4 3.0, M5 5.9 N·m (class 8.8)", "VDI 2230 table values", "not set in drawings"],
      ["Joint friction", "0.10 (0.15)", "Aluminium on aluminium, dry", "estimate"],
      ["Second stage on top", "10.95 kg, centre of mass 84 mm high", "CAD and catalogue masses", "not weighed"],
    ];
    $("inputs-table").innerHTML = "<tr><th>Input</th><th>Value</th><th>Source</th><th>Not known?</th></tr>" +
      rows.map((r) => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td><td>${r[3] ? badge("warn", r[3]) : ""}</td></tr>`).join("");
    $("eq-ffull").textContent = fmt(D.checks.hand.bumper.force_at_full_stroke_N);
    const fem = D.fem;
    const kv = [
      ["Part", "base, start end x = 0 to 100 mm"],
      ["Elements", `${fmt(fem.mesh.elements)} tetrahedra (10 nodes)`],
      ["Nodes", fmt(fem.mesh.nodes)],
      ["Load area, pocket", `${fmt(fem.load_area.pocket)} mm²`],
      ["Load area, band", `${fmt(fem.load_area.band)} mm²`],
      ["Wall stiffness", `${fmt(D.fem_curves.pocket.elastic_stiffness_n_per_mm / 1000, 1)} kN/mm (pocket), ${fmt(D.fem_curves.band.elastic_stiffness_n_per_mm / 1000, 1)} kN/mm (band)`],
    ];
    $("fem-kv").innerHTML = kv.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("");
    $("fem-f1").textContent = fmt(fem.modes_hz[0]);
    $("fem-t1").textContent = fmt(1000 / fem.modes_hz[0], 2);
  }

  // ---------------------------------------------------------------- plots
  const hasPlotly = typeof window.Plotly !== "undefined";
  function baseLayout(xTitle, yTitle, extra) {
    const ink = css("--ink"), muted = css("--muted"), grid = css("--grid");
    return Object.assign({
      margin: { l: 58, r: 14, t: 10, b: 46 }, paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: css("--sans"), size: 12, color: ink },
      xaxis: { title: { text: xTitle, font: { color: muted } }, gridcolor: grid, zeroline: false, linecolor: grid },
      yaxis: { title: { text: yTitle, font: { color: muted } }, gridcolor: grid, zeroline: false, linecolor: grid, rangemode: "tozero" },
      legend: { orientation: "h", y: -0.22, font: { size: 12 } }, hovermode: "x unified", showlegend: true,
    }, extra || {});
  }
  const PCONF = { displaylogo: false, responsive: true, modeBarButtonsToRemove: ["lasso2d", "select2d"] };
  function hline(y, color, text, x0, x1) {
    return { shape: { type: "line", xref: x0 === undefined ? "paper" : "x", x0: x0 === undefined ? 0 : x0, x1: x1 === undefined ? 1 : x1, y0: y, y1: y,
      line: { color, width: 1.5, dash: "dash" } },
      ann: { xref: "paper", x: 1, xanchor: "right", y, yanchor: "bottom", text, showarrow: false, font: { size: 11, color } } };
  }
  function plot(id, traces, layout) {
    if (!hasPlotly) { $(id).innerHTML = '<p class="muted">The chart library did not load (no internet?).</p>'; return; }
    Plotly.react(id, traces, layout, PCONF);
  }
  function renderTime(c) {
    const S = c.series, s = c.summary;
    const t = S.t_ms;
    const s1 = css("--s1"), s2 = css("--s2"), s3 = css("--s3"), s4 = css("--s4"), bad = css("--bad"), warn = css("--warn"), ref = css("--ref");
    const total = t.map((_, i) => S.bumper_1[i] + S.bumper_2[i] + S.metal[i]);
    const kn = (a) => a.map((v) => v / 1000);
    plot("plot-force", [
      { x: t, y: kn(S.bumper_1), name: "bumper 1", line: { color: s1, width: 2 } },
      { x: t, y: kn(S.bumper_2), name: "bumper 2", line: { color: s3, width: 2, dash: "dash" } },
      { x: t, y: kn(S.metal), name: "metal hit", line: { color: s2, width: 2 } },
      { x: t, y: kn(total), name: "total on the wall", line: { color: css("--ink"), width: 1.5, dash: "dot" } },
    ], baseLayout("time (ms)", "force (kN)"));
    const L1 = hline(cfg.bumper.stroke, warn, "bumper stroke 7 mm");
    const L2 = hline(cfg.bumper.stroke + cfg.metal_contact.gap_after_stroke, bad, "metal touches metal (9 mm)");
    plot("plot-travel", [{ x: t, y: S.travel_mm, name: "travel past the first touch", line: { color: s1, width: 2 } }],
      baseLayout("time (ms)", "travel (mm)", { shapes: [L1.shape, L2.shape], annotations: [L1.ann, L2.ann], showlegend: false,
        yaxis: { title: { text: "travel (mm)" }, gridcolor: css("--grid"), range: [0, Math.max(10, Math.max(...S.travel_mm) * 1.1)] } }));
    // Read head with the RSF test pulse around the peak.
    const k = S.head.indexOf(Math.max(...S.head));
    const tp = [], ap = [];
    for (let i = 0; i <= 60; i++) { const tt = i / 60 * 6; tp.push(t[k] - 3 + tt); ap.push(HEAD_LIMIT * Math.sin(Math.PI * tt / 6)); }
    const H = hline(HEAD_LIMIT, bad, "RSF rating 1000 m/s²");
    plot("plot-head", [
      { x: t, y: S.head, name: "read head", line: { color: s1, width: 2 } },
      { x: tp, y: ap, name: "RSF test pulse (6 ms)", line: { color: ref, width: 1.5 } },
    ], baseLayout("time (ms)", "acceleration (m/s²)", { shapes: [H.shape], annotations: [H.ann] }));
    const B1 = hline(C0, bad, "C0: balls dent the tracks"), B3 = hline(C0 / 3, warn, "C0/3"), B5 = hline(C0 / 5, ref, "C0/5");
    const cols = [s1, s2, s3, s4];
    const names = ["block front left", "block front right", "block rear left", "block rear right"];
    plot("plot-blocks", S.block_p.map((p, b) => ({ x: t, y: kn(p), name: names[b], line: { color: cols[b], width: 2 } })),
      baseLayout("time (ms)", "equivalent load P (kN)", { shapes: [B1.shape, B3.shape, B5.shape].filter((x) => x.y0 / 1000 < Math.max(...S.block_p.flat()) / 1000 * 1.6 || x.y0 === C0 / 5).map((sh) => Object.assign({}, sh, { y0: sh.y0 / 1000, y1: sh.y1 / 1000 })),
        annotations: [B1.ann, B3.ann, B5.ann].filter((a) => a.y / 1000 < Math.max(...S.block_p.flat()) / 1000 * 1.6 || a.y === C0 / 5).map((a) => Object.assign({}, a, { y: a.y / 1000 })) }));
    plot("plot-loop", [
      { x: S.travel_mm, y: kn(S.bumper_1.map((v, i) => v + S.bumper_2[i])), name: "both bumpers", line: { color: s1, width: 2 }, mode: "lines" },
      { x: S.travel_mm, y: kn(S.metal), name: "metal hit", line: { color: s2, width: 2 }, mode: "lines" },
    ], baseLayout("travel past the first touch (mm)", "force (kN)", { hovermode: "closest" }));
    const e = c.energy;
    const inT = [["motion energy at the touch", e.kinetic_at_touch, s1], ["work of the motor", e.motor_work, s2]];
    const outT = [["taken by the bumpers", e.bumper_work, s3], ["taken by the end wall (metal hit)", e.wall_work, bad],
      ["guide block springs, gravity, magnet", -(e.block_spring_work + e.gravity_magnet_work), ref], ["still moving (turning)", e.kinetic_left, s4]];
    const tr = [];
    inT.forEach(([n, v, col]) => tr.push({ type: "bar", orientation: "h", y: ["energy in"], x: [v], name: n, marker: { color: col }, hovertemplate: `${n}: %{x:.2f} J<extra></extra>` }));
    outT.forEach(([n, v, col]) => tr.push({ type: "bar", orientation: "h", y: ["energy out"], x: [v], name: n, marker: { color: col }, hovertemplate: `${n}: %{x:.2f} J<extra></extra>` }));
    plot("plot-energy", tr, baseLayout("energy (J)", "", { barmode: "stack", hovermode: "closest", yaxis: { automargin: true },
      annotations: [{ xref: "paper", yref: "paper", x: 1, y: 1.05, showarrow: false, xanchor: "right", font: { size: 12, color: css("--muted") },
        text: `difference in − out: ${fmt(e.residual * 1000, 3)} mJ (${fmt(e.residual_pct, 4)} %)` }] }));
  }

  function renderJoints(c) {
    const j = c.summary.joints || {};
    const names = Object.keys(j);
    const ok = css("--ok"), warn = css("--warn"), bad = css("--bad");
    const col = (u) => u < 0.8 ? ok : u <= 1 ? warn : bad;
    const u = names.map((n) => j[n].slip_use_mu_low);
    const shown = u.map((v) => Math.min(v, 5));
    plot("plot-joints", [{ type: "bar", orientation: "h", y: names, x: shown, marker: { color: u.map(col) },
      text: u.map((v) => fmt(v, 2) + (v > 5 ? " (off the scale)" : "")), textposition: "outside", hovertemplate: "%{y}: %{text}<extra></extra>", name: "slip use" }],
    baseLayout("slip use at friction 0.10 (1 = slides)", "", { showlegend: false, hovermode: "closest", margin: { l: 220, r: 60, t: 10, b: 46 },
      xaxis: { range: [0, Math.max(1.3, Math.min(5.5, Math.max(...shown) * 1.25))], gridcolor: css("--grid"), title: { text: "slip use at friction 0.10 (1 = slides)" } },
      shapes: [{ type: "line", x0: 1, x1: 1, yref: "paper", y0: 0, y1: 1, line: { color: bad, dash: "dash", width: 1.5 } }] }));
    $("joints-table").innerHTML = "<tr><th>Joint</th><th class='num'>clamp / screw</th><th class='num'>side force</th><th class='num'>slip use 0.10 / 0.15</th><th class='num'>shear use if it slides</th></tr>" +
      names.map((n) => { const x = j[n]; return `<tr><td>${esc(n)} (${x.screws}×)</td><td class="num">${fmt(x.clamp_force_per_screw)} N</td><td class="num">${fmt(x.shear_max)} N</td>
      <td class="num">${fmt(x.slip_use_mu_low, 2)} / ${fmt(x.slip_use_mu_high, 2)}</td><td class="num">${fmt(x.screw_shear_use_if_slip, 2)}</td></tr>`; }).join("");
    const bl = c.summary.blocks;
    $("blocks-table").innerHTML = "<tr><th>Guide block</th><th class='num'>up/down</th><th class='num'>sideways</th><th class='num'>P</th><th class='num'>C0/P</th></tr>" +
      bl.map((b, i) => `<tr><td>${["front left", "front right", "rear left", "rear right"][i]}</td><td class="num">${fmt(b.fz_max)} N</td><td class="num">${fmt(b.fy_max)} N</td>
      <td class="num">${fmt(b.p_eq_max)} N</td><td class="num">${fmt(b.fsl, 2)}</td></tr>`).join("");
  }

  // ---------------------------------------------------------------- payload map
  const table = cases.map((c, i) => [c, i]).filter(([c]) => c.group === "table");
  const PL = [...new Set(table.map(([c]) => c.payload_kg))].sort((a, b) => a - b);
  const HT = [...new Set(table.map(([c]) => c.com_height_mm))].sort((a, b) => a - b);
  function renderMap(c) {
    const ok = css("--ok-bg"), warn = css("--warn-bg"), bad = css("--bad-bg");
    const maps = [
      ["map-fsl", (x) => x.summary.block_fsl, (v) => v >= 5 ? 0 : v >= 3 ? 1 : 2, (v) => fmt(v, 1)],
      ["map-head", (x) => x.summary.read_head.accel_peak, (v) => v <= HEAD_LIMIT ? 0 : 2, (v) => fmt(v)],
      ["map-slip", (x) => x.summary.joints["payload to carriage-top"] ? x.summary.joints["payload to carriage-top"].slip_use_mu_low : 0, (v) => v < 0.8 ? 0 : v <= 1 ? 1 : 2, (v) => v ? fmt(v, 2) : "—"],
      ["map-base", (x) => 100 * Math.max(x.summary.base.pocket.plastic_strain_max, x.summary.base.band.plastic_strain_max), (v) => v <= 0 ? 0 : v < 0.2 ? 1 : 2, (v) => fmt(v, 2)],
    ];
    maps.forEach(([id, get, cls, f]) => {
      const z = [], text = [], cd = [];
      HT.forEach((h) => {
        const zr = [], tr = [], cr = [];
        PL.forEach((p) => {
          const hit = table.find(([x]) => x.payload_kg === p && x.com_height_mm === h);
          const v = get(hit[0]);
          zr.push(cls(v)); tr.push(f(v)); cr.push(hit[1]);
        });
        z.push(zr); text.push(tr); cd.push(cr);
      });
      const shapes = [];
      if (c.group === "table") {
        const xi = PL.indexOf(c.payload_kg), yi = HT.indexOf(c.com_height_mm);
        shapes.push({ type: "rect", x0: xi - 0.5, x1: xi + 0.5, y0: yi - 0.5, y1: yi + 0.5, line: { color: css("--ink"), width: 3 } });
      }
      plot(id, [{ type: "heatmap", z, text, customdata: cd, texttemplate: "%{text}", zmin: 0, zmax: 2, showscale: false, xgap: 2, ygap: 2,
        colorscale: [[0, ok], [0.33, ok], [0.34, warn], [0.66, warn], [0.67, bad], [1, bad]],
        hovertemplate: "%{x}, %{y}: %{text}<extra></extra>", x: PL.map((p) => p + " kg"), y: HT.map((h) => h + " mm") }],
      baseLayout("payload", "centre of mass above the carriage", { hovermode: "closest", showlegend: false, shapes,
        xaxis: { type: "category", title: { text: "payload" } }, yaxis: { type: "category", title: { text: "centre of mass height" } }, margin: { l: 70, r: 10, t: 6, b: 46 } }));
      if (hasPlotly && !$(id)._clickBound) {
        $(id).on("plotly_click", (ev) => { const i = ev.points[0].customdata; if (i !== undefined) { sel.value = i; select(i); } });
        $(id)._clickBound = true;
      }
    });
  }

  // ---------------------------------------------------------------- FEM viewer
  const fem = { ready: false, load: "pocket", cache: {} };
  function stepsOf(job) {
    if (!F || !F[job]) return [];
    return F[job].steps;
  }
  function stepField(job, i) {
    const key = job + i;
    if (fem.cache[key]) return fem.cache[key];
    const st = F[job].steps[i];
    const r = { force: st.force, ux: decode(st.ux), uy: decode(st.uy), uz: decode(st.uz), vm: decode(st.vm), pe: decode(st.pe),
      dent: st.dent ? decode(st.dent) : new Float32Array(fem.n) };
    fem.cache[key] = r;
    return r;
  }
  function fieldAt(job, force) {
    const st = stepsOf(job);
    const n = fem.n;
    const zero = { ux: new Float32Array(n), uy: new Float32Array(n), uz: new Float32Array(n), vm: new Float32Array(n), pe: new Float32Array(n), dent: new Float32Array(n) };
    if (!st.length || force <= 0) return { f: zero, w: "no load", beyond: false };
    let lo = -1;
    for (let i = 0; i < st.length; i++) if (st[i].force <= force + 1e-6) lo = i;
    const beyond = force > st[st.length - 1].force + 1;
    if (lo === st.length - 1 || beyond) return { f: stepField(job, st.length - 1), w: `last solved step, ${kN(st[st.length - 1].force)}`, beyond };
    const A = lo < 0 ? Object.assign({ force: 0 }, zero) : stepField(job, lo);
    const B = stepField(job, lo + 1);
    const a = (force - A.force) / (B.force - A.force);
    const out = {};
    ["ux", "uy", "uz", "vm", "pe", "dent"].forEach((k) => {
      const r = new Float32Array(n);
      for (let i = 0; i < n; i++) r[i] = A[k][i] * (1 - a) + B[k][i] * a;
      out[k] = r;
    });
    return { f: out, w: `between the solved steps ${kN(A.force)} and ${kN(B.force)} (linear in between)`, beyond };
  }
  // Colour maps
  function lerp(c1, c2, t) { return [c1[0] + (c2[0] - c1[0]) * t, c1[1] + (c2[1] - c1[1]) * t, c1[2] + (c2[2] - c1[2]) * t]; }
  const hex = (h) => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
  function ramp(stops, t) {
    t = Math.max(0, Math.min(1, t));
    const k = Math.min(stops.length - 2, Math.floor(t * (stops.length - 1)));
    return lerp(hex(stops[k]), hex(stops[k + 1]), t * (stops.length - 1) - k);
  }
  const BLUES = ["#e3eefb", "#9ec5f4", "#5598e7", "#256abf", "#0d366b"];
  const VIRIDIS = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"];
  const HEAT = ["#fde0c5", "#f6a96b", "#e0662f", "#b3261e", "#6b0f0b"];
  function colourFor(mode, v, max) {
    if (mode === "vm") {
      if (v < STRESS_AMBER) return ramp(BLUES, v / STRESS_AMBER);
      if (v < RP) return lerp(hex("#f2c14e"), hex("#d08a00"), (v - STRESS_AMBER) / (RP - STRESS_AMBER));
      return v < RM ? hex("#d0352b") : hex("#7a120d");
    }
    if (mode === "vmc") return ramp(VIRIDIS, v / max);
    if (mode === "pe") return v <= 1e-7 ? hex("#cfd6da") : ramp(HEAT, v / MAT.elongation);
    if (mode === "dent") return v <= 1e-4 ? hex("#cfd6da") : ramp(HEAT, v / Math.max(max, 1e-3));
    return ramp(BLUES, v / max);
  }
  function legendFor(mode, max) {
    const cv = $("fem-legend"), ctx = cv.getContext("2d");
    const W = cv.width;
    let lo = 0, hi = max, text = "";
    if (mode === "vm") { hi = RM * 1.1; text = `0 to ${fmt(STRESS_AMBER)} MPa blue (safety ≥ 1.5) · ${fmt(STRESS_AMBER)} to ${RP} MPa amber · above Rp0.2 = ${RP} MPa red (yields) · dark red above Rm = ${RM} MPa`; }
    else if (mode === "vmc") text = `0 to ${fmt(max)} MPa (largest value of this load step)`;
    else if (mode === "pe") { hi = MAT.elongation; text = `grey: no plastic strain · 0 to 5 % plastic strain (5 % = elongation at break)`; }
    else if (mode === "u") text = `0 to ${fmt(max * 1000, 1)} µm total displacement`;
    else text = `grey: below 0.1 µm · up to ${fmt(Math.max(max, 1e-3) * 1000, 2)} µm lasting dent`;
    for (let x = 0; x < W; x++) {
      const v = lo + (hi - lo) * x / (W - 1);
      const c = colourFor(mode, mode === "pe" ? v + 1e-9 : mode === "dent" ? v + 1.1e-4 * (x > 0) : v, max);
      ctx.fillStyle = `rgb(${c.map((q) => Math.round(q * 255)).join(",")})`;
      ctx.fillRect(x, 0, 1, cv.height);
    }
    $("fem-legend-text").textContent = text;
  }
  function initFem() {
    if (!F) { $("viewer").innerHTML += '<div class="nolib">The 3D results (fem_fields.js) did not load.</div>'; return; }
    if (typeof window.THREE === "undefined" || !THREE.OrbitControls) {
      $("viewer").innerHTML += '<div class="nolib">The 3D library did not load. This view needs an internet connection.</div>'; return;
    }
    const sx = decode(F.surface.x), sy = decode(F.surface.y), sz = decode(F.surface.z);
    const n = sx.length;
    fem.n = n;
    fem.p0 = new Float32Array(3 * n);
    for (let i = 0; i < n; i++) { fem.p0[3 * i] = sx[i]; fem.p0[3 * i + 1] = sy[i]; fem.p0[3 * i + 2] = sz[i]; }
    fem.tris = decodeBytes(F.surface.tris, Uint32Array);
    fem.flags = decodeBytes(F.surface.flags, Uint8Array);
    const el = $("viewer");
    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(new THREE.Color(css("--digital") || "#eef4f5"));
    el.insertBefore(renderer.domElement, el.firstChild);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 1, 5000);
    camera.up.set(0, 0, 1);
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(50, 105, 20);
    function resetView() { camera.position.set(260, -150, 230); controls.target.set(45, 105, 15); controls.update(); }
    resetView();
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.75));
    const dl = new THREE.DirectionalLight(0xffffff, 0.55); dl.position.set(150, -200, 300); scene.add(dl);
    const dl2 = new THREE.DirectionalLight(0xffffff, 0.25); dl2.position.set(-200, 200, 100); scene.add(dl2);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(fem.p0), 3));
    geo.setAttribute("color", new THREE.BufferAttribute(new Float32Array(3 * n), 3));
    geo.setIndex(new THREE.BufferAttribute(fem.tris, 1));
    const mesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true, side: THREE.DoubleSide }));
    scene.add(mesh);
    const gGeo = new THREE.BufferGeometry();
    gGeo.setAttribute("position", new THREE.BufferAttribute(fem.p0, 3));
    gGeo.setIndex(new THREE.BufferAttribute(fem.tris, 1));
    const ghost = new THREE.Mesh(gGeo, new THREE.MeshBasicMaterial({ color: 0x555555, wireframe: true, transparent: true, opacity: 0.12 }));
    ghost.visible = false; scene.add(ghost);
    const arrows = new THREE.Group(); scene.add(arrows);
    const axes = new THREE.AxesHelper(30); axes.position.set(0, -15, 0); scene.add(axes);
    Object.assign(fem, { renderer, scene, camera, controls, mesh, geo, ghost, arrows, resetView });
    function resize() {
      const w = el.clientWidth, h = el.clientHeight;
      renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", resize); resize();
    (function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
    // Probe on click
    const ray = new THREE.Raycaster();
    renderer.domElement.addEventListener("click", (ev) => {
      const r = renderer.domElement.getBoundingClientRect();
      const m = new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(m, camera);
      const hit = ray.intersectObject(mesh)[0];
      if (!hit || !fem.field) return;
      const ids = [hit.face.a, hit.face.b, hit.face.c];
      const pos = geo.attributes.position.array;
      let best = ids[0], bd = Infinity;
      ids.forEach((i) => { const d = (pos[3 * i] - hit.point.x) ** 2 + (pos[3 * i + 1] - hit.point.y) ** 2 + (pos[3 * i + 2] - hit.point.z) ** 2; if (d < bd) { bd = d; best = i; } });
      const f = fem.field, i = best;
      const um = Math.hypot(f.ux[i], f.uy[i], f.uz[i]);
      $("fem-probe").innerHTML = `x ${fmt(fem.p0[3 * i], 1)}  y ${fmt(fem.p0[3 * i + 1], 1)}  z ${fmt(fem.p0[3 * i + 2], 1)} mm<br>
        von Mises ${fmt(f.vm[i], 0)} MPa · plastic ${fmt(f.pe[i] * 100, 3)} %<br>
        displacement ${fmt(um * 1000, 2)} µm (x ${fmt(f.ux[i] * 1000, 2)}) · dent ${fmt(fem.dent ? fem.dent[i] * 1000 : 0, 3)} µm`;
    });
    $("fem-reset").addEventListener("click", resetView);
    fem.ready = true;
  }
  function updateFem(c) {
    const s = c.summary;
    const forceP = s.base.pocket.force, forceB = s.base.band.force;
    $("fem-sub").innerHTML = `This case puts <b>${kN(forceP)}</b> on the two pocket walls (both bumpers) and <b>${forceB > 0 ? kN(forceB) : "nothing"}</b> on the end wall face (metal hit).
      The two loads are separate FEM runs.`;
    if (!fem.ready) return;
    const job = fem.load;
    const force = job === "pocket" ? forceP : forceB;
    const res = fieldAt(job, force);
    const f = res.f;
    fem.field = f;
    const n = fem.n;
    const st = stepsOf(job);
    // Lasting part: the elastic-plastic run minus a purely elastic run at the
    // same force (both from the export script).
    const dent = f.dent;
    fem.dent = dent;
    const mode = $("fem-field").value;
    let vals, max = 0;
    if (mode === "vm" || mode === "vmc") vals = f.vm;
    else if (mode === "pe") vals = f.pe;
    else if (mode === "dent") vals = dent;
    else { vals = new Float32Array(n); for (let i = 0; i < n; i++) vals[i] = Math.hypot(f.ux[i], f.uy[i], f.uz[i]); }
    for (let i = 0; i < n; i++) if (vals[i] > max) max = vals[i];
    if (max <= 0) max = 1;
    const col = fem.geo.attributes.color.array;
    const showBC = $("fem-bc").checked;
    const loadBit = job === "pocket" ? 1 : 2;
    for (let i = 0; i < n; i++) {
      let c3 = colourFor(mode, vals[i], max);
      if (showBC && (fem.flags[i] & 4)) c3 = (i % 2) ? [0.35, 0.38, 0.4] : [0.55, 0.58, 0.6];
      if (showBC && (fem.flags[i] & loadBit) && force > 0) c3 = lerp(c3, [0.55, 0.3, 0.85], 0.75);
      col[3 * i] = c3[0]; col[3 * i + 1] = c3[1]; col[3 * i + 2] = c3[2];
    }
    fem.geo.attributes.color.needsUpdate = true;
    if (fem.autoFor !== current + job) {
      // Draw the largest displacement as about 4 mm.
      let um = 0;
      for (let i = 0; i < n; i++) um = Math.max(um, Math.hypot(f.ux[i], f.uy[i], f.uz[i]));
      $("fem-scale").value = um > 0 ? Math.max(0, Math.min(3, Math.log10(4 / um))).toFixed(2) : 2;
      fem.autoFor = current + job;
    }
    const scaleExp = parseFloat($("fem-scale").value);
    const scale = scaleExp <= 0 ? 0 : Math.round(Math.pow(10, scaleExp));
    $("fem-scale-v").textContent = scale;
    const pos = fem.geo.attributes.position.array;
    for (let i = 0; i < n; i++) {
      pos[3 * i] = fem.p0[3 * i] + scale * f.ux[i];
      pos[3 * i + 1] = fem.p0[3 * i + 1] + scale * f.uy[i];
      pos[3 * i + 2] = fem.p0[3 * i + 2] + scale * f.uz[i];
    }
    fem.geo.attributes.position.needsUpdate = true;
    fem.geo.computeBoundingSphere();
    fem.ghost.visible = $("fem-ghost").checked;
    // Load arrows
    while (fem.arrows.children.length) fem.arrows.remove(fem.arrows.children[0]);
    if (showBC && force > 0) {
      const g = cfg.geometry;
      const pts = job === "pocket" ? g.bumper_y.map((y) => [g.pocket_back_x, y, g.bumper_z]) : [[g.end_wall_inner_x, 105, 32], [g.end_wall_inner_x, 50, 32], [g.end_wall_inner_x, 160, 32]];
      pts.forEach((p) => fem.arrows.add(new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(p[0] + 45, p[1], p[2]), 42, 0x8a4fd6, 10, 6)));
    }
    let vmax = 0, pmax = 0, umax = 0, dmax = 0;
    for (let i = 0; i < n; i++) { vmax = Math.max(vmax, f.vm[i]); pmax = Math.max(pmax, f.pe[i]); umax = Math.max(umax, Math.hypot(f.ux[i], f.uy[i], f.uz[i])); dmax = Math.max(dmax, dent[i]); }
    $("fem-overlay").innerHTML = force > 0 ?
      `<b>${job === "pocket" ? "Bumper load on the pocket walls" : "Metal hit on the end wall face"}: ${kN(force)}</b><br>
       Field ${res.w}.${res.beyond ? " <b>The case force is beyond the solved range.</b>" : ""}<br>
       Largest on the surface: ${fmt(vmax)} MPa · plastic ${fmt(pmax * 100, 3)} % · ${fmt(umax * 1000, 1)} µm · dent ${fmt(dmax * 1000, 2)} µm<br>
       Deformation drawn ×${scale}.` :
      `<b>${job === "pocket" ? "Bumper load" : "Metal hit"}: no force in this case.</b> ${job === "band" ? "Metal does not hit metal. Pick the bumper load." : ""}`;
    legendFor(mode, max);
    renderFemCurve(c);
  }
  function renderFemCurve(c) {
    const s = c.summary;
    const tr = [];
    const s1 = css("--s1"), s2 = css("--s2");
    [["pocket", s1, "pocket walls (bumpers)"], ["band", s2, "end wall face (metal hit)"]].forEach(([k, col, name]) => {
      const cv = D.fem_curves[k].curve;
      tr.push({ x: cv.map((p) => p.displacement), y: cv.map((p) => p.force / 1000), name, line: { color: col, width: 2 }, mode: "lines" });
      if (F && F[k]) tr.push({ x: F[k].steps.map((p) => p.load_displacement), y: F[k].steps.map((p) => p.force / 1000), name: name + ", re-run for this page", mode: "markers", marker: { color: col, size: 7, symbol: "circle-open" } });
      const b = s.base[k];
      if (b.force > 0) tr.push({ x: [b.displacement], y: [b.force / 1000], name: "this case, " + k, mode: "markers", marker: { color: col, size: 12, line: { color: css("--ink"), width: 2 } } });
    });
    plot("plot-femcurve", tr, baseLayout("wall displacement (mm)", "force (kN)", { hovermode: "closest", xaxis: { range: [0, 1.2], title: { text: "wall displacement (mm)" }, gridcolor: css("--grid") } }));
  }
  function renderMaterial() {
    const e = RP / MAT.youngs_modulus;
    plot("plot-material", [{ x: [0, e * 100, (e + MAT.plastic_strain_at_rm) * 100, (e + MAT.elongation) * 100], y: [0, RP, RM, RM], mode: "lines+markers", name: "7075-T651 (model)", line: { color: css("--s1"), width: 2 } }],
      baseLayout("strain (%)", "stress (MPa)", { showlegend: false, hovermode: "closest", margin: { l: 58, r: 14, t: 6, b: 40 } }));
  }

  // ---------------------------------------------------------------- proof
  function nearestStep(job, force) {
    const st = stepsOf(job);
    if (!st.length || force <= 0) return null;
    return st.reduce((a, b) => Math.abs(b.force - force) < Math.abs(a.force - force) ? b : a);
  }
  function renderProof(c) {
    const s = c.summary, ch = D.checks;
    const rows = [];
    const add = (name, what, result, cls, tol) => rows.push(`<tr><td>${name}</td><td>${what}</td><td>${result}</td><td class="num">${tol}</td><td>${badge(cls, cls === "ok" ? "pass" : cls === "warn" ? "watch" : cls === "bad" ? "fail" : "info")}</td></tr>`);
    const same = ch.same_as_results_json;
    add("Same numbers as the study", "The page data come from a new run of the study scripts. Compared with the committed results.",
      `${same.count} numbers, largest difference ${(same.max_rel * 100).toExponential(1)} %`, same.max_rel < 1e-6 ? "ok" : "bad", "identical");
    const e = c.energy;
    add("Energy balance", "Motion energy + motor work = work on bumpers + work on the wall + what is left. Checks that the solver keeps its books. It does not check the inputs.",
      `in ${fmt(e.kinetic_at_touch + e.motor_work, 3)} J, difference ${fmt(e.residual * 1000, 4)} mJ`, Math.abs(e.residual_pct) < 0.5 ? "ok" : "bad", "0.5 %");
    const im = c.impulse;
    add("Impulse balance", "Sum of force × time = mass × change of speed, along the travel.",
      `${fmt(im.impulse, 3)} N·s against ${fmt(im.mass_times_speed_change, 3)} N·s (${fmt(im.error_pct, 2)} %)`, Math.abs(im.error_pct) < 1 ? "ok" : "bad", "1 %");
    const od = c.one_direction;
    const dT = 100 * (od.travel_mm - s.travel_past_first_touch_mm) / s.travel_past_first_touch_mm;
    const pk1 = Math.max(od.peak_force_bumpers, od.peak_force_metal), pk6 = Math.max(s.peak_force_bumpers, s.peak_force_metal);
    const dF = 100 * (pk1 - pk6) / pk6;
    add("Independent simple model", "A second model, in one direction only (no turning, no guide blocks), with its own integrator and 10 times smaller time steps.",
      `travel ${fmt(od.travel_mm, 2)} against ${fmt(s.travel_past_first_touch_mm, 2)} mm (${fmt(dT, 1)} %), peak force ${kN(pk1)} against ${kN(pk6)} (${fmt(dF, 1)} %)`,
      Math.abs(dT) < 3 && Math.abs(dF) < 15 ? "ok" : "warn", "3 % travel, 15 % force");
    const dp = ch.damper_page;
    add("Bumper law against the damper sizing page", "5 kg at 2 m/s into two bumpers, motor off. The same case on the separate damper sizing page.",
      `${fmt(dp.model_compression_mm, 2)} mm, ${fmt(dp.model_peak_force)} N against ${dp.page_compression_mm} mm, ${fmt(dp.page_peak_force)} N`,
      Math.abs(dp.model_compression_mm - dp.page_compression_mm) < 0.2 ? "ok" : "bad", "0.2 mm");
    const eIn = s.kinetic_energy + s.motor_work;
    const hb = ch.hand.bumper;
    const consistent = (eIn > hb.energy_two_bumpers_J) === s.bumpers_fully_in;
    add("Bumper capacity, by hand", `Two bumpers take ${hb.energy_two_bumpers_J} J in 7 mm. If more energy comes in, they must be pressed past 7 mm.`,
      `${fmt(eIn, 1)} J in; pressed past 7 mm: ${s.bumpers_fully_in ? "yes" : "no"} (travel ${fmt(s.travel_past_first_touch_mm, 2)} mm)`, consistent ? "ok" : "bad", "same answer");
    const decel = (s.peak_force_total - (s.motor_pushes ? cfg.crash.motor_force : 0)) / s.moving_mass / 9.80665;
    add("Peak deceleration, by hand", "(peak force on the wall − motor force) / mass. The model value also holds the turning.",
      `${fmt(decel)} g against ${fmt(s.peak_deceleration_g)} g`, Math.abs(decel - s.peak_deceleration_g) / s.peak_deceleration_g < 0.1 ? "ok" : "warn", "10 %");
    if (F) {
      ["pocket", "band"].forEach((job) => {
        const b = s.base[job];
        const st = nearestStep(job, b.force);
        if (!st) return;
        const r = st.reaction[0];
        add(`FEM supports carry the load (${job})`, "Sum of the reaction forces at the fixed bottom strips, at the solved step closest to this case.",
          `${kN(r, 2)} against ${kN(st.force, 2)} applied (${fmt(100 * (r - st.force) / st.force, 2)} %)`, Math.abs(r - st.force) / st.force < 0.01 ? "ok" : "warn", "1 %");
        const stAll = stepsOf(job);
        if (stAll.length && stAll[0].dent_load_mean !== undefined) {
          const dm = interp(b.force, [0].concat(stAll.map((x) => x.force)), [0].concat(stAll.map((x) => x.dent_load_mean)));
          add(`Lasting dent, second method (${job})`, "The study takes the dent as the wall displacement minus the elastic spring-back F/k. Here the same FEM is run again with a purely elastic material, and the difference of the two runs at this force is taken (mean over the load face). It is measured with the load on, so it still holds a small elastic part. Both are estimates; they should agree to a few µm.",
            `${fmt(Math.max(0, dm) * 1000, 2)} µm against ${fmt(b.lasting_dent * 1000, 2)} µm in the study`, Math.abs(dm - b.lasting_dent) < 0.005 ? "ok" : "warn", "5 µm");
        }
        const cv = D.fem_curves[job].curve;
        const d0 = interp(st.force, cv.map((p) => p.force), cv.map((p) => p.displacement));
        add(`FEM re-run gives the same wall (${job})`, "The 3D fields on this page come from a new FEM run. Its wall displacement is compared with the committed curve that the crash model uses.",
          `${fmt(st.load_displacement * 1000, 1)} µm against ${fmt(d0 * 1000, 1)} µm at ${kN(st.force)}`, Math.abs(st.load_displacement - d0) / d0 < 0.02 ? "ok" : "warn", "2 %");
      });
    }
    const T = 1000 / D.fem.modes_hz[0];
    // Length of the force pulse on the wall: time above half of its peak.
    function above(arr) {
      const pk = Math.max(...arr); let best = 0, cur = 0;
      for (let i = 1; i < arr.length; i++) { if (arr[i] >= 0.5 * pk && pk > 0) { cur += c.series.t_ms[i] - c.series.t_ms[i - 1]; best = Math.max(best, cur); } else cur = 0; }
      return best;
    }
    const bumpPulse = above(c.series.bumper_1.map((v, i) => v + c.series.bumper_2[i]));
    const metalPulse = s.metal_hit ? above(c.series.metal) : 0;
    const pulse = s.metal_hit ? metalPulse : bumpPulse;
    add("Static FEM is fair", "A load that changes slower than the wall can vibrate acts like a static load. Rule of thumb: pulse longer than 3 × the period of the wall.",
      `wall period ${fmt(T, 2)} ms; bumper force pulse ${fmt(bumpPulse, 1)} ms${s.metal_hit ? `, metal hit ${fmt(metalPulse, 2)} ms` : ""}`, pulse > 3 * T ? "ok" : "warn", "3 ×");
    $("proof-table").innerHTML = "<tr><th>Check</th><th>What it does</th><th>Result for this case</th><th class='num'>Tolerance</th><th></th></tr>" + rows.join("");
  }
  function interp(x, xs, ys) {
    if (x <= xs[0]) return ys[0];
    for (let i = 1; i < xs.length; i++) if (x <= xs[i]) return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
    return ys[ys.length - 1];
  }
  function renderStatic() {
    if (F && F.mesh_check) {
      const m = F.mesh_check;
      const ref = m.find((r) => r.mesh === "normal") || m[0];
      $("mesh-table").innerHTML = "<tr><th>Mesh</th><th class='num'>size at the pocket</th><th class='num'>nodes</th><th class='num'>wall deflection</th><th class='num'>peak stress</th><th class='num'>stress, 99.5 % of nodes below</th><th class='num'>support reaction</th></tr>" +
        m.map((r) => `<tr><td>${r.mesh}</td><td class="num">${fmt(r.size_at_pocket_mm, 2)} mm</td><td class="num">${fmt(r.nodes)}</td>
        <td class="num">${fmt(r.wall_displacement_mm * 1000, 2)} µm (${fmt(100 * (r.wall_displacement_mm / ref.wall_displacement_mm - 1), 1)} %)</td>
        <td class="num">${fmt(r.von_mises_max, 1)} MPa (${fmt(100 * (r.von_mises_max / ref.von_mises_max - 1), 1)} %)</td>
        <td class="num">${fmt(r.von_mises_p995, 1)} MPa</td><td class="num">${fmt(r.reaction_x)} N</td></tr>`).join("");
      const fine = m.find((r) => r.mesh === "fine");
      if (fine) {
        const dd = Math.abs(fine.wall_displacement_mm / ref.wall_displacement_mm - 1) * 100;
        const ds = (fine.von_mises_max / ref.von_mises_max - 1) * 100;
        $("mesh-note").innerHTML = `<p class="note ${Math.abs(ds) > 10 ? "warn" : ""}">From the normal to the fine mesh, the wall deflection changes by ${fmt(dd, 1)} % and the peak stress by ${fmt(ds, 1)} %.
          ${Math.abs(ds) <= 5 ? "Both are small: the mesh of the study is fine enough." : Math.abs(ds) <= 10 ? "The stress still moves a little with the mesh. Read the peak stress with about this uncertainty." :
          "The peak stress keeps rising with a finer mesh. That is the sign of a sharp inner corner, where the theoretical stress is not finite. The real part has a small radius there. Read the peak stress as an upper estimate and judge yielding by the plastic strain, which is spread over a larger volume."}</p>`;
      }
    } else $("mesh-table").innerHTML = "<tr><td>The mesh check is not in the data.</td></tr>";
    const h = D.checks.hand.pocket_wall;
    $("hand-wall").innerHTML = `<p>The wall behind each pocket is ${h.thickness} mm thick and ${h.span} mm wide. It is held on both sides by the thicker wall and at the bottom.
      As a simple bound, take a strip of the full height (${fmt(h.height, 1)} mm) that spans the ${h.span} mm width, clamped at both ends, with ${fmt(h.load_per_pocket)} N (half of 5 kN):</p>
      <div class="eq">bending stress  σ = M / W,  W = h·t²/6 = ${fmt(h.height * h.thickness ** 2 / 6, 1)} mm³
point load in the middle:   M = F·L/8  = ${fmt(h.point_load.moment)} N·mm  →  σ = ${fmt(h.point_load.stress)} MPa,  deflection ${fmt(h.point_load.deflection * 1000, 0)} µm
load spread over the span:  M = F·L/12 = ${fmt(h.spread_load.moment)} N·mm  →  σ = ${fmt(h.spread_load.stress)} MPa,  deflection ${fmt(h.spread_load.deflection * 1000, 0)} µm
FEM at 5 kN:                peak σ = ${fmt(h.fem_stress)} MPa,  wall displacement ${fmt(h.fem_displacement * 1000, 0)} µm
shear through the wall around the 20 mm disc: τ = F / (π·d·t) = ${fmt(D.checks.hand.punching_shear_MPa, 1)} MPa</div>
      <p><b>Stress:</b> the FEM value lies at the low end of the hand range, as it should: the real wall is also held at the bottom, and the load is a disc,
      not a point. <b>Deflection:</b> the FEM moves ${fmt(h.fem_displacement * 1000, 0)} µm, more than the ${fmt(h.spread_load.deflection * 1000, 0)} to ${fmt(h.point_load.deflection * 1000, 0)} µm of the thin wall alone.
      The rest is the whole end of the base bending and turning, because it is held only on the two bottom strips at the sides. You can see this in the
      3D view with "Displacement": the whole end wall moves, not only the thin wall behind the pocket.</p>`;
  }

  // ---------------------------------------------------------------- doubt
  function baseLabel(c) {
    return c.label.replace(", motor off", "").replace(", 2.2 m/s trip", "");
  }
  function renderDoubt(c) {
    const s = c.summary;
    const sp = D.spread[baseLabel(c)];
    let h = "";
    if (sp) {
      const sw = sp.sweep;
      const rng = (k) => [Math.min(...sw.map((r) => r[k])), Math.max(...sw.map((r) => r[k]))];
      const F1 = rng("peak_force_total"), B1 = rng("block_fsl"), H1 = rng("head_accel");
      h += `<p>The force of a bumper past its 7 mm stroke is not known (ACE gives no data). The model uses 3.6 kN/mm and the study ran it
        from 1.8 to 9 kN/mm, with the bumper force × 0.7 to × 1.3 for speed and temperature. 9 runs of the named case
        <b>${esc(niceLabel(Object.assign({}, c, { label: baseLabel(c), group: "named" })))}</b> (2.0 m/s, motor pushing):</p>
        <div class="tablewrap"><table><tr><th></th><th class="num">this model</th><th class="num">lowest</th><th class="num">highest</th></tr>
        <tr><td>Peak force on the end wall</td><td class="num">${kN(cases.find((x) => x.label === baseLabel(c)).summary.peak_force_total)}</td><td class="num">${kN(F1[0])}</td><td class="num">${kN(F1[1])}</td></tr>
        <tr><td>Guide blocks C0/P</td><td class="num">${fmt(cases.find((x) => x.label === baseLabel(c)).summary.block_fsl, 2)}</td><td class="num">${fmt(B1[0], 2)}</td><td class="num">${fmt(B1[1], 2)}</td></tr>
        <tr><td>Read head (m/s²)</td><td class="num">${fmt(cases.find((x) => x.label === baseLabel(c)).summary.read_head.accel_peak)}</td><td class="num">${fmt(H1[0])}</td><td class="num">${fmt(H1[1])}</td></tr>
        </table></div>
        <p>So the read head result can be anywhere from well inside to well over its rating. The guide block result is firmer.</p>`;
      const tbl = sw.map((r) => `<tr><td class="num">${fmt(r.solid_stiffness)}</td><td class="num">${r.rate}</td><td class="num">${kN(r.peak_force_total)}</td><td class="num">${kN(r.peak_force_metal)}</td><td class="num">${fmt(r.block_fsl, 2)}</td><td class="num">${fmt(r.head_accel)}</td></tr>`).join("");
      h += `<details><summary>All 9 runs</summary><div class="tablewrap"><table><tr><th class="num">past 7 mm (N/mm)</th><th class="num">factor</th><th class="num">total force</th><th class="num">metal</th><th class="num">C0/P</th><th class="num">read head</th></tr>${tbl}</table></div></details>`;
    } else {
      h += `<p>The spread of the unknown bumper inputs was run for the three named cases only. For a payload case, look at the
        named case with the nearest mass (no payload, 1 kg, or the second stage, 15 kg in total).</p>`;
    }
    $("spread").innerHTML = h;
  }
  function renderLimits() {
    const rows = [
      ["The carriage is rigid", "At the metal hit the real carriage end gives a little. That lowers the metal force.", "results on the safe side"],
      ["The bumper and the metal hit are separate FEM runs", "In a metal-hit case both act on the end wall at the same time. Each is read at its own peak. The combined stress is not computed.", "stress in the end wall may be a little higher"],
      ["The FEM supports are fully fixed", "The base is held by 12 M5 screws and friction. From 2 kg the base slides on the table (see the joints). Then the real support is a stop edge or dowel pins, not these strips.", "valid only if the base cannot slide"],
      ["Static FEM", "Fine for the bumper load (ms). Only an estimate for the metal hit (0.5 ms against a wall period of 0.35 ms).", "metal hit: some dynamic overshoot possible"],
      ["Joint clamp forces from table torques", "No torques are set yet. With half the clamp force, every slip use doubles.", "set and check the torques"],
      ["Moving mass 4.24 kg is an estimate", "Weigh the first carriage. The energy goes with the mass.", "small"],
      ["Bumper curve fitted to a bigger bumper", "The curve shape of the TA17-7 comes from the TA37-16. The energy at 7 mm is the ACE value.", "shape of the force pulse"],
    ];
    $("limits-table").innerHTML = "<tr><th>Limit</th><th>What it means</th><th>Effect</th></tr>" + rows.map((r) => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`).join("");
    const f = [];
    f.push(`<p class="note warn"><b>The 9 J emergency rating of the bumpers is not used.</b> The model scales the bumper curve so that one bumper takes 6 J
      at its full 7 mm (the normal rating). ACE also gives 9 J for an emergency stop, in the same 7 mm. If that is right, the real force curve in a crash
      is about 1.5 times higher than modelled. Then 0 kg and 1 kg would stay inside the stroke (13.4 and 15.7 J against 18 J), with a higher peak force
      over the stroke but no hard rise past it. The study's spread (force × 0.7 to × 1.3) covers part of this, not all. Ask ACE which curve applies.</p>`);
    f.push(`<p class="note"><b>The peak stress at the sharp inner corners is an upper estimate.</b> CalculiX extrapolates the stress to the corner nodes.
      Where the metal yields, that value can be higher than the material can carry. The study handles this the right way: once there is plastic strain,
      it reads the stress from the material curve. The 3D view shows the raw values, so you can see where this happens.</p>`);
    const mc = F && F.mesh_check ? F.mesh_check : null;
    const mn = mc && mc.find((r) => r.mesh === "normal"), mf = mc && mc.find((r) => r.mesh === "fine");
    if (mn && mf) {
      const ds = 100 * (mf.von_mises_max / mn.von_mises_max - 1);
      f.push(`<p class="note warn"><b>The peak stress depends on the mesh by about ${fmt(ds)} %.</b> On a finer mesh the wall deflection changes by only
        ${fmt(100 * (mf.wall_displacement_mm / mn.wall_displacement_mm - 1), 1)} %, so the wall stiffness that the crash model uses is right. But the single highest
        stress rises from ${fmt(mn.von_mises_max)} to ${fmt(mf.von_mises_max)} MPa at 5 kN, while 99.5 % of the nodes stay the same. The peak sits at a sharp inner
        corner. So the first yield may start about ${fmt(ds)} % earlier than the study says (about ${fmt(16 / (1 + ds / 100), 0)} kN instead of 16 kN on the pocket
        walls). This changes no verdict: in the second-stage case the wall then yields a little more, and the dent should stay well below 0.01 mm.</p>`);
    }
    f.push(`<p class="note"><b>No mistakes found in the calculation.</b> A new run of the study scripts gives the same ${D.checks.same_as_results_json.count} numbers.
      The energy and impulse balances close in all ${cases.length} cases (worst ${fmt(D.checks.energy_worst_pct, 4)} % and ${fmt(D.checks.impulse_worst_pct, 2)} %).
      The simple one-direction model agrees with the main model. The open points are the inputs above, not the arithmetic.</p>`);
    $("findings").innerHTML = f.join("");
  }

  // ---------------------------------------------------------------- wiring
  function select(i) {
    const t0 = performance.now();
    try {
      current = +i;
      const c = cases[current];
      renderVerdict(c);
      renderStory(c);
      updateFem(c);
      renderTime(c);
      renderJoints(c);
      renderMap(c);
      renderProof(c);
      renderDoubt(c);
      try { history.replaceState(null, "", "#case=" + current); } catch (e) { /* opened from disk */ }
      statusEl.textContent = `Shown in ${Math.round(performance.now() - t0)} ms.` + (hasPlotly ? "" : " Charts need an internet connection.");
      statusEl.className = "status";
    } catch (e) { fail(e); }
  }
  try {
    renderInputs();
    renderMaterial();
    renderStatic();
    renderLimits();
    initFem();
    sel.addEventListener("change", () => select(sel.value));
    document.querySelectorAll("#seg-load button").forEach((b) => b.addEventListener("click", () => {
      document.querySelectorAll("#seg-load button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      fem.load = b.dataset.v;
      try { updateFem(cases[current]); } catch (e) { fail(e); }
    }));
    ["fem-field", "fem-scale", "fem-bc", "fem-ghost"].forEach((id) => $(id).addEventListener("input", () => { try { updateFem(cases[current]); } catch (e) { fail(e); } }));
    const m = /case=(\d+)/.exec(location.hash);
    const start = m && cases[+m[1]] ? +m[1] : 0;
    sel.value = start;
    select(start);
    if (window.matchMedia) window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => select(current));
  } catch (e) { fail(e); }
})();
