"""Run the crash cases and check every part. Writes the results and figures.

Run it from the repository root, after run_fem.py:

    freecadcmd modules/compact-stage/simulation/cases/end-stop-crash/evaluate.py

Any Python 3.11+ with numpy and matplotlib also works. FreeCAD's Python has
both.

Output (simulation/results/end-stop-crash/):
- results.json: the numbers of every case and every check;
- payload-table.csv: payload against centre-of-mass height;
- figures (PNG).
"""

import csv
import functools
import json
import math
import os
import sys
import tomllib

import numpy as np

HERE = os.path.dirname(os.path.abspath(globals().get("__file__", os.path.join(
    os.getcwd(), "modules", "compact-stage", "simulation", "cases", "end-stop-crash", "x"))))
sys.path.insert(0, HERE)
import crash_model as cm  # noqa: E402

print = functools.partial(print, flush=True)
CASE = "end-stop-crash"
G = cm.G


# ---------------------------------------------------------------------------
# Screw joints
# ---------------------------------------------------------------------------

SCREW = {  # stress area (mm2), 8.8 yield force = 640 MPa x As
    "M3": {"As": 5.03}, "M4": {"As": 8.78}, "M5": {"As": 14.2},
}


def clamp_force(j, cfg):
    """Clamp force from the torque, VDI 2230 torque formula (N)."""
    mu = cfg["joints"]["friction_thread"]
    k = 0.16 * j["pitch"] + 0.58 * j["d2"] * mu + 0.5 * j["d_km"] * mu  # mm
    return j["torque"] * 1e3 / k


def cluster_wrench(rec, model, parts, point_m, external):
    """Force and moment the joint must put on a group of parts (time series).

    parts: Part objects (positions in the assembly, m). point_m: joint centre.
    external: function(rec_index) -> list of (force 3, point 3) acting on the
    group from outside the joint (gravity is added here).
    """
    a0 = rec["a"]
    al = rec["al"]
    n = len(a0)
    F = np.zeros((n, 3))
    M = np.zeros((n, 3))
    for p in parts:
        r = p.com - model.com
        ap = a0 + np.cross(al, r)
        fin = p.mass * ap - np.array([0.0, 0.0, -p.mass * G])
        F += fin
        M += np.cross(p.com - point_m, fin) + (p.inertia @ al.T).T
    for k in range(n):
        for f, x in external(k):
            F[k] -= f
            M[k] -= np.cross(x - point_m, f)
    return F, M


def joint_check(j, cfg, F, M):
    """Slip, opening and screw force of a bolted joint, over time.

    F, M: force and moment the joint must put on the clamped part, about the
    centre of the screws, in the joint plane (N, N m).
    """
    jc = cfg["joints"]
    holes = np.array(j["holes"]) * 1e-3
    c = holes.mean(axis=0)
    dx = holes[:, 0] - c[0]
    dy = holes[:, 1] - c[1]
    n = len(holes)
    sx = float(np.sum(dx * dx))
    sy = float(np.sum(dy * dy))
    rr = np.hypot(dx, dy)
    fv = clamp_force(j, cfg)
    fv_eff = fv * (1.0 - jc["settling"])
    phi = jc["load_factor"]
    # Pull on each screw (positive = the part pulls away from the joint).
    T = -F[:, 2:3] / n * np.ones((1, n))
    if sy > 0:
        T = T - np.outer(M[:, 0], dy) / sy
    if sx > 0:
        T = T + np.outer(M[:, 1], dx) / sx
    fkr = np.maximum(fv_eff - (1.0 - phi) * T, 0.0)
    shear = np.hypot(F[:, 0], F[:, 1])
    torsion = np.abs(M[:, 2])
    out = {"clamp_force_per_screw": fv, "screws": n}
    for key, mu in (("mu_low", jc["friction_joint"]), ("mu_high", jc["friction_joint_high"])):
        cap_f = mu * fkr.sum(axis=1)
        cap_t = mu * (fkr * rr).sum(axis=1)
        u = shear / np.maximum(cap_f, 1e-9)
        if np.any(rr > 0):
            u = u + torsion / np.maximum(cap_t, 1e-9)
        out["slip_use_" + key] = float(min(u.max(), 99.0))
    out["shear_max"] = float(shear.max())
    out["torsion_max"] = float(torsion.max())
    out["pull_max_per_screw"] = float(max(T.max(), 0.0))
    out["opens"] = bool(np.any(fkr <= 0.0))
    out["screw_force_max"] = float(fv + phi * max(T.max(), 0.0))
    out["screw_yield_8_8"] = 640.0 * SCREW[j["size"]]["As"]
    out["required_friction"] = float((shear / np.maximum(fkr.sum(axis=1), 1e-9)).max())
    out["shift_if_slip_mm"] = j["clearance"]
    # If the joint slips, the screws take the side load in shear (8.8: shear
    # strength about 0.6 x 800 MPa on the stress area). Torsion adds to the
    # outermost screw.
    tau_cap = 0.6 * 800.0 * SCREW[j["size"]]["As"]
    r_out = float(rr.max()) if np.any(rr > 0) else 0.0
    per_screw = shear / n + (torsion * r_out / max(float(np.sum(rr * rr)), 1e-12) if r_out > 0 else 0.0)
    out["screw_shear_use_if_slip"] = float(per_screw.max() / tau_cap)
    return out


