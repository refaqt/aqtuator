// Seal strip over four carriage rollers: shape, roller forces, stress, fatigue
// life, and the pull that a screw travel gives.
//
// This is a port of shape() in ../strip-seal-preload/strip_seal_preload.py to
// plain JavaScript, so it can run in a browser with no server. The energy, the
// contact bounds and the fixed point loop are the same. The sparse solve is
// replaced by a banded one, because the matrix has only five diagonals.
//
// Units: mm, N, MPa. A pull is in N per mm of strip width.
//
// Layout, x along the strip, y up. x = 0 is roller 1. The strip centre line
// lies at y = 0 on the profile.
//   Roller 1 and 4 are above the strip and press it on the profile (magnets).
//   Roller 2 and 3 are below the strip and lift it.
//   rho = D/2 + t/2 is the distance from a roller centre to the strip centre
//   line where they touch. Roller 1 centre is at y = rho. Roller 2 centre is at
//   y = lift - rho, so the height difference of the centres is
//   dz = lift - 2 rho, and lift = dz + D + t.

// ---------------------------------------------------------------------------
// Materials, copied from the two Python cases. Stresses in MPa.
// ---------------------------------------------------------------------------

export const MATERIALS = {
  "301": {
    name: "EN 1.4310 / AISI 301, Alleima 11R51 at Rm 2050",
    E: 185000, Rm: 2050, Rp02: 1975,
    // Reverse bending limit, 50 % survival at 2e6 cycles, measured at 0.25 mm
    // (775 MPa) and 0.50 mm (630 MPa). Power law between them, exponent 0.299.
    sigmaW: (t) => [775 * (0.25 / t) ** 0.299, 775 * (0.25 / t) ** 0.299],
    measuredT: [0.25, 0.50],
    source: "Alleima 11R51 data sheet: Rm 2050, Rp0.2 1975, E 185 GPa, " +
      "fatigue limit 775 MPa at 0.25 mm and 630 MPa at 0.50 mm.",
  },
  "304": {
    name: "EN 1.4301 / AISI 304, +C1300 (strongest class sold)",
    E: 179000, Rm: 1300, Rp02: 760,
    // No maker publishes a fatigue limit for 304 strip. Range from twelve IPCO
    // belt grades: 0.32 to 0.48 of Rm.
    sigmaW: () => [0.32 * 1300, 0.48 * 1300],
    measuredT: null,
    source: "EN 10151 Rm 1300-1500 and E; ASTM A666 half hard yield 760 MPa " +
      "minimum. No fatigue data published: estimate 0.32-0.48 Rm from IPCO belt grades.",
  },
};

// Plastic strips (liners) on the ceiling of carriage-top, sliding on the
// steel strip. Dynamic friction against steel, dry. The mcam values are
// pin-on-disk at 3 MPa and 0.33 m/s, much faster and harder pressed than
// here, so they are a guide only.
export const LINERS = {
  PTFE: { name: "PTFE, unfilled", mu: [0.05, 0.20],
    source: "Engineering ToolBox, PTFE on steel, clean and dry: 0.05-0.2." },
  UHMW: { name: "UHMW-PE (TIVAR 1000)", mu: [0.15, 0.30],
    source: "mcam TIVAR 1000 data sheet, ISO 7148-2: 0.15-0.30 (0.12 by QTM 55007)." },
  POM: { name: "POM-C (Acetron C)", mu: [0.30, 0.45],
    source: "mcam Acetron C data sheet, ISO 7148-2: 0.3-0.45 (0.25 by QTM 55007)." },
  PA6: { name: "PA6 (Ertalon 6 SA)", mu: [0.40, 0.60],
    source: "mcam Ertalon 6 SA data sheet, ISO 7148-2: 0.4-0.6." },
};
// Steel strip on bare aluminium (the slopes of both carriage halves).
// Engineering ToolBox, aluminium on mild steel, clean and dry, kinetic.
export const MU_ALU = 0.47;

export const DEFAULTS = {
  // Roller places from the compact-stage CAD of 2026-10-28.
  t: 0.15,          // mm, strip thickness
  D: 10,            // mm, roller diameter
  a: 36.83,         // mm, roller 1 to 2 (and 3 to 4)
  b: 112,           // mm, roller 2 to 3
  dz: 1.85,         // mm, centre of 2/3 minus centre of 1/4 (lift 12 mm)
  // The strip runs in a channel between the two carriage halves.
  carriage: true,   // false: free strip, no carriage surfaces
  stick: 0.5,       // mm, how far each roller sticks out of its carriage half
  slope: 19.44,     // degrees, slopes of both halves (12 mm over 34 mm)
  ceilOut: 8.45,    // mm, flat ceiling starts this far outside rollers 2 and 3
  clear: 13.5,      // mm, flat ceiling of carriage-top above the profile
  liner: 0.5,       // mm, plastic strip on the flat ceiling, thickness
  linerWidth: 10,   // mm, its width along the strip, centred between rollers 2 and 3
  linerMat: "PTFE",
  material: "301",
  width: 186,       // mm, the widest strip through the carriage
  length: 1000,     // mm, strip length between the clamps
  u: 0.03,          // mm, screw travel after the strip lies without pull
  plate: false,     // plate factor 1/(1 - nu^2) on the bending stress
  k: 20,            // N/mm^3, stiffness of the magnet strips under the strip
  q: 0.005,         // N/mm^2 (MPa), pull of the magnet strips on the strip
};

