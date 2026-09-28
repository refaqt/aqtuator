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

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { checkSolver, shape, screwCurve, DEFAULTS } from "./strip_model.js";

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
    dz: r.lift - (r.D + r.t), k: Infinity, q: 0 };
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

const curve = screwCurve(DEFAULTS);
check(curve[0].u === 0 && curve.every((c, i) => i === 0 || c.u > curve[i - 1].u),
  "screw travel starts at zero and rises with the pull");
check(curve.every((c, i) => i === 0 || c.archHeight < curve[i - 1].archHeight),
  "the arch between rollers 2 and 3 gets lower as the pull rises");
check(curve.every((c) => c.archHeight > 0) && curve[curve.length - 1].archHeight < 0.1 * curve[0].archHeight,
  `the arch above the roller tops stays positive and goes towards zero: ` +
  `${curve[0].archHeight.toFixed(2)} mm with no pull, ${curve[curve.length - 1].archHeight.toFixed(2)} mm at the highest pull`);

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nAll checks passed.");
