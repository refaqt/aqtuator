// Motion controller against a milling force: a stage, a discrete controller
// at the loop rate, and a sine cutting force with a mean. Three cases:
//
//   "linear"     linear motor. One rigid mass, the stage.
//   "colloc"     BLDC motor, coupling, ball screw, stage. The controller reads
//                the rotary encoder on the motor (collocated).
//   "noncolloc"  the same mechanics. The controller reads a linear encoder on
//                the stage (non-collocated).
//
// Units inside this file: SI (m, N, s, Hz, kg). The page converts to µm.
//
// The loop (reference is zero, so the controller only fights the force):
//
//   F_d (on the stage) ───────────┐
//                                 v
//   0 ─(+)─ C(z) ─ ZOH ── u ──> plant ─┬─ stage position y_s
//       ^-                             └─ measured position y_m
//       └──────── sample at fs ────────────┘
//
// With y_m = G_mu·u + G_md·F_d and y_s = G_su·u + G_sd·F_d, and u = −C·y_m:
//
//   U / F_d   = −C·G_md / (1 + C·G_mu)                 (controller force)
//   Y_s / F_d = G_sd − G_su·C·G_md / (1 + C·G_mu)      (compliance)
//
// For the linear motor all four are the same G, so Y/F_d = G/(1 + C·G).
//
// Ball screw in linear coordinates, r = pitch/(2π) in m/rad. Three masses
// in a chain, joined by two springs:
//
//   m1 ──k_c── m_s ──k_a── m
//
//   motor     m1  = J_rotor / r²        motor force u = torque / r
//   screw     m_s = J_screw / r²        J_screw = π·ρ·L·d⁴/32, steel
//   stage     m                          cutting force F_d
//   coupling  k_c = k_coupling / r²     (torsion, seen along the axis)
//   axial     1/k_a = 1/k_shaft + 1/k_nut + 1/k_bearing
//             k_shaft = E·π·d_root²/4 / x_nut   (fixed bearing at the motor
//             end, supported far end: the shaft between the fixed bearing
//             and the nut carries the load)
//
// Each spring has a damper, c = 2·ζ·√(k·μ), with μ the two masses on either
// side of it (the rest of the chain added to the near side). That ratio is
// exact for its mode when the other spring is rigid.
//
//   m1·x1'' = u − k_c·(x1 − xs) − c_c·(x1' − xs')
//   m_s·xs'' = k_c·(x1 − xs) + c_c·(x1' − xs') − k_a·(xs − x) − c_a·(xs' − x')
//   m·x''   = F_d + k_a·(xs − x) + c_a·(xs' − x')
//
// The screw does not twist, and there is no backlash and no friction.
//
// The plant is a state space. The hold is exact: Φ = e^{AT} and Γ come from
// one matrix exponential. G(z) = c·(zI − Φ)⁻¹·Γ. For one mass this is
// T² (z + 1) / (2 m (z − 1)²), the formula in plantAt.
//
// Controller, continuous time:
//
//   C(s) = K · 1/s · (s + ωi)(s + ωd) / (s + ωlp)²
//   ωi = 2π f_b/10,  ωd = 2π f_b/3,  ωlp = 2π · 4 f_b
//
// It is cut into three first-order sections, and each one is translated to
// discrete time with the bilinear (Tustin) rule s = (2/T)(z − 1)/(z + 1):
//
//   1/s                  ->  (T/2)(z + 1)/(z − 1)
//   (s + a)/(s + b)      ->  ((c + a) z + (a − c)) / ((c + b) z + (b − c)),  c = 2/T
//
// Each section runs as the difference equation
//
//   out[k] = b0 · in[k] + b1 · in[k−1] − a1 · out[k−1]
//
// K is set so that |C·G_mu| = 1 at f_b. f_b is the highest bandwidth where
// the loop meets four robustness rules: peak sensitivity |1/(1 + C·G)| at
// most 6 dB, phase margin at least 30°, gain margin at least 6 dB, and a
// stable closed loop. The rules must hold on a family of plants: each
// resonance moved ±15 % in frequency, with the same controller. Each case is
// tuned on its own plant with these rules.

const DEFAULTS = {
  Famp: 50,        // N, amplitude (peak) of the sine part of the cutting force
  Fmean: 50,       // N, mean cutting force
  teeth: 2,        // number of teeth on the cutter
  rpm: 12000,      // spindle speed, rev/min
  m: 2,            // kg, moving mass of the stage
  fs: 10000,       // Hz, controller loop rate
  pm: 30,          // degrees, target phase margin
  pitch: 5,        // mm per revolution, ball-screw pitch
  kc: 450,         // N·m/rad, coupling stiffness
  d: 16,           // mm, ball-screw diameter (sets the screw inertia)
  L: 400,          // mm, ball-screw length
  Jr: 119,         // g·cm², rotor inertia of the BLDC motor
  zeta: 0.02,      // damping ratio of the coupling, metal bellows or disc: an estimate, 0.01 to 0.03
  droot: 13.324,   // mm, screw root diameter, HIWIN 16-5
  xnut: 380,       // mm, nut distance from the fixed bearing
  knut: 118,       // N/µm, nut, HIWIN 16-5T4: 12 kgf/µm at 30 % of C, no preload
  kbear: 104,      // N/µm, fixed support BK12, TBI Motion: 10.6 kgf/µm
  zetaA: 0.02,     // damping ratio of the axial spring (shaft, nut, bearing): an estimate, 0.01 to 0.05
  msDb: 6,         // dB, highest allowed peak of the sensitivity |1/(1 + C·G)|
  gmMinDb: 6,      // dB, lowest allowed gain margin
  spread: 0.15,    // ± share by which each resonance frequency may move
};

const CASES = ["linear", "colloc", "noncolloc"];
const STEEL = 7850;       // kg/m³
const E_STEEL = 2.06e11;  // Pa, 2.1·10⁴ kgf/mm² as in the TBI Motion catalogue

// ---------------------------------------------------------------------------
// Complex numbers as [re, im].
// ---------------------------------------------------------------------------

const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const cdiv = (a, b) => {
  const d = b[0] * b[0] + b[1] * b[1];
  return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
};
const cadd = (a, b) => [a[0] + b[0], a[1] + b[1]];
const csub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const cabs = (a) => Math.hypot(a[0], a[1]);
const carg = (a) => Math.atan2(a[1], a[0]);

