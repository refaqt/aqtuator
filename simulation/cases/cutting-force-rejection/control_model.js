// Motion controller against a milling force: a moving mass, a discrete
// controller at the loop rate, and a sine cutting force with a mean.
//
// Units inside this file: SI (m, N, s, Hz, kg). The page converts to µm.
//
// The loop (reference is zero, so the controller only fights the force):
//
//   F_d ──────────────┐
//                     v
//   0 ─(+)─ C(z) ─ ZOH ─(+)─ G(s) = 1/(m s²) ─┬─ y
//       ^-                                      │
//       └──────────── sample at fs ────────────┘
//
//   Y / F_d = G_zoh(z) / (1 + G_zoh(z) · C(z))     (compliance)
//
// Plant with a zero-order hold (the controller force stays constant for one
// sample). This already holds the half-sample lag of the hold:
//
//   G_zoh(z) = T² (z + 1) / (2 m (z − 1)²)
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
// K is set so that |C·G| = 1 at f_b. f_b is set so that the phase margin is
// the target (30°). An optional extra one-sample computation delay z⁻¹ can be
// switched on. It is not the hold lag: that one is already inside G_zoh.

const DEFAULTS = {
  Famp: 50,        // N, amplitude (peak) of the sine part of the cutting force
  Fmean: 50,       // N, mean cutting force
  teeth: 2,        // number of teeth on the cutter
  rpm: 12000,      // spindle speed, rev/min
  m: 2,            // kg, moving mass of the stage
  fs: 10000,       // Hz, controller loop rate
  delay: false,    // extra one-sample computation delay
  pm: 30,          // degrees, target phase margin
};

// ---------------------------------------------------------------------------
// Complex numbers as [re, im].
// ---------------------------------------------------------------------------

const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const cdiv = (a, b) => {
  const d = b[0] * b[0] + b[1] * b[1];
  return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
};
const cadd = (a, b) => [a[0] + b[0], a[1] + b[1]];
const cabs = (a) => Math.hypot(a[0], a[1]);

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

// ---------------------------------------------------------------------------
// Frequency responses. f in Hz, 0 < f < fs/2. Phases in radians, unwrapped.
// ---------------------------------------------------------------------------

// Plant with hold. With z = e^{jθ}:
//   (z + 1)/(z − 1)² = −cos(θ/2) / (2 sin²(θ/2)) · e^{−jθ/2}
// so the phase is −π − θ/2 and the gain is T² cos(θ/2) / (4 m sin²(θ/2)).
function plantAt(f, p) {
  const T = 1 / p.fs, theta = 2 * Math.PI * f * T;
  const mag = T * T * Math.cos(theta / 2) / (4 * p.m * Math.sin(theta / 2) ** 2);
  const ph = -Math.PI - theta / 2;
  return { h: [mag * Math.cos(ph), mag * Math.sin(ph)], ph };
}

// Controller C(z), with gain K and the optional delay.
function controllerAt(f, p, tuned) {
  const T = 1 / p.fs, theta = 2 * Math.PI * f * T;
  let h = [tuned.K, 0], ph = 0;
  for (const s of tuned.sections) {
    const r = sectionAt(s, theta);
    h = cmul(h, r.h);
    ph += r.ph;
  }
  if (p.delay) {
    h = cmul(h, [Math.cos(theta), -Math.sin(theta)]);
    ph -= theta;
  }
  return { h, ph };
}

function loopAt(f, p, tuned) {
  const g = plantAt(f, p), c = controllerAt(f, p, tuned);
  return { h: cmul(g.h, c.h), ph: g.ph + c.ph, g, c };
}

// Compliance Y/F_d in m/N (complex).
function complianceAt(f, p, tuned) {
  const l = loopAt(f, p, tuned);
  return cdiv(l.g.h, cadd([1, 0], l.h));
}

// Controller force per newton of cutting force, U/F_d = −C·G/(1 + C·G)
// (complex, no unit). Well below f_b the controller takes the whole force,
// far above it the mass does.
function forceRatioAt(f, p, tuned) {
  const l = loopAt(f, p, tuned);
  const r = cdiv(l.h, cadd([1, 0], l.h));
  return [-r[0], -r[1]];
}

