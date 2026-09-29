// Checks for control_model.js. Node 18 or newer, no packages:
//
//     node simulation/cases/cutting-force-rejection/check_model.mjs
//
// For each case (linear motor, ball screw with the motor encoder, ball screw
// with the linear encoder):
// 1. The tuning meets the robustness rules on every plant of the family
//    (resonances moved ±15 %): peak sensitivity at most 6 dB, phase margin
//    at least 30°, gain margin at least 6 dB, stable. |C·G| = 1 at f_b, and
//    2 % above f_b a rule breaks, so f_b is the highest one.
// 2. A constant force gives no lasting deflection (the integrator).
// 3. The time simulation agrees with the discrete compliance where both
//    should hold (tooth frequency well below half the loop rate), for the
//    vibration, the controller force and the mean controller power.
// Then:
// 4. The state-space plant with hold matches the exact formula for one mass.
// 5. f_b does not depend on the mass of the linear motor stage.
// 6. With stiff springs, the ball screw is one mass m1 + m_s + m.
// 7. With a very stiff axial spring, the ball screw is the two-mass model.
// 8. The two resonances sit at the natural frequencies of the chain.
// 9. A narrow resonance and a soft axial spring do not break the tuning.
// 10. The stability test agrees with the gain margin.
// 11. The Tustin controller matches C(s) at low frequency.
// 12. The sensitivity peak matches a dense scan.
// 13. The linear motor has no resonance, so its family is one plant.
// Chatter:
// 14. The fast sine compliance equals the exact sampled steady state.
// 15. For one mass on a spring, the lobes give the textbook lowest real part
//     −1/(4kζ(1 + ζ)) at r = √(1 + 2ζ).
// 16. Each lobe point solves 1 + a·(1 − e^{−jωT})·G = 0 with a = −1/(2 Re G).
// 17. The floor matches a dense scan, and the lobes touch it but never go
//     below it.

// The model is a plain script (see its end), so it hands over one object.
import "./control_model.js";
const M = globalThis.ControlModel;

