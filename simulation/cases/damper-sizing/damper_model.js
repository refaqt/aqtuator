// End damper for a linear motor stage. Two phases:
//
//   1. Runaway. The carriage starts at rest at one end. The motor pushes with
//      its full force over the acceleration stroke. Its back voltage lowers
//      the force as the speed grows, so the speed levels off. If the drive
//      has a speed limit, the carriage speeds up to that limit and then
//      rolls on at it.
//   2. Damper. The carriage hits the damper with the impact speed. The damper
//      pushes back with F_d = c·vⁿ, so its force falls as the speed falls. The
//      motor may keep pushing (worst case). The page picks c so that the speed
//      at the end of the damper stroke is the allowed end speed.
//
// Units inside this file: SI (m, N, s, kg, V, ohm, H). The page converts.
//
// Motor model, three phase, sine commutation, current on the q axis only (no
// field weakening). Data sheet values are line to line, so per phase:
//
//   E   = Ke/√3 · v               back voltage, rms
//   R_p = R/2,  L_p = L/2          resistance and inductance
//   ω   = 2π·v/τ                  electrical frequency, τ = pole pitch
//   V_p = η·V_dc/√6               the most phase voltage the drive can give,
//                                 rms (space vector modulation gives V_dc/√2
//                                 line to line; η is the part we can use)
//
//   (E + R_p·I)² + (ω·L_p·I)² ≤ V_p²     and     I ≤ F_max/k_f
//
// The force is F = k_f·I with the largest current that meets both.
//
// Damper phase, written along the position x (v > 0):
//
//   m·v·dv/dx = F_motor(v)·push − c·vⁿ
//
// with the damper work W_d = ∫c·vⁿ dx, the motor work W_m = ∫F_motor dx and
// the time t = ∫dx/v carried along as extra states. The energy balance is
//
//   ½·m·v₀² + W_m = W_d + ½·m·v_end²

const DEFAULTS = {
  m: 5.0,          // kg, moving mass
  sAcc: 0.218,     // m, stroke over which the motor can speed up the carriage
  Fmax: 512,       // N, the highest motor force (current limit × force constant)
  vLimit: 2.0,     // m/s, the speed limit of the drive (top speed of the stage); 0 = no limit
  Vdc: 310,        // V, DC bus of the drive
  eta: 0.95,       // the part of the bus voltage the drive can use
  kf: 92.5,        // N per A rms
  ke: 53.4,        // V rms per m/s, line to line
  R: 19.0,         // ohm, line to line (hot coil)
  L: 64e-3,        // H, line to line
  tau: 0.030,      // m, pole pitch (one electrical period)
  sDamp: 0.015,    // m, damper stroke
  n: 2,            // damper force law F = c·vⁿ
  vEnd: 0.1,       // m/s, the speed allowed at the end of the damper stroke
  push: false,     // the motor keeps pushing during the damper stroke
  cSet: 0,         // damping constant set by hand, in N·(s/m)ⁿ; 0 = size it
  Erated: 59,      // J, catalog energy per impact of the chosen damper
  vRated: 5,       // m/s, catalog highest impact speed of the chosen damper
  // Type of end stop: "damper" (oil shock absorber, F = c·vⁿ) or "bumper"
  // (polyurethane or elastomer block, F depends on the compression only).
  stopType: "damper",
  // Bumper defaults: ACE TUBUS TA22-10 (co-polyester elastomer, Shore 55D),
  // from the ACE product page: 102 in-lbs (11.5 J) per stroke, 186 in-lbs
  // (21.0 J) for emergency use, 10 mm stroke, 58 to 73 % of the energy absorbed.
  sBump: 0.010,    // m, usable stroke of the bumper
  Ebump: 11.5,     // J, energy per stroke at the full stroke (catalog)
  EbumpMax: 21.0,  // J, energy for emergency use (catalog)
  pBump: 1,        // shape of the force curve F = F_full·(x/s)^p; 1 = linear spring
  absorb: 0.6,     // part of the stored energy the bumper turns into heat
};

