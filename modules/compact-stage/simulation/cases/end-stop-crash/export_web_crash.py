"""Crash cases, time histories and checks for the results web page.

Run it from the repository root, after run_fem.py:

    freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/export_web_crash.py

Any Python 3.11+ with numpy also works. It uses the functions of evaluate.py
and crash_model.py (read from those files), so it computes exactly the same
cases. It adds what the page needs to show that the numbers hold together:

- the time history of each case (forces, travel, accelerations, block loads);
- an energy balance and an impulse balance of each case;
- an independent model in one direction only, with its own simple integrator;
- hand calculations of the bumper capacity and of the pocket wall;
- a comparison with the committed results.json (must be the same numbers).

Output: simulation/cases/end-stop-crash-results/crash_data.js (committed), one
plain script for the web page (window.CRASH_DATA).
"""

import functools
import json
import math
import os
import sys
import tomllib

import numpy as np

print = functools.partial(print, flush=True)

HERE = os.path.dirname(os.path.abspath(globals().get("__file__", os.path.join(
    os.getcwd(), "modules", "compact-stage", "simulation", "cases", "end-stop-crash", "x"))))
MODULE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(MODULE, "..", ".."))
WEB = os.path.join(REPO, "simulation", "cases", "end-stop-crash-results")
RESULTS = os.path.join(MODULE, "simulation", "results", "end-stop-crash")
POINTS = 450  # time samples per case on the page


def load_evaluate():
    """The functions of evaluate.py, without running its main()."""
    path = os.path.join(HERE, "evaluate.py")
    with open(path) as f:
        src = f.read()
    head, tail = src.rsplit("\nmain()", 1)
    if tail.strip():
        raise SystemExit("evaluate.py changed: it no longer ends with main()")
    ns = {"__file__": path, "__name__": "evaluate"}
    exec(compile(head, path, "exec"), ns)
    return ns


EV = load_evaluate()
cm = EV["cm"]
G = cm.G


def sig(x, n=4):
    """Round to n significant digits, to keep the page data small."""
    if isinstance(x, (list, tuple, np.ndarray)):
        return [sig(v, n) for v in x]
    x = float(x)
    if x == 0 or not math.isfinite(x):
        return 0.0 if not math.isfinite(x) else x
    return float("%.*g" % (n, x))


def pick(t, keep):
    """About POINTS indices spread over the time, plus the peaks in keep."""
    n = len(t)
    idx = set(np.linspace(0, n - 1, min(n, POINTS)).astype(int).tolist())
    for arr in keep:
        k = int(np.argmax(arr))
        idx.update(range(max(0, k - 2), min(n, k + 3)))
    return np.array(sorted(idx))


def block_series(cfg, model, rec):
    """Equivalent load P of each guide block over time (same rule as block_check)."""
    gd = cfg["guides"]
    m0 = np.array([gd["m0x"], gd["m0y"], gd["m0z"]]) * 1e-3
    own = np.abs(rec["th"]) * model.k_own
    out = []
    for b in range(4):
        p = (np.abs(rec["blocks"][:, b, 1]) + np.abs(rec["blocks"][:, b, 2])
             + gd["c0"] * (own[:, 0] / m0[0] + own[:, 1] / m0[1] + own[:, 2] / m0[2]))
        out.append(p)
    return np.array(out)