// Solve M·x = b for complex M (n × n) and b (n). Gauss with row pivots.
function csolve(M, b) {
  const n = b.length;
  const A = M.map((row, i) => [...row.map((v) => [...v]), [...b[i]]]);
  for (let c = 0; c < n; c++) {
    let piv = c;
    for (let r = c + 1; r < n; r++) if (cabs(A[r][c]) > cabs(A[piv][c])) piv = r;
    [A[c], A[piv]] = [A[piv], A[c]];
    for (let r = c + 1; r < n; r++) {
      const f = cdiv(A[r][c], A[c][c]);
      for (let k = c; k <= n; k++) A[r][k] = csub(A[r][k], cmul(f, A[c][k]));
    }
  }
  const x = new Array(n);
  for (let r = n - 1; r >= 0; r--) {
    let s = A[r][n];
    for (let k = r + 1; k < n; k++) s = csub(s, cmul(A[r][k], x[k]));
    x[r] = cdiv(s, A[r][r]);
  }
  return x;
}

// Solve M·x = a and M·x = b at once, for real a and b. Used for the plant
// responses, so it is kept lean.
function csolve2(M, a, b) {
  const n = a.length;
  const re = M.map((row) => row.map((v) => v[0])), im = M.map((row) => row.map((v) => v[1]));
  const r = [a.map((v) => [v, 0]), b.map((v) => [v, 0])];
  for (let c = 0; c < n; c++) {
    let piv = c;
    for (let i = c + 1; i < n; i++) if (Math.hypot(re[i][c], im[i][c]) > Math.hypot(re[piv][c], im[piv][c])) piv = i;
    for (const A of [re, im, r[0], r[1]]) [A[c], A[piv]] = [A[piv], A[c]];
    const pr = re[c][c], pi = im[c][c], pd = pr * pr + pi * pi;
    for (let i = c + 1; i < n; i++) {
      const fr = (re[i][c] * pr + im[i][c] * pi) / pd, fi = (im[i][c] * pr - re[i][c] * pi) / pd;
      for (let k = c; k < n; k++) {
        const xr = re[c][k], xi = im[c][k];
        re[i][k] -= fr * xr - fi * xi;
        im[i][k] -= fr * xi + fi * xr;
      }
      for (const R of r) R[i] = [R[i][0] - (fr * R[c][0] - fi * R[c][1]), R[i][1] - (fr * R[c][1] + fi * R[c][0])];
    }
  }
  return r.map((R) => {
    const x = new Array(n);
    for (let i = n - 1; i >= 0; i--) {
      let s = R[i];
      for (let k = i + 1; k < n; k++) s = csub(s, cmul([re[i][k], im[i][k]], x[k]));
      x[i] = cdiv(s, [re[i][i], im[i][i]]);
    }
    return x;
  });
}

// ---------------------------------------------------------------------------
// Real matrices as arrays of rows.
// ---------------------------------------------------------------------------

const zeros = (n, m = n) => Array.from({ length: n }, () => new Array(m).fill(0));
const eye = (n) => zeros(n).map((row, i) => { row[i] = 1; return row; });
function matmul(A, B) {
  const n = A.length, m = B[0].length, q = B.length;
  const C = zeros(n, m);
  for (let i = 0; i < n; i++) for (let k = 0; k < q; k++) {
    const a = A[i][k];
    if (a !== 0) for (let j = 0; j < m; j++) C[i][j] += a * B[k][j];
  }
  return C;
}
const norm1 = (A) => Math.max(...A[0].map((_, j) => A.reduce((s, row) => s + Math.abs(row[j]), 0)));

// e^A by scaling and squaring, with a Taylor series on A/2^s, |A/2^s| ≤ 0.5.
function expm(A) {
  const n = A.length;
  const s = Math.max(0, Math.ceil(Math.log2(norm1(A) || 1)) + 1);
  const As = A.map((row) => row.map((v) => v / 2 ** s));
  let E = eye(n), term = eye(n);
  for (let k = 1; k <= 18; k++) {
    term = matmul(term, As).map((row) => row.map((v) => v / k));
    E = E.map((row, i) => row.map((v, j) => v + term[i][j]));
  }
  for (let i = 0; i < s; i++) E = matmul(E, E);
  return E;
}

// ---------------------------------------------------------------------------
// Mechanics and plants.
// ---------------------------------------------------------------------------

// The ball-screw drive in linear coordinates, with its mode frequencies.
// modes: the two natural frequencies of the chain (the third is the rigid
// motion). antis: the antiresonances the motor encoder sees, the natural
// frequencies of the screw and the stage while the motor stands still.
// sc and sa scale the coupling and the axial stiffness, for the plant family
// of the tuning. The dampers follow, so each ζ stays the same.
function mechanics(p, sc = 1, sa = 1) {
  const r = p.pitch / 1000 / (2 * Math.PI);
  const d = p.d / 1000, L = p.L / 1000;
  const Js = Math.PI * STEEL * L * d ** 4 / 32;
  const Jr = p.Jr * 1e-7;
  const m1 = Jr / r ** 2, ms = Js / r ** 2, m = p.m;
  const kc = sc * p.kc / r ** 2;
  const kShaft = E_STEEL * Math.PI * (p.droot / 1000) ** 2 / 4 / (p.xnut / 1000);
  const kNut = p.knut * 1e6, kBear = p.kbear * 1e6;
  const ka = sa / (1 / kShaft + 1 / kNut + 1 / kBear);
  const muC = m1 * (ms + m) / (m1 + ms + m), muA = (m1 + ms) * m / (m1 + ms + m);
  const cc = 2 * p.zeta * Math.sqrt(kc * muC), ca = 2 * p.zetaA * Math.sqrt(ka * muA);
  // Roots of ω⁴ − b·ω² + c = 0, as frequencies in Hz, low first.
  const roots = (b, c) => {
    const disc = Math.sqrt(Math.max(0, b * b / 4 - c));
    return [b / 2 - disc, b / 2 + disc].map((w2) => Math.sqrt(Math.max(0, w2)) / (2 * Math.PI));
  };
  const modes = roots(kc / m1 + kc / ms + ka / ms + ka / m, kc * ka * (m1 + ms + m) / (m1 * ms * m));
  const antis = roots(kc / ms + ka / ms + ka / m, kc * ka / (ms * m));
  return { r, Js, Jr, m1, ms, m, kc, kShaft, kNut, kBear, ka, cc, ca, modes, antis };
}