# ---------------------------------------------------------------------------
# One crash case
# ---------------------------------------------------------------------------

def run_case(cfg, fem, parts, label, push=True, speed=None, solid=None, rate=1.0, joints=True,
             upper=None):
    model = cm.CrashModel(cfg, parts, fem=fem, solid_stiffness=solid, rate=rate, push=push, speed=speed)
    rec = model.run(t_end=0.08)
    g = cfg["geometry"]
    gd = cfg["guides"]
    mm = 1e-3
    t = rec["t"]
    ux = rec["u"][:, 0]
    travel = -ux.min()  # m, past the first touch
    fb = rec["fb"]
    fbs = fb.sum(axis=1)
    fm = rec["fm"]
    ftot = fbs + fm
    m = model.m
    v = model.speed
    e_kin = 0.5 * m * v * v
    # Base: read the stress curves at the peak forces.
    base = {}
    if fem is not None:
        for key, force in (("pocket", float(fbs.max())), ("band", float(fm.max()))):
            lv = fem[key]["levels"]
            cv = fem[key]["curve"]
            F = np.array([c["force"] for c in cv])
            fmax = F.max()
            def at(name, src=cv):
                return float(np.interp(force, F, [c[name] for c in src]))
            disp = at("displacement")
            k_el = fem[key]["elastic_stiffness_n_per_mm"]
            base[key] = {
                "force": force,
                "beyond_fem_range": force > fmax,
                "von_mises_max": at("von_mises_max"),
                "plastic_strain_max": at("peeq_max"),
                "displacement": disp,
                "lasting_dent": max(0.0, disp - force / k_el),
            }
    # Guide blocks.
    blocks = cm.block_check(cfg, model, rec)
    worst = max(blocks, key=lambda b: b["p_eq_max"])
    p = worst["p_eq_max"]
    if p <= gd["c0"]:
        # Fatigue used up by one crash: the high loads only act over the few
        # millimetres of the stop.
        dmg = 0.0
        ds = np.abs(np.diff(ux))
        pe = np.array([max(b2 for b2 in (abs(rec["blocks"][k, i, 1]) + abs(rec["blocks"][k, i, 2])
                                         for i in range(4))) for k in range(len(t))])
        dmg = float(np.sum(ds * (pe[1:] / gd["c_dyn"]) ** 3) / (gd["nominal_life_km"] * 1e3))
    else:
        dmg = None
    # Read head.
    ah = cm.point_accel(rec, model.r_head)
    amag = np.linalg.norm(ah, axis=1)
    k = int(np.argmax(amag))
    dv = float(np.max(rec["v"][:, 0]) - np.min(rec["v"][:, 0]))
    head_disp = rec["u"] + np.cross(rec["th"], model.r_head)
    # Travel against the rail ends.
    first_touch = g["bumper_tip_x"] - g["pocket_back_x"]
    block_end = g["block_outer_x"] - first_touch - travel / mm
    out = {
        "label": label,
        "moving_mass": m,
        "centre_of_mass_mm": (model.com / mm).tolist(),
        "impact_speed": v,
        "kinetic_energy": e_kin,
        "motor_pushes": push,
        "motor_work": (cfg["crash"]["motor_force"] * travel) if push else 0.0,
        "bumper_rating_emergency": 2 * cfg["bumper"]["energy_emergency"],
        "travel_past_first_touch_mm": travel / mm,
        "bumpers_fully_in": travel / mm > cfg["bumper"]["stroke"],
        "metal_hit": bool(fm.max() > 0),
        "metal_overlap_mm": rec["metal_peak"] / mm,
        "peak_force_per_bumper": float(fb.max()),
        "peak_force_bumpers": float(fbs.max()),
        "peak_force_metal": float(fm.max()),
        "peak_force_total": float(ftot.max()),
        "peak_deceleration_g": float(-rec["a"][:, 0].min() / G),
        "rebound_speed": float(max(rec["v"][:, 0].max(), 0.0)),
        "base": base,
        "blocks": blocks,
        "block_worst_p": p,
        "block_fsl": gd["c0"] / p,
        "block_over_c0": p > gd["c0"],
        "block_life_used_per_crash": dmg,
        "read_head": {
            "accel_peak": float(amag[k]),
            "accel_peak_x": float(np.abs(ah[:, 0]).max()),
            "pulse_width_ms": cm.pulse_width(t, amag) * 1e3,
            "velocity_change": dv,
            "test_velocity_change": 2.0 / math.pi * cfg["read_head"]["shock_limit"] * cfg["read_head"]["shock_duration"] * 1e-3,
            "side_shift_um": float(np.abs(head_disp[:, 1] - head_disp[0, 1]).max() / 1e-6),
            "lift_um": float(np.abs(head_disp[:, 2] - head_disp[0, 2]).max() / 1e-6),
        },
        "block_end_to_rail_end_mm": block_end - g["rail_end_x"],
        "block_body_to_rail_end_mm": block_end + g["block_e2_length"] - g["rail_end_x"],
        "pitch_max_mrad": float(np.abs(rec["th"][:, 1]).max() * 1e3),
        "yaw_max_mrad": float(np.abs(rec["th"][:, 2]).max() * 1e3),
    }
    if joints:
        out["joints"] = joints_for(cfg, model, rec, parts)
    if upper:
        out["upper_stage"] = upper_blocks(cfg, model, rec, parts)
    out["_rec"] = rec
    out["_model"] = model
    return out


