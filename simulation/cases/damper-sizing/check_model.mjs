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
// 6. With no speed limit, the defaults (MK21, 5 kg, 218 mm, 310 V, hot coil)
//    give about 3.80 m/s, the value of the hand simulation of 2026-10-19.
//    With the default speed limit of 2 m/s, the impact speed is 2 m/s.
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
  const p = { ...M.DEFAULTS, Vdc: 1e9, vLimit: 0 };
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

// 6. The defaults, with and without the speed limit.
{
  const r = M.solve({ ...M.DEFAULTS, vLimit: 0 });
  check(Math.abs(r.v0 - 3.80) < 0.03, `no speed limit: impact speed ${r.v0.toFixed(3)} m/s, hand simulation 3.80 m/s`);
  check(r.v0 < r.vNoLoad && !r.limited, `no speed limit: impact speed below the no-load speed ${r.vNoLoad.toFixed(3)} m/s`);
  const d = M.solve({ ...M.DEFAULTS });
  check(d.limited && Math.abs(d.v0 - M.DEFAULTS.vLimit) < 1e-12,
    `defaults: impact speed ${d.v0.toFixed(3)} m/s, speed limit ${M.DEFAULTS.vLimit} m/s, ${d.Ek0.toFixed(1)} J`);
  // Full force from rest to the limit, then the rest of the stroke at the limit.
  const p = { ...M.DEFAULTS, Vdc: 1e9 };
  const a = M.accelerate(p);
  const s1 = p.m * p.vLimit ** 2 / (2 * p.Fmax);
  const tw = p.m * p.vLimit / p.Fmax + (p.sAcc - s1) / p.vLimit;
  check(near(a.t, tw, 1e-5), `speed limit, constant force: time ${(a.t * 1e3).toFixed(4)} ms, exact ${(tw * 1e3).toFixed(4)} ms`);
}

// 10. Bumper, linear spring (p = 1), motor off: k = 2·E_r/s², the carriage
//     stops at x = v₀·√(m/k) after a quarter period (π/2)·√(m/k), and comes
//     back at √(1 − absorb)·v₀.
{
  const p = { ...M.DEFAULTS, stopType: "bumper", pBump: 1, push: false };
  const r = M.solveBumper(p);
  const k = 2 * p.Ebump / p.sBump ** 2;
  const xw = r.v0 * Math.sqrt(p.m / k);
  check(near(r.bumper.xMax, xw, 1e-6) && !r.bumper.bottomed,
    `bumper p = 1: compression ${(r.bumper.xMax * 1e3).toFixed(4)} mm, exact ${(xw * 1e3).toFixed(4)} mm`);
  check(near(r.FdPeak, k * xw, 1e-6), `bumper p = 1: peak force ${r.FdPeak.toFixed(1)} N, k·x = ${(k * xw).toFixed(1)} N`);
  const tw = Math.PI / 2 * Math.sqrt(p.m / k);
  check(near(r.bumper.t, tw, 1e-4), `bumper p = 1: time to stop ${(r.bumper.t * 1e3).toFixed(4)} ms, exact ${(tw * 1e3).toFixed(4)} ms`);
  const vb = Math.sqrt(1 - p.absorb) * r.v0;
  check(near(r.vBack, vb, 1e-6), `bumper p = 1: rebound ${r.vBack.toFixed(4)} m/s, √(1 − absorb)·v₀ = ${vb.toFixed(4)} m/s`);
}

// 11. Bumper, p = 2, motor off: ½·m·v₀² = F_full·s/3·(x/s)³.
{
  const p = { ...M.DEFAULTS, stopType: "bumper", pBump: 2, push: false };
  const r = M.solveBumper(p);
  const xw = p.sBump * Math.cbrt(3 * r.Ek0 / (M.bumperFull(p) * p.sBump));
  check(near(r.bumper.xMax, xw, 1e-6), `bumper p = 2: compression ${(r.bumper.xMax * 1e3).toFixed(4)} mm, exact ${(xw * 1e3).toFixed(4)} mm`);
}

// 12. Bumper energy balance, with and without the push, for p = 0.5, 1 and 2.
for (const pBump of [0.5, 1, 2]) {
  for (const push of [false, true]) {
    const p = { ...M.DEFAULTS, stopType: "bumper", pBump, push, sBump: 0.03, Ebump: 60 };
    const r = M.solveBumper(p);
    check(Math.abs(r.balance) <= 1e-4 * r.Etotal, `bumper p = ${pBump}, push ${push}: energy balance off by ` +
      `${r.balance.toExponential(2)} J of ${r.Etotal.toFixed(2)} J`);
  }
}

// 13. A bumper that is too small bottoms out. With the motor off, the energy
//     left at full compression is the impact energy minus the catalog energy.
{
  const p = { ...M.DEFAULTS, stopType: "bumper", push: false, Ebump: 4 };
  const r = M.solveBumper(p);
  check(r.bumper.bottomed && near(r.Ek1, r.Ek0 - p.Ebump, 1e-6),
    `bumper bottoms out: ${r.Ek1.toFixed(4)} J left, ${r.Ek0.toFixed(2)} − ${p.Ebump} J = ${(r.Ek0 - p.Ebump).toFixed(4)} J`);
}

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