const MAGNET_REACH = 0.2;   // mm, the magnets pull only this close

const NU = 0.3;
const OUTSIDE = 60;   // mm of strip modelled outside each outer roller
const DX = 0.1;       // mm grid

// ---------------------------------------------------------------------------
// Banded solver
// ---------------------------------------------------------------------------

// Solve A z = r for a symmetric positive definite pentadiagonal A, given by
// its diagonal d0, first upper diagonal d1 and second upper diagonal d2.
// LDL^T with L unit lower banded.
function solvePenta(d0, d1, d2, r) {
  const n = d0.length;
  const D = new Float64Array(n), L1 = new Float64Array(n), L2 = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    // L2[i] = A[i][i-2] / D[i-2], L1[i] = (A[i][i-1] - L2[i] L1[i-1] D[i-2]) / D[i-1]
    let l2 = 0, l1 = 0;
    if (i >= 2) l2 = d2[i - 2] / D[i - 2];
    if (i >= 1) {
      let v = d1[i - 1];
      if (i >= 2) v -= l2 * L1[i - 1] * D[i - 2];
      l1 = v / D[i - 1];
    }
    let di = d0[i];
    if (i >= 1) di -= l1 * l1 * D[i - 1];
    if (i >= 2) di -= l2 * l2 * D[i - 2];
    D[i] = di; L1[i] = l1; L2[i] = l2;
  }
  const z = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let v = r[i];
    if (i >= 1) v -= L1[i] * z[i - 1];
    if (i >= 2) v -= L2[i] * z[i - 2];
    z[i] = v;
  }
  for (let i = 0; i < n; i++) z[i] /= D[i];
  for (let i = n - 1; i >= 0; i--) {
    let v = z[i];
    if (i + 1 < n) v -= L1[i + 1] * z[i + 1];
    if (i + 2 < n) v -= L2[i + 2] * z[i + 2];
    z[i] = v;
  }
  return z;
}

// H as bands: h0[i] = H[i][i], h1[i] = H[i][i+1], h2[i] = H[i][i+2].
function bandMul(h0, h1, h2, y) {
  const n = y.length, g = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let v = h0[i] * y[i];
    if (i + 1 < n) v += h1[i] * y[i + 1];
    if (i + 2 < n) v += h2[i] * y[i + 2];
    if (i >= 1) v += h1[i - 1] * y[i - 1];
    if (i >= 2) v += h2[i - 2] * y[i - 2];
    g[i] = v;
  }
  return g;
}

function hAt(h0, h1, h2, i, j) {
  if (i > j) [i, j] = [j, i];
  if (j === i) return h0[i];
  if (j === i + 1) return h1[i];
  if (j === i + 2) return h2[i];
  return 0;
}

// Lowest 0.5 y'Hy + f'y over the free points, with the points in lo and hi
// held on their bound. Returns all points.
function solveFixed(h0, h1, h2, f, lb, ub, lo, hi) {
  const n = lb.length;
  const out = new Float64Array(n);
  const free = [];
  for (let i = 0; i < n; i++) {
    if (lo[i]) out[i] = lb[i];
    else if (hi[i]) out[i] = ub[i];
    else free.push(i);
  }
  const m = free.length;
  if (m) {
    const d0 = new Float64Array(m), d1 = new Float64Array(m), d2 = new Float64Array(m);
    const r = new Float64Array(m);
    for (let k = 0; k < m; k++) {
      const i = free[k];
      d0[k] = h0[i];
      if (k + 1 < m && free[k + 1] - i <= 2) d1[k] = hAt(h0, h1, h2, i, free[k + 1]);
      if (k + 2 < m && free[k + 2] - i <= 2) d2[k] = hAt(h0, h1, h2, i, free[k + 2]);
      let v = -f[i];
      for (let j = Math.max(0, i - 2); j <= Math.min(n - 1, i + 2); j++) {
        if (lo[j] || hi[j]) v -= hAt(h0, h1, h2, i, j) * out[j];
      }
      r[k] = v;
    }
    const z = solvePenta(d0, d1, d2, r);
    for (let k = 0; k < m; k++) out[free[k]] = z[k];
  }
  return out;
}

