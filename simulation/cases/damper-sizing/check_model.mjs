// Checks for damper_model.js. Node 18 or newer, no packages:
//
//     node simulation/cases/damper-sizing/check_model.mjs
//
// 1. With no voltage limit and a constant force, the impact speed is √(2·F·s/m).
// 2. n = 1, no motor push: v falls in a straight line with x, so
//    c = m·(v₀ − v_end)/stroke.
// 3. n = 2, no motor push: v = v₀·exp(−c·x/m), so c = m·ln(v₀/v_end)/stroke.
// 4. The energy balance ½·m·v₀² + W_m = W_d + ½·m·v_end² closes, for n = 1
//    and n = 2, with and without the motor push.
// 5. With no current, the voltage limit gives the no-load speed η·V_dc/(√2·Ke).
// 6. The defaults (MK21, 5 kg, 218 mm, 310 V, hot coil) give about 3.80 m/s,
//    the value of the hand simulation of 2026-10-19.
// 7. The sized damper gives the allowed end speed.
// 8. The constant-force reference holds the same energy as the damper.
// 9. A damping constant set by hand is used as it is. With the motor pushing,
//    the speed levels off at the terminal speed, where c·vⁿ = F_motor(v).

import "./damper_model.js";
const M = globalThis.DamperModel;

let failed = 0;
const check = (ok, text) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${text}`);
  if (!ok) failed++;
};
const near = (got, want, tol) => Math.abs(got / want - 1) <= tol;

// 1. Constant force.
{
  const p = { ...M.DEFAULTS, Vdc: 1e9 };
  const a = M.accelerate(p);
  const want = Math.sqrt(2 * p.Fmax * p.sAcc / p.m);
  check(near(a.v0, want, 1e-6), `constant force: impact speed ${a.v0.toFixed(5)} m/s, √(2Fs/m) = ${want.toFixed(5)} m/s`);
  const tw = Math.sqrt(2 * p.sAcc * p.m / p.Fmax);
  check(near(a.t, tw, 1e-5), `constant force: time ${(a.t * 1e3).toFixed(4)} ms, √(2sm/F) = ${(tw * 1e3).toFixed(4)} ms`);
}

// 2 and 3. Exact damper constants with no motor push.
for (const n of [1, 2]) {
  const p = { ...M.DEFAULTS, n, push: false };
  const v0 = 3.8;
  const s = M.sizeDamper(p, v0);
  const want = n === 1 ? p.m * (v0 - p.vEnd) / p.sDamp : p.m * Math.log(v0 / p.vEnd) / p.sDamp;
  check(near(s.c, want, 1e-6), `n = ${n}, no push: c = ${s.c.toPrecision(7)}, exact ${want.toPrecision(7)}`);
}

// 4 and 7. Energy balance and end speed.
for (const n of [1, 2]) {
  for (const push of [false, true]) {
    const p = { ...M.DEFAULTS, n, push };
    const r = M.solve(p);
    const scale = r.Ek0 + r.Wm;
    check(Math.abs(r.balance) <= 1e-4 * scale, `n = ${n}, push ${push}: energy balance off by ` +
      `${r.balance.toExponential(2)} J of ${scale.toFixed(2)} J`);
    check(near(r.damper.vEnd, p.vEnd, 1e-5) && !r.damper.stopped, `n = ${n}, push ${push}: end speed ` +
      `${r.damper.vEnd.toFixed(6)} m/s, allowed ${p.vEnd} m/s, c = ${r.c.toPrecision(4)}`);
    // 8. Same energy in the even-force reference.
    const e = r.Fconst * p.sDamp;
    check(near(e, r.Wd, 1e-9), `n = ${n}, push ${push}: constant force ${r.Fconst.toFixed(1)} N × stroke = ` +
      `${e.toFixed(3)} J, damper work ${r.Wd.toFixed(3)} J`);
  }
}

// 5. No-load speed.
{
  const p = { ...M.DEFAULTS };
  const v = M.noLoadSpeed(p);
  check(M.motorForce(v * 0.9999, p) > 0 && M.motorForce(v * 1.0001, p) === 0,
    `no-load speed ${v.toFixed(4)} m/s: force just below ${M.motorForce(v * 0.9999, p).toExponential(2)} N, just above 0 N`);
  check(M.motorForce(0, p) === p.Fmax, `at rest the motor gives its full force ${p.Fmax} N`);
}

// 9. Hand-set constant and the terminal speed.
{
  const p = { ...M.DEFAULTS, n: 2, push: true, cSet: 2000, sDamp: 0.5 };
  const r = M.solve(p);
  const vt = M.terminalSpeed(p, p.cSet);
  check(r.c === 2000 && r.manual, `hand-set c = ${r.c} is used`);
  check(near(r.damper.vEnd, vt, 1e-3), `push, long stroke: end speed ${r.damper.vEnd.toFixed(5)} m/s, terminal speed ` +
    `${vt.toFixed(5)} m/s`);
  check(near(p.cSet * vt ** 2, M.motorForce(vt, p), 1e-9), `terminal speed: damper force equals motor force ` +
    `${M.motorForce(vt, p).toFixed(2)} N`);
}

// 6. The defaults.
{
  const r = M.solve({ ...M.DEFAULTS });
  check(Math.abs(r.v0 - 3.80) < 0.03, `defaults: impact speed ${r.v0.toFixed(3)} m/s, hand simulation 3.80 m/s`);
  check(r.v0 < r.vNoLoad, `defaults: impact speed below the no-load speed ${r.vNoLoad.toFixed(3)} m/s`);
}

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
