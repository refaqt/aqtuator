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

export const DEFAULTS = {
  t: 0.25,          // mm, strip thickness
  D: 10,            // mm, roller diameter
  a: 26.2,          // mm, roller 1 to 2 (and 3 to 4)
  b: 119,           // mm, roller 2 to 3
  dz: -4.25,        // mm, centre of 2/3 minus centre of 1/4 (lift 6 mm)
  material: "301",
  width: 150,       // mm
  length: 1000,     // mm, strip length between the clamps
  u: 0.5,           // mm, screw travel after the strip lies without pull
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

// Lowest 0.5 y'Hy + f'y with lb <= y <= ub, by the same active set method as
// _bounded_qp() in the Python case. y is the start.
function boundedQP(h0, h1, h2, f, lb, ub, y) {
  const n = y.length;
  const lo = new Uint8Array(n), hi = new Uint8Array(n);
  const close = (p, q) => Math.abs(p - q) <= 1e-8 + 1e-5 * Math.abs(q);
  for (let i = 0; i < n; i++) {
    lo[i] = close(y[i], lb[i]) ? 1 : 0;
    hi[i] = !lo[i] && close(y[i], ub[i]) ? 1 : 0;
  }
  for (let it = 0; it < 1000; it++) {
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
    const g = bandMul(h0, h1, h2, out);
    for (let i = 0; i < n; i++) g[i] += f[i];
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

  // Bounds, and which support sets each bound: -1 profile, 0..3 roller.
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
  const xm = rollers[3] / 2;
  let sumFy = 0, endF = 0;
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
    if (owner >= 0) {
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
    archTop, archAt, archMid: y[iMid],
    // Force ON THE ROLLER is minus the force on the strip.
    rollerForces: supports.map((s) => ({ fx: -s.fx, fy: -s.fy })),
    profileForces: profileF.map((f) => -f),
    sumFy, endF,
    layout: { rho, lift, rollers, centres },
  };
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
    out.push({ T, extra: s.extra, archTop: s.archTop, archMid: s.archMid,
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