function gradient(h0, h1, h2, f, y) {
  const g = bandMul(h0, h1, h2, y);
  for (let i = 0; i < y.length; i++) g[i] += f[i];
  return g;
}

// Lowest 0.5 y'Hy + f'y with lb <= y <= ub, by the same active set method as
// _bounded_qp() in the Python case. y is the start. That method changes every
// wrong set at once and is fast, but in a narrow channel it can go round in a
// circle. Then the slower method below takes over.
function boundedQP(h0, h1, h2, f, lb, ub, y) {
  const n = y.length;
  const lo = new Uint8Array(n), hi = new Uint8Array(n);
  const close = (p, q) => Math.abs(p - q) <= 1e-8 + 1e-5 * Math.abs(q);
  for (let i = 0; i < n; i++) {
    lo[i] = close(y[i], lb[i]) ? 1 : 0;
    hi[i] = !lo[i] && close(y[i], ub[i]) ? 1 : 0;
  }
  for (let it = 0; it < 200; it++) {
    const out = solveFixed(h0, h1, h2, f, lb, ub, lo, hi);
    const g = gradient(h0, h1, h2, f, out);
    let changed = false;
    for (let i = 0; i < n; i++) {
      if (lo[i]) {
        if (g[i] < -1e-9) { lo[i] = 0; changed = true; }
      } else if (hi[i]) {
        if (g[i] > 1e-9) { hi[i] = 0; changed = true; }
      } else if (out[i] < lb[i] - 1e-12) {
        lo[i] = 1; changed = true;
      } else if (out[i] > ub[i] + 1e-12) {
        hi[i] = 1; changed = true;
      }
    }
    if (!changed) return { y: out, g, lo, hi };
  }
  return boundedQPSafe(h0, h1, h2, f, lb, ub, y);
}

// Primal active set method: it stays inside the bounds, walks towards the
// best point until it meets a new bound, and lets go of one bound at a time.
// The energy goes down at every step, so it cannot circle.
function boundedQPSafe(h0, h1, h2, f, lb, ub, start) {
  const n = start.length;
  const y = new Float64Array(n);
  const lo = new Uint8Array(n), hi = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    y[i] = Math.min(Math.max(start[i], lb[i]), ub[i]);
    lo[i] = y[i] <= lb[i] ? 1 : 0;
    hi[i] = !lo[i] && y[i] >= ub[i] ? 1 : 0;
  }
  // A bound whose release only puts it straight back is a rounding effect:
  // keep it. The force tolerance follows the size of the matrix.
  const keep = new Uint8Array(n);
  let tol = 0;
  for (let i = 0; i < n; i++) tol = Math.max(tol, h0[i]);
  tol *= 1e-12;
  let released = -1;
  for (let it = 0; it < 50000; it++) {
    const out = solveFixed(h0, h1, h2, f, lb, ub, lo, hi);
    let alpha = 1, block = -1, toLo = false;
    for (let i = 0; i < n; i++) {
      if (lo[i] || hi[i]) continue;
      const d = out[i] - y[i];
      if (d < 0 && out[i] < lb[i]) {
        const s = (lb[i] - y[i]) / d;
        if (s < alpha) { alpha = s; block = i; toLo = true; }
      } else if (d > 0 && out[i] > ub[i]) {
        const s = (ub[i] - y[i]) / d;
        if (s < alpha) { alpha = s; block = i; toLo = false; }
      }
    }
    if (block >= 0) {
      if (block === released && alpha < 1e-9) keep[block] = 1;
      released = -1;
      for (let i = 0; i < n; i++) if (!(lo[i] || hi[i])) y[i] += alpha * (out[i] - y[i]);
      if (toLo) { lo[block] = 1; y[block] = lb[block]; } else { hi[block] = 1; y[block] = ub[block]; }
      continue;
    }
    y.set(out);
    const g = gradient(h0, h1, h2, f, y);
    let worst = -1, worstV = tol;
    for (let i = 0; i < n; i++) {
      if (keep[i]) continue;
      const v = lo[i] ? -g[i] : hi[i] ? g[i] : 0;
      if (v > worstV) { worst = i; worstV = v; }
    }
    if (worst < 0) return { y, g, lo, hi };
    lo[worst] = 0; hi[worst] = 0;
    released = worst;
  }
  throw new Error("contact solver did not settle");
}

// ---------------------------------------------------------------------------
// Strip shape
// ---------------------------------------------------------------------------

export function layout(p) {
  const rho = p.D / 2 + p.t / 2;
  const lift = p.dz + 2 * rho;
  const rollers = [0, p.a, p.a + p.b, 2 * p.a + p.b];
  const centres = rollers.map((xc, k) => [xc, k === 0 || k === 3 ? rho : lift - rho]);
  return { rho, lift, rollers, centres };
}

