// Hard turning with the tool on two stacked compact stages.
//
// The lathe has a rigid bed and a rigid spindle. The tool sits on a cross
// slide made of two compact stages (MAXWELL MK21 linear motor, HIWIN QEH15SA
// blocks on EGR15U rails, 200 mm travel each):
//
//   lower stage  moves along Z, the spindle axis (the feed in longitudinal turning)
//   upper stage  sits on the lower carriage, moves along X (radial, the depth of cut)
//   tool holder  on the upper carriage, tool tip pointing at the part (+X)
//
// Axes: X radial (+X into the part), Y up, Z along the spindle. Units inside
// this file: SI (m, N, s, kg), except where a name ends in Mm (millimetres).
//
// This file needs control_model.js (the cutting force page) loaded first.
// It reuses its tuned linear motor loop, its exact sampled compliance and its
// stability lobes. Nothing is copied.
//
// The compliance at the tool tip is the sum of two parts in series:
//
//   G_tip(f) = G_servo(f) + G_struct(f)
//
//   G_servo   the position loop of each motor, from control_model.js: one rigid
//             mass, the robust tuning of that page, the exact compliance at the
//             samples. X: the upper stage (upper carriage + tool holder).
//             Z: the lower stage (everything that moves along Z). Y: none.
//   G_struct  a 3 × 3 compliance from a rigid-body model. Body 1 is the lower
//             carriage with the base of the upper stage, on the 4 lower blocks.
//             Body 2 is the upper carriage with the tool holder, on the 4 upper
//             blocks. A tip mass sits on the tool shank. Each block is a spring
//             up/down (radial) and a spring sideways (lateral). Along its own
//             travel each body is held by its motor, which this part takes as
//             rigid, because G_servo already holds that compliance. The tilts
//             of both carriages are in it, so a vertical force also moves the
//             tip along X (the off-diagonal terms).
//
// Turning forces: Kienzle, Fc = kc1 · b · h^(1 − mc), with the chip width b and
// chip thickness h from the depth of cut, the feed and the nose radius. The
// thrust in the X–Z plane is Ft = rt · Fc, normal to the chord of the engaged
// edge (Colwell). Regenerative chatter, one spindle turn of delay:
//
//   1 + b · Kt · (1 − e^{−jωT}) · Φ(jω) = 0,   Φ = u_hᵀ · G_tip · w
//
//   u_h  direction in which the chip gets thicker (the edge normal, X–Z plane)
//   w    the force on the tool per newton of Fc: rt · u_h + (0, 1, 0)
//   Kt   dFc/dh per unit chip width, (1 − mc) · kc1 · h^(−mc), the tangent of Kienzle
//
// So b_lim = −1/(2 · Kt · Re Φ), the same formula as the cutting force page
// with one tooth, and the lobes come from its lobes() function.