// Continuous plant of one case. Indices into the state:
//   im  motor position (the motor force works on it), iv its speed,
//   is  stage position, iy measured position.
function plantFor(p, id, sc = 1, sa = 1) {
  if (id === "linear") {
    return { id, n: 2, sc: 1, sa: 1, A: [[0, 1], [0, 0]], Bu: [0, 1 / p.m], Bd: [0, 1 / p.m],
      im: 0, iv: 1, is: 0, iy: 0 };
  }
  const q = mechanics(p, sc, sa);
  const { m1, ms, m, kc, ka, cc, ca } = q;
  return { id, n: 6, mech: q, sc, sa,
    A: [
      [0, 1, 0, 0, 0, 0],
      [-kc / m1, -cc / m1, kc / m1, cc / m1, 0, 0],
      [0, 0, 0, 1, 0, 0],
      [kc / ms, cc / ms, -(kc + ka) / ms, -(cc + ca) / ms, ka / ms, ca / ms],
      [0, 0, 0, 0, 0, 1],
      [0, 0, ka / m, ca / m, -ka / m, -ca / m],
    ],
    Bu: [0, 1 / m1, 0, 0, 0, 0], Bd: [0, 0, 0, 0, 0, 1 / m],
    im: 0, iv: 1, is: 4, iy: id === "colloc" ? 0 : 4 };
}

// Exact step of length h, with the controller force u and the mean force
// constant, and a sine force F_amp·sin(ω t) on the stage:
//
//   x(t0 + h) = Φ·x + Gu·u + Gf·F_mean + F_amp·(Ss·sin ω t0 + Sc·cos ω t0)
//
// One matrix exponential of the plant with the two inputs and a sine
// generator (s' = ω c, c' = −ω s) added as states.
function stepMatrices(pl, h, w = 0) {
  const n = pl.n, N = n + 4;
  const M = zeros(N);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) M[i][j] = pl.A[i][j] * h;
    M[i][n] = pl.Bu[i] * h;
    M[i][n + 1] = pl.Bd[i] * h;
    M[i][n + 2] = pl.Bd[i] * h;
  }
  M[n + 2][n + 3] = w * h;
  M[n + 3][n + 2] = -w * h;
  const E = expm(M);
  const col = (j) => E.slice(0, n).map((row) => row[j]);
  return { Phi: E.slice(0, n).map((row) => row.slice(0, n)), Gu: col(n), Gf: col(n + 1), Ss: col(n + 2), Sc: col(n + 3) };
}

// The plant with its hold, at the loop rate. Cached on the plant.
function discrete(pl, T) {
  if (!pl.disc || pl.disc.T !== T) {
    pl.disc = { T, ...stepMatrices(pl, T) };
    pl.memo = new Map();
  }
  return pl.disc;
}

// Plant with hold for one mass, as a formula. With z = e^{jθ}:
//   (z + 1)/(z − 1)² = −cos(θ/2) / (2 sin²(θ/2)) · e^{−jθ/2}
// so the phase is −π − θ/2 and the gain is T² cos(θ/2) / (4 m sin²(θ/2)).
// The checks compare the state-space plant with it.
function plantAt(f, p) {
  const T = 1 / p.fs, theta = 2 * Math.PI * f * T;
  const mag = T * T * Math.cos(theta / 2) / (4 * p.m * Math.sin(theta / 2) ** 2);
  const ph = -Math.PI - theta / 2;
  return { h: [mag * Math.cos(ph), mag * Math.sin(ph)], ph };
}

// The four discrete plant responses at f, complex:
//   mu: motor force to measured position, md: cutting force to measured,
//   su: motor force to stage position,    sd: cutting force to stage.
// The cutting force is treated as held too, like the motor force. This is
// close below about fs/4. The time simulation uses the true sine.
// The responses are kept per frequency: the tuning asks for the same
// frequencies many times while only the controller changes.
function plantResp(f, p, pl) {
  const T = 1 / p.fs, d = discrete(pl, T), n = pl.n;
  const hit = pl.memo.get(f);
  if (hit) return hit;
  if (pl.memo.size > 50000) pl.memo.clear();
  const th = 2 * Math.PI * f * T, z = [Math.cos(th), Math.sin(th)];
  const M = d.Phi.map((row, i) => row.map((v, j) => (i === j ? csub(z, [v, 0]) : [-v, 0])));
  const [xu, xd] = csolve2(M, d.Gu, d.Gf);
  const r = { mu: xu[pl.iy], md: xd[pl.iy], su: xu[pl.is], sd: xd[pl.is], n };
  pl.memo.set(f, r);
  return r;
}

// ---------------------------------------------------------------------------
// Controller sections.
// ---------------------------------------------------------------------------

function leadLag(a, b, T) {
  const c = 2 / T, d = c + b;
  return { b0: (c + a) / d, b1: (a - c) / d, a1: (b - c) / d };
}

// The three sections of C(z)/K for a given bandwidth f_b.
function sections(fb, T) {
  const w = 2 * Math.PI * fb;
  return [
    { b0: T / 2, b1: T / 2, a1: -1 },     // integrator
    leadLag(w / 10, 4 * w, T),            // (s + ωi)/(s + ωlp)
    leadLag(w / 3, 4 * w, T),             // (s + ωd)/(s + ωlp)
  ];
}

// Response of one section at z = e^{jθ}, with its phase. The phase of each
// factor b0 z + b1 is continuous in θ from 0 to π, so no unwrapping is needed.
function sectionAt(s, theta) {
  const z = [Math.cos(theta), Math.sin(theta)];
  const num = [s.b0 * z[0] + s.b1, s.b0 * z[1]];
  const den = [z[0] + s.a1, z[1]];
  return { h: cdiv(num, den), ph: Math.atan2(num[1], num[0]) - Math.atan2(den[1], den[0]) };
}

// Controller C(z), with gain K.
function controllerAt(f, p, tuned) {
  const T = 1 / p.fs, theta = 2 * Math.PI * f * T;
  let h = [tuned.K, 0], ph = 0;
  for (const s of tuned.sections) {
    const r = sectionAt(s, theta);
    h = cmul(h, r.h);
    ph += r.ph;
  }
  return { h, ph };
}

// ---------------------------------------------------------------------------
// Frequency responses. f in Hz, 0 < f < fs/2.
// ---------------------------------------------------------------------------

// Loop C·G_mu at f. The phases here are wrapped to (−π, π]. frequencyData
// unwraps them over its grid.
function loopAt(f, p, tuned) {
  const g = plantResp(f, p, tuned.plant), c = controllerAt(f, p, tuned);
  const h = cmul(g.mu, c.h);
  return { h, g, c };
}