export const hasLiner = (p) => p.liner > 0 && (p.linerWidth ?? 0) > 0;

// The channel between the carriage halves, as heights above the profile
// (the top of the base), against x. Rollers 1 and 4 sit in carriage-top, on
// the low edge of its slope. Rollers 2 and 3 sit in carriage-bottom, on the
// high edge of its slope. Each roller sticks out p.stick from its half.
//   ceiling(x): underside of carriage-top, or of the liner. The liner is a
//               short strip of p.linerWidth in the middle of the flat ceiling.
//   floor(x):   top of carriage-bottom
// Returns null where a surface does not reach. kind: "liner" or "alu".
export function channel(p) {
  const tan = Math.tan((p.slope ?? 0) * Math.PI / 180);
  const { lift, rollers } = layout(p);
  const xm = rollers[3] / 2;
  const xs = p.a - p.ceilOut;           // end of the sloped ceiling
  const ceiling = (x) => {
    if (x < 0 || x > rollers[3]) return null;
    const d = Math.min(x, rollers[3] - x);
    if (d < xs) return { h: p.t + p.stick + tan * d, kind: "alu", slope: true };
    if (hasLiner(p) && Math.abs(x - xm) <= p.linerWidth / 2) {
      return { h: p.clear - p.liner, kind: "liner", slope: false };
    }
    return { h: p.clear, kind: "alu", slope: false };
  };
  const floor = (x) => {
    if (x < 0 || x > rollers[3]) return null;
    const d = Math.min(x, rollers[3] - x);
    if (d < p.a) {
      const h = lift - p.stick - tan * (p.a - d);
      return h < 0 ? null : { h, kind: "alu", slope: true };   // below the base: no carriage there
    }
    return { h: lift - p.stick, kind: "alu", slope: false };
  };
  return { ceiling, floor, tan, xm };
}