// Exact steady state at the samples under F_amp · e^{jωt}, for any ω that is
// not a multiple of fs/2, also above half the loop rate. Over one sample the
// controller force u is constant, and the mass integrates u and the sine:
//
//   x[k+1] = x[k] + T·v[k] + T²/(2m)·u[k] + Dx·e^{jωkT}
//   v[k+1] = v[k] + T/m·u[k]             + Dv·e^{jωkT}
//   u[k]   = −C(z)·x[k]
//
// With x[k] = X·z^k, v[k] = V·z^k, u[k] = U·z^k and z = e^{jωT} this is a
// 2 × 2 linear system in X and V. The controller works u[k]·(x[k+1] − x[k])
// in each sample, so its mean power is ½·Re(U · conj(X·(z − 1))) / T.
// Returns X in m, V in m/s, U in N (complex) and pMean in W.
function sampledSteadyAt(f, p, tuned) {
  const T = 1 / p.fs, m = p.m, w = 2 * Math.PI * f;
  const z = [Math.cos(w * T), Math.sin(w * T)];
  const zm1 = [z[0] - 1, z[1]];
  const jw = [0, w];
  const F = [p.Famp / m, 0];
  const Dv = cmul(F, cdiv(zm1, jw));
  const Dx = cmul(F, cadd(cdiv(zm1, cmul(jw, jw)), cdiv([-T, 0], jw)));
  const C = controllerAt(f, p, tuned).h;
  // (z − 1 + C·T²/(2m))·X − T·V = Dx   and   (C·T/m)·X + (z − 1)·V = Dv
  const a11 = cadd(zm1, cmul(C, [T * T / (2 * m), 0])), a12 = [-T, 0];
  const a21 = cmul(C, [T / m, 0]), a22 = zm1;
  const det = cadd(cmul(a11, a22), cmul([-a12[0], -a12[1]], a21));
  const X = cdiv(cadd(cmul(Dx, a22), cmul([-a12[0], -a12[1]], Dv)), det);
  const V = cdiv(cadd(cmul(a11, Dv), cmul([-a21[0], -a21[1]], Dx)), det);
  const U = cmul([-C[0], -C[1]], X);
  const dX = cmul(X, zm1);
  const pMean = 0.5 * (U[0] * dX[0] + U[1] * dX[1]) / T;
  return { X, V, U, pMean };
}

// ---------------------------------------------------------------------------
// Tuning: find f_b for the target phase margin.
// ---------------------------------------------------------------------------

// Loop gain and phase at f_b with K = 1.
function loopAtFb(fb, p) {
  const t = { K: 1, sections: sections(fb, 1 / p.fs) };
  return loopAt(fb, p, t);
}

function tune(p) {
  const pmTarget = (p.pm ?? 30) * Math.PI / 180;
  const pmOf = (fb) => Math.PI + loopAtFb(fb, p).ph;
  // The phase margin falls as f_b rises, from about 38° at a slow f_b.
  let lo = p.fs * 1e-5, hi = p.fs * 0.2;
  if (pmOf(lo) < pmTarget) throw new Error("the phase margin target is above what this controller can reach");
  for (let i = 0; i < 100; i++) {
    const mid = Math.sqrt(lo * hi);
    if (pmOf(mid) > pmTarget) lo = mid; else hi = mid;
  }
  const fb = Math.sqrt(lo * hi);
  const secs = sections(fb, 1 / p.fs);
  const K = 1 / cabs(loopAtFb(fb, p).h);
  const tuned = { fb, K, sections: secs };
  return { ...tuned, ...margins(p, tuned) };
}