// Compliance Y_s/F_d at the stage in m/N (complex).
function complianceAt(f, p, tuned) {
  const l = loopAt(f, p, tuned);
  const r = cdiv(cmul(l.c.h, l.g.md), cadd([1, 0], l.h));
  return csub(l.g.sd, cmul(l.g.su, r));
}

// Controller force per newton of cutting force, U/F_d = −C·G_md/(1 + C·G_mu)
// (complex, no unit). Well below f_b the controller takes the whole force,
// far above it the mass does.
function forceRatioAt(f, p, tuned) {
  const l = loopAt(f, p, tuned);
  const r = cdiv(cmul(l.c.h, l.g.md), cadd([1, 0], l.h));
  return [-r[0], -r[1]];
}

// Exact steady state at the samples under F_amp · e^{jωt} on the stage, for
// any ω that is not a multiple of fs/2, also above half the loop rate. Over
// one sample u is constant, and the plant integrates u and the sine exactly:
//
//   x[k+1] = Φ·x[k] + Gu·u[k] + F_amp·(Ss + j·Sc)·e^{jωkT},   u[k] = −C(z)·y_m[k]
//
// With x[k] = X·z^k and z = e^{jωT} this is one linear system in X. The
// controller works u[k]·(x_motor[k+1] − x_motor[k]) in each sample, so its
// mean power is ½·Re(U · conj(X_motor·(z − 1))) / T.
// Returns X (the stage position) in m, U in N (complex) and pMean in W.
function sampledSteadyAt(f, p, tuned) {
  const pl = tuned.plant, T = 1 / p.fs, w = 2 * Math.PI * f, n = pl.n;
  const s = stepMatrices(pl, T, w);
  const z = [Math.cos(w * T), Math.sin(w * T)];
  const C = controllerAt(f, p, tuned).h;
  const M = s.Phi.map((row, i) => row.map((v, j) => {
    let e = [-v, 0];
    if (i === j) e = cadd(e, z);
    if (j === pl.iy) e = cadd(e, cmul(C, [s.Gu[i], 0]));
    return e;
  }));
  const X = csolve(M, s.Ss.map((v, i) => [v * p.Famp, s.Sc[i] * p.Famp]));
  const U = cmul([-C[0], -C[1]], X[pl.iy]);
  const dX = cmul(X[pl.im], [z[0] - 1, z[1]]);
  const pMean = 0.5 * (U[0] * dX[0] + U[1] * dX[1]) / T;
  return { X: X[pl.is], U, pMean, n };
}

// Compliance at the samples for a true sine force F·e^{jωt} on the stage, in
// m/N (complex), for 0 < f < fs/2. The force is not held. Over one sample it
// adds
//
//   g = ∫₀ᵀ e^{A(T−τ)}·B_d·e^{jωτ} dτ = (jωI − A)⁻¹·(e^{jωT}·I − Φ)·B_d
//
// and with x[k] = X·z^k and u[k] = −C(z)·y_m[k]:
//
//   (z·I − Φ + Γ_u·C·e_m)·X = g,   compliance = X at the stage.
//
// It equals sampledSteadyAt, without a matrix exponential per frequency. The
// held force of complianceAt adds half a sample of lag, which moves the real
// part. The chatter limit needs the true phase, so it uses this one.
function sineComplianceAt(f, p, tuned) {
  const pl = tuned.plant, T = 1 / p.fs, d = discrete(pl, T), w = 2 * Math.PI * f;
  const z = [Math.cos(w * T), Math.sin(w * T)];
  const Mg = pl.A.map((row, i) => row.map((v, j) => (i === j ? [-v, w] : [-v, 0])));
  const rhs = d.Phi.map((row, i) => row.reduce((s, v, j) =>
    cadd(s, cmul(i === j ? [z[0] - v, z[1]] : [-v, 0], [pl.Bd[j], 0])), [0, 0]));
  const g = csolve(Mg, rhs);
  const C = controllerAt(f, p, tuned).h;
  const M = d.Phi.map((row, i) => row.map((v, j) => {
    let e = [-v, 0];
    if (i === j) e = cadd(e, z);
    if (j === pl.iy) e = cadd(e, cmul(C, [d.Gu[i], 0]));
    return e;
  }));
  return csolve(M, g)[pl.is];
}

// ---------------------------------------------------------------------------
// Chatter: the stability lobes and the depth that is stable at every speed.
// ---------------------------------------------------------------------------
//
// Regenerative chatter in one direction (Tlusty; Altintas, Manufacturing
// Automation, chapter on machine tool vibrations): the chip thickness holds
// the wave of the last tooth, so the loop is
//
//   1 + K·a·(1 − e^{−jωT})·G(jω) = 0,   T = 60/(teeth · rev/min)
//
// A real depth of cut a solves it only where Re G < 0:
//
//   a_lim = −1/(2·K·Re G(jω_c))
//   ω_c·T = ε + 2πk,  ε = 2·arg G − π  (taken in 0 to 2π),  k = 0, 1, 2 …
//
// Each k is one lobe. The lowest a_lim over all chatter frequencies is
// −1/(2·K·min Re G): below this depth the cut is stable at any speed. The
// cutting stiffness K, the factor 2 and, in milling, the directional factor
// are the same for every drive, so this file returns −1/Re G in N/m and the
// page divides by one reference drive.

// One point of lobe k at the chatter frequency f, for compliance g (Re g < 0).
// Returns the depth −1/Re g in N/m, the tooth period T in s and the rev/min.
function lobePoint(g, f, teeth, k) {
  let eps = 2 * carg(g) - Math.PI;
  eps -= 2 * Math.PI * Math.floor(eps / (2 * Math.PI));
  const T = (eps + 2 * Math.PI * k) / (2 * Math.PI * f);
  return { depth: -1 / g[0], T, rpm: 60 / (teeth * T), eps };
}