// Shape of the strip centre line under a pull in N per mm of width.
// opts: { profile: true, exact: true, dx: DX, outside: OUTSIDE, start: y }
//
// The strip lies on magnet strips. They are an elastic bed of stiffness p.k
// (N per mm of sink, per mm^2 of strip) that only pushes, plus a magnetic
// pull p.q (N/mm^2) on the strip wherever it is within MAGNET_REACH of them. With
// p.k = Infinity the profile is rigid, as in the Python case. A rigid profile
// gives the right shape but not the right force at rollers 1 and 4: the
// roller pins the strip on the profile at one point, and the moment there is
// then carried by two forces with no distance between them. The elastic bed
// spreads that couple over a length of about (EI / k)^(1/4).
export function shape(p, pull, opts = {}) {
  const m = MATERIALS[p.material];
  const E = opts.E ?? m.E;
  const profile = opts.profile ?? true;
  const exact = opts.exact ?? true;
  const dx = opts.dx ?? DX;
  const outside = opts.outside ?? OUTSIDE;
  const EI = E * p.t ** 3 / 12;
  const { rho, lift, rollers, centres } = layout(p);

  const x0 = -outside, x1 = rollers[3] + outside;
  const n = Math.round((x1 - x0) / dx) + 1;
  const x = new Float64Array(n);
  for (let i = 0; i < n; i++) x[i] = x0 + i * dx;

  // Bounds, and which support sets each bound: -1 profile, 0..3 roller,
  // 4 carriage-top bare, 5 liner, 6 carriage-bottom.
  const k = p.k ?? Infinity;
  const rigid = profile && !(k < Infinity);
  const bed = profile && !rigid;
  const lb = new Float64Array(n).fill(rigid ? 0 : -1e3);
  const ub = new Float64Array(n).fill(1e3);
  const lbOwner = new Int8Array(n).fill(rigid ? -1 : -2);
  const ubOwner = new Int8Array(n).fill(-2);
  for (let k = 0; k < 4; k++) {
    const xc = rollers[k];
    for (let i = 0; i < n; i++) {
      const d = x[i] - xc;
      if (Math.abs(d) >= rho) continue;
      const h = Math.sqrt(rho * rho - d * d);
      if (k === 0 || k === 3) {
        const v = rho - h;
        if (v < ub[i]) { ub[i] = v; ubOwner[i] = k; }
      } else {
        const v = lift - rho + h;
        if (v > lb[i]) { lb[i] = v; lbOwner[i] = k; }
      }
    }
  }
  // The channel. The strip centre line is t/2 above its underside, and the
  // profile is at y = -t/2, so a surface at height h above the profile
  // bounds the centre line at h - t (ceiling) or h (floor).
  const ch = profile && p.carriage ? channel(p) : null;
  if (ch) {
    for (let i = 0; i < n; i++) {
      const c = ch.ceiling(x[i]), f = ch.floor(x[i]);
      if (c && c.h - p.t < ub[i]) { ub[i] = c.h - p.t; ubOwner[i] = c.kind === "liner" ? 5 : 4; }
      if (f && f.h > lb[i]) { lb[i] = f.h; lbOwner[i] = 6; }
    }
  }
  // Extra obstacles, such as the carriage faces around the strip:
  // opts.walls = [{x0, x1, y0, y1, side: 'up'|'down'}], a straight wall for the strip centre
  // line from (x0, y0) to (x1, y1). 'up' is a ceiling, 'down' a floor. Their forces on the
  // strip come back in wallF, per mm of width; a ceiling pushes down, so wallF.up <= 0.
  for (const w of (opts.walls ?? [])) {
    for (let i = 0; i < n; i++) {
      if (x[i] < w.x0 || x[i] > w.x1) continue;
      const v = w.y0 + (x[i] - w.x0) * (w.y1 - w.y0) / (w.x1 - w.x0);
      if (w.side === 'up') { if (v < ub[i]) { ub[i] = v; ubOwner[i] = 9; } }
      else if (v > lb[i]) { lb[i] = v; lbOwner[i] = 8; }
    }
  }
  const q = profile ? (p.q ?? 0) : 0;
  const yFar = bed ? -q / k : 0;          // flat far away, sunk by the magnet pull
  for (const i of [0, 1, n - 2, n - 1]) { lb[i] = yFar; ub[i] = yFar; }
  for (let i = 0; i < n; i++) if (ub[i] < lb[i] + 1e-9) ub[i] = lb[i] + 1e-9;

  // Start: straight lines through the roller contacts, or a given shape.
  let y = new Float64Array(n);
  if (opts.start && opts.start.length === n) {
    y.set(opts.start);
  } else {
    const ys = [0, lift, lift, 0];
    for (let i = 0; i < n; i++) {
      let v = 0;
      if (x[i] > 0 && x[i] < rollers[3]) {
        for (let k = 0; k < 3; k++) {
          if (x[i] >= rollers[k] && x[i] <= rollers[k + 1]) {
            const f = (x[i] - rollers[k]) / (rollers[k + 1] - rollers[k]);
            v = ys[k] + f * (ys[k + 1] - ys[k]);
          }
        }
      }
      y[i] = v;
    }
  }
  for (let i = 0; i < n; i++) y[i] = Math.min(Math.max(y[i], lb[i]), ub[i]);

  let res;
  let onBed = new Uint8Array(n);
  let pulled = new Uint8Array(n);
  for (let step = 0; step < 300; step++) {
    const h0 = new Float64Array(n), h1 = new Float64Array(n), h2 = new Float64Array(n);
    const f = new Float64Array(n);
    const pullNow = new Uint8Array(n);
    if (q > 0) {
      for (let i = 0; i < n; i++) {
        if (y[i] < MAGNET_REACH) { pullNow[i] = 1; f[i] = q * dx; }
      }
    }
    // Magnet strips: a spring to y = 0 wherever the strip sits below it.
    const bedNow = new Uint8Array(n);
    if (bed) {
      for (let i = 0; i < n; i++) {
        if (y[i] < -1e-12 || (onBed[i] && y[i] <= 1e-12)) { bedNow[i] = 1; h0[i] += k * dx; }
      }
    }
    // Bending: EI dx sum wb_k (y[k] - 2 y[k+1] + y[k+2])^2 / dx^4
    for (let k = 0; k < n - 2; k++) {
      let wb = 1;
      if (exact) {
        const s = (y[k + 2] - y[k]) / (2 * dx);
        wb = (1 + s * s) ** -2.5;
      }
      const c = EI * wb / dx ** 3;
      h0[k] += c; h0[k + 1] += 4 * c; h0[k + 2] += c;
      h1[k] += -2 * c; h1[k + 1] += -2 * c; h2[k] += c;
    }
    // Pull: T dx sum wt_k (y[k+1] - y[k])^2 / dx^2
    for (let k = 0; k < n - 1; k++) {
      let wt = 1;
      if (exact) {
        const s = (y[k + 1] - y[k]) / dx;
        wt = 2 / (Math.sqrt(1 + s * s) + 1);
      }
      const c = pull * wt / dx;
      h0[k] += c; h0[k + 1] += c; h1[k] += -c;
    }
    res = boundedQP(h0, h1, h2, f, lb, ub, y);
    let change = 0;
    for (let i = 0; i < n; i++) change = Math.max(change, Math.abs(res.y[i] - y[i]));
    if (step < 10) y = res.y;
    else for (let i = 0; i < n; i++) y[i] = 0.5 * (y[i] + res.y[i]);
    let same = true;
    for (let i = 0; i < n; i++) {
      if (bedNow[i] !== onBed[i] || pullNow[i] !== pulled[i]) { same = false; break; }
    }
    onBed = bedNow;
    pulled = pullNow;
    if (change < 1e-5 && same) break;
  }

  // Curvature at the inner nodes.
  const kappa = new Float64Array(n);
  let extra = 0, kMax = 0, kMin = 0, iAbs = 1;
  for (let i = 1; i < n - 1; i++) {
    const s = (y[i + 1] - y[i - 1]) / (2 * dx);
    kappa[i] = (y[i + 1] - 2 * y[i] + y[i - 1]) / dx ** 2 / (1 + s * s) ** 1.5;
    if (kappa[i] > kMax) kMax = kappa[i];
    if (kappa[i] < kMin) kMin = kappa[i];
    if (Math.abs(kappa[i]) > Math.abs(kappa[iAbs])) iAbs = i;
  }
  for (let i = 0; i < n - 1; i++) {
    const s = (y[i + 1] - y[i]) / dx;
    extra += (Math.sqrt(1 + s * s) - 1) * dx;
  }

  // Forces on the strip, per mm of width. At the solution H y = lambda, where
  // lambda is the force of a bound (a roller, or the rigid profile) and H
  // holds the magnet bed spring. So a bound pushes with g = H y, and the bed
  // pushes with -k dx y where the strip sinks into it. A roller pushes along
  // the line from its centre to the contact point, which gives the x part.
  const g = res.g, yr = res.y;
  const supports = [0, 1, 2, 3].map(() => ({ fx: 0, fy: 0 }));
  const profileF = [0, 0];     // left and right of the carriage middle
  // Carriage surfaces: force on the strip, and the normal force for friction.
  const contacts = { 4: { fx: 0, fy: 0, n: 0 }, 5: { fx: 0, fy: 0, n: 0 }, 6: { fx: 0, fy: 0, n: 0 } };
  const xm = rollers[3] / 2;
  let sumFy = 0, endF = 0;
  const wallF = { up: 0, down: 0 };
  for (let i = 0; i < n; i++) {
    const side = x[i] < xm ? 0 : 1;
    if (pulled[i]) {
      profileF[side] -= q * dx;
      sumFy -= q * dx;
    }
    if (onBed[i]) {
      const f = -k * dx * yr[i];
      profileF[side] += f;
      sumFy += f;
    }
    if (!(res.lo[i] || res.hi[i]) || i < 2 || i > n - 3) {
      if (i < 2 || i > n - 3) endF += g[i];
      continue;
    }
    const owner = res.lo[i] ? lbOwner[i] : ubOwner[i];
    sumFy += g[i];
    if (owner === 8 || owner === 9) {
      wallF[owner === 9 ? 'up' : 'down'] += g[i];
    } else if (owner >= 4) {
      // A surface pushes along its normal. On a slope the normal leans
      // towards the carriage middle (floor) or away from it (ceiling).
      const sf = owner === 6 ? ch.floor(x[i]) : ch.ceiling(x[i]);
      const tn = sf.slope ? ch.tan : 0;
      const fx = (x[i] < xm ? -1 : 1) * g[i] * tn;
      contacts[owner].fy += g[i];
      contacts[owner].fx += fx;
      contacts[owner].n += Math.hypot(fx, g[i]);
    } else if (owner >= 0) {
      const [xc, yc] = centres[owner];
      const nx = x[i] - xc, ny = yr[i] - yc;
      supports[owner].fy += g[i];
      supports[owner].fx += Math.abs(ny) > 1e-9 ? g[i] * nx / ny : 0;
    } else if (owner === -1) {
      profileF[side] += g[i];
    }
  }

  // Arch between rollers 2 and 3.
  let archTop = -Infinity, archAt = rollers[1];
  for (let i = 0; i < n; i++) {
    if (x[i] >= rollers[1] && x[i] <= rollers[2] && y[i] > archTop) {
      archTop = y[i]; archAt = x[i];
    }
  }
  const iMid = Math.round((rollers[1] + rollers[2]) / 2 / dx + outside / dx);

  let top = -Infinity, gapOut = 0;
  for (let i = 0; i < n; i++) {
    top = Math.max(top, y[i]);
    if (x[i] < -rho || x[i] > rollers[3] + rho) gapOut = Math.max(gapOut, y[i] - yFar);
  }

  return {
    x, y, kappa, pull,
    rMin: 1 / Math.abs(kappa[iAbs]),
    at: 1 + rollers.reduce((best, xc, k) =>
      Math.abs(x[iAbs] - xc) < Math.abs(x[iAbs] - rollers[best]) ? k : best, 0),
    kMax, kMin, top, extra, gapOut,
    // Arch height: from the line through the tops of rollers 2 and 3 to the
    // underside of the strip. Roller top = lift - t/2, strip underside at the
    // arch top = archTop - t/2, so the t/2 cancels.
    archTop, archAt, archMid: y[iMid], archHeight: archTop - lift,
    // Force ON THE ROLLER is minus the force on the strip.
    rollerForces: supports.map((s) => ({ fx: -s.fx, fy: -s.fy })),
    // Forces ON the carriage surfaces, per mm of width; n is the normal force.
    carriageForces: [
      { name: "Carriage-top, bare aluminium", mu: [MU_ALU, MU_ALU], ...onPart(contacts[4]) },
      { name: "Ceiling liner", mu: LINERS[p.linerMat]?.mu ?? [MU_ALU, MU_ALU], ...onPart(contacts[5]) },
      { name: "Carriage-bottom", mu: [MU_ALU, MU_ALU], ...onPart(contacts[6]) },
    ],
    profileForces: profileF.map((f) => -f),
    sumFy, endF, wallF,
    layout: { rho, lift, rollers, centres },
  };
}

