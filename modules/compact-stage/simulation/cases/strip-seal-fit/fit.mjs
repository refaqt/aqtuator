// Seal strip in the compact stage, with no plastic strip on the ceiling: how far must rollers
// 2 and 3 go down, and which pull keeps the strip off both carriage halves with an infinite
// fatigue life? Uses the solver of the seal strip designer page.
// Run from the repository root: node modules/compact-stage/simulation/cases/strip-seal-fit/fit.mjs
// Writes results/strip-seal-fit/sweep.csv, profile.csv and fit.json, and prints a summary.
import { writeFileSync } from "node:fs";
import { DEFAULTS, MATERIALS, channel, shape, stressAndLife, screwCurve, travelForPull } from "../../../../../simulation/cases/strip-seal-designer/strip_model.js";

const OUT = new URL("../../results/strip-seal-fit/", import.meta.url);
const W = 185.6;              // strip width, mm: 0.2 mm room on each side of the 186 mm openings
const t = 0.15;               // strip thickness, mm
const FLOOR = 40 - t;         // floor of the strip pocket in the base: the model profile
const MARGIN = 1.2;           // wanted margin on the fatigue limit
// Read from the CAD (assembly coordinates, 2026-10-29). Rollers 1/4 axis z 45, rollers 2/3
// axis z 47, carriage-top ceiling z 53.5, carriage-top underside at roller 1 z 40.5,
// carriage-bottom flat top z 51.5. Rollers 2/3 go down by drop; carriage-bottom stays.
const base = {
  ...DEFAULTS, t, width: W, a: 155.603 - 118.77, b: 112,
  stick: 40.5 - (FLOOR + t), clear: 53.5 - FLOOR, liner: 0, linerWidth: 0,
  length: 433.5 - 6.5,        // between the two preload screws
};
const params = (drop) => ({ ...base, dz: 47 - drop - 45, stick23: 52 - drop - 51.5 });
const pulls = [];
for (let T = 0; T <= 400; T += 5) pulls.push(T);
const sigmaW = MATERIALS[base.material].sigmaW(t)[0];

const rows = [];
for (let drop = 0; drop <= 4.01; drop += 0.5) {
  const p = params(drop);
  let start;
  for (const T of pulls) {
    let s;
    try { s = shape(p, T / W, { start }); } catch (e) { continue; }
    start = s.y;
    const f = stressAndLife(p, s);
    const sar = Math.max(0, ...f.cycles.map((c) => (c.mean > 0 ? c.amp / (1 - c.mean / f.Rm) : c.amp)));
    const [top, , bottom] = s.carriageForces.map((c) => c.n * W);
    rows.push({ drop, T, top, bottom, peak: f.peak, rMin: s.rMin, sar, ratio: sar / sigmaW,
      infinite: f.life[0] === Infinity, roller1: Math.hypot(s.rollerForces[0].fx, s.rollerForces[0].fy) * W,
      roller2: Math.hypot(s.rollerForces[1].fx, s.rollerForces[1].fy) * W, archTop: s.archTop });
  }
}
const free = (r) => r.top < 1e-3 && r.bottom < 1e-3 && r.infinite;
// For each drop: the window of pulls with no carriage contact and the stress at least MARGIN
// below the fatigue limit. The pull is set by hole positions, to tens of newtons, so the
// widest window wins (the smaller drop on a tie), and the pull goes in its middle.
const windows = [];
for (let drop = 0; drop <= 4.01; drop += 0.5) {
  const good = rows.filter((r) => r.drop === drop && free(r) && r.ratio <= 1 / MARGIN).map((r) => r.T);
  if (good.length) windows.push({ drop, lo: Math.min(...good), hi: Math.max(...good) });
}
let pick;
if (windows.length) {
  const w = windows.reduce((q, r) => (r.hi - r.lo > q.hi - q.lo + 1e-9 ? r : q));
  const T = Math.round((w.lo + w.hi) / 2 / 5) * 5;
  pick = { ...rows.find((r) => r.drop === w.drop && r.T === T), window: [w.lo, w.hi] };
} else {
  // No point reaches the margin: take the free point with the lowest stress
  const ok = rows.filter(free).sort((q, r) => q.ratio - r.ratio);
  pick = ok[0];
}
const good = windows;

writeFileSync(new URL("sweep.csv", OUT), "drop_mm,pull_N,carriage_top_N,carriage_bottom_N,peak_MPa,r_min_mm,sar_MPa,sar_over_limit,infinite,roller1_N,roller2_N\n" +
  rows.map((r) => [r.drop, r.T, r.top.toFixed(3), r.bottom.toFixed(3), r.peak.toFixed(1), r.rMin.toFixed(2),
    r.sar.toFixed(1), r.ratio.toFixed(3), r.infinite, r.roller1.toFixed(1), r.roller2.toFixed(1)].join(",")).join("\n") + "\n");

// Per drop: the pull window with no contact, and the best margin in it
const perDrop = [];
for (let drop = 0; drop <= 4.01; drop += 0.5) {
  const rs = rows.filter((r) => r.drop === drop);
  const okd = rs.filter(free);
  perDrop.push({ drop, pulls: okd.map((r) => r.T),
    best: okd.length ? okd.reduce((q, r) => (r.ratio < q.ratio ? r : q)) : null,
    minTop: Math.min(...rs.map((r) => r.top)), minBottom: Math.min(...rs.map((r) => r.bottom)) });
}

const out = { sigmaW, margin: MARGIN, perDrop, windows, pick: pick || null, metGoal: good.length > 0 };
if (pick) {
  const p = params(pick.drop);
  const s = shape(p, pick.T / W);
  const curve = screwCurve(p, pulls.map((T) => T / W));
  out.travel = travelForPull(curve, pick.T / W);   // both ends together
  out.archTop = s.archTop;
  // Smallest gaps to carriage-top and carriage-bottom, mm
  const ch = channel(p);
  out.gaps = { ceiling: Infinity, floor: Infinity };
  for (let i = 0; i < s.x.length; i++) {
    const c = ch.ceiling(s.x[i]), f = ch.floor(s.x[i]);
    if (c) out.gaps.ceiling = Math.min(out.gaps.ceiling, c.h - t - s.y[i]);
    if (f) out.gaps.floor = Math.min(out.gaps.floor, s.y[i] - f.h);
  }
  // Centre line in assembly z, with x from roller 1 of the carriage
  const rho = p.D / 2 + t / 2;
  const lines = ["x_from_roller1_mm,z_centre_mm"];
  for (let i = 0; i < s.x.length; i++) lines.push(`${s.x[i].toFixed(3)},${(FLOOR + t / 2 + s.y[i]).toFixed(5)}`);
  writeFileSync(new URL("profile.csv", OUT), lines.join("\n") + "\n");
  out.rho = rho;
}
writeFileSync(new URL("fit.json", OUT), JSON.stringify(out, null, 1));
for (const d of perDrop) {
  const b = d.best;
  console.log(`drop ${d.drop.toFixed(1)} mm: no-contact pulls ${d.pulls.length ? d.pulls[0] + "-" + d.pulls[d.pulls.length - 1] + " N" : "none"}` +
    (b ? `, best ${b.T} N peak ${b.peak.toFixed(0)} MPa sar/limit ${b.ratio.toFixed(3)}` : `, least contact top ${d.minTop.toFixed(2)} N bottom ${d.minBottom.toFixed(2)} N`));
}
console.log("windows", JSON.stringify(windows));
console.log("pick", JSON.stringify(pick), "travel", out.travel, "gaps", JSON.stringify(out.gaps), "goal met", out.metGoal);