// Stability lobes for any compliance function comp(f) -> [re, im] in m/N.
// Scans f from fLo to fHi, then refines the lowest Re G. Returns the lower
// envelope of all lobes on an even rev/min grid (NaN where no lobe reaches),
// and the floor −1/min Re G. Depths in N/m.
function lobes(comp, fLo, fHi, teeth, rpmLo, rpmHi, nf = 3000, nr = 400) {
  const f = logspace(fLo, fHi, nf);
  const G = f.map(comp);
  let iMin = 0;
  for (let i = 1; i < nf; i++) if (G[i][0] < G[iMin][0]) iMin = i;
  // Golden section between the two neighbours of the lowest grid point.
  let a = f[Math.max(0, iMin - 1)], b = f[Math.min(nf - 1, iMin + 1)];
  const gr = (Math.sqrt(5) - 1) / 2;
  for (let it = 0; it < 40; it++) {
    const c = b - gr * (b - a), d = a + gr * (b - a);
    if (comp(c)[0] < comp(d)[0]) b = d; else a = c;
  }
  const fMin = (a + b) / 2, gMin = comp(fMin);
  const minRe = Math.min(gMin[0], G[iMin][0]);

  const rpm = Array.from({ length: nr }, (_, i) => rpmLo + (rpmHi - rpmLo) * i / (nr - 1));
  const env = new Array(nr).fill(Infinity);
  const dr = (rpmHi - rpmLo) / (nr - 1);
  const put = (A, B) => {
    const [lo, hi] = A.rpm < B.rpm ? [A, B] : [B, A];
    for (let i = Math.max(0, Math.ceil((lo.rpm - rpmLo) / dr)); i < nr && rpm[i] <= hi.rpm; i++) {
      const s = hi.rpm > lo.rpm ? (rpm[i] - lo.rpm) / (hi.rpm - lo.rpm) : 0;
      env[i] = Math.min(env[i], lo.depth + s * (hi.depth - lo.depth));
    }
  };
  // Join neighbouring frequencies of the same lobe with straight lines. Where
  // ε wraps past 0 or 2π the lobe number changes, so that step is skipped.
  let prev = null;
  for (let i = 0; i < nf; i++) {
    if (!(G[i][0] < 0)) { prev = null; continue; }
    const w = 2 * Math.PI * f[i];
    const eps = lobePoint(G[i], f[i], teeth, 0).eps;
    const kLo = Math.max(0, Math.ceil((w * 60 / (teeth * rpmHi) - eps) / (2 * Math.PI)) - 1);
    const kHi = Math.floor((w * 60 / (teeth * rpmLo) - eps) / (2 * Math.PI)) + 1;
    const pts = new Map();
    for (let k = kLo; k <= kHi; k++) pts.set(k, lobePoint(G[i], f[i], teeth, k));
    if (prev && Math.abs(eps - prev.eps) < Math.PI) {
      for (const [k, P] of pts) if (prev.pts.has(k)) put(prev.pts.get(k), P);
    }
    prev = { eps, pts };
  }
  return { rpm, depth: env.map((v) => (Number.isFinite(v) ? v : NaN)), floor: -1 / minRe, minRe, fMin };
}

// The chatter lobes of one tuned case, with the exact sine compliance, up to
// just below half the loop rate.
function chatter(p, tuned, rpmLo, rpmHi, nr = 800) {
  return lobes((f) => sineComplianceAt(f, p, tuned), tuned.fb / 200, p.fs / 2 * 0.98, p.teeth, rpmLo, rpmHi, 3000, nr);
}

// ---------------------------------------------------------------------------
// Tuning: find the highest f_b that meets the robustness rules.
// ---------------------------------------------------------------------------

const wrap = (a) => a - 2 * Math.PI * Math.round(a / (2 * Math.PI));

// The controller for a bandwidth f_b, with K set so that |C·G| = 1 there.
function controllerFor(fb, p, pl) {
  const secs = sections(fb, 1 / p.fs);
  const K = 1 / cabs(loopAt(fb, p, { K: 1, sections: secs, plant: pl }).h);
  return { plant: pl, fb, K, sections: secs };
}

// The plants the controller must work on: the nominal one, and for the ball
// screw the same drive with each resonance moved by ± spread in frequency.
// A frequency changes with √k, so the stiffness scales by (1 ± spread)².
// Coupling and axial spring move on their own: 3 × 3 = 9 plants.
function plantFamily(p, id) {
  const nominal = plantFor(p, id);
  const d = p.spread ?? 0.15;
  if (id === "linear" || !(d > 0)) return [nominal];
  const scales = [1, (1 - d) ** 2, (1 + d) ** 2];
  const out = [];
  for (const sc of scales) for (const sa of scales) out.push(sc === 1 && sa === 1 ? nominal : plantFor(p, id, sc, sa));
  return out;
}

// The rules every plant of the family must meet with one controller:
//   peak sensitivity  max |1/(1 + C·G)| ≤ msDb (6 dB, so the loop stays at
//                     least 0.5 away from −1 in any direction)
//   phase margin      ≥ pm (30°) at every gain crossover
//   gain margin       ≥ gmMinDb (6 dB) at every −180° crossing
//   stable            largest closed-loop pole |z| < 1
// fine: the fine frequency grid (1000 points, with dense bands around each
// resonance). Otherwise the coarse grid of the search,
// which also stops at the first broken rule.
// Returns ok, the worst value of each margin with the plant that gave it,
// and the list of broken rules.
function robustness(p, tuned, family, fine = true) {
  const msMax = 10 ** ((p.msDb ?? 6) / 20), pmMin = p.pm ?? 30, gmMin = 10 ** ((p.gmMinDb ?? 6) / 20);
  const w = { ms: 0, pmDeg: Infinity, gm: Infinity, rho: 0 };
  const broken = [];
  for (const pl of family) {
    const t = { ...tuned, plant: pl };
    const m = fine ? margins(p, t, 1000) : margins(p, t, 260, 16, p.fs * 1e-7);
    const rho = spectralRadius(p, t);
    const at = { sc: pl.sc, sa: pl.sa };
    if (m.ms > w.ms) Object.assign(w, { ms: m.ms, fMs: m.fMs, msAt: at });
    if (m.pmDeg < w.pmDeg) Object.assign(w, { pmDeg: m.pmDeg, fc: m.fc, pmAt: at });
    if (m.gm < w.gm) Object.assign(w, { gm: m.gm, f180: m.f180, gmAt: at });
    if (rho > w.rho) Object.assign(w, { rho, rhoAt: at });
    if (!(rho < 1)) broken.push({ rule: "unstable", ...at });
    else {
      if (!(m.ms <= msMax)) broken.push({ rule: "Ms", ...at });
      if (!(m.pmDeg >= pmMin)) broken.push({ rule: "PM", ...at });
      if (!(m.gm >= gmMin)) broken.push({ rule: "GM", ...at });
    }
    if (!fine && broken.length) break;
  }
  w.msDb = 20 * Math.log10(w.ms);
  w.gmDb = 20 * Math.log10(w.gm);
  return { ok: broken.length === 0, worst: w, broken };
}