const G0 = 9.80665;

// The motor force at speed v.
function motorForce(v, p) {
  const Imax = p.Fmax / p.kf;
  const Vp = p.eta * p.Vdc / Math.sqrt(6);
  const E = p.ke / Math.sqrt(3) * Math.abs(v);
  const Rp = p.R / 2, Lp = p.L / 2, w = 2 * Math.PI * Math.abs(v) / p.tau;
  if (E >= Vp) return 0;
  const a = Rp * Rp + (w * Lp) ** 2, b = 2 * E * Rp, c = E * E - Vp * Vp;
  if (a <= 0) return p.Fmax;
  const I = (-b + Math.sqrt(b * b - 4 * a * c)) / (2 * a);
  return p.kf * Math.min(Imax, I);
}

// The speed at which the drive runs out of voltage with no current.
const noLoadSpeed = (p) => p.eta * p.Vdc / Math.sqrt(2) / p.ke;

// Phase 1, in time (the speed starts at zero). RK4 on (x, v), then the last
// step is cut back to land on the end of the stroke. When the speed reaches
// the speed limit of the drive, the step is cut back to land on it, and the
// carriage rolls on at that speed with no motor force.
function accelerate(p) {
  const tGuess = Math.sqrt(2 * p.sAcc * p.m / p.Fmax);
  const vCap = noLoadSpeed(p);
  const tCap = p.sAcc / Math.max(1e-9, Math.min(vCap, Math.sqrt(2 * p.Fmax * p.sAcc / p.m)));
  const dt = Math.max(tGuess, tCap) / 20000;
  const f = (v) => motorForce(v, p) / p.m;
  let t = 0, x = 0, v = 0;
  const trace = [{ t, x, v, F: motorForce(0, p) }];
  const every = 50;
  for (let i = 1; ; i++) {
    const k1v = f(v), k1x = v;
    const k2v = f(v + dt / 2 * k1v), k2x = v + dt / 2 * k1v;
    const k3v = f(v + dt / 2 * k2v), k3x = v + dt / 2 * k2v;
    const k4v = f(v + dt * k3v), k4x = v + dt * k3v;
    const xn = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x);
    const vn = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v);
    if (p.vLimit > 0 && vn >= p.vLimit) {
      const u = (p.vLimit - v) / (vn - v);
      const xl = x + u * (xn - x);
      if (xl < p.sAcc) {
        t += u * dt; x = xl; v = p.vLimit;
        trace.push({ t, x, v, F: motorForce(v, p) }, { t, x, v, F: 0 });
        t += (p.sAcc - x) / v; x = p.sAcc;
        trace.push({ t, x, v, F: 0 });
        break;
      }
    }
    if (xn >= p.sAcc) {
      const u = (p.sAcc - x) / (xn - x);
      t += u * dt; v += u * (vn - v); x = p.sAcc;
      trace.push({ t, x, v, F: motorForce(v, p) });
      break;
    }
    t += dt; x = xn; v = vn;
    if (i % every === 0) trace.push({ t, x, v, F: motorForce(v, p) });
    if (i > 5e6) throw new Error("the carriage does not reach the end of the acceleration stroke");
  }
  return { v0: v, t, trace, vNoLoad: vCap, limited: p.vLimit > 0 && v >= p.vLimit };
}