def joints_for(cfg, model, rec, parts):
    mm = 1e-3
    jd = {j["name"]: j for j in cfg["joint"]}
    res = {}
    by = {p.name: p for p in parts}
    zf = np.zeros(3)
    g = cfg["geometry"]

    def centre(j):
        h = np.array(j["holes"]).mean(axis=0)
        return np.array([h[0], h[1], j["plane_z"]]) * mm

    # Payload or upper stage on carriage-top.
    top_parts = [p for p in parts if p.group in ("payload", "upper-carriage", "upper-fixed")]
    if top_parts:
        j = jd["payload to carriage-top"]
        F, M = cluster_wrench(rec, model, top_parts, centre(j), lambda k: [])
        res[j["name"]] = joint_check(j, cfg, F, M)
    # carriage-top (with what sits on it) on carriage-bottom.
    j = jd["carriage-top to carriage-bottom"]
    grp = [by["carriage-top"]] + top_parts
    F, M = cluster_wrench(rec, model, grp, centre(j), lambda k: [])
    res[j["name"]] = joint_check(j, cfg, F, M)
    # Forcer: motor thrust and magnetic pull act on it from the stators.
    j = jd["forcer to carriage-bottom"]
    xf = np.array(g["forcer_force_point"]) * mm
    fmag = np.array([0.0, 0.0, -cfg["magnet"]["attraction"]])
    fmot = np.array([-cfg["crash"]["motor_force"] if model.push else 0.0, 0.0, 0.0])
    F, M = cluster_wrench(rec, model, [by["forcer"]], centre(j), lambda k: [(fmag, xf), (fmot, xf)])
    res[j["name"]] = joint_check(j, cfg, F, M)
    # Read head.
    j = jd["read head to carriage-bottom"]
    head = cm.Part("read head", cfg["read_head"]["mass"], g["read_head"], [36.0, 14.8, 13.5])
    F, M = cluster_wrench(rec, model, [head], centre(j), lambda k: [])
    res[j["name"]] = joint_check(j, cfg, F, M)
    # One guide block: its rail pushes on it.
    j = dict(jd["carriage-bottom to one guide block"])
    worst = None
    for b in range(4):
        xb = g["block_x"][b // 2]
        yb = g["block_y"][b % 2]
        jb = dict(j)
        jb["holes"] = [[xb + h[0], yb + h[1]] for h in j["holes"]]
        blk = cm.Part("block", 0.15, [xb, yb, 24.9], [40.0, 34.0, 20.0])
        xr = np.array([xb, yb, g["block_z"]]) * mm
        F, M = cluster_wrench(rec, model, [blk], centre(jb), lambda k, b=b, xr=xr: [(rec["blocks"][k, b], xr)])
        r = joint_check(jb, cfg, F, M)
        if worst is None or r["slip_use_mu_low"] > worst["slip_use_mu_low"]:
            worst = r
    res[j["name"]] = worst
    # Base on the machine table: everything the carriage does to the base.
    j = jd["base to machine table"]
    base_part = cm.Part("base", cfg["fixed"][0]["mass"], cfg["fixed"][0]["com"], cfg["fixed"][0]["size"])
    F, M = cluster_wrench(rec, model, parts, centre(j), lambda k: [])
    # F is what the base puts on the carriage. The table must put the same on
    # the base, plus the weight of the base itself (that adds clamp force).
    F[:, 2] += base_part.mass * G
    res[j["name"]] = joint_check(j, cfg, F, M)
    return res


def upper_blocks(cfg, model, rec, parts):
    """Guide blocks of the upper stage: the crash pushes its carriage sideways."""
    gd = cfg["guides"]
    up = [p for p in parts if p.group == "upper-carriage"]
    m, com, J = cm.combine(up)
    a = rec["a"] + np.cross(rec["al"], com - model.com)
    g = cfg["geometry"]
    z_balls = (g["carriage_top_plane"] + g["block_z"]) * 1e-3
    rail_gap = (g["block_y"][1] - g["block_y"][0]) * 1e-3
    f_lat = m * np.abs(a[:, 0])                       # along the lower travel = across the upper rails
    f_vert = m * (G - a[:, 2]) + cfg["magnet"]["attraction"]
    roll = f_lat * (com[2] - z_balls)                 # tips the upper carriage over its rails
    fz = f_vert / 4.0 + roll / rail_gap / 2.0
    fy = f_lat / 4.0
    p = np.abs(fz) + fy
    return {"mass": m, "lateral_force_max": float(f_lat.max()), "block_p_max": float(p.max()),
            "block_fsl": float(gd["c0"] / p.max())}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not k.startswith("_")}
    if isinstance(d, (list, tuple)):
        return [strip(v) for v in d]
    if isinstance(d, (np.floating, np.integer)):
        return d.item()
    if isinstance(d, np.bool_):
        return bool(d)
    return d