// Tune for the rules above. Scan up from a slow f_b, take the first place
// where a rule breaks, and bisect there. Rules can hold again at a higher
// f_b, but such a loop would be fragile, so the search stops at the first
// break.
function tune(p, id = "linear") {
  const family = plantFamily(p, id), pl = family[0];
  const okAt = (fb) => robustness(p, controllerFor(fb, p, pl), family, false).ok;
  const grid = logspace(p.fs * 1e-4, p.fs * 0.2, 60);
  if (!okAt(grid[0])) throw new Error("the robustness rules are stricter than this controller can reach");
  let lo = NaN, hi = NaN;
  for (let i = 1; i < grid.length; i++) {
    if (!okAt(grid[i])) { lo = grid[i - 1]; hi = grid[i]; break; }
  }
  if (Number.isNaN(lo)) throw new Error("no bandwidth meets the robustness rules");
  for (let i = 0; i < 20; i++) {
    const mid = Math.sqrt(lo * hi);
    if (okAt(mid)) lo = mid; else hi = mid;
  }
  // The search used a coarse grid. If the fine one finds a broken rule, step
  // f_b down until it agrees, then bisect that last step on the fine grid.
  const fineAt = (f) => {
    const t = { id, ...controllerFor(f, p, pl) };
    return { t, rob: robustness(p, t, family, true) };
  };
  let fb = lo, cur = fineAt(fb), bad = NaN;
  for (let i = 0; i < 200 && !cur.rob.ok; i++) {
    bad = fb;
    fb *= 0.99;
    cur = fineAt(fb);
  }
  for (let i = 0; i < 4 && !Number.isNaN(bad) && cur.rob.ok; i++) {
    const mid = Math.sqrt(fb * bad), next = fineAt(mid);
    if (next.rob.ok) { fb = mid; cur = next; } else bad = mid;
  }
  const { t: tuned, rob } = cur;
  // The margins of the nominal plant, for the charts and the table.
  Object.assign(tuned, margins(p, tuned));
  tuned.rho = spectralRadius(p, tuned);
  tuned.stable = tuned.rho < 1;
  tuned.robust = rob.ok;
  tuned.worst = rob.worst;
  tuned.family = family.length;
  // What stops a faster loop: the rules that break 2 % above f_b.
  tuned.limit = robustness(p, controllerFor(fb * 1.02, p, pl), family, true).broken;
  return tuned;
}

// All gain crossovers and all −180° crossings up to fs/2. The phase margin
// is the worst one over the crossovers. The gain margin is the smallest one
// over the crossings where the loop gain is below 1. (Below f_b the phase is
// also under −180°, from the integrator, but there the gain is far above 1.)
// fc and f180 are where these worst values sit. ms is the peak of the
// sensitivity |1/(1 + C·G)|, at fMs: 1/ms is the closest the loop comes to −1.
// fLo sets the start of the grid. The tuning passes a fixed start, so every
// step of its search asks for the same frequencies.
function margins(p, tuned, nGrid = 2000, iters = 40, fLo = tuned.fb / 1000) {
  const nyq = p.fs / 2;
  const grid = logspace(fLo, nyq * 0.9999, nGrid);
  // A lightly damped resonance is a narrow peak, easy to step over. Add a
  // dense band around it, and around the place where it folds back below
  // half the loop rate when it sits above.
  const mech = tuned.plant.mech;
  if (mech) {
    // The motor encoder also sees the antiresonances. The stage encoder
    // does not.
    const peaks = tuned.plant.id === "colloc" ? [...mech.modes, ...mech.antis] : mech.modes;
    for (const f0 of peaks) {
      const fa = Math.abs(f0 - p.fs * Math.round(f0 / p.fs));
      for (const fc of f0 < nyq ? [f0] : [fa]) {
        if (fc > 0 && fc < nyq) grid.push(...logspace(fc * 0.8, Math.min(fc * 1.25, nyq * 0.9999), Math.max(30, Math.round(nGrid / 8))));
      }
    }
    grid.sort((a, b) => a - b);
  }
  const L = (f) => loopAt(f, p, tuned).h;
  const mag = (f) => cabs(L(f));
  const pmAt = (f) => wrap(Math.PI + carg(L(f)));
  const sens = (f) => 1 / cabs(cadd([1, 0], L(f)));
  const bisect = (fn, a, b) => {
    let fa = fn(a);
    for (let i = 0; i < iters; i++) {
      const c = Math.sqrt(a * b), fc = fn(c);
      if (Math.sign(fc) === Math.sign(fa)) { a = c; fa = fc; } else b = c;
    }
    return Math.sqrt(a * b);
  };
  let fc = NaN, pm = Infinity, f180 = NaN, gm = Infinity;
  const vals = grid.map((f) => L(f));
  let iMs = 0, ms = 0;
  for (let i = 0; i < grid.length; i++) {
    const s = 1 / cabs(cadd([1, 0], vals[i]));
    if (s > ms) { ms = s; iMs = i; }
  }
  for (let i = 1; i < grid.length; i++) {
    const a = vals[i - 1], b = vals[i];
    if ((cabs(a) - 1) * (cabs(b) - 1) < 0) {
      const f = bisect((x) => Math.log(mag(x)), grid[i - 1], grid[i]);
      const m = pmAt(f);
      if (m < pm) { pm = m; fc = f; }
    }
    // The loop crosses the negative real axis: Im changes sign with Re < 0.
    if (a[1] * b[1] < 0 && a[0] + b[0] < 0) {
      const f = bisect((x) => L(x)[1], grid[i - 1], grid[i]);
      const g = 1 / mag(f);
      if (g > 1 && g < gm) { gm = g; f180 = f; }
    }
  }
  // Refine the sensitivity peak between the grid neighbours: golden section
  // on log f.
  let a = Math.log(grid[Math.max(0, iMs - 1)]), b = Math.log(grid[Math.min(grid.length - 1, iMs + 1)]);
  const g = (Math.sqrt(5) - 1) / 2;
  let x1 = b - g * (b - a), x2 = a + g * (b - a), s1 = sens(Math.exp(x1)), s2 = sens(Math.exp(x2));
  for (let i = 0; i < iters; i++) {
    if (s1 > s2) { b = x2; x2 = x1; s2 = s1; x1 = b - g * (b - a); s1 = sens(Math.exp(x1)); }
    else { a = x1; x1 = x2; s1 = s2; x2 = a + g * (b - a); s2 = sens(Math.exp(x2)); }
  }
  let fMs = grid[iMs];
  if (Math.max(s1, s2) > ms) { ms = Math.max(s1, s2); fMs = Math.exp(s1 > s2 ? x1 : x2); }
  return { fc, pmDeg: pm * 180 / Math.PI, f180, gm, gmDb: 20 * Math.log10(gm), ms, msDb: 20 * Math.log10(ms), fMs };
}

