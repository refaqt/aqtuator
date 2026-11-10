// Checks the data of the end-stop crash results page before it is published.
// Node 18 or newer, no packages:
//   node simulation/cases/end-stop-crash-results/check_data.mjs
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const ctx = { window: {} };
vm.createContext(ctx);
for (const f of ["crash_data.js", "fem_fields.js"]) {
  vm.runInContext(fs.readFileSync(path.join(here, f), "utf8"), ctx, { filename: f });
}
// The page script must at least parse.
new vm.Script(fs.readFileSync(path.join(here, "page.js"), "utf8"), { filename: "page.js" });

const D = ctx.window.CRASH_DATA;
const F = ctx.window.FEM_FIELDS;
let failed = 0;
function check(ok, text) {
  console.log((ok ? "ok    " : "FAIL  ") + text);
  if (!ok) failed++;
}

const count = (g) => D.cases.filter((c) => c.group === g).length;
check(count("named") === 4 && count("motor off") === 3 && count("overspeed") === 3 && count("table") === 35,
  "case groups: 4 named, 3 motor off, 3 overspeed, 35 payload table");
check(D.checks.same_as_results_json.count > 500 && D.checks.same_as_results_json.max_rel < 1e-9,
  `page data equal the committed results.json (${D.checks.same_as_results_json.count} numbers)`);
for (const c of D.cases) {
  const S = c.series;
  const n = S.t_ms.length;
  const keys = ["travel_mm", "bumper_1", "bumper_2", "metal", "head", "decel_g"];
  const sameLen = keys.every((k) => S[k].length === n) && S.block_p.every((b) => b.length === n);
  const rising = S.t_ms.every((t, i) => i === 0 || t > S.t_ms[i - 1]);
  if (!sameLen || !rising) check(false, `${c.label}: time series lengths or time order`);
  if (Math.abs(c.energy.residual_pct) > 0.5) check(false, `${c.label}: energy balance ${c.energy.residual_pct} %`);
  if (Math.abs(c.impulse.error_pct) > 1) check(false, `${c.label}: impulse balance ${c.impulse.error_pct} %`);
  if (!c.summary.metal_hit) {
    const d = Math.abs(c.one_direction.travel_mm / c.summary.travel_past_first_touch_mm - 1);
    if (d > 0.03) check(false, `${c.label}: simple model travel differs by ${(100 * d).toFixed(1)} %`);
  }
}
check(failed === 0, `all ${D.cases.length} cases: series, energy (0.5 %), impulse (1 %), simple model travel (3 %)`);

const dp = D.checks.damper_page;
check(Math.abs(dp.model_compression_mm - dp.page_compression_mm) < 0.2, "bumper law agrees with the damper sizing page");

check(F && F.surface && F.pocket && F.band && F.mesh_check, "FEM fields present");
const nNodes = F.mesh.surface_nodes;
const qLen = (q) => Buffer.from(q.b64, "base64").length / 2;
check(qLen(F.surface.x) === nNodes, `surface has ${nNodes} nodes`);
for (const job of ["pocket", "band"]) {
  const st = F[job].steps;
  check(st.length >= 8, `${job}: ${st.length} load steps`);
  const lenOk = st.every((s) => ["ux", "uy", "uz", "vm", "pe"].every((k) => qLen(s[k]) === nNodes));
  check(lenOk, `${job}: every field has one value per surface node`);
  const r0 = st[0].reaction[0] / st[0].force - 1;
  const rMax = Math.max(...st.map((s) => Math.abs(s.reaction[0] / s.force - 1)));
  check(Math.abs(r0) < 0.005 && rMax < 0.02, `${job}: supports carry the load (first step ${(100 * r0).toFixed(2)} %, worst ${(100 * rMax).toFixed(2)} %)`);
  const cv = D.fem_curves[job].curve;
  let worst = 0;
  for (const s of st) {
    if (s.force > D.fem_curves[job].force_reached) continue;
    let d0 = null;
    for (let i = 1; i < cv.length; i++) {
      if (s.force <= cv[i].force) {
        const a = (s.force - cv[i - 1].force) / (cv[i].force - cv[i - 1].force);
        d0 = cv[i - 1].displacement + a * (cv[i].displacement - cv[i - 1].displacement);
        break;
      }
    }
    if (d0) worst = Math.max(worst, Math.abs(s.load_displacement / d0 - 1));
  }
  check(worst < 0.02, `${job}: FEM re-run matches the committed wall curve (worst ${(100 * worst).toFixed(2)} %)`);
}
check(F.mesh_check.length === 3, "mesh check has three meshes");

if (failed) {
  console.log(`${failed} check(s) failed.`);
  process.exit(1);
}
console.log("All checks passed.");
