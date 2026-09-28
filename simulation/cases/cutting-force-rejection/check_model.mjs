// Checks for control_model.js. Node 18 or newer, no packages:
//
//     node simulation/cases/cutting-force-rejection/check_model.mjs
//
// 1. The tuning hits the target: |C·G| = 1 at f_b and a 30° phase margin.
// 2. f_b does not depend on the mass. K grows with the mass.
// 3. A constant force gives no lasting deflection (the integrator).
// 4. The time simulation agrees with the discrete compliance where both
//    should hold (tooth frequency well below half the loop rate).
// 5. The Tustin controller matches C(s) at low frequency.

import * as M from "./control_model.js";

let failed = 0;
const check = (ok, text) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${text}`);
  if (!ok) failed++;
};
const near = (got, want, tol) => Math.abs(got / want - 1) <= tol;

for (const delay of [false, true]) {
  const p = { ...M.DEFAULTS, delay };
  const t = M.tune(p);
  const tag = delay ? "with delay" : "no delay";

  const l = M.loopAt(t.fb, p, t);
  check(near(M.cabs(l.h), 1, 1e-6), `${tag}: |C·G| at f_b = ${M.cabs(l.h).toFixed(6)}`);
  check(Math.abs(t.pmDeg - 30) < 0.1, `${tag}: phase margin ${t.pmDeg.toFixed(3)}°`);
  check(near(t.fc, t.fb, 1e-3), `${tag}: gain crossover ${t.fc.toFixed(1)} Hz = f_b ${t.fb.toFixed(1)} Hz`);
  check(t.gmDb > 3, `${tag}: gain margin ${t.gmDb.toFixed(2)} dB`);

  const t2 = M.tune({ ...p, m: 5 * p.m });
  check(near(t2.fb, t.fb, 1e-6) && near(t2.K, 5 * t.K, 1e-6),
    `${tag}: five times the mass keeps f_b and gives five times K`);

  const n = 3 * M.settleSamples(p, t);
  const r = M.simulate(p, t, { samples: n, Famp: 0, window: n - 10 });
  const rest = Math.max(Math.abs(r.lo), Math.abs(r.hi));
  check(rest < 1e-3 * r.peak, `${tag}: constant force, deflection falls from ` +
    `${(r.peak * 1e6).toFixed(2)} µm to ${(rest * 1e9).toFixed(3)} nm`);

  for (const f of [t.fb / 5, t.fb, 2 * t.fb]) {
    const q = { ...p, rpm: f * 60 / p.teeth };
    const sim = M.steadyAmplitude(q, t);
    const tf = M.cabs(M.complianceAt(f, q, t)) * p.Famp;
    check(near(sim, tf, 0.02), `${tag}: at ${f.toFixed(0)} Hz, simulation ${(sim * 1e6).toFixed(3)} µm, ` +
      `compliance × force ${(tf * 1e6).toFixed(3)} µm`);
  }
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