// ---------------------------------------------------------------------------
// Closed loop at the samples, and its stability.
// ---------------------------------------------------------------------------

// One sample of the closed loop without the cutting force. The state is the
// plant state, then the input and output memory of each controller section.
function closedLoopStep(p, tuned, state) {
  const pl = tuned.plant, n = pl.n, d = discrete(pl, 1 / p.fs);
  const x = state.slice(0, n), next = new Array(state.length).fill(0);
  let s = x[pl.iy];
  tuned.sections.forEach((c, i) => {
    const out = c.b0 * s + c.b1 * state[n + 2 * i] - c.a1 * state[n + 2 * i + 1];
    next[n + 2 * i] = s;
    next[n + 2 * i + 1] = out;
    s = out;
  });
  const u = -tuned.K * s;
  for (let i = 0; i < n; i++) {
    let v = d.Gu[i] * u;
    for (let j = 0; j < n; j++) v += d.Phi[i][j] * x[j];
    next[i] = v;
  }
  return next;
}

// Spectral radius of the closed loop at the samples: the largest |pole|.
// Found as ‖A^N‖^(1/N) with N = 2^20, by squaring. Below 1: stable.
function spectralRadius(p, tuned) {
  const N = tuned.plant.n + 2 * tuned.sections.length;
  const cols = eye(N).map((e) => closedLoopStep(p, tuned, e));
  let A = zeros(N).map((row, i) => row.map((_, j) => cols[j][i]));
  let logScale = 0;
  const steps = 20;
  for (let i = 0; i < steps; i++) {
    const nrm = norm1(A);
    if (nrm === 0) return 0;
    A = A.map((row) => row.map((v) => v / nrm));
    logScale = 2 * (logScale + Math.log(nrm));
    A = matmul(A, A);
  }
  return Math.exp((logScale + Math.log(norm1(A) || 1e-300)) / 2 ** steps);
}

function logspace(a, b, n) {
  const la = Math.log10(a), lb = Math.log10(b);
  return Array.from({ length: n }, (_, i) => 10 ** (la + (lb - la) * i / (n - 1)));
}

const toothFreq = (p) => p.teeth * p.rpm / 60;

// Everything the frequency charts need, on one grid from fLo up to just
// below fs/2. Phases are unwrapped along the grid. The plant starts near
// −180°, like a mass.
function frequencyData(p, tuned, n = 600, fLo = tuned.fb / 200) {
  const f = logspace(fLo, p.fs / 2 * 0.98, n);
  let gPrev = -Math.PI;
  return f.map((fi) => {
    const l = loopAt(fi, p, tuned);
    let gph = carg(l.g.mu);
    gph += 2 * Math.PI * Math.round((gPrev - gph) / (2 * Math.PI));
    gPrev = gph;
    const r = cdiv(cmul(l.c.h, l.g.md), cadd([1, 0], l.h));
    const y = csub(l.g.sd, cmul(l.g.su, r));
    return {
      f: fi,
      G: cabs(l.g.mu), Gph: gph,
      C: cabs(l.c.h), Cph: l.c.ph,
      L: cabs(l.h), Lph: gph + l.c.ph,
      S: 1 / cabs(cadd([1, 0], l.h)),               // sensitivity, no unit
      Y: cabs(y),                                   // m/N
      mass: 1 / (p.m * (2 * Math.PI * fi) ** 2),    // m/N, the bare stage mass
    };
  });
}

// ---------------------------------------------------------------------------
// Time simulation. The plant moves in continuous time and is integrated
// exactly between samples. The controller runs at the loop rate.
// ---------------------------------------------------------------------------

// Step matrices for a step h at the tooth frequency, cached on the plant.
function stepCached(pl, h, w) {
  pl.steps ??= new Map();
  const key = `${h}|${w}`;
  if (!pl.steps.has(key)) {
    if (pl.steps.size > 8) pl.steps.clear();
    pl.steps.set(key, stepMatrices(pl, h, w));
  }
  return pl.steps.get(key);
}

// x ← one exact step from time t0. Writes into out.
function advance(S, x, u, Fmean, Famp, w, t0, out) {
  const n = x.length, sn = Famp * Math.sin(w * t0), cs = Famp * Math.cos(w * t0);
  for (let i = 0; i < n; i++) {
    let v = S.Gu[i] * u + S.Gf[i] * Fmean + S.Ss[i] * sn + S.Sc[i] * cs;
    const row = S.Phi[i];
    for (let j = 0; j < n; j++) v += row[j] * x[j];
    out[i] = v;
  }
  return out;
}