// Phase 2 along x for a damping constant c. State s = [v, W_d, W_m, t].
// The step keeps the change of v per step below 1 %. Stops at the end of the
// stroke, or when the speed falls below vStop.
function damp(p, v0, c, { record = false, vStop = 0 } = {}) {
  const push = p.push ? 1 : 0;
  const d = (s) => {
    const v = Math.max(s[0], 1e-12);
    const Fd = c * v ** p.n, Fm = push * motorForce(v, p);
    return [(Fm - Fd) / (p.m * v), Fd, Fm, 1 / v];
  };
  const add = (s, k, h) => s.map((y, i) => y + h * k[i]);
  const hMax = p.sDamp / 2000;
  let x = 0, s = [v0, 0, 0, 0];
  const point = () => {
    const v = s[0], Fd = c * Math.max(v, 0) ** p.n, Fm = push * motorForce(v, p);
    return { x, v, t: s[3], Fd, Fm, Wd: s[1], Wm: s[2], Ek: 0.5 * p.m * v * v, a: (Fm - Fd) / p.m };
  };
  const trace = record ? [point()] : null;
  let stopped = false;
  for (let i = 0; x < p.sDamp - 1e-15; i++) {
    const k1 = d(s);
    let h = Math.min(hMax, p.sDamp - x, 0.01 * s[0] / Math.max(1e-30, Math.abs(k1[0])));
    h = Math.max(h, p.sDamp * 1e-9);
    const k2 = d(add(s, k1, h / 2)), k3 = d(add(s, k2, h / 2)), k4 = d(add(s, k3, h));
    const sn = s.map((y, j) => y + h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]));
    if (sn[0] <= Math.max(vStop, 1e-6)) {
      // Cut the step back to where the speed reaches the stop speed.
      const target = Math.max(vStop, 1e-6);
      const u = Math.min(1, Math.max(0, (s[0] - target) / (s[0] - sn[0])));
      s = s.map((y, j) => y + u * (sn[j] - y));
      x += u * h;
      stopped = true;
      if (record) trace.push(point());
      break;
    }
    s = sn; x += h;
    if (record) trace.push(point());
    if (i > 2e6) throw new Error("the damper calculation does not converge");
  }
  return { vEnd: stopped ? Math.max(0, s[0]) : s[0], stopped, xEnd: x, Wd: s[1], Wm: s[2], t: s[3], trace };
}

// The damping constant c that gives the allowed end speed. The end speed falls
// as c grows, so bisection on log c finds it.
function sizeDamper(p, v0) {
  const end = (c) => damp(p, v0, c, { vStop: p.vEnd * 0.5 }).vEnd;
  if (end(0) <= p.vEnd) return { c: 0, none: true };
  // Scale: the c of a damper that stops v0 in the stroke with no push.
  let hi = p.m * v0 ** (2 - p.n) / p.sDamp, lo = hi;
  while (end(hi) > p.vEnd) { hi *= 4; if (hi > 1e30) throw new Error("no damping constant reaches the end speed"); }
  while (end(lo) <= p.vEnd) lo /= 4;
  for (let i = 0; i < 80 && hi / lo > 1 + 1e-10; i++) {
    const mid = Math.sqrt(lo * hi);
    if (end(mid) > p.vEnd) lo = mid; else hi = mid;
  }
  return { c: Math.sqrt(lo * hi), none: false };
}

// The speed where the damper force equals the motor force (bisection; the
// damper force grows with v, the motor force falls).
function terminalSpeed(p, c) {
  let lo = 0, hi = noLoadSpeed(p);
  for (let i = 0; i < 100; i++) {
    const v = (lo + hi) / 2;
    if (c * v ** p.n < motorForce(v, p)) lo = v; else hi = v;
  }
  return (lo + hi) / 2;
}

