// Checks for turning_model.js. Node 18 or newer, no packages:
//
//     node simulation/cases/hard-turning-stability/check_model.mjs
//
// 1. The motor loops meet the robustness rules of the cutting force page.
// 2. With very stiff guides and shank (within 1 %), the tip compliance along X and Z is the
//    linear motor loop of the cutting force page, for the same mass.
// 3. The static structure is the sum of the two block sets and the shank,
//    each worked out on its own (series springs), and it is symmetric.
// 4. With rigid carriages, the shank is one mass on a spring: the peak sits at
//    √(k/m), with height 1/(2ζk).
// 5. The structure tends to its static value at low frequency, and to the tip
//    mass line −1/(m ω²) far above every mode.
// 6. The step from the sampled loop to the bare mass at 0.98·fs/2 is small
//    against the lowest real part.
// 7. The chip width and the edge normal are continuous where the nose meets
//    the straight edge, and the forces match a hand calculation.
// 8. The stable depth at the chosen speed solves the chatter equation, and
//    agrees with the lobe envelope of control_model.js.
// 9. The lobes never go below the floor, and touch it.
// 10. For one direction only (chip and force along X), the floor is the one
//     of the cutting force page: −1/min Re G.

import "../cutting-force-rejection/control_model.js";
import "./turning_model.js";
const CM = globalThis.ControlModel;
const T = globalThis.TurningModel;