// Run the loop for a number of samples. The cutting force starts at t = 0.
//   record: 'all' keeps the stage position and the applied controller force
//           u at every sample, 'none' keeps nothing.
//   window: from this sample on, track min and max of the stage position,
//           also between samples (sub points per sample), min and max of u,
//           the peak of the controller power u·v, and the work u·Δx.
//           v and x are at the motor side, where u pushes.
//   fine:   keep [t, x_stage, u, v_motor] at the sub points of the window.
function simulate(p, tuned, opts = {}) {
  const pl = tuned.plant, n = pl.n, T = 1 / p.fs;
  const w = 2 * Math.PI * toothFreq(p);
  const Fmean = opts.Fmean ?? p.Fmean, Famp = opts.Famp ?? p.Famp;
  const N = opts.samples;
  const sub = opts.sub ?? 1;
  const from = opts.window ?? N;
  const full = stepCached(pl, T, w), part = stepCached(pl, T / sub, w);
  const secs = tuned.sections, K = tuned.K;
  const sin_ = secs.map(() => 0), sout = secs.map(() => 0);
  let x = new Array(n).fill(0), y = new Array(n).fill(0);
  let lo = Infinity, hi = -Infinity, peak = 0;
  let uLo = Infinity, uHi = -Infinity, uPeak = 0, pPeak = 0, work = 0;
  const xs = opts.record === "all" ? new Float64Array(N + 1) : null;
  const us = opts.record === "all" ? new Float64Array(N) : null;
  const fine = opts.fine ? [] : null;
  for (let k = 0; k < N; k++) {
    // Sample the position, run the controller: u = −K · C1 · C2 · C3 · y.
    let s = x[pl.iy];
    for (let i = 0; i < secs.length; i++) {
      const c = secs[i];
      const out = c.b0 * s + c.b1 * sin_[i] - c.a1 * sout[i];
      sin_[i] = s;
      sout[i] = out;
      s = out;
    }
    const u = -K * s;
    if (xs) { xs[k] = x[pl.is]; us[k] = u; }
    if (Math.abs(u) > uPeak) uPeak = Math.abs(u);
    const t0 = k * T, xm0 = x[pl.im];
    if (k >= from) {
      if (u < uLo) uLo = u;
      if (u > uHi) uHi = u;
      if (Math.abs(u * x[pl.iv]) > pPeak) pPeak = Math.abs(u * x[pl.iv]);
      if (x[pl.is] < lo) lo = x[pl.is];
      if (x[pl.is] > hi) hi = x[pl.is];
      // Step through the sample in sub parts: the stage moves on between
      // samples and the peak can fall there. u stays constant, but the speed
      // changes, so the power does too.
      for (let j = 1; j <= sub; j++) {
        advance(part, x, u, Fmean, Famp, w, t0 + T * (j - 1) / sub, y);
        [x, y] = [y, x];
        const xj = x[pl.is], vj = x[pl.iv];
        if (xj < lo) lo = xj;
        if (xj > hi) hi = xj;
        if (Math.abs(u * vj) > pPeak) pPeak = Math.abs(u * vj);
        if (fine) fine.push([t0 + T * j / sub, xj, u, vj]);
      }
      // u is constant over the sample, so its work is exactly u · Δx.
      work += u * (x[pl.im] - xm0);
    } else {
      advance(full, x, u, Fmean, Famp, w, t0, y);
      [x, y] = [y, x];
    }
    if (!Number.isFinite(x[pl.is])) break;
    if (Math.abs(x[pl.is]) > peak) peak = Math.abs(x[pl.is]);
  }
  if (xs) xs[N] = x[pl.is];
  const tWin = Math.max(0, N - from) * T;
  return { xs, us, fine, lo, hi, amp: (hi - lo) / 2, peak, T,
    uAmp: (uHi - uLo) / 2, uPeak, pPeak, pMean: tWin > 0 ? work / tWin : NaN };
}

// Samples until the start transient has died out. The slowest closed-loop pole
// sits near the integrator frequency f_b/10. A lightly damped resonance can
// be slower, so the largest pole |z| = ρ also sets a floor. Capped at 2 s.
function settleSamples(p, tuned) {
  const byFb = Math.ceil(15 / (tuned.fb / 10) * p.fs);
  const byRho = tuned.rho > 0 && tuned.rho < 1 ? Math.ceil(Math.log(1e-5) / Math.log(tuned.rho)) : 0;
  return Math.min(Math.max(byFb, byRho), Math.ceil(2 * p.fs));
}

// The steady state under the sine part of the force alone. The mean force
// only moves the stage during the start transient: the integrator takes it
// back to zero. The window is a whole number of tooth periods, so the mean
// power is not biased by a part period. Returns, in SI units:
//   amp    vibration amplitude of the stage (half of peak to peak), m
//   uAmp   controller force amplitude (half of peak to peak), N
//   pPeak  peak controller power |u·v|, W
//   pMean  mean controller power, W. Negative: the controller takes energy
//          out. In the steady state it takes out exactly what the cutting
//          force puts in.
function steadyState(p, tuned) {
  const ft = toothFreq(p);
  const settle = settleSamples(p, tuned);
  const periods = Math.min(200, Math.max(3, Math.ceil(ft * 0.02)));  // at least 3 periods
  const win = Math.max(8, Math.round(periods / ft * p.fs));
  const sub = Math.min(64, Math.max(4, Math.ceil(8 * ft / p.fs)));
  const r = simulate(p, tuned, { samples: settle + win, window: settle, sub, Fmean: 0 });
  return { amp: r.amp, uAmp: r.uAmp, pPeak: r.pPeak, pMean: r.pMean };
}

// Steady-state amplitude of the vibration (half of peak to peak), in m.
const steadyAmplitude = (p, tuned) => steadyState(p, tuned).amp;

// Samples in the start trace: a third of the settle time from f_b.
const entrySamples = (p, tuned) => Math.ceil(Math.ceil(15 / (tuned.fb / 10) * p.fs) / 3);

// The start of the cut: mean plus sine from t = 0, as a trace.
function entryTrace(p, tuned, n = entrySamples(p, tuned)) {
  return simulate(p, tuned, { samples: n, record: "all" });
}

// A few periods of the steady state, with points between the samples.
function steadyTrace(p, tuned, periods = 4) {
  const ft = toothFreq(p);
  const settle = settleSamples(p, tuned);
  const win = Math.max(8, Math.ceil(periods / ft * p.fs));
  const sub = Math.min(64, Math.max(4, Math.ceil(24 * ft / p.fs)));
  const r = simulate(p, tuned, { samples: settle + win, window: settle, sub, fine: true });
  const t0 = settle / p.fs;
  return { points: r.fine.map(([t, x, u, v]) => [t - t0, x, u, v]), sub, amp: r.amp, mid: (r.hi + r.lo) / 2,
    uAmp: r.uAmp, pPeak: r.pPeak, pMean: r.pMean, t0 };
}

// The steady state against spindle speed. amp in m, uAmp in N, powers in W,
// ratio = uAmp / Famp in N/N. tf is |U/F_d| from the discrete transfer
// function (NaN from half the loop rate on). mass is the stage mass alone.
function sweep(p, tuned, rpmLo, rpmHi, n = 120) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const rpm = rpmLo + (rpmHi - rpmLo) * i / (n - 1);
    const q = { ...p, rpm };
    const ft = toothFreq(q);
    const st = steadyState(q, tuned);
    out.push({ rpm, f: ft, ...st, ratio: st.uAmp / p.Famp,
      tf: ft < p.fs / 2 ? cabs(forceRatioAt(ft, q, tuned)) : NaN,
      mass: p.Famp / (p.m * (2 * Math.PI * ft) ** 2) });
  }
  return out;
}

// A plain script, not a module. Browsers refuse to load a module for a page
// opened straight from disk (file://), so the page would never calculate.
// The page and the checks both read the functions from this one object.
globalThis.ControlModel = {
  DEFAULTS, CASES, cabs, expm, mechanics, plantFor, stepMatrices, plantResp, sections, plantAt,
  controllerAt, loopAt, complianceAt, forceRatioAt, sampledSteadyAt, sineComplianceAt, lobePoint, lobes, chatter, tune, margins, spectralRadius,
  plantFamily, robustness,
  logspace, toothFreq, frequencyData, simulate, settleSamples, steadyState, steadyAmplitude,
  entrySamples, entryTrace, steadyTrace, sweep,
};