// Phase margin at the gain crossover, gain margin where the phase passes −180°.
function margins(p, tuned) {
  const nyq = p.fs / 2;
  const grid = logspace(tuned.fb / 1000, nyq * 0.9999, 2000);
  const mag = (f) => cabs(loopAt(f, p, tuned).h);
  const ph = (f) => loopAt(f, p, tuned).ph;
  const bisect = (fn, a, b) => {
    let fa = fn(a);
    for (let i = 0; i < 80; i++) {
      const c = Math.sqrt(a * b), fc = fn(c);
      if (Math.sign(fc) === Math.sign(fa)) { a = c; fa = fc; } else b = c;
    }
    return Math.sqrt(a * b);
  };
  let fc = NaN, f180 = NaN;
  for (let i = 1; i < grid.length; i++) {
    if (Number.isNaN(fc) && mag(grid[i - 1]) >= 1 && mag(grid[i]) < 1) {
      fc = bisect((f) => Math.log(mag(f)), grid[i - 1], grid[i]);
    }
    if (Number.isNaN(f180) && ph(grid[i - 1]) > -Math.PI && ph(grid[i]) <= -Math.PI) {
      f180 = bisect((f) => ph(f) + Math.PI, grid[i - 1], grid[i]);
    }
  }
  const pm = (Math.PI + ph(fc)) * 180 / Math.PI;
  const gm = Number.isNaN(f180) ? Infinity : 1 / mag(f180);
  return { fc, pmDeg: pm, f180, gm, gmDb: 20 * Math.log10(gm) };
}

function logspace(a, b, n) {
  const la = Math.log10(a), lb = Math.log10(b);
  return Array.from({ length: n }, (_, i) => 10 ** (la + (lb - la) * i / (n - 1)));
}

const toothFreq = (p) => p.teeth * p.rpm / 60;

// Everything the frequency charts need, on one grid up to just below fs/2.
function frequencyData(p, tuned, n = 600) {
  const f = logspace(tuned.fb / 200, p.fs / 2 * 0.98, n);
  const rows = f.map((fi) => {
    const l = loopAt(fi, p, tuned);
    const y = cdiv(l.g.h, cadd([1, 0], l.h));
    return {
      f: fi,
      G: cabs(l.g.h), Gph: l.g.ph,
      C: cabs(l.c.h), Cph: l.c.ph,
      L: cabs(l.h), Lph: l.ph,
      Y: cabs(y),                                   // m/N
      mass: 1 / (p.m * (2 * Math.PI * fi) ** 2),    // m/N, the bare mass
    };
  });
  return rows;
}

// ---------------------------------------------------------------------------
// Time simulation. The mass moves in continuous time and is integrated exactly
// between samples. The controller runs at the loop rate.
// ---------------------------------------------------------------------------

// Move the mass from time t0 over a step h, under a constant force P plus
// Famp · sin(ω t). Exact for this force.
function advance(x, v, P, Famp, w, t0, h, m) {
  let dx = v * h + P * h * h / (2 * m);
  let dv = P * h / m;
  if (Famp !== 0 && w > 0) {
    const t1 = t0 + h, k = Famp / (m * w);
    dv += k * (Math.cos(w * t0) - Math.cos(w * t1));
    dx += k * (Math.cos(w * t0) * h - (Math.sin(w * t1) - Math.sin(w * t0)) / w);
  }
  return [x + dx, v + dv];
}