const onPart = (c) => ({ fx: -c.fx, fy: -c.fy, n: c.n });

// Friction on the carriage when it moves, in N for the whole width: the sum
// of mu times the normal force over the sliding contacts. The rollers roll
// and add none. Returns [low, high] from the friction range of each contact.
export function carriageFriction(p, s) {
  const out = [0, 0];
  for (const c of s.carriageForces) {
    out[0] += c.mu[0] * c.n * p.width;
    out[1] += c.mu[1] * c.n * p.width;
  }
  return out;
}

// ---------------------------------------------------------------------------
// Stress and fatigue
// ---------------------------------------------------------------------------

function turningPoints(series) {
  const pts = [series[0]];
  for (const v of series.slice(1)) if (v !== pts[pts.length - 1]) pts.push(v);
  if (pts.length < 3) return pts;
  const out = [pts[0]];
  for (let i = 1; i < pts.length - 1; i++) {
    if ((pts[i] - pts[i - 1]) * (pts[i + 1] - pts[i]) < 0) out.push(pts[i]);
  }
  out.push(pts[pts.length - 1]);
  return out;
}

// Three point rainflow, ASTM E1049, as rainflow() in the fatigue case.
function rainflow(series) {
  const stack = [], cycles = [];
  for (const p of turningPoints(series)) {
    stack.push(p);
    while (stack.length >= 3) {
      const rOld = Math.abs(stack[stack.length - 2] - stack[stack.length - 3]);
      const rNew = Math.abs(stack[stack.length - 1] - stack[stack.length - 2]);
      if (rNew < rOld) break;
      cycles.push([rOld, (stack[stack.length - 3] + stack[stack.length - 2]) / 2, 1]);
      stack.splice(stack.length - 3, 2);
    }
  }
  for (let i = 0; i < stack.length - 1; i++) {
    cycles.push([Math.abs(stack[i + 1] - stack[i]), (stack[i] + stack[i + 1]) / 2, 0.5]);
  }
  return cycles;
}