let failed = 0;
const check = (ok, text) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${text}`);
  if (!ok) failed++;
};
const near = (got, want, tol) => Math.abs(got / want - 1) <= tol;
const q = { ...T.TURNING_DEFAULTS };
const um = (v) => (v * 1e6).toFixed(5);

// 1. Robust tuning of both loops.
const loops = T.servoLoops(q);
for (const [ax, L] of Object.entries(loops)) {
  const w = L.tuned.worst;
  check(L.tuned.robust && w.msDb <= L.p.msDb + 0.01 && w.pmDeg >= L.p.pm - 0.01 && w.gmDb >= L.p.gmMinDb - 0.01 && w.rho < 1,
    `${ax}: loop at ${L.tuned.fb.toFixed(1)} Hz for ${L.m.toFixed(2)} kg, sensitivity peak ${w.msDb.toFixed(2)} dB, ` +
    `phase margin ${w.pmDeg.toFixed(1)}°, gain margin ${w.gmDb.toFixed(1)} dB`);
}

// 2. Stiff structure: the tip is the motor loop.
{
  const stiff = { ...q, kRadial: 1e7, shankMm: 200, overhangMm: 1 };
  const S = T.structure(stiff);
  for (const f of [50, 300, 1000, 4000]) {
    const G = T.tipAt(f, S, loops);
    for (const [d, L, ax] of [[0, loops.x, "X"], [2, loops.z, "Z"]]) {
      const want = CM.sineComplianceAt(f, L.p, L.tuned);
      check(near(CM.cabs(G[d][d]), CM.cabs(want), 1e-2),
        `stiff structure, ${ax} at ${f} Hz: tip ${um(CM.cabs(G[d][d]))} µm/N, motor loop ${um(CM.cabs(want))} µm/N`);
    }
  }
}

// 3. Static structure from the parts.
const S = T.structure(q);
const Cs = T.structStatic(S);
{
  const g = T.geometry(q);
  const lo = T.blockSetCompliance(q, "lower", g.tip), up = T.blockSetCompliance(q, "upper", g.tip);
  const tool = T.toolSpring(q);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const want = lo[r][c] + up[r][c] + (r === c ? 1 / tool.k[r] : 0);
    const tol = Math.max(Math.abs(want) * 1e-6, 1e-15);
    check(Math.abs(Cs[r][c] - want) <= tol,
      `static compliance [${"XYZ"[r]}${"XYZ"[c]}] ${um(Cs[r][c])} µm/N, lower + upper + shank ${um(want)} µm/N`);
  }
  let asym = 0;
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) asym = Math.max(asym, Math.abs(Cs[r][c] - Cs[c][r]));
  check(asym < 1e-6 * Cs[1][1], `static compliance is symmetric, largest difference ${um(asym)} µm/N`);
}

// 4. The shank alone.
{
  const rigid = { ...q, kRadial: 1e8 };
  const Sr = T.structure(rigid);
  const tool = T.toolSpring(rigid);
  const fn = Math.sqrt(tool.k[1] / tool.mTip) / (2 * Math.PI);
  const f = CM.logspace(fn * 0.9, fn * 1.1, 4001);
  let iMax = 0, peak = 0;
  f.forEach((fi, i) => { const v = CM.cabs(T.structAt(fi, Sr)[1][1]); if (v > peak) { peak = v; iMax = i; } });
  const want = 1 / (2 * rigid.zetaTool * tool.k[1]);
  check(near(f[iMax], fn, 2e-3), `shank mode at ${f[iMax].toFixed(0)} Hz, √(k/m)/2π = ${fn.toFixed(0)} Hz`);
  check(near(peak, want, 5e-3), `shank peak ${um(peak)} µm/N, 1/(2ζk) = ${um(want)} µm/N`);
}

// 5. Low and high frequency.
{
  const G = T.structAt(0.01, S);
  // The loss 2ζ of the springs makes the magnitude at 0 Hz 1/√(1 + 4ζ²) of
  // the undamped static value (here about 0.2 % lower).
  check(near(CM.cabs(G[1][1]), Cs[1][1] / Math.sqrt(1 + 4 * q.zetaGuide ** 2), 2e-3),
    `structure at 0.01 Hz ${um(CM.cabs(G[1][1]))} µm/N, static ${um(Cs[1][1])} µm/N / √(1 + 4ζ²)`);
  const fHigh = 400000, mTip = T.toolSpring(q).mTip;
  const H = T.structAt(fHigh, S);
  const want = -1 / (mTip * (2 * Math.PI * fHigh) ** 2);
  check(near(H[1][1][0], want, 0.05), `structure at ${fHigh} Hz ${(H[1][1][0] * 1e9).toFixed(4)} nm/N, tip mass line ${(want * 1e9).toFixed(4)} nm/N`);
}

// 6. The step at the end of the sampled range.
const r = T.analyse(q);
{
  for (const [ax, L] of Object.entries(loops)) {
    const fe = 0.98 * L.p.fs / 2;
    const a = CM.sineComplianceAt(fe * (1 - 1e-9), L.p, L.tuned), b = T.servoAt(fe, L);
    const step = CM.cabs(CM.csub(a, b));
    const rel = step / Math.abs(r.lobes.minRe);
    check(rel < 0.05, `${ax}: step at ${fe.toFixed(0)} Hz is ${(step * 1e9).toFixed(4)} nm/N, ` +
      `${(rel * 100).toFixed(2)} % of the lowest real part`);
  }
}

// 7. Cut geometry and forces.
{
  const apN = q.rNose * (1 - Math.cos(q.kappa * Math.PI / 180));
  const bA = T.chipWidth(apN * (1 - 1e-9), q.feed, q.rNose, q.kappa), bB = T.chipWidth(apN * (1 + 1e-9), q.feed, q.rNose, q.kappa);
  check(Math.abs(bA - bB) < 1e-6, `chip width continuous where the nose ends (ap ${apN.toFixed(4)} mm): ${bA.toFixed(6)} and ${bB.toFixed(6)} mm`);
  const pA = T.cut({ ...q, ap: apN * (1 - 1e-9) }).phi, pB = T.cut({ ...q, ap: apN * (1 + 1e-9) }).phi;
  check(Math.abs(pA - pB) < 1e-6, `edge normal continuous there: ${(pA * 180 / Math.PI).toFixed(5)}° and ${(pB * 180 / Math.PI).toFixed(5)}°`);
  const th1 = Math.acos(1 - q.ap / q.rNose), th2 = Math.asin(q.feed / (2 * q.rNose));
  const b = q.rNose * (th1 + th2), h = q.ap * q.feed / b;
  const Fc = q.kc1 * b * h ** (1 - q.mc);
  const c = r.cut;
  check(near(c.b, b, 1e-12) && near(c.Fc, Fc, 1e-12),
    `chip width ${c.b.toFixed(4)} mm, thickness ${(c.h * 1000).toFixed(2)} µm, Fc ${c.Fc.toFixed(1)} N (hand ${Fc.toFixed(1)} N)`);
  check(near(c.phi, (th1 - th2) / 2, 1e-9), `edge normal ${(c.phi * 180 / Math.PI).toFixed(3)}° from X, on the nose (θ1 − θ2)/2 = ${((th1 - th2) / 2 * 180 / Math.PI).toFixed(3)}°`);
  // A long straight edge: the normal turns towards the entering angle κ
  // (measured from X, as the edge is measured from the feed direction).
  const big = T.cut({ ...q, ap: 50 });
  const wantB = q.rNose * (q.kappa * Math.PI / 180 + th2) + (50 - apN) / Math.sin(q.kappa * Math.PI / 180);
  check(near(big.b, wantB, 1e-12) && Math.abs(big.phi * 180 / Math.PI - q.kappa) < 2,
    `ap 50 mm: chip width ${big.b.toFixed(3)} mm, edge normal ${(big.phi * 180 / Math.PI).toFixed(2)}° (straight edge alone: ${q.kappa}°)`);
}

// 8. The limit at the chosen speed.
{
  const c = r.cut, Tsp = 60 / c.rpm, f = r.apAtRpm.f, w = 2 * Math.PI * f;
  const Phi = T.oriented(T.tipAt(f, S, loops), c);
  const bLim = -1 / (2 * c.Kt * 1e6 * Phi[0]);
  const e = [1 - Math.cos(w * Tsp), Math.sin(w * Tsp)];
  const res = CM.cadd([1, 0], CM.cmul([bLim * c.Kt * 1e6, 0], CM.cmul(e, Phi)));
  check(CM.cabs(res) < 0.02, `limit at ${c.rpm.toFixed(0)} rev/min: chip width ${(bLim * 1000).toFixed(4)} mm at ${f.toFixed(1)} Hz, ` +
    `|1 + b·Kt·(1 − e^(−jωT))·Φ| = ${CM.cabs(res).toExponential(2)}`);
  check(near(bLim * 1000, r.apAtRpm.b, 1e-6), `the same chip width as the result, ${r.apAtRpm.b.toFixed(4)} mm`);
  // The envelope of control_model.js lobes() at speeds well above the chosen
  // one, where the lobes are wide enough to compare point by point.
  const phi = (fi) => T.oriented(T.tipAt(fi, S, loops), c);
  for (const rpm of [3000, 5000]) {
    const L = CM.lobes(phi, 10, 60000, 1, rpm * 0.999, rpm * 1.001, 8000, 3);
    const viaLobes = L.depth[1] / (2 * c.Kt * 1e6) * 1000;
    const direct = T.limitAtRpm(phi, 10, 60000, rpm, q, c.Kt * 1e6).b;
    check(near(direct, viaLobes, 0.01), `at ${rpm} rev/min: chip width ${direct.toFixed(4)} mm, lobe envelope ${viaLobes.toFixed(4)} mm`);
  }
}

// 9. Lobes and floor.
{
  const ap = r.lobes.ap.filter(Number.isFinite);
  const lo = Math.min(...ap);
  check(lo >= r.lobes.apFloor * (1 - 1e-6) && lo <= r.lobes.apFloor * 1.05,
    `lowest lobe ${lo.toFixed(4)} mm, floor ${r.lobes.apFloor.toFixed(4)} mm (never below, touches within 5 %)`);
  check(r.apAtRpm.ap >= r.lobes.apFloor * (1 - 1e-6), `limit at the chosen speed ${r.apAtRpm.ap.toFixed(4)} mm is not below the floor`);
}

// 10. One direction: the floor of the cutting force page.
{
  const c1 = { ...r.cut, uh: [1, 0, 0], w: [1, 0, 0] };
  const stiff = T.structure({ ...q, kRadial: 1e7, shankMm: 200, overhangMm: 1 });
  const L = loops.x;
  const viaTurn = CM.lobes((f) => T.oriented(T.tipAt(f, stiff, loops), c1), L.tuned.fb / 200, L.p.fs / 2 * 0.98, 1, 1000, 30000, 3000, 50);
  const viaPage = CM.chatter({ ...L.p, teeth: 1 }, L.tuned, 1000, 30000, 50);
  check(near(viaTurn.floor, viaPage.floor, 2e-3), `one direction, stiff structure: floor ${(viaTurn.floor / 1e6).toFixed(3)} N/µm, ` +
    `cutting force page ${(viaPage.floor / 1e6).toFixed(3)} N/µm`);
}

console.log(failed ? `\n${failed} check(s) failed` : "\nall checks passed");
process.exit(failed ? 1 : 0);
