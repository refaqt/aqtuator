// SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
// SPDX-License-Identifier: GPL-3.0-or-later
//
// Checks the data of the forcer cooling results page before it is published.
// Node 18 or newer, no packages:
//   node simulation/cases/forcer-cooling-thermal-results/check_data.mjs
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const ctx = { window: {} };
vm.createContext(ctx);
for (const f of ["thermal_data.js", "thermal_fields.js"]) {
  vm.runInContext(fs.readFileSync(path.join(here, f), "utf8"), ctx, { filename: f });
}
// The page script must at least parse.
new vm.Script(fs.readFileSync(path.join(here, "page.js"), "utf8"), { filename: "page.js" });

const D = ctx.window.THERMAL_DATA;
const F = ctx.window.THERMAL_FIELDS;
let failed = 0;
function check(ok, text) {
  console.log((ok ? "ok    " : "FAIL  ") + text);
  if (!ok) failed++;
}

const R = D.results;
const M = R.main;
check(Math.abs(M.balance.error_pct) < 0.5, `energy balance of the main case: ${M.balance.error_pct.toFixed(3)} %`);
for (const s of R.sweeps || []) {
  if (Math.abs(s.balance.error_pct) > 0.5) check(false, `${s.label}: energy balance ${s.balance.error_pct.toFixed(3)} %`);
}
check(failed === 0, `energy balance of all ${(R.sweeps || []).length} sweep cases within 0.5 %`);
const w = D.checks;
check(Math.abs(w.water_rise_hand - w.water_rise_model) < 0.02, "water warm-up agrees with the heat into the water");
check(Math.abs(w.loss_hand - w.loss_model) < 0.05, "copper loss agrees with the coil temperature");
check(M.coil_max > M.forcer_face_mean && M.forcer_face_mean > M.params.t_in, "coil > forcer face > water inlet");
check(M.water_out > M.params.t_in, "water leaves warmer than it enters");
const sorted = (a) => a.every((v, i) => i === 0 || v >= a[i - 1] - 1e-9);
check(sorted(M.water_profile.T), "water temperature rises along its path");
const fl = (R.sweeps || []).filter((s) => s.group === "flow");
check(fl.length >= 4 && fl.every((s, i) => i === 0 || s.coil_max <= fl[i - 1].coil_max + 1e-6), "more flow gives a cooler coil");
check(R.transient && R.transient.length > 20 && R.transient.every((x, i) => i === 0 || x.t > R.transient[i - 1].t),
  "warm-up history present, time rising");
check(R.mech_main && isFinite(R.mech_main.top_lift_um), "thermal growth present");
check(D.materials.length >= 12 && D.materials.every((m) => m.source.startsWith("https://")), "every material has a data sheet link");
check(D.hydraulics.pumps.some((p) => p.recommended), "a pump is recommended");

const n = F.n;
const qLen = (q) => Buffer.from(q.b64, "base64").length / 2;
check(["x", "y", "z", "T", "ux", "uy", "uz", "cux", "cuy", "cuz"].every((k) => qLen(F[k]) === n), `every field has one value per point (${n} points)`);
check(Buffer.from(F.kind, "base64").length === n && Buffer.from(F.body, "base64").length === n, "boundary kind and part for every point");
const tris = new Uint32Array(Uint8Array.from(Buffer.from(F.tris, "base64")).buffer);
check(tris.length % 3 === 0 && tris.every((t) => t < n), `${tris.length / 3} triangles, all point to existing points`);
check(F.bodies.reduce((a, b) => a + b.n, 0) === n, "parts add up to all points");

if (failed) {
  console.log(`\n${failed} check(s) failed`);
  process.exit(1);
}
console.log("\nall checks passed");