function cyclesToFailure(sar, sw, Rm) {
  if (sar <= sw) return Infinity;
  const s1 = 0.9 * Rm;
  const slope = Math.log10(sw / s1) / Math.log10(2e6 / 1e3);
  return 1e3 * (sar / s1) ** (1 / slope);
}

// Stress along the strip, the highest stress, and the crossings to failure.
// One crossing is one pass of the carriage over one point of the strip: that
// point sees the whole curvature profile once. The bending stress history is
// cut into cycles by rainflow (repeated passes, difference of n+1 and n passes
// so the end residue cancels, as in the fatigue case). The pull adds a mean.
export function stressAndLife(p, s) {
  const m = MATERIALS[p.material];
  const pf = p.plate ? 1 / (1 - NU * NU) : 1;
  const c = m.E * p.t / 2 * pf;            // bending stress per curvature
  const membrane = s.pull / p.t;
  const bendMax = c * Math.max(s.kMax, -s.kMin);
  const peak = membrane + bendMax;

  // Bending stress history at the top surface, thinned to turning points.
  const hist = turningPoints(Array.from(s.kappa, (k) => Math.round(c * k * 10) / 10));
  const repeat = (r) => { let a = []; for (let i = 0; i < r; i++) a = a.concat(hist); return a; };
  const count = (r) => {
    const out = new Map();
    for (const [rng, mean, cnt] of rainflow(repeat(r))) {
      const key = `${(rng / 2).toFixed(1)}|${mean.toFixed(1)}`;
      out.set(key, (out.get(key) || 0) + cnt);
    }
    return out;
  };
  const more = count(5), less = count(4);
  const cycles = [];
  for (const [key, v] of more) {
    const nCyc = v - (less.get(key) || 0);
    if (nCyc > 1e-9) {
      const [amp, mean] = key.split("|").map(Number);
      cycles.push({ amp, mean: mean + membrane, n: nCyc });
    }
  }
  cycles.sort((q, r) => r.amp - q.amp);

  const sws = m.sigmaW(p.t);
  const life = sws.map((sw) => {
    if (peak >= m.Rp02) return 0;
    let dmg = 0;
    for (const cy of cycles) {
      if (cy.mean >= m.Rm) return 0;
      const sar = cy.mean > 0 ? cy.amp / (1 - cy.mean / m.Rm) : cy.amp;
      const nf = cyclesToFailure(sar, sw, m.Rm);
      if (nf !== Infinity) dmg += cy.n / nf;
    }
    return dmg === 0 ? Infinity : 1 / dmg;
  });
  const main = cycles[0] || { amp: 0, mean: membrane, n: 0 };
  const sarMain = main.mean > 0 ? main.amp / (1 - main.mean / m.Rm) : main.amp;
  const extrapolated = m.measuredT
    ? p.t < m.measuredT[0] || p.t > m.measuredT[1] : false;

  return {
    membrane, bendMax, peak, pf,
    stress: Array.from(s.kappa, (k) => c * k),
    cycles, mainAmp: main.amp, mainMean: main.mean, sarMain,
    sigmaW: sws, life, extrapolated,
    Rp02: m.Rp02, Rm: m.Rm,
  };
}

