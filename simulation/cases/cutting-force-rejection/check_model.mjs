// Checks for control_model.js. Node 18 or newer, no packages:
//
//     node simulation/cases/cutting-force-rejection/check_model.mjs
//
// For each case (linear motor, ball screw with the motor encoder, ball screw
// with the linear encoder):
// 1. The tuning hits the target: |C·G| = 1 at f_b and a 30° phase margin.
// 2. A constant force gives no lasting deflection (the integrator).
// 3. The time simulation agrees with the discrete compliance where both
//    should hold (tooth frequency well below half the loop rate), for the
//    vibration, the controller force and the mean controller power.
// Then:
// 4. The state-space plant with hold matches the exact formula for one mass.
// 5. f_b does not depend on the mass of the linear motor stage.
// 6. With a very stiff coupling, the ball screw is one mass m1 + m2.
// 7. The resonance sits at √(k/μ)/2π.
// 8. The stability test agrees with the gain margin.
// 9. The Tustin controller matches C(s) at low frequency.

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
  check(Math.abs(t.pmDeg - 30) < 0.1, `${tag}: worst phase margin ${t.pmDeg.toFixed(3)}° at ${t.fc.toFixed(1)} Hz`);
  check(t.gmDb > 1, `${tag}: gain margin ${t.gmDb.toFixed(2)} dB at ${t.f180.toFixed(1)} Hz`);

  const n = 3 * M.settleSamples(p, t);
  const r = M.simulate(p, t, { samples: n, Famp: 0, window: n - 10 });
  const rest = Math.max(Math.abs(r.lo), Math.abs(r.hi));
  if (id === "colloc") {
    // The integrator holds the motor still. The stage stays off by the
    // twist of the coupling under the mean force: F_mean / k.
    const want = p.Fmean / M.mechanics(p).k;
    check(near(rest, want, 1e-3), `${tag}: constant force, the stage stays off by ${(rest * 1e9).toFixed(2)} nm, ` +
      `F_mean / k = ${(want * 1e9).toFixed(2)} nm`);
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

// With a very stiff coupling, both ball-screw plants are one mass m1 + m2.
{
  const p = { ...M.DEFAULTS, kc: 1e7 };
  const q = M.mechanics(p);
  const one = { ...p, m: q.m1 + q.m2 };
  for (const id of ["colloc", "noncolloc"]) {
    const pl = M.plantFor(p, id);
    let worst = 0;
    for (const f of M.logspace(10, 500, 20)) {
      worst = Math.max(worst, Math.abs(M.cabs(M.plantResp(f, p, pl).mu) / M.cabs(M.plantAt(f, one).h) - 1));
    }
    check(worst < 0.01, `${id}: stiff coupling acts as one mass of ${(q.m1 + q.m2).toFixed(1)} kg, ` +
      `worst error ${(worst * 100).toFixed(3)} % up to 500 Hz`);
  }
}

// The resonance, as the peak of |x2/u|·ω²·(m1 + m2) with little damping.
{
  const p = { ...M.DEFAULTS, zeta: 0.01 };
  const q = M.mechanics(p);
  const pl = M.plantFor(p, "noncolloc");
  let best = 0, fPeak = 0;
  for (const f of M.logspace(q.fRes / 2, q.fRes * 2, 2000)) {
    const v = M.cabs(M.plantResp(f, p, pl).mu) * (2 * Math.PI * f) ** 2;
    if (v > best) { best = v; fPeak = f; }
  }
  check(near(fPeak, q.fRes, 0.02), `resonance peak at ${fPeak.toFixed(0)} Hz, √(k/μ)/2π = ${q.fRes.toFixed(0)} Hz`);
}

// A soft coupling with little damping: a narrow resonance peak near f_b. The
// tuning must not step over it.
{
  const p = { ...M.DEFAULTS, kc: 50, pitch: 10, zeta: 0.02, L: 800, d: 12 };
  const t = M.tune(p, "colloc");
  check(t.pmDeg >= 29.9 && t.stable, `colloc, soft coupling with ζ = 0.02: f_b ${t.fb.toFixed(1)} Hz, ` +
    `worst phase margin ${t.pmDeg.toFixed(2)}° at ${t.fc.toFixed(0)} Hz, largest pole |z| ${t.rho.toFixed(5)}`);
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

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