def main():
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    out_dir = os.path.join(root, "simulation", "results", CASE)
    with open(os.path.join(HERE, "case.toml"), "rb") as f:
        cfg = tomllib.load(f)
    fem_path = os.path.join(out_dir, "fem.json")
    if not os.path.exists(fem_path):
        print("ERROR: run run_fem.py first (no %s)" % fem_path)
        sys.exit(1)
    with open(fem_path) as f:
        fem = json.load(f)

    # Check the bumper model against the damper sizing page.
    x, fpk = cm.one_dof_check(cfg)
    print("Check against the damper sizing page (5 kg, 2 m/s, motor off): %.2f mm, %.0f N "
          "(page: 6.2 mm, 2620 N)" % (x, fpk))
    results = {"check_damper_page": {"compression_mm": x, "peak_force": fpk}}

    moving = cm.stage_parts(cfg, moving_only=True)
    named = {}
    named["no payload"] = run_case(cfg, fem, moving, "no payload")
    named["1 kg at 50 mm"] = run_case(cfg, fem, moving + cm.payload_part(cfg, 1.0, 50.0), "1 kg at 50 mm")
    for pos in cfg["cross_stage"]["carriage_positions"]:
        lab = "cross stage, upper carriage %+.0f mm" % pos
        named[lab] = run_case(cfg, fem, moving + cm.cross_stage_parts(cfg, pos), lab, upper=True)
    for lab, r in named.items():
        print("%-40s m %.2f kg, E %.1f J, travel %.2f mm, bumpers %.0f N, metal %.0f N, "
              "fsl %.2f, head %.0f m/s2" % (lab, r["moving_mass"], r["kinetic_energy"],
                                            r["travel_past_first_touch_mm"], r["peak_force_bumpers"],
                                            r["peak_force_metal"], r["block_fsl"], r["read_head"]["accel_peak"]))

    # Spread of the unknown inputs, for the three named cases.
    spread = {}
    for lab in ("no payload", "1 kg at 50 mm", "cross stage, upper carriage +0 mm"):
        parts = named[lab]["_model"].parts
        rows = []
        for solid in cfg["bumper"]["solid_stiffness_sweep"]:
            for rate in cfg["bumper"]["rate_factor_sweep"]:
                r = run_case(cfg, fem, parts, lab, solid=solid, rate=rate, joints=False)
                rows.append({"solid_stiffness": solid, "rate": rate,
                             "peak_force_total": r["peak_force_total"],
                             "peak_force_metal": r["peak_force_metal"],
                             "block_fsl": r["block_fsl"],
                             "head_accel": r["read_head"]["accel_peak"]})
        r_off = run_case(cfg, fem, parts, lab, push=False, joints=False)
        r_trip = run_case(cfg, fem, parts, lab, speed=cfg["crash"]["speed_trip"], joints=False)
        spread[lab] = {"sweep": rows,
                       "motor_off": {"peak_force_total": r_off["peak_force_total"], "block_fsl": r_off["block_fsl"],
                                     "head_accel": r_off["read_head"]["accel_peak"], "metal": r_off["peak_force_metal"]},
                       "speed_trip": {"peak_force_total": r_trip["peak_force_total"], "block_fsl": r_trip["block_fsl"],
                                      "head_accel": r_trip["read_head"]["accel_peak"], "metal": r_trip["peak_force_metal"]}}
        print("spread %-30s total force %.0f to %.0f N" % (lab, min(x["peak_force_total"] for x in rows),
                                                           max(x["peak_force_total"] for x in rows)))

    # Payload table.
    table = []
    tc = cfg["table"]
    for mp in tc["payload"]:
        for h in tc["com_height"]:
            r = run_case(cfg, fem, moving + cm.payload_part(cfg, mp, h), "%g kg at %g mm" % (mp, h))
            jp = r["joints"].get("payload to carriage-top")
            row = {
                "payload_kg": mp, "com_height_mm": h,
                "energy_J": r["kinetic_energy"] + r["motor_work"],
                "bumpers_fully_in": r["bumpers_fully_in"],
                "peak_force_bumpers_N": r["peak_force_bumpers"],
                "peak_force_metal_N": r["peak_force_metal"],
                "peak_deceleration_g": r["peak_deceleration_g"],
                "block_p_max_N": r["block_worst_p"],
                "block_fsl": r["block_fsl"],
                "read_head_m_s2": r["read_head"]["accel_peak"],
                "base_pocket_mises_MPa": r["base"]["pocket"]["von_mises_max"],
                "base_pocket_plastic_strain": r["base"]["pocket"]["plastic_strain_max"],
                "base_band_mises_MPa": r["base"]["band"]["von_mises_max"],
                "base_band_plastic_strain": r["base"]["band"]["plastic_strain_max"],
                "base_lasting_dent_mm": max(r["base"]["pocket"]["lasting_dent"], r["base"]["band"]["lasting_dent"]),
                "payload_slip_use": jp["slip_use_mu_low"] if jp else 0.0,
                "payload_screw_force_N": jp["screw_force_max"] if jp else 0.0,
                "payload_joint_opens": jp["opens"] if jp else False,
                "base_slip_use": r["joints"]["base to machine table"]["slip_use_mu_low"],
                "forcer_slip_use": r["joints"]["forcer to carriage-bottom"]["slip_use_mu_low"],
            }
            table.append(row)
            print("table %5.1f kg %5.0f mm: total %.0f N, fsl %.2f, head %.0f, payload slip %.2f"
                  % (mp, h, r["peak_force_total"], r["block_fsl"], r["read_head"]["accel_peak"],
                     row["payload_slip_use"]))

    with open(os.path.join(out_dir, "payload-table.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0].keys()))
        w.writeheader()
        for row in table:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})

    results["cases"] = {k: strip(v) for k, v in named.items()}
    results["spread"] = strip(spread)
    results["table"] = strip(table)
    results["fem"] = {"modes_hz": fem.get("modes_hz", [])[:6],
                      "pocket_stiffness_n_per_mm": fem["pocket"]["elastic_stiffness_n_per_mm"],
                      "band_stiffness_n_per_mm": fem["band"]["elastic_stiffness_n_per_mm"],
                      "pocket_force_reached": fem["pocket"].get("force_reached"),
                      "band_force_reached": fem["band"].get("force_reached")}
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=1)

    try:
        import figures
        figures.make_all(cfg, fem, named, table, out_dir)
    except ImportError as e:
        print("No figures (%s)" % e)
    print("Done: %s" % out_dir)


main()
