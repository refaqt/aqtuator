// Checks for strip_model.js. Node 18 or newer, no packages:
//
//     node simulation/cases/strip-seal-designer/check_model.mjs
//
// 1. The closed form for a strip under pull over two point supports, the same
//    check as check_solver() in ../strip-seal-preload/strip_seal_preload.py.
// 2. The Python solver itself: reference.json holds its results, written by
//    `strip_seal_preload.py --reference`. Rigid profile, no magnet pull.
// 3. The forces on the strip add up to zero, and the roller force does not
//    change with the grid once the magnet strips are elastic.
// 4. The screw curve starts at zero and rises.
// 5. With the carriage channel, the strip stays between the two carriage
//    halves, and the forces still add up to zero.
// 6. The plastic pad on the ceiling sits only in the middle, as wide as set.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { checkSolver, shape, screwCurve, channel, carriageFriction, DEFAULTS } from "./strip_model.js";

const here = dirname(fileURLToPath(import.meta.url));
let failed = 0;
const check = (ok, text) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${text}`);
  if (!ok) failed++;
};

for (const r of checkSolver()) {
  check(r.ok, `closed form at ${r.pull} N/mm: ${r.got.toFixed(2)} mm, ` +
    `expected ${r.want.toFixed(2)} mm`);
}

const ref = JSON.parse(readFileSync(join(here, "reference.json"), "utf8"));
for (const r of ref) {
  const p = { ...DEFAULTS, material: r.material, t: r.t, D: r.D, a: r.a, b: r.b,
    dz: r.lift - (r.D + r.t), k: Infinity, q: 0, carriage: false };
  const s = shape(p, r.pull, { dx: 0.05, outside: 120 });
  for (const [name, got, want, tol] of [
    ["tightest radius", s.rMin, r.r_min, 0.02],
    ["highest point", s.top, r.top, 0.02],
    ["extra length", s.extra, r.extra, 0.02],
  ]) {
    check(Math.abs(got / want - 1) <= tol,
      `${r.label}, ${r.pull} N/mm, ${name}: ${got.toFixed(3)}, Python ${want.toFixed(3)}`);
  }
}

const coarse = shape(DEFAULTS, 0.36, { dx: 0.1 });
const fine = shape(DEFAULTS, 0.36, { dx: 0.05 });
const f1 = coarse.rollerForces[0].fy, f2 = fine.rollerForces[0].fy;
check(Math.abs(f1 / f2 - 1) < 0.03,
  `roller 1 force, grid 0.1 and 0.05 mm: ${f1.toFixed(3)} and ${f2.toFixed(3)} N/mm`);
const big = Math.max(...coarse.rollerForces.map((f) => Math.abs(f.fy)));
check(Math.abs(coarse.sumFy) < 1e-4 * big,
  `vertical forces add to zero: rest ${coarse.sumFy.toExponential(1)} N/mm`);

// The free strip, without the carriage, so the arch can rise.
const free = { ...DEFAULTS, carriage: false };
const curve = screwCurve(free);
check(curve[0].u === 0 && curve.every((c, i) => i === 0 || c.u > curve[i - 1].u),
  "screw travel starts at zero and rises with the pull");
check(curve.every((c, i) => i === 0 || c.archHeight < curve[i - 1].archHeight),
  "the arch between rollers 2 and 3 gets lower as the pull rises");
check(curve.every((c) => c.archHeight > 0) && curve[curve.length - 1].archHeight < 0.1 * curve[0].archHeight,
  `the arch above the roller tops stays positive and goes towards zero: ` +
  `${curve[0].archHeight.toFixed(2)} mm with no pull, ${curve[curve.length - 1].archHeight.toFixed(2)} mm at the highest pull`);

// The channel between the carriage halves.
const ch = channel(DEFAULTS);
for (const pull of [0, 0.29, 2]) {
  const s = shape(DEFAULTS, pull);
  let worst = Infinity;
  for (let i = 0; i < s.x.length; i++) {
    const c = ch.ceiling(s.x[i]), f = ch.floor(s.x[i]);
    if (c) worst = Math.min(worst, c.h - DEFAULTS.t - s.y[i]);
    if (f) worst = Math.min(worst, s.y[i] - f.h);
  }
  check(worst > -1e-6, `strip inside the channel at ${pull} N/mm: smallest gap ${worst.toFixed(4)} mm`);
  const fy = [...s.rollerForces, ...s.carriageForces].map((r) => Math.abs(r.fy));
  check(Math.abs(s.sumFy) < 1e-4 * Math.max(...fy),
    `with the channel, vertical forces add to zero at ${pull} N/mm: rest ${s.sumFy.toExponential(1)} N/mm`);
}
// The plastic pad: only in the middle, and as wide as set.
for (const w of [10, 30]) {
  const p = { ...DEFAULTS, linerWidth: w };
  const c = channel(p);
  let lo = Infinity, hi = -Infinity;
  for (let x = 0; x <= 2 * p.a + p.b; x += 0.05) {
    if (c.ceiling(x)?.kind === "liner") { lo = Math.min(lo, x); hi = Math.max(hi, x); }
  }
  check(Math.abs(hi - lo - w) < 0.1 && Math.abs((hi + lo) / 2 - c.xm) < 0.1,
    `plastic pad ${w} mm wide: from ${lo.toFixed(2)} to ${hi.toFixed(2)} mm, middle ${c.xm.toFixed(2)} mm`);
}
const s54 = shape(DEFAULTS, 54 / DEFAULTS.width);
const [fLo, fHi] = carriageFriction(DEFAULTS, s54);
check(fLo > 0 && fHi >= fLo, `friction on the carriage at 54 N: ${fLo.toFixed(1)} to ${fHi.toFixed(1)} N`);

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nAll checks passed.");