// The whole file sits in one function. The page loads it as a plain script
// next to control_model.js, and plain scripts share their top-level names, so
// a second "zeros" or "E_STEEL" would stop the page.
(() => {
"use strict";
const CM = globalThis.ControlModel;

const TURNING_DEFAULTS = {
  // Cut. Finish hard turning with a CBN insert.
  ap: 0.2,          // mm, depth of cut
  feed: 0.1,        // mm per revolution
  vc: 150,          // m/min, cutting speed
  D: 50,            // mm, workpiece diameter
  rNose: 0.8,       // mm, nose radius of the insert
  kappa: 95,        // degrees, entering angle of the straight edge (CNMG/DNMG style)
  // Material: hardened steel, 60 HRC row of the ISCAR table (55 HRC: 4600, 0.25).
  kc1: 4700,        // N/mm², specific cutting force for 1 mm² chip section
  mc: 0.25,         // chip thickness factor
  rt: 1.5,          // Ft/Fc, thrust over cutting force. An estimate, range 1.1 to 2.5
  // Drive and loop, as on the cutting force page.
  fs: 10000,        // Hz, position loop rate
  // Masses, from the end-stop crash case of the compact stage (case.toml).
  mStageMoving: 4.24,  // kg, carriage, forcer, blocks, read head, dampers of one stage
  mStageFixed: 6.71,   // kg, base, rails, stators, strip of one stage
  mHolder: 1.5,        // kg, tool holder and tool. An estimate
  // Guide blocks: HIWIN QEH15SA, ZA preload, catalogue GW-13-1-EN-2606-K, Table 3.44.
  kRadial: 115,     // N/µm per block, up and down
  kLatRatio: 1.0,   // lateral over radial. Not in the catalogue: an estimate, range 0.5 to 1
  zetaGuide: 0.03,  // damping ratio of the guide springs. An estimate, range 0.02 to 0.05
  // Stage geometry, from the compact stage CAD (case.toml of the crash case).
  blockAlongMm: 124.2,   // block centres along the travel
  blockAcrossMm: 138,    // rail centres across the travel
  blockHeightMm: 18,     // ball rows above the bottom of the stage base
  stageHeightMm: 60,     // bottom of the base to the top of the carriage
  forcerOffsetMm: [-13.0, -4.1, 20.3],  // forcer point from the block centre: along, across, up
  // Tool.
  tipHeightMm: 25,  // tool tip above the top of the upper carriage. An estimate
  tipReachMm: 130,  // tool tip ahead of the upper carriage centre, along +X. An estimate
  xPosMm: 0,        // upper carriage position from the middle of its travel, ±100
  shankMm: 20,      // square shank
  overhangMm: 25,   // free length of the shank
  zetaTool: 0.03,   // damping ratio of the shank. An estimate
  // Stability chart.
  rpmLo: 500,
  rpmHi: 6000,
};

const E_STEEL = 2.1e11;   // Pa
const RHO_STEEL = 7850;   // kg/m³
const MOTOR_RIGID = 1e13; // N/m, the motor along its travel inside G_struct (taken as rigid)

// ---------------------------------------------------------------------------
// Small real matrix helpers.
// ---------------------------------------------------------------------------

const zeros = (n, m = n) => Array.from({ length: n }, () => new Array(m).fill(0));
const skew = (t) => [[0, -t[2], t[1]], [t[2], 0, -t[0]], [-t[1], t[0], 0]];
// J(t) maps the generalised motion q = [u; θ] of a rigid body (about the
// origin) to the motion of its point t: d = u + θ × t = u − skew(t)·θ.
const jac = (t) => {
  const S = skew(t);
  return [0, 1, 2].map((i) => [i === 0 ? 1 : 0, i === 1 ? 1 : 0, i === 2 ? 1 : 0, -S[i][0], -S[i][1], -S[i][2]]);
};
const rowAt = (t, n) => [0, 1, 2, 3, 4, 5].map((j) => jac(t).reduce((s, row, i) => s + n[i] * row[j], 0));

// Real 3 × 3 inverse.
function inv3(A) {
  const [a, b, c] = A[0], [d, e, f] = A[1], [g, h, i] = A[2];
  const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  return [
    [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
    [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
    [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
  ];
}

// ---------------------------------------------------------------------------
// Geometry of the stack, global coordinates in mm, origin at the centre of
// the lower blocks on the bottom plane of the lower base.
// ---------------------------------------------------------------------------

function geometry(q) {
  const a = q.blockAlongMm / 2, c = q.blockAcrossMm / 2, hb = q.blockHeightMm, H = q.stageHeightMm;
  const [fa, fc, fh] = q.forcerOffsetMm;
  const x0 = q.xPosMm;
  // Lower stage: travel along Z, across is X.
  const lowerBlocks = [];
  for (const sz of [-1, 1]) for (const sx of [-1, 1]) lowerBlocks.push([sx * c, hb, sz * a]);
  const lowerMotor = { p: [fc, fh, fa], n: [0, 0, 1] };
  // Upper stage: its base on the lower carriage top, travel along X, across is Z.
  const upperBlocks = [];
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) upperBlocks.push([x0 + sx * a, H + hb, sz * c]);
  const upperMotor = { p: [x0 + fa, H + fh, fc], n: [1, 0, 0] };
  const tip = [x0 + q.tipReachMm, 2 * H + q.tipHeightMm, 0];
  return { lowerBlocks, upperBlocks, lowerMotor, upperMotor, tip };
}

// Mass properties. Each body is a box (an estimate for the inertia only).
// Body 1: the lower carriage and the base of the upper stage.
// Body 2: the upper carriage and the tool holder.
function bodies(q, g) {
  const H = q.stageHeightMm;
  const m1 = q.mStageMoving + q.mStageFixed, m2 = q.mStageMoving + q.mHolder;
  const b1 = { m: m1, c: [q.xPosMm * q.mStageFixed / m1 * 0.5, H, 0], box: [330, 60, 210] };
  const b2 = { m: m2, c: [q.xPosMm + q.tipReachMm * q.mHolder / m2, 2 * H - 10, 0], box: [230, 50, 210] };
  return [b1, b2];
}

// The masses each motor moves along its travel.
const servoMass = (q) => ({
  x: q.mStageMoving + q.mHolder,
  z: 2 * q.mStageMoving + q.mStageFixed + q.mHolder,
});

// Shank stiffness and tip mass. The shank lies along X. Bending in Y and Z
// (cantilever 3EI/L³), stretching along X (EA/L). The clamp is not counted.
function toolSpring(q) {
  const s = q.shankMm / 1000, L = q.overhangMm / 1000;
  const I = s ** 4 / 12, A = s * s;
  const kBend = 3 * E_STEEL * I / L ** 3, kAxial = E_STEEL * A / L;
  const mTip = 0.24 * RHO_STEEL * A * L + 0.01;  // a quarter of the free shank, plus the insert
  return { k: [kAxial, kBend, kBend], mTip };
}

// ---------------------------------------------------------------------------
// Structure model: 15 coordinates, body 1 (6), body 2 (6), tip (3).
// ---------------------------------------------------------------------------

function structure(q) {
  const g = geometry(q);
  const mm = (p) => p.map((v) => v / 1000);
  const N = 15;
  const Kre = zeros(N), Kim = zeros(N), M = zeros(N);
  const kR = q.kRadial * 1e6, kL = q.kRadial * q.kLatRatio * 1e6;
  // A spring with stiffness k and loss 2ζ, acting along the row vector r.
  const add = (r, k, zeta) => {
    for (let i = 0; i < N; i++) if (r[i]) for (let j = 0; j < N; j++) if (r[j]) {
      Kre[i][j] += k * r[i] * r[j];
      Kim[i][j] += 2 * zeta * k * r[i] * r[j];
    }
  };
  // A spring between body A (offset oA, or ground) and body B (offset oB).
  const between = (oA, oB, p, n) => {
    const r = new Array(N).fill(0), g6 = rowAt(mm(p), n);
    for (let j = 0; j < 6; j++) {
      if (oA !== null) r[oA + j] -= g6[j];
      r[oB + j] += g6[j];
    }
    return r;
  };
  const up = [0, 1, 0];
  // Lower blocks: ground to body 1. Radial is Y, lateral is X.
  for (const p of g.lowerBlocks) {
    add(between(null, 0, p, up), kR, q.zetaGuide);
    add(between(null, 0, p, [1, 0, 0]), kL, q.zetaGuide);
  }
  add(between(null, 0, g.lowerMotor.p, g.lowerMotor.n), MOTOR_RIGID, 0);
  // Upper blocks: body 1 to body 2. Radial is Y, lateral is Z.
  for (const p of g.upperBlocks) {
    add(between(0, 6, p, up), kR, q.zetaGuide);
    add(between(0, 6, p, [0, 0, 1]), kL, q.zetaGuide);
  }
  add(between(0, 6, g.upperMotor.p, g.upperMotor.n), MOTOR_RIGID, 0);
  // Tool: body 2 at the tip point to the tip mass.
  const tool = toolSpring(q);
  for (let d = 0; d < 3; d++) {
    const n = [0, 0, 0];
    n[d] = 1;
    const r = new Array(N).fill(0), g6 = rowAt(mm(g.tip), n);
    for (let j = 0; j < 6; j++) r[6 + j] -= g6[j];
    r[12 + d] = 1;
    add(r, tool.k[d], q.zetaTool);
  }
  // Masses: M = m·J(c)ᵀJ(c) + diag(0, 0, 0, Ic), about the origin.
  bodies(q, g).forEach((b, k) => {
    const o = 6 * k, J = jac(mm(b.c));
    const [lx, ly, lz] = b.box.map((v) => v / 1000);
    const Ic = [b.m * (ly * ly + lz * lz) / 12, b.m * (lx * lx + lz * lz) / 12, b.m * (lx * lx + ly * ly) / 12];
    for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) {
      let s = 0;
      for (let r = 0; r < 3; r++) s += J[r][i] * J[r][j];
      M[o + i][o + j] += b.m * s + (i === j && i >= 3 ? Ic[i - 3] : 0);
    }
  });
  for (let d = 0; d < 3; d++) M[12 + d][12 + d] = tool.mTip;
  return { Kre, Kim, M, g, tool, N };
}

// Compliance of the structure at the tool tip, 3 × 3 complex, in m/N.
// Column d: the tip motion for a unit force on the tip in direction d.
// (K(1 + 2jζ) − ω²M)·x = F, by Gauss elimination with row pivots, for the
// three unit forces at once. The structure has no controller, so this holds
// at any frequency.
function structAt(f, S) {
  const w2 = (2 * Math.PI * f) ** 2, N = S.N;
  const re = S.Kre.map((row, i) => row.map((v, j) => v - w2 * S.M[i][j]));
  const im = S.Kim.map((row) => row.slice());
  // Right-hand sides: columns N, N + 1, N + 2.
  for (let i = 0; i < N; i++) {
    for (let d = 0; d < 3; d++) { re[i].push(i === 12 + d ? 1 : 0); im[i].push(0); }
  }
  const W = N + 3;
  for (let c = 0; c < N; c++) {
    let piv = c;
    for (let r = c + 1; r < N; r++) if (Math.hypot(re[r][c], im[r][c]) > Math.hypot(re[piv][c], im[piv][c])) piv = r;
    [re[c], re[piv]] = [re[piv], re[c]];
    [im[c], im[piv]] = [im[piv], im[c]];
    const pr = re[c][c], pi = im[c][c], pd = pr * pr + pi * pi;
    for (let r = c + 1; r < N; r++) {
      if (re[r][c] === 0 && im[r][c] === 0) continue;
      const fr = (re[r][c] * pr + im[r][c] * pi) / pd, fi = (im[r][c] * pr - re[r][c] * pi) / pd;
      for (let k = c; k < W; k++) {
        const xr = re[c][k], xi = im[c][k];
        re[r][k] -= fr * xr - fi * xi;
        im[r][k] -= fr * xi + fi * xr;
      }
    }
  }
  const G = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (let d = 0; d < 3; d++) {
    const xr = new Array(N), xi = new Array(N);
    for (let r = N - 1; r >= 0; r--) {
      let sr = re[r][N + d], si = im[r][N + d];
      for (let k = r + 1; k < N; k++) {
        sr -= re[r][k] * xr[k] - im[r][k] * xi[k];
        si -= re[r][k] * xi[k] + im[r][k] * xr[k];
      }
      const ar = re[r][r], ai = im[r][r], ad = ar * ar + ai * ai;
      xr[r] = (sr * ar + si * ai) / ad;
      xi[r] = (si * ar - sr * ai) / ad;
    }
    for (let r = 0; r < 3; r++) G[r][d] = [xr[12 + r], xi[12 + r]];
  }
  return G;
}

// Static compliance of the structure at the tip, 3 × 3 real, in m/N.
const structStatic = (S) => structAt(0, { ...S, Kim: zeros(S.N) }).map((row) => row.map((v) => v[0]));

// The static compliance of one block set at a point, by hand: the 6 × 6
// stiffness of the springs, inverted, moved to the point. The checks compare
// the sum of both sets plus the shank with the full model at f = 0.
function blockSetCompliance(q, which, point) {
  const g = geometry(q);
  const K = zeros(6);
  const kR = q.kRadial * 1e6, kL = q.kRadial * q.kLatRatio * 1e6;
  const mm = (p) => p.map((v) => v / 1000);
  const lat = which === "lower" ? [1, 0, 0] : [0, 0, 1];
  const springs = [];
  for (const p of which === "lower" ? g.lowerBlocks : g.upperBlocks) {
    springs.push([p, [0, 1, 0], kR], [p, lat, kL]);
  }
  const m = which === "lower" ? g.lowerMotor : g.upperMotor;
  springs.push([m.p, m.n, MOTOR_RIGID]);
  for (const [p, n, k] of springs) {
    const r = rowAt(mm(p), n);
    for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) K[i][j] += k * r[i] * r[j];
  }
  // Invert the 6 × 6 with the complex solver (real numbers).
  const Kc = K.map((row) => row.map((v) => [v, 0]));
  const J = jac(mm(point));
  const C = zeros(3);
  for (let d = 0; d < 3; d++) {
    const Q = [0, 1, 2, 3, 4, 5].map((j) => [J[d][j], 0]);  // generalised force of a unit force
    const qd = CM.csolve(Kc, Q).map((v) => v[0]);
    for (let r = 0; r < 3; r++) C[r][d] = J[r].reduce((s, v, j) => s + v * qd[j], 0);
  }
  return C;
}

// ---------------------------------------------------------------------------
// Servo part: the linear motor loop of the cutting force page.
// ---------------------------------------------------------------------------

function servoLoops(q) {
  const ms = servoMass(q);
  const make = (m) => {
    const p = { ...CM.DEFAULTS, m, fs: q.fs };
    const tuned = CM.tune(p, "linear");
    return { p, tuned, m };
  };
  return { x: make(ms.x), z: make(ms.z) };
}

// Compliance of one loop at f, in m/N. Below 0.98·fs/2 the exact compliance at
// the samples. Above it the controller is far too slow to act, and the motor
// side is the bare mass, −1/(m ω²). The checks show the step there is small.
function servoAt(f, L) {
  if (f < 0.98 * L.p.fs / 2) return CM.sineComplianceAt(f, L.p, L.tuned);
  return [-1 / (L.m * (2 * Math.PI * f) ** 2), 0];
}

// The full tip compliance, 3 × 3 complex, m/N.
function tipAt(f, S, loops) {
  const G = structAt(f, S);
  if (loops) {
    G[0][0] = CM.cadd(G[0][0], servoAt(f, loops.x));
    G[2][2] = CM.cadd(G[2][2], servoAt(f, loops.z));
  }
  return G;
}

// ---------------------------------------------------------------------------
// The cut: chip width, chip thickness, edge normal and forces.
// ---------------------------------------------------------------------------

// Engaged edge length b (mm) for a depth ap on a nose radius r with a
// straight edge at the entering angle κ, at feed f per turn.
function chipWidth(ap, f, r, kappaDeg) {
  const k = kappaDeg * Math.PI / 180;
  const th2 = Math.asin(Math.min(1, f / (2 * r)));
  const apNose = r * (1 - Math.cos(k));
  if (ap <= apNose) return r * (Math.acos(1 - ap / r) + th2);
  return r * (k + th2) + (ap - apNose) / Math.sin(k);
}

function cut(q) {
  const r = q.rNose, f = q.feed, ap = q.ap, k = q.kappa * Math.PI / 180;
  const th2 = Math.asin(Math.min(1, f / (2 * r)));
  const apNose = r * (1 - Math.cos(k));
  // End points of the engaged edge, in (radial into the part, along the feed).
  // The nose centre is the origin. The deepest point is (r, 0).
  const P2 = [r * Math.cos(th2), -r * Math.sin(th2)];
  let P1;
  if (ap <= apNose) {
    const t1 = Math.acos(1 - ap / r);
    P1 = [r * Math.cos(t1), r * Math.sin(t1)];
  } else {
    // Up the straight edge, along the tangent of the nose at angle κ.
    const s = (ap - apNose) / Math.sin(k);
    P1 = [r * Math.cos(k) - s * Math.sin(k), r * Math.sin(k) + s * Math.cos(k)];
  }
  // The chord from P2 to P1. Its normal, pointing into the part, sets the
  // direction of the chip thickness and of the thrust (Colwell).
  // Turning the chord from P2 to P1 by −90° gives the normal into the part.
  // For an entering angle above 90° and a long straight edge, it leans past
  // the feed direction, so its radial part may become negative.
  const d = [P1[0] - P2[0], P1[1] - P2[1]];
  let n = [d[1], -d[0]];
  const len = Math.hypot(n[0], n[1]);
  n = [n[0] / len, n[1] / len];
  const phi = Math.atan2(n[1], n[0]);
  const b = chipWidth(ap, f, r, q.kappa);
  const A = ap * f, h = A / b;
  const Fc = q.kc1 * b * h ** (1 - q.mc);
  const Ft = q.rt * Fc;
  const Kt = (1 - q.mc) * q.kc1 * h ** (-q.mc);       // N/mm² = N/mm per mm of width
  const rpm = q.vc * 1000 / (Math.PI * q.D);
  // Global directions: +X into the part, feed along −Z, so the edge normal
  // leans to −Z by φ.
  const uh = [Math.cos(phi), 0, -Math.sin(phi)];
  const w = [q.rt * uh[0], 1, q.rt * uh[2]];
  return { b, h, A, phi, Fc, Ft, Fx: Ft * Math.cos(phi), Fz: Ft * Math.sin(phi), Kt, rpm, uh, w, apNose,
    nose: ap <= apNose, power: Fc * q.vc / 60 };
}

// Oriented compliance Φ = u_hᵀ · G · w, m/N (complex).
function oriented(G, c) {
  let s = [0, 0];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    const k = c.uh[i] * c.w[j];
    if (k) s = CM.cadd(s, [k * G[i][j][0], k * G[i][j][1]]);
  }
  return s;
}

// Depth of cut (mm) for a chip width b (mm): invert chipWidth by bisection.
function depthForWidth(bMm, q) {
  let lo = 0, hi = 20 * q.rNose;
  if (chipWidth(hi, q.feed, q.rNose, q.kappa) < bMm) return hi;
  for (let i = 0; i < 80; i++) {
    const mid = (lo + hi) / 2;
    if (chipWidth(mid, q.feed, q.rNose, q.kappa) < bMm) lo = mid; else hi = mid;
  }
  return (lo + hi) / 2;
}

// ---------------------------------------------------------------------------
// Everything for the page.
// ---------------------------------------------------------------------------

function analyse(qIn = {}, opts = {}) {
  const q = { ...TURNING_DEFAULTS, ...qIn };
  const S = structure(q);
  const loops = servoLoops(q);
  const c = cut(q);
  const Cs = structStatic(S);

  // Frequency grid for the charts.
  const fMode = Math.sqrt(S.tool.k[1] / S.tool.mTip) / (2 * Math.PI);
  const fHi = Math.min(60000, Math.max(3 * fMode, q.fs));
  const fLo = 10;
  const grid = CM.logspace(fLo, fHi, opts.nChart ?? 500);
  const Kt = c.Kt * 1e6;                                     // N/m²
  const bOf = (depth) => depth / (2 * Kt) * 1000;            // −1/Re Φ (N/m) to chip width (mm)
  const tip = grid.map((f) => tipAt(f, S, loops));
  const dirs = ["X", "Y", "Z"];
  const lowest = dirs.map((_, d) => {
    let iMax = 0;
    for (let i = 1; i < grid.length; i++) if (CM.cabs(tip[i][d][d]) > CM.cabs(tip[iMax][d][d])) iMax = i;
    return { f: grid[iMax], k: 1 / CM.cabs(tip[iMax][d][d]) };
  });
  const structPeaks = dirs.map((_, d) => {
    let iMax = 0;
    const s = grid.map((f) => CM.cabs(structAt(f, S)[d][d]));
    for (let i = 1; i < grid.length; i++) if (s[i] > s[iMax]) iMax = i;
    return grid[iMax];
  });

  // Chatter.
  const cache = new Map();
  const phi = (f) => {
    let v = cache.get(f);
    if (!v) { v = oriented(tipAt(f, S, loops), c); cache.set(f, v); }
    return v;
  };
  const lob = CM.lobes(phi, fLo, fHi, 1, q.rpmLo, q.rpmHi, opts.nf ?? 2500, opts.nr ?? 600);
  const apLobe = lob.depth.map((v) => (Number.isFinite(v) ? depthForWidth(bOf(v), q) : NaN));
  const bFloor = bOf(lob.floor);
  const apFloor = depthForWidth(bFloor, q);
  // The limit at the chosen speed: the lowest lobe that passes there.
  const apAtRpm = limitAtRpm(phi, fLo, fHi, c.rpm, q, Kt);

  // Which part sets the limit: the floor with the structure alone (motors
  // rigid) and with the motor loops alone (structure rigid).
  const dense = CM.logspace(fLo, fHi, opts.nSplit ?? 3000);
  const floorOf = (fn) => {
    let lo = Infinity, fAt = NaN;
    for (const f of dense) { const v = fn(f)[0]; if (v < lo) { lo = v; fAt = f; } }
    return { ap: lo < 0 ? depthForWidth(bOf(-1 / lo), q) : Infinity, f: fAt };
  };
  const split = {
    struct: floorOf((f) => oriented(structAt(f, S), c)),
    servo: floorOf((f) => {
      const Z = [[0, 0], [0, 0], [0, 0]].map(() => [[0, 0], [0, 0], [0, 0]]);
      Z[0][0] = servoAt(f, loops.x);
      Z[2][2] = servoAt(f, loops.z);
      return oriented(Z, c);
    }),
  };
  const phiChart = grid.map((f) => phi(f));

  // Static error: the force on the tool is −Fx, −Fc (down), +Fz (feed along −Z).
  const F = [-c.Fx, -c.Fc, c.Fz];
  const defl = [0, 1, 2].map((r) => Cs[r][0] * F[0] + Cs[r][1] * F[1] + Cs[r][2] * F[2]);

  return {
    q, S, loops, cut: c, Cs, grid, tip, lowest, structPeaks,
    staticK: [0, 1, 2].map((d) => 1 / Cs[d][d]),
    lobes: { rpm: lob.rpm, ap: apLobe, apFloor, bFloor, fMin: lob.fMin, minRe: lob.minRe },
    apAtRpm, margin: apAtRpm.ap / q.ap, split, phiChart, defl, diameterError: 2 * defl[0],
    motorUse: { x: c.Fx / 181, z: c.Fz / 181 },
  };
}

// The stable depth at one spindle speed T = 60/rpm. Along the chatter
// frequency f the loop phase ψ(f) = ωT − ε(f) must be a multiple of 2π, with
// ε = 2·arg Φ − π as in lobePoint. Each such f is one lobe passing this
// speed, with depth −1/Re Φ. The lowest one is the limit. ψ is taken on a
// dense grid and each crossing is placed by linear interpolation, then Φ is
// read there.
function limitAtRpm(phi, fLo, fHi, rpm, q, Kt, n = 8000) {
  const T = 60 / rpm;
  const epsOf = (G) => {
    let e = 2 * CM.carg(G) - Math.PI;
    return e - 2 * Math.PI * Math.floor(e / (2 * Math.PI));
  };
  let best = { depth: Infinity, f: NaN };
  let prev = null;
  for (const fi of CM.logspace(fLo, fHi, n)) {
    const G = phi(fi), eps = epsOf(G);
    const psi = 2 * Math.PI * fi * T - eps;
    if (prev && prev.G[0] < 0 && G[0] < 0 && Math.abs(eps - prev.eps) < Math.PI) {
      const k0 = Math.floor(prev.psi / (2 * Math.PI)), k1 = Math.floor(psi / (2 * Math.PI));
      for (let k = Math.min(k0, k1) + 1; k <= Math.max(k0, k1); k++) {
        const s = (2 * Math.PI * k - prev.psi) / (psi - prev.psi);
        const fm = prev.f + s * (fi - prev.f), Gm = phi(fm);
        if (Gm[0] < 0 && -1 / Gm[0] < best.depth) best = { depth: -1 / Gm[0], f: fm };
      }
    }
    prev = { f: fi, G, psi, eps };
  }
  const bMm = best.depth / (2 * Kt) * 1000;
  return { ap: depthForWidth(bMm, q), b: bMm, f: best.f };
}

globalThis.TurningModel = {
  TURNING_DEFAULTS, geometry, bodies, servoMass, toolSpring, structure, structAt, structStatic,
  blockSetCompliance, servoLoops, servoAt, tipAt, chipWidth, cut, oriented, depthForWidth, analyse,
  limitAtRpm, inv3,
};
})();