// Everything the page shows.
function solve(p) {
  const acc = accelerate(p);
  const v0 = acc.v0;
  const sz = p.cSet > 0 ? { c: p.cSet, none: false, manual: true } : sizeDamper(p, v0);
  const dp = damp(p, v0, sz.c, { record: true });
  const tr = dp.trace;
  const Ek0 = 0.5 * p.m * v0 * v0;
  const Ek1 = 0.5 * p.m * dp.vEnd * dp.vEnd;
  const Etotal = Ek0 + dp.Wm;                    // catalog way: E = E1 + E2
  let FdPeak = 0, aPeak = 0;
  for (const q of tr) { FdPeak = Math.max(FdPeak, q.Fd); aPeak = Math.max(aPeak, -q.a); }
  const Fconst = (Ek0 + dp.Wm - Ek1) / p.sDamp;  // same energy, even force
  return {
    stopType: "damper",
    v0, tAcc: acc.t, accTrace: acc.trace, vNoLoad: acc.vNoLoad, limited: acc.limited, vNoVolt: Math.sqrt(2 * p.Fmax * p.sAcc / p.m),
    c: sz.c, none: sz.none, manual: !!sz.manual, damper: dp, trace: tr,
    Ek0, Ek1, Wm: dp.Wm, Wd: dp.Wd, Etotal, balance: Ek0 + dp.Wm - dp.Wd - Ek1,
    me: 2 * Etotal / (v0 * v0),
    FdPeak, aPeakG: aPeak / G0, Fconst, aConstG: (Fconst - (p.push ? motorForce(v0, p) : 0)) / p.m / G0,
    FmEnd: p.push ? motorForce(dp.vEnd, p) : 0,
    // With the motor pushing, a damper F = c·vⁿ alone only slows the carriage
    // to the speed where both forces are equal: (F_motor/c)^(1/n).
    vTerminal: p.push && sz.c > 0 ? terminalSpeed(p, sz.c) : 0,
    energyUse: Etotal / p.Erated, speedUse: v0 / p.vRated,
  };
}

// ----- Bumper ---------------------------------------------------------------
// A polyurethane or elastomer bumper pushes back with a force that depends on
// the compression x only, not on the speed:
//
//   F_b(x) = F_full·(x/s)^p,   F_full = (p+1)·E_r/s
//
// so that the work up to the full stroke s is the catalog energy E_r. p = 1 is
// a linear spring. p > 1 gets stiffer as it compresses, like a solid cylinder.
// p < 1 takes most of the energy early, as ACE says of its TA profile dampers.
//
// The carriage moves m·dv/dt = F_motor(v)·push − F_b(x) until it stops (v = 0)
// or the bumper is fully compressed (x = s). Then metal hits metal: whatever
// kinetic energy is left goes into the frame with no stroke at all.
//
// The bumper turns a part `absorb` of its work into heat. With the motor off,
// the rest pushes the carriage back: ½·m·v_r² = (1 − absorb)·W_b.
const bumperFull = (p) => (p.pBump + 1) * p.Ebump / p.sBump;
const bumperForce = (x, p) => x <= 0 ? 0 : bumperFull(p) * Math.min(1, x / p.sBump) ** p.pBump;
// Work of the bumper up to compression x (exact).
const bumperWork = (x, p) => bumperFull(p) * p.sBump / (p.pBump + 1) * Math.min(1, x / p.sBump) ** (p.pBump + 1);