let failed = 0;
const check = (ok, text) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${text}`);
  if (!ok) failed++;
};
const near = (got, want, tol) => Math.abs(got / want - 1) <= tol;

for (const id of M.CASES) {
  const p = { ...M.DEFAULTS };
  const t = M.tune(p, id);
  const tag = id;

  check(t.stable, `${tag}: stable, largest closed-loop pole |z| = ${t.rho.toFixed(5)}`);
  const l = M.loopAt(t.fb, p, t);
  check(near(M.cabs(l.h), 1, 1e-6), `${tag}: |C·G| at f_b = ${M.cabs(l.h).toFixed(6)}`);
  // At least 30°. More when a resonance sets the limit: a slightly higher
  // f_b would make the loop cross 1 again there, with a poor margin.
  check(t.pmDeg >= 29.9, `${tag}: worst phase margin ${t.pmDeg.toFixed(3)}° at ${t.fc.toFixed(1)} Hz`);
  check(t.gmDb >= 5.9, `${tag}: gain margin ${t.gmDb.toFixed(2)} dB at ${t.f180.toFixed(1)} Hz`);
  const w = t.worst;
  check(t.robust && w.msDb <= p.msDb + 0.01 && w.pmDeg >= p.pm - 0.01 && w.gmDb >= p.gmMinDb - 0.01 && w.rho < 1,
    `${tag}: over ${t.family} plants, worst sensitivity peak ${w.msDb.toFixed(2)} dB, phase margin ` +
    `${w.pmDeg.toFixed(1)}°, gain margin ${w.gmDb.toFixed(1)} dB, largest pole |z| ${w.rho.toFixed(5)}`);
  check(t.limit.length > 0, `${tag}: f_b ${t.fb.toFixed(1)} Hz is the highest, 2 % above it breaks ` +
    t.limit.map((b) => `${b.rule} (coupling × ${b.sc.toFixed(3)}, axial × ${b.sa.toFixed(3)})`).join(", "));

  const n = 3 * M.settleSamples(p, t);
  const r = M.simulate(p, t, { samples: n, Famp: 0, window: n - 10 });
  const rest = Math.max(Math.abs(r.lo), Math.abs(r.hi));
  if (id === "colloc") {
    // The integrator holds the motor still. The stage stays off by what the
    // two springs give under the mean force: F_mean·(1/k_c + 1/k_a).
    const q = M.mechanics(p);
    const want = p.Fmean * (1 / q.kc + 1 / q.ka);
    check(near(rest, want, 1e-3), `${tag}: constant force, the stage stays off by ${(rest * 1e9).toFixed(1)} nm, ` +
      `F_mean·(1/k_c + 1/k_a) = ${(want * 1e9).toFixed(1)} nm`);
  } else {
    check(rest < 1e-3 * r.peak, `${tag}: constant force, deflection falls from ` +
      `${(r.peak * 1e6).toFixed(3)} µm to ${(rest * 1e9).toFixed(4)} nm`);
  }

  for (const f of [t.fb / 5, t.fb, 2 * t.fb]) {
    const q = { ...p, rpm: f * 60 / p.teeth };
    const st = M.steadyState(q, t);
    const tf = M.cabs(M.complianceAt(f, q, t)) * p.Famp;
    check(near(st.amp, tf, 0.02), `${tag}: at ${f.toFixed(0)} Hz, simulation ${(st.amp * 1e6).toFixed(4)} µm, ` +
      `compliance × force ${(tf * 1e6).toFixed(4)} µm`);
    const ratio = M.cabs(M.forceRatioAt(f, q, t));
    check(near(st.uAmp / p.Famp, ratio, 0.02), `${tag}: at ${f.toFixed(0)} Hz, controller force ` +
      `${(st.uAmp / p.Famp).toFixed(4)} N/N, transfer function ${ratio.toFixed(4)} N/N`);
  }

  // The mean controller power, against the exact sampled steady state. Also
  // above half the loop rate, where only the sampled solution holds.
  for (const f of [t.fb / 5, t.fb, 2 * t.fb, 0.37 * p.fs, 1.3 * p.fs]) {
    const q = { ...p, rpm: f * 60 / p.teeth };
    const st = M.steadyState(q, t);
    const ex = M.sampledSteadyAt(f, q, t);
    check(Math.abs(st.pMean - ex.pMean) <= 0.01 * st.pPeak, `${tag}: at ${f.toFixed(0)} Hz, mean controller power ` +
      `${st.pMean.toPrecision(3)} W, exact ${ex.pMean.toPrecision(3)} W (peak ${st.pPeak.toPrecision(3)} W)`);
  }
}

// The state-space plant with hold, against the formula for one mass.
{
  const p = { ...M.DEFAULTS };
  const pl = M.plantFor(p, "linear");
  let worst = 0;
  for (const f of M.logspace(1, 0.49 * p.fs, 50)) {
    const a = M.plantResp(f, p, pl).mu, b = M.plantAt(f, p).h;
    worst = Math.max(worst, M.cabs([a[0] - b[0], a[1] - b[1]]) / M.cabs(b));
  }
  check(worst < 1e-6, `state-space hold plant matches T²(z + 1)/(2m(z − 1)²), worst error ${worst.toExponential(2)}`);
}

// f_b does not depend on the mass of the linear motor stage. K grows with it.
{
  const p = { ...M.DEFAULTS };
  const t = M.tune(p, "linear"), t2 = M.tune({ ...p, m: 5 * p.m }, "linear");
  check(near(t2.fb, t.fb, 1e-4) && near(t2.K, 5 * t.K, 1e-4),
    `linear: five times the mass keeps f_b (${t.fb.toFixed(2)}, ${t2.fb.toFixed(2)} Hz) and gives five times K`);
}

// With stiff springs, both ball-screw plants are one mass m1 + m_s + m.
{
  const p = { ...M.DEFAULTS, kc: 1e7, knut: 1e6, kbear: 1e6, droot: 100 };
  const q = M.mechanics(p);
  const one = { ...p, m: q.m1 + q.ms + q.m };
  for (const id of ["colloc", "noncolloc"]) {
    const pl = M.plantFor(p, id);
    let worst = 0;
    for (const f of M.logspace(10, 500, 20)) {
      worst = Math.max(worst, Math.abs(M.cabs(M.plantResp(f, p, pl).mu) / M.cabs(M.plantAt(f, one).h) - 1));
    }
    check(worst < 0.01, `${id}: stiff springs act as one mass of ${one.m.toFixed(1)} kg, ` +
      `worst error ${(worst * 100).toFixed(3)} % up to 500 Hz`);
  }
}

// With a very stiff axial spring, the chain is the two-mass model of before:
// motor m1 on the coupling, screw and stage together. Its resonance is
// √(k_c/μ)/2π with μ = m1·(m_s + m)/(m1 + m_s + m), 1.22 kHz at the defaults.
// f_b is the value of the two-mass model under the robustness rules, as found
// with this model on 2026-09-28; the check guards it against later changes.
{
  const p = { ...M.DEFAULTS, knut: 1e9, kbear: 1e9, droot: 1e4 };
  const q = M.mechanics(p);
  const mu = q.m1 * (q.ms + q.m) / (q.m1 + q.ms + q.m);
  const f2 = Math.sqrt(q.kc / mu) / (2 * Math.PI);
  check(near(q.modes[0], f2, 0.01), `stiff axial spring: first mode ${q.modes[0].toFixed(0)} Hz, ` +
    `two-mass resonance ${f2.toFixed(0)} Hz`);
  const t = M.tune(p, "noncolloc");
  check(near(t.fb, 158.9, 0.01), `stiff axial spring: non-collocated f_b ${t.fb.toFixed(1)} Hz, two-mass model 158.9 Hz`);
}

// The two resonances, as the peaks of |x/u|·ω² with little damping.
{
  const p = { ...M.DEFAULTS, zeta: 0.01, zetaA: 0.01 };
  const q = M.mechanics(p);
  const pl = M.plantFor(p, "noncolloc");
  for (const f0 of q.modes) {
    let best = 0, fPeak = 0;
    for (const f of M.logspace(f0 / 1.3, f0 * 1.3, 2000)) {
      if (f >= p.fs / 2) break;
      const v = M.cabs(M.plantResp(f, p, pl).mu) * (2 * Math.PI * f) ** 2;
      if (v > best) { best = v; fPeak = f; }
    }
    check(near(fPeak, f0, 0.02), `resonance peak at ${fPeak.toFixed(0)} Hz, natural frequency ${f0.toFixed(0)} Hz`);
  }
}

// A soft axial spring: the stage mode sits near f_b. The tuning must stay
// stable at the target margin.
{
  const p = { ...M.DEFAULTS, knut: 20, kbear: 20 };
  for (const id of ["colloc", "noncolloc"]) {
    const t = M.tune(p, id);
    check(t.robust && t.stable, `${id}, soft axial spring (${(M.mechanics(p).ka / 1e6).toFixed(1)} N/µm): ` +
      `f_b ${t.fb.toFixed(1)} Hz, worst phase margin ${t.pmDeg.toFixed(2)}°, largest pole |z| ${t.rho.toFixed(5)}`);
  }
}

// A soft coupling with little damping: a narrow resonance peak near f_b. The
// tuning must not step over it.
{
  const p = { ...M.DEFAULTS, kc: 50, pitch: 10, zeta: 0.02, zetaA: 0.02, L: 800, d: 12 };
  const t = M.tune(p, "colloc");
  check(t.robust && t.stable, `colloc, soft coupling with ζ = 0.02: f_b ${t.fb.toFixed(1)} Hz, ` +
    `worst phase margin ${t.pmDeg.toFixed(2)}° at ${t.fc.toFixed(0)} Hz, largest pole |z| ${t.rho.toFixed(5)}`);
}

// A very sharp resonance (ζ = 0.008) whose peak just touches |C·G| = 1: no
// grid sees that crossing. The tuning must still end with a stable loop.
{
  const p = { ...M.DEFAULTS, m: 3.77, fs: 11649, pitch: 11.98, kc: 1091, d: 23.48, L: 1352.5, Jr: 237.1,
    zeta: 0.00793, droot: 19.48, xnut: 61.37, knut: 168.5, kbear: 28.17, zetaA: 0.054 };
  const t = M.tune(p, "colloc");
  check(t.stable && t.robust, `colloc, sharp resonance: f_b ${t.fb.toFixed(1)} Hz, ` +
    `gain margin ${t.gmDb.toFixed(2)} dB, largest pole |z| ${t.rho.toFixed(6)}`);
}

// The stability test agrees with the gain margin: a bit less gain than the
// margin allows is stable, a bit more is not.
{
  const p = { ...M.DEFAULTS };
  const t = M.tune(p, "noncolloc");
  const lo = M.spectralRadius(p, { ...t, K: t.K * t.gm * 0.95 });
  const hi = M.spectralRadius(p, { ...t, K: t.K * t.gm * 1.05 });
  check(lo < 1 && hi > 1, `noncolloc: gain × ${(t.gm * 0.95).toFixed(3)} gives |z| ${lo.toFixed(5)}, ` +
    `gain × ${(t.gm * 1.05).toFixed(3)} gives |z| ${hi.toFixed(5)}`);
}

// Tustin against the continuous controller, well below fs/2.
{
  const p = { ...M.DEFAULTS };
  const t = M.tune(p);
  const f = t.fb / 20, s = [0, 2 * Math.PI * f], w = 2 * Math.PI * t.fb;
  const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const div = (a, b) => { const d = b[0] ** 2 + b[1] ** 2; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
  let c = div([t.K, 0], s);
  c = mul(c, div([w / 10, s[1]], [4 * w, s[1]]));
  c = mul(c, div([w / 3, s[1]], [4 * w, s[1]]));
  const cz = M.controllerAt(f, p, t).h;
  check(near(M.cabs(cz), M.cabs(c), 0.01), `Tustin controller at ${f.toFixed(1)} Hz: ` +
    `${M.cabs(cz).toExponential(4)} against C(s) ${M.cabs(c).toExponential(4)} N/m`);
}

// The sensitivity peak from margins, against a dense scan of 1/|1 + C·G|.
for (const id of M.CASES) {
  const p = { ...M.DEFAULTS };
  const t = M.tune(p, id);
  let best = 0;
  for (const f of M.logspace(t.fb / 1000, 0.4999 * p.fs, 200000)) {
    const h = M.loopAt(f, p, t).h;
    best = Math.max(best, 1 / Math.hypot(1 + h[0], h[1]));
  }
  check(t.ms >= best * 0.9999 && near(t.ms, best, 0.005), `${id}: sensitivity peak ${t.ms.toFixed(4)}, dense scan ${best.toFixed(4)}`);
}

// The linear motor has no resonance: the spread changes nothing.
{
  const p = { ...M.DEFAULTS };
  const a = M.tune(p, "linear"), b = M.tune({ ...p, spread: 0 }, "linear");
  check(a.family === 1 && a.fb === b.fb, `linear: one plant in the family, f_b ${a.fb.toFixed(2)} Hz with and without the spread`);
}

// Chatter 14: the fast sine compliance against sampledSteadyAt.
for (const id of M.CASES) {
  const p = { ...M.DEFAULTS };
  const t = M.tune(p, id);
  let worst = 0;
  for (const f of [30, t.fb, 660, 3000]) {
    const a = M.sineComplianceAt(f, p, t), X = M.sampledSteadyAt(f, p, t).X;
    worst = Math.max(worst, Math.hypot(a[0] - X[0] / p.Famp, a[1] - X[1] / p.Famp) / M.cabs(a));
  }
  check(worst < 1e-9, `${id}: sine compliance equals the sampled steady state, worst error ${worst.toExponential(2)}`);
}

// Chatter 15 and 16: one mass on a spring, G = 1/(k(1 − r² + 2jζr)).
const residual = (g, f, teeth, k) => {
  const L = M.lobePoint(g, f, teeth, k), a = L.depth / 2, th = 2 * Math.PI * f * L.T;
  const q = [1 - Math.cos(th), Math.sin(th)];               // 1 − e^{−jθ}
  const r = [a * (q[0] * g[0] - q[1] * g[1]), a * (q[0] * g[1] + q[1] * g[0])];
  return Math.hypot(1 + r[0], r[1]);
};
{
  const k = 2e7, fn = 500, z = 0.03;
  const comp = (f) => { const r = f / fn, d = k * ((1 - r * r) ** 2 + (2 * z * r) ** 2); return [(1 - r * r) / d, -2 * z * r / d]; };
  const L = M.lobes(comp, 10, 5000, 2, 1000, 30000);
  const want = -1 / (4 * k * z * (1 + z));
  check(near(L.minRe, want, 1e-6) && near(L.fMin, fn * Math.sqrt(1 + 2 * z), 1e-3),
    `one mass on a spring: lowest Re G ${L.minRe.toExponential(5)} at ${L.fMin.toFixed(2)} Hz, ` +
    `textbook ${want.toExponential(5)} at ${(fn * Math.sqrt(1 + 2 * z)).toFixed(2)} Hz`);
  let worst = 0;
  for (const f of [510, 530, 600, 800]) for (const kk of [0, 1, 5]) worst = Math.max(worst, residual(comp(f), f, 2, kk));
  check(worst < 1e-12, `one mass on a spring: lobe points solve the chatter equation, worst residual ${worst.toExponential(2)}`);
}

// Chatter 16 and 17 for each drive.
for (const id of M.CASES) {
  const p = { ...M.DEFAULTS };
  const t = M.tune(p, id);
  const c = M.chatter(p, t, 1000, 30000);
  let worst = 0;
  for (const f of M.logspace(t.fb / 2, p.fs / 2 * 0.9, 40)) {
    const g = M.sineComplianceAt(f, p, t);
    if (g[0] < 0) for (const kk of [0, 1, 7]) worst = Math.max(worst, residual(g, f, p.teeth, kk));
  }
  check(worst < 1e-9, `${id}: lobe points solve the chatter equation, worst residual ${worst.toExponential(2)}`);
  let best = 0;
  for (const f of M.logspace(t.fb / 200, p.fs / 2 * 0.98, 100000)) best = Math.min(best, M.sineComplianceAt(f, p, t)[0]);
  const lowest = Math.min(...c.depth.filter(Number.isFinite));
  check(c.minRe <= best * (1 - 1e-9) && near(c.minRe, best, 1e-4) && lowest >= c.floor * (1 - 1e-9) && near(lowest, c.floor, 0.01),
    `${id}: floor −1/min Re G ${(c.floor / 1e6).toFixed(3)} N/µm at ${c.fMin.toFixed(1)} Hz, dense scan ` +
    `${(-1 / best / 1e6).toFixed(3)} N/µm, lowest lobe from 1000 to 30000 rev/min ${(lowest / 1e6).toFixed(3)} N/µm`);
}

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