// Run the loop for a number of samples. The cutting force starts at t = 0.
//   record: 'all' keeps x and the applied controller force u at every sample,
//           'none' keeps nothing.
//   window: from this sample on, track min and max of x, also between
//           samples (sub points per sample), min and max of u, the peak of
//           the controller power u·v, and the work u·Δx the controller does.
//   fine:   keep [t, x, u, v] at the sub points of the window.
function simulate(p, tuned, opts = {}) {
  const T = 1 / p.fs, m = p.m;
  const w = 2 * Math.PI * toothFreq(p);
  const Fmean = opts.Fmean ?? p.Fmean, Famp = opts.Famp ?? p.Famp;
  const n = opts.samples;
  const sub = opts.sub ?? 1;
  const from = opts.window ?? n;
  const secs = tuned.sections, K = tuned.K;
  const sin_ = secs.map(() => 0), sout = secs.map(() => 0);
  let x = 0, v = 0, uPrev = 0;
  let lo = Infinity, hi = -Infinity, peak = 0;
  let uLo = Infinity, uHi = -Infinity, uPeak = 0, pPeak = 0, work = 0;
  const xs = opts.record === "all" ? new Float64Array(n + 1) : null;
  const us = opts.record === "all" ? new Float64Array(n) : null;
  const fine = opts.fine ? [] : null;
  for (let k = 0; k < n; k++) {
    // Sample the position, run the controller: u = −K · C1 · C2 · C3 · y.
    let s = x;
    for (let i = 0; i < secs.length; i++) {
      const c = secs[i];
      const out = c.b0 * s + c.b1 * sin_[i] - c.a1 * sout[i];
      sin_[i] = s;
      sout[i] = out;
      s = out;
    }
    const uNow = -K * s;
    const u = p.delay ? uPrev : uNow;
    uPrev = uNow;
    if (xs) { xs[k] = x; us[k] = u; }
    if (Math.abs(u) > uPeak) uPeak = Math.abs(u);
    const t0 = k * T, P = u + Fmean;
    if (k >= from) {
      if (u < uLo) uLo = u;
      if (u > uHi) uHi = u;
      if (Math.abs(u * v) > pPeak) pPeak = Math.abs(u * v);
      // Also look between samples: the mass moves on, the peak can fall there.
      // u stays constant, but the speed v changes, so the power does too.
      for (let j = 1; j <= sub; j++) {
        const [xj, vj] = advance(x, v, P, Famp, w, t0, T * j / sub, m);
        if (xj < lo) lo = xj;
        if (xj > hi) hi = xj;
        if (Math.abs(u * vj) > pPeak) pPeak = Math.abs(u * vj);
        if (fine) fine.push([t0 + T * j / sub, xj, u, vj]);
      }
      if (x < lo) lo = x;
      if (x > hi) hi = x;
    }
    const xOld = x;
    [x, v] = advance(x, v, P, Famp, w, t0, T, m);
    // u is constant over the sample, so its work is exactly u · Δx.
    if (k >= from) work += u * (x - xOld);
    if (Math.abs(x) > peak) peak = Math.abs(x);
  }
  if (xs) xs[n] = x;
  const tWin = Math.max(0, n - from) * T;
  return { xs, us, fine, lo, hi, amp: (hi - lo) / 2, peak, T,
    uAmp: (uHi - uLo) / 2, uPeak, pPeak, pMean: tWin > 0 ? work / tWin : NaN };
}

// Samples until the start transient has died out. The slowest closed-loop pole
// sits near the integrator frequency f_b/10.
const settleSamples = (p, tuned) => Math.ceil(15 / (tuned.fb / 10) * p.fs);

// The steady state under the sine part of the force alone. The mean force
// only moves the mass during the start transient: the integrator takes it
// back to zero. The window is a whole number of tooth periods, so the mean
// power is not biased by a part period. Returns, in SI units:
//   amp    vibration amplitude (half of peak to peak), m
//   uAmp   controller force amplitude (half of peak to peak), N
//   pPeak  peak controller power |u·v|, W
//   pMean  mean controller power, W. Negative: the controller takes energy
//          out of the stage. In the steady state it takes out exactly what
//          the cutting force puts in.
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

// The start of the cut: mean plus sine from t = 0, as a trace.
function entryTrace(p, tuned) {
  const n = Math.ceil(settleSamples(p, tuned) / 3);
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
// ratio = uAmp / Famp in N/N. tf is |C·G/(1 + C·G)|, the force ratio from the
// discrete transfer function (NaN from half the loop rate on).
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
  DEFAULTS, cabs, sections, plantAt, controllerAt, loopAt, complianceAt,
  forceRatioAt, sampledSteadyAt, tune, margins, logspace, toothFreq,
  frequencyData, simulate, settleSamples, steadyState, steadyAmplitude,
  entryTrace, steadyTrace, sweep,
};