// In time, RK4 on (x, v, W_m). The last step is cut back to land on v = 0 or
// on x = s, whichever comes first.
function bump(p, v0) {
  const push = p.push ? 1 : 0;
  const acc = (x, v) => (push * motorForce(v, p) - bumperForce(x, p)) / p.m;
  // A linear spring with the same full force gives the time scale.
  const tScale = Math.min(p.sBump / v0, Math.sqrt(p.m * p.sBump / bumperFull(p)));
  const dt = tScale / 4000;
  const point = (t, x, v, Wm) => {
    const Fb = bumperForce(x, p), Fm = push * motorForce(v, p);
    return { x, v, t, Fd: Fb, Fm, Wd: bumperWork(x, p), Wm, Ek: 0.5 * p.m * v * v, a: (Fm - Fb) / p.m };
  };
  let t = 0, x = 0, v = v0, Wm = 0;
  const trace = [point(t, x, v, Wm)];
  let end = "";
  for (let i = 1; ; i++) {
    const f = (s) => [s[1], acc(s[0], s[1]), push * motorForce(s[1], p) * s[1]];
    const s = [x, v, Wm];
    const add = (a, k, h) => a.map((y, j) => y + h * k[j]);
    const k1 = f(s), k2 = f(add(s, k1, dt / 2)), k3 = f(add(s, k2, dt / 2)), k4 = f(add(s, k3, dt));
    const sn = s.map((y, j) => y + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]));
    // Cut the step back to the first of v = 0 and x = s.
    const uStop = sn[1] <= 0 ? v / (v - sn[1]) : Infinity;
    const uFull = sn[0] >= p.sBump ? (p.sBump - x) / (sn[0] - x) : Infinity;
    if (uStop <= 1 || uFull <= 1) {
      const u = Math.min(uStop, uFull);
      t += u * dt; x += u * (sn[0] - x); v += u * (sn[1] - v); Wm += u * (sn[2] - Wm);
      if (uFull < uStop) { x = p.sBump; end = "full"; } else { v = 0; end = "stopped"; }
      trace.push(point(t, x, v, Wm));
      break;
    }
    t += dt; [x, v, Wm] = sn;
    if (i % 4 === 0) trace.push(point(t, x, v, Wm));
    if (i > 5e6) throw new Error("the bumper calculation does not converge");
  }
  return { xMax: x, vEnd: v, bottomed: end === "full", t, Wd: bumperWork(x, p), Wm, trace };
}

// Everything the page shows for a bumper.
function solveBumper(p) {
  const acc = accelerate(p);
  const v0 = acc.v0;
  const b = bump(p, v0);
  const Ek0 = 0.5 * p.m * v0 * v0;
  const Ek1 = 0.5 * p.m * b.vEnd * b.vEnd;      // left for metal-on-metal contact
  const Etotal = Ek0 + b.Wm;
  let aPeak = 0;
  for (const q of b.trace) aPeak = Math.max(aPeak, -q.a);
  const FbPeak = bumperForce(b.xMax, p);
  const Fconst = (Etotal - Ek1) / p.sBump;       // same energy, even force over the full bumper stroke
  const FmEnd = p.push ? motorForce(0, p) : 0;
  // With the motor still pushing, the carriage settles where F_b(x) = F_motor(0).
  const xHold = p.push ? p.sBump * Math.min(1, FmEnd / bumperFull(p)) ** (1 / p.pBump) : 0;
  const Eback = p.push || b.bottomed ? 0 : (1 - p.absorb) * b.Wd;
  return {
    stopType: "bumper",
    v0, tAcc: acc.t, accTrace: acc.trace, vNoLoad: acc.vNoLoad, limited: acc.limited, vNoVolt: Math.sqrt(2 * p.Fmax * p.sAcc / p.m),
    bumper: b, trace: b.trace, Ffull: bumperFull(p),
    Ek0, Ek1, Wm: b.Wm, Wd: b.Wd, Etotal, balance: Ek0 + b.Wm - b.Wd - Ek1,
    FdPeak: FbPeak, aPeakG: aPeak / G0, Fconst, aConstG: (Fconst - FmEnd) / p.m / G0,
    FmEnd, xHold,
    Eheat: p.absorb * b.Wd, Eback, vBack: Math.sqrt(2 * Eback / p.m),
    energyUse: Etotal / p.Ebump, emergencyUse: Etotal / p.EbumpMax, strokeUse: b.xMax / p.sBump,
  };
}

// A plain script, not a module. Browsers refuse to load a module for a page
// opened straight from disk (file://), so the page would never calculate.
// The page and the checks both read the functions from this one object.
globalThis.DamperModel = {
  DEFAULTS, G0, motorForce, noLoadSpeed, accelerate, damp, sizeDamper, terminalSpeed, solve,
  bumperFull, bumperForce, bumperWork, bump, solveBumper,
};