def energy_check(model, rec):
    """Energy balance from the first touch to the deepest point of the crash.

    In: kinetic energy at the touch, work of the motor, of gravity and the
    magnet, and of the guide block springs. Out: work done on the bumpers and
    on the end wall, and the kinetic energy that is left (mostly turning).
    """
    q = np.concatenate([rec["u"], rec["th"]], axis=1)
    qd = np.concatenate([rec["v"], rec["w"]], axis=1)
    k = int(np.argmin(rec["u"][:, 0]))
    m, J = model.m, model.J

    def ke(i):
        return 0.5 * m * float(qd[i, :3] @ qd[i, :3]) + 0.5 * float(qd[i, 3:] @ J @ qd[i, 3:])

    e0 = ke(0)  # one time step after the first touch
    # Work of the contact forces: force times the shortening of each contact.
    w_b = 0.0
    for i, r in enumerate(model.r_bump):
        d = -(q[:, 0] + q[:, 4] * r[2] - q[:, 5] * r[1])
        w_b += float(np.trapezoid(rec["fb"][:k + 1, i], d[:k + 1]))
    r = model.r_end
    dm = -(q[:, 0] + q[:, 4] * r[2] - q[:, 5] * r[1]) - model.gap
    w_m = float(np.trapezoid(rec["fm"][:k + 1], dm[:k + 1]))
    # Constant forces (motor, gravity, magnet) and the block springs.
    motor = np.zeros(6)
    if model.push:
        rf = model.r_forcer
        f = -model.f_motor
        motor = np.array([f, 0.0, 0.0, 0.0, rf[2] * f, -rf[1] * f])
    c_rest = model.c6 - motor
    w_motor = float(motor @ (q[k] - q[0]))
    w_const = float(c_rest @ (q[k] - q[0]))
    K = model.K6

    def v_spring(i):
        return -0.5 * float(q[i] @ K @ q[i])

    w_spring = v_spring(0) - v_spring(k)
    e_in = e0 + w_motor
    resid = ke(0) + w_motor + w_const + w_spring - w_b - w_m - ke(k)
    return {"kinetic_at_touch": e0, "motor_work": w_motor, "gravity_magnet_work": w_const,
            "block_spring_work": w_spring, "bumper_work": w_b, "wall_work": w_m,
            "kinetic_left": ke(k), "residual": resid, "residual_pct": 100.0 * resid / e_in,
            "time_of_deepest_point_ms": float(rec["t"][k] * 1e3)}


def impulse_check(model, rec):
    """Push of all forces along x over time = mass x change of speed."""
    fx = rec["fb"].sum(axis=1) + rec["fm"] + model.c6[0]
    imp = float(np.trapezoid(fx, rec["t"]))
    dv = float(rec["v"][-1, 0] - rec["v"][0, 0])
    # rec starts one step after the touch: use the first recorded speed.
    return {"impulse": imp, "mass_times_speed_change": model.m * dv,
            "error_pct": 100.0 * (imp - model.m * dv) / (model.m * abs(dv))}


def one_direction_model(model):
    """The same force laws, but in one direction only, with its own integrator.

    No turning, no guide blocks. Semi-implicit Euler with a 0.2 us step. It
    shows how much the turning of the carriage changes the result.
    """
    m, v, x, dt = model.m, model.speed, 0.0, 2e-7
    push = model.f_motor if model.push else 0.0
    peak_pos = 0.0
    peak_b = peak_m = 0.0
    bump_back = False
    metal_peak = 0.0
    rebound = 0.0
    t = 0.0
    while t < 0.05:
        fb = 2.0 * model.bumper.load(x)
        if v < 0:
            bump_back = True
        if bump_back:
            fb *= 1.0 - model.bumper.absorbed
        fm = 0.0
        if model.metal is not None:
            dmx = x - model.gap
            if dmx > 0 or metal_peak > 0:
                if dmx >= metal_peak:
                    fm = model.metal.load(dmx)
                else:
                    fm = max(0.0, model.metal.load(metal_peak) - model.metal.k_el * (metal_peak - dmx))
            metal_peak = max(metal_peak, dmx)
        a = (push - fb - fm) / m
        v += a * dt
        x += v * dt
        t += dt
        peak_pos = max(peak_pos, x)
        peak_b = max(peak_b, fb)
        peak_m = max(peak_m, fm)
        rebound = max(rebound, -v)  # the same rule as evaluate.py: fastest speed back
        if v < 0 and x < 0 and push == 0.0:
            break
        if push and t > 0.03:
            break
    return {"travel_mm": peak_pos * 1e3, "peak_force_bumpers": peak_b, "peak_force_metal": peak_m,
            "rebound_speed": rebound}