// ---------------------------------------------------------------------------
// Screw preload
// ---------------------------------------------------------------------------

// The strip is fitted with loose screws: it lies over the rollers with no
// pull and takes the path length extra(0). Tightening the screw moves the end
// by u. The strip takes up u in two ways: the arch gets flatter (the path gets
// shorter) and the steel stretches. The pull T solves
//
//     u = extra(0) - extra(T) + L T / (E t)
//
// The pull is the same along the whole strip: it slides on the magnets.
export const PULL_GRID = [0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1,
  1.5, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50];

export function screwCurve(p, grid = PULL_GRID) {
  const m = MATERIALS[p.material];
  const out = [];
  let start;
  for (const T of grid) {
    const s = shape(p, T, { start });
    start = s.y;
    out.push({ T, extra: s.extra, archTop: s.archTop, archHeight: s.archHeight, archMid: s.archMid,
      rMin: s.rMin, peak: stressAndLife(p, s).peak });
  }
  const e0 = out[0].extra;
  for (const r of out) r.u = e0 - r.extra + p.length * r.T / (m.E * p.t);
  return out;
}

function interp(xs, ys, v) {
  if (v <= xs[0]) return ys[0];
  for (let i = 1; i < xs.length; i++) {
    if (v <= xs[i]) {
      const f = (v - xs[i - 1]) / (xs[i] - xs[i - 1]);
      return ys[i - 1] + f * (ys[i] - ys[i - 1]);
    }
  }
  return ys[ys.length - 1];
}

// Pull for a screw travel u, from the curve. Past the last point the steel
// stretch alone is used.
export function pullForTravel(p, curve, u) {
  const last = curve[curve.length - 1];
  if (u > last.u) {
    const m = MATERIALS[p.material];
    return last.T + (u - last.u) / (p.length / (m.E * p.t));
  }
  return interp(curve.map((r) => r.u), curve.map((r) => r.T), Math.max(0, u));
}

export function travelForPull(curve, T) {
  return interp(curve.map((r) => r.T), curve.map((r) => r.u), T);
}

// ---------------------------------------------------------------------------
// Self check, same as check_solver() in the Python case: a strip under pull
// between two point supports with no profile, against the closed form.
// ---------------------------------------------------------------------------

export function checkSolver() {
  // Tiny rollers, so the supports are points. Lift 6 mm, ramp as drawn.
  const p = { ...DEFAULTS, D: 0.02 };
  const rise = 6.0;
  p.dz = rise - (p.D + p.t);
  p.a = 2 * Math.sqrt(2 * 30 * rise / 2 - (rise / 2) ** 2);
  const EI = MATERIALS["301"].E * p.t ** 3 / 12;
  const results = [];
  for (const pull of [10, 40]) {
    const lam = Math.sqrt(EI / pull);
    const b = p.a / (2 * lam);
    const want = 2 * lam ** 2 * (b * Math.exp(b) - Math.sinh(b)) / (rise * Math.sinh(b));
    const got = shape(p, pull, { profile: false, exact: false, dx: 0.05, outside: 120 }).rMin;
    results.push({ pull, want, got, ok: Math.abs(got / want - 1) <= 0.05 });
  }
  return results;
}
