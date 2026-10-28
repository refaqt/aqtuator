// Seal strip in the real carriage, 0.15 mm thick: how high the strip bows over the bottom
// rollers, how hard it presses on carriage-top, and how much the strip ends must move to set
// the pull. Uses the solver of the seal strip designer page, with the carriage faces as walls.
// Prints JSON. Run: node strip_pull.mjs
import { DEFAULTS, shape, stressAndLife } from "../../../../../simulation/cases/strip-seal-designer/strip_model.js";

const W = 186;                 // strip width, mm
const t = 0.15;                // strip thickness, mm
const L = 430;                 // strip length between the two strip ends, mm
const E = 185000;
const h = t / 2, z0 = 40 + h;  // strip centre line on the base
// Read from the CAD at y = 105 (assembly coordinates, carriage as placed in the assembly):
// top roller axis x 118.77, carriage-top slope (118.77, 40.5) to (147.1, 50.5), ceiling 53.5;
// carriage-bottom slope (121.6, 39.5) to (155.6, 51.5), flat top 51.5, bottom roller on the
// slope edge at x 155.6. The bottom roller sticks out 1.5 mm, like the top roller: axis z 48.0.
// The top roller is taken as raised, so it just touches the strip.
const p = { ...DEFAULTS, t, a: 155.6 - 118.77, b: 112.0, width: W, length: L };
p.dz = 48.0 - (40 + t + 5);
const X = (x) => x - 118.77, Y = (z) => z - z0;
const CEILING = 53.5;
const walls = (raise) => [
  { x0: X(118.77), y0: Y(40.5 - h), x1: X(147.1), y1: Y(50.5 - h), side: "up" },
  { x0: X(147.1), y0: Y(CEILING + raise - h), x1: X(276.1), y1: Y(CEILING + raise - h), side: "up" },
  { x0: X(276.1), y0: Y(50.5 - h), x1: X(304.43), y1: Y(40.5 - h), side: "up" },
  { x0: X(121.6), y0: Y(39.5 + h), x1: X(155.6), y1: Y(51.5 + h), side: "down" },
  { x0: X(267.6), y0: Y(51.5 + h), x1: X(301.6), y1: Y(39.5 + h), side: "down" },
];
const pulls = [250, 200, 160, 140, 125, 110, 90, 70, 50, 35, 25, 15, 10];
const out = { W, t, L, ceilingGap: CEILING - (53.0 + t), free: [], raised: {} };

// 1. No carriage walls: how high the strip would bow
for (const T of [10, 25, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500]) {
  const s = shape(p, T / W);
  out.free.push({ T, arch: s.archHeight, rMin: s.rMin, peak: stressAndLife(p, s).peak });
}
// 2. With the carriage walls, the ceiling as drawn or raised
for (const raise of [0, 0.5, 1, 1.5, 2]) {
  let start; const rows = [];
  for (const T of pulls) {
    try {
      const s = shape(p, T / W, { walls: walls(raise), start });
      start = s.y;
      rows.push({ T, extra: s.extra, contact: -s.wallF.up * W, arch: s.archHeight, rMin: s.rMin,
        peak: stressAndLife(p, s).peak });
    } catch (e) { /* the contact solver did not settle at this pull; leave the point out */ }
  }
  const ref = rows.find((r) => r.T === 125);
  for (const r of rows) r.du = ref.extra - r.extra + L * (r.T - 125) / W / (E * t);  // u(T) - u(125)
  out.raised[raise] = rows;
}
console.log(JSON.stringify(out));