def case_record(cfg, label, group, res):
    rec = res["_rec"]
    model = res["_model"]
    t = rec["t"]
    ah = cm.point_accel(rec, model.r_head)
    amag = np.linalg.norm(ah, axis=1)
    fb = rec["fb"]
    fm = rec["fm"]
    pb = block_series(cfg, model, rec)
    idx = pick(t, [fb.sum(axis=1), fm, amag, pb.max(axis=0), -rec["u"][:, 0]])
    series = {
        "t_ms": sig(t[idx] * 1e3, 5),
        "travel_mm": sig(-rec["u"][idx, 0] * 1e3),
        "speed": sig(-rec["v"][idx, 0]),
        "bumper_1": sig(fb[idx, 0]),
        "bumper_2": sig(fb[idx, 1]),
        "metal": sig(fm[idx]),
        "decel_g": sig(rec["a"][idx, 0] / G),
        "head": sig(amag[idx]),
        "pitch_mrad": sig(rec["th"][idx, 1] * 1e3),
        "yaw_mrad": sig(rec["th"][idx, 2] * 1e3),
        "block_p": [sig(pb[b, idx]) for b in range(4)],
    }
    summary = EV["strip"](res)
    out = {"label": label, "group": group, "summary": summary, "series": series,
           "energy": energy_check(model, rec), "impulse": impulse_check(model, rec),
           "one_direction": one_direction_model(model),
           "parts": [{"name": p.name, "mass": p.mass, "com_mm": sig((p.com * 1e3).tolist(), 5),
                      "group": p.group} for p in model.parts]}
    return out


def compare(a, b, path="", out=None):
    """Largest relative difference between two nested number trees."""
    if out is None:
        out = {"max_rel": 0.0, "where": "", "count": 0}
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k in b:
                compare(a[k], b[k], path + "/" + k, out)
    elif isinstance(a, list) and isinstance(b, list):
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, "%s[%d]" % (path, i), out)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        out["count"] += 1
        den = max(abs(a), abs(b), 1e-9)
        rel = abs(a - b) / den
        if rel > out["max_rel"] and max(abs(a), abs(b)) > 1e-6:
            out["max_rel"] = rel
            out["where"] = path
    return out


def hand_checks(cfg, fem):
    b = cfg["bumper"]
    n = b["curve_exponent"]
    s = b["stroke"] * 1e-3
    f_full = b["energy_per_stroke"] / (s * (1.0 - 1.0 / (1.0 + n)))
    # Pocket wall behind one bumper: a plate 3 mm thick, 24 mm wide (pocket
    # width), 22.4 mm high (z = 17.5 to 39.9). As a bound, take a strip that
    # spans the 24 mm width, clamped at both sides, and ignore the help of the
    # bottom edge. The real plate is held on three edges, so it is stiffer.
    t, L, h = 3.0, 24.0, 22.35
    W = 2500.0  # N on one pocket, half of 5 kN
    Z = h * t * t / 6.0
    I = h * t ** 3 / 12.0
    E = cfg["material_base"]["youngs_modulus"]
    pt = {"moment": W * L / 8.0, "stress": W * L / 8.0 / Z, "deflection": W * L ** 3 / (192 * E * I)}
    ud = {"moment": W * L / 12.0, "stress": W * L / 12.0 / Z, "deflection": W * L ** 3 / (384 * E * I)}
    lv = [x for x in fem["pocket"]["levels"] if x["force"] == 5000.0][0]
    return {
        "bumper": {"force_at_full_stroke_N": f_full, "energy_two_bumpers_J": 2 * b["energy_per_stroke"],
                   "energy_two_bumpers_emergency_J": 2 * b["energy_emergency"],
                   "stroke_mm": b["stroke"], "exponent": n},
        "pocket_wall": {"thickness": t, "span": L, "height": h, "load_per_pocket": W,
                        "point_load": pt, "spread_load": ud,
                        "fem_stress": lv["von_mises_max_at_peak"], "fem_displacement": lv["displacement_at_peak"],
                        "fem_stiffness": fem["pocket"]["elastic_stiffness_n_per_mm"]},
        "punching_shear_MPa": W / (math.pi * cfg["fem"]["pocket_disc_diameter"] * t),
        "end_wall_period_ms": 1e3 / fem["modes_hz"][0],
    }


def main():
    with open(os.path.join(HERE, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)
    with open(os.path.join(RESULTS, "fem.json")) as f:
        fem = json.load(f)
    with open(os.path.join(RESULTS, "results.json")) as f:
        committed = json.load(f)

    run_case = EV["run_case"]
    moving = cm.stage_parts(cfg, moving_only=True)
    cases = []
    named = [("no payload", moving, False),
             ("1 kg at 50 mm", moving + cm.payload_part(cfg, 1.0, 50.0), False)]
    for pos in cfg["cross_stage"]["carriage_positions"]:
        named.append(("cross stage, upper carriage %+.0f mm" % pos, moving + cm.cross_stage_parts(cfg, pos), True))
    rerun = {}
    for label, parts, upper in named:
        r = run_case(cfg, fem, parts, label, upper=upper)
        rerun[label] = EV["strip"](r)
        cases.append(case_record(cfg, label, "named", r))
        print("named %-40s head %.0f m/s2, fsl %.2f" % (label, r["read_head"]["accel_peak"], r["block_fsl"]))
        if label.endswith("+108 mm"):
            continue
        r = run_case(cfg, fem, parts, label + ", motor off", push=False, upper=upper)
        cases.append(case_record(cfg, label + ", motor off", "motor off", r))
        r = run_case(cfg, fem, parts, label + ", 2.2 m/s trip", speed=cfg["crash"]["speed_trip"], upper=upper)
        cases.append(case_record(cfg, label + ", 2.2 m/s trip", "overspeed", r))
        print("   + motor off and 2.2 m/s variants")

    for mp in cfg["table"]["payload"]:
        for h in cfg["table"]["com_height"]:
            label = "%g kg at %g mm" % (mp, h)
            r = run_case(cfg, fem, moving + cm.payload_part(cfg, mp, h), label)
            rec = case_record(cfg, label, "table", r)
            rec["payload_kg"] = mp
            rec["com_height_mm"] = h
            cases.append(rec)
        print("table %g kg done" % mp)

    same = compare(rerun, committed["cases"])
    print("Compared with the committed results.json: %d numbers, largest difference %.2e (%s)"
          % (same["count"], same["max_rel"], same["where"]))
    worst_e = max(abs(c["energy"]["residual_pct"]) for c in cases)
    worst_i = max(abs(c["impulse"]["error_pct"]) for c in cases)
    print("Largest energy balance error %.3f %%, impulse error %.3f %%" % (worst_e, worst_i))

    x, fpk = cm.one_dof_check(cfg)
    data = {
        "inputs": cfg,
        "fem": {k: fem[k] for k in ("mesh", "material", "load_area", "modes_hz")},
        "fem_curves": {k: {"curve": fem[k]["curve"], "levels": fem[k]["levels"],
                           "elastic_stiffness_n_per_mm": fem[k]["elastic_stiffness_n_per_mm"],
                           "force_reached": fem[k]["force_reached"]} for k in ("pocket", "band")},
        "cases": cases,
        "spread": committed["spread"],
        "checks": {
            "same_as_results_json": same,
            "damper_page": {"model_compression_mm": x, "model_peak_force": fpk,
                            "page_compression_mm": 6.2, "page_peak_force": 2620.0},
            "hand": hand_checks(cfg, fem),
            "energy_worst_pct": worst_e,
            "impulse_worst_pct": worst_i,
        },
    }
    os.makedirs(WEB, exist_ok=True)
    js = os.path.join(WEB, "crash_data.js")
    with open(js, "w") as f:
        f.write("// Made by modules/compact-stage/simulation/cases/end-stop-crash/export_web_crash.py."
                " Do not edit.\n")
        f.write("window.CRASH_DATA = ")
        json.dump(data, f, separators=(",", ":"))
        f.write(";\n")
    print("Done: %s (%.1f MB)" % (js, os.path.getsize(js) / 1e6))


main()
