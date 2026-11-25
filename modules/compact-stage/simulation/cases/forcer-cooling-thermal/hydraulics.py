# SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Water flow, pressure loss and heat transfer of the forcer cooling.

Plain Python and numpy. run_thermal.py and evaluate.py import it.

One pump feeds a supply manifold. Seven branches leave it in parallel: six
axes (each like this compact stage) and the spindle. They meet again in a
return manifold and go back to the tank of the chiller.

Units inside: SI (m, Pa, m3/s, W). Flows in and out are in l/min.
"""

import math

LPM = 1.0 / 60000.0          # m3/s per l/min
BAR = 1e5


def props(cfg):
    w = cfg["water"]
    return w["rho"], w["mu"], w["k"], w["pr"], w["cp"]


# ---------------------------------------------------------------------------
# Friction and heat transfer
# ---------------------------------------------------------------------------

def rect_fre(a):
    """Laminar Darcy f Re of a rectangular duct, side ratio a <= 1 (Shah and London)."""
    return 96.0 * (1 - 1.3553 * a + 1.9467 * a ** 2 - 1.7012 * a ** 3 + 0.9564 * a ** 4 - 0.2537 * a ** 5)


def darcy(re, fre_lam=64.0):
    """Darcy friction factor of a smooth duct. Laminar below 2300, Petukhov
    (smooth, turbulent) above 4000, straight line between."""
    if re < 1e-9:
        return 0.0
    if re <= 2300:
        return fre_lam / re
    ft = (0.790 * math.log(max(re, 4000.0)) - 1.64) ** -2
    if re >= 4000:
        return ft
    fl = fre_lam / 2300.0
    g = (re - 2300.0) / 1700.0
    return (1 - g) * fl + g * ft


def nusselt(re, pr, nu_lam):
    """Mean Nusselt number. Gnielinski for turbulent flow; between Re 2300 and
    10 000 the 2013 Gnielinski blend of laminar and turbulent values."""
    def turb(r):
        f = (0.790 * math.log(r) - 1.64) ** -2
        return (f / 8) * (r - 1000) * pr / (1 + 12.7 * math.sqrt(f / 8) * (pr ** (2 / 3) - 1))
    if re <= 2300:
        return nu_lam
    if re >= 1e4:
        return turb(re)
    g = (re - 2300.0) / (1e4 - 2300.0)
    return (1 - g) * nu_lam + g * turb(1e4)


def duct(cfg, q_lpm, dh_mm, area_mm2, length_mm, k_minor, fre_lam=64.0):
    """Pressure loss (Pa) of a straight duct with minor losses, at flow q."""
    rho, mu, _, _, _ = props(cfg)
    q = q_lpm * LPM
    v = q / (area_mm2 * 1e-6)
    re = rho * v * dh_mm * 1e-3 / mu
    f = darcy(re, fre_lam)
    dp = (f * length_mm / dh_mm + k_minor) * 0.5 * rho * v ** 2
    return dp, v, re


def film(cfg, q_lpm, zone):
    """Film coefficient (W/(m2 K)) on the wetted wall of one zone."""
    rho, mu, k, pr, _ = props(cfg)
    h = cfg["hydraulics"]
    if zone == "channel":
        w, d = h["channel_w"], h["channel_d"]
        area = w * d
        dh = 2 * w * d / (w + d)
        nu_lam = h["nu_lam_channel"]
    else:
        dh = h["passage_d"]
        area = math.pi * dh ** 2 / 4
        nu_lam = 4.36
    v = q_lpm * LPM / (area * 1e-6)
    re = rho * v * dh * 1e-3 / mu
    nu = nusselt(re, pr, nu_lam)
    return nu * k / (dh * 1e-3), re, v


# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------

def axis_branch(cfg, q_lpm, hose_length=None, detail=False):
    """Pressure loss (Pa) of one axis branch at flow q, manifold to manifold."""
    h = cfg["hydraulics"]
    L = h["hose_length"] if hose_length is None else hose_length
    parts = []
    a_h = math.pi * h["hose_id"] ** 2 / 4
    parts.append(("hoses (2 x %.1f m, 2.6 mm bore)" % (L / 1000.0),)
                 + duct(cfg, q_lpm, h["hose_id"], a_h, 2 * L, 0.0))
    parts.append(("push-in fittings (2)",) + duct(cfg, q_lpm, h["hose_id"], a_h, 0.0,
                                                    2 * h["k_fitting"]))
    a_p = math.pi * h["passage_d"] ** 2 / 4
    parts.append(("block passages (2 mm)",) + duct(cfg, q_lpm, h["passage_d"], a_p,
                                                    h["passage_length"], h["k_passage"]))
    a_port = math.pi * h["port_d"] ** 2 / 4
    parts.append(("ports into the channel (2.5 mm)",) + duct(cfg, q_lpm, h["port_d"], a_port,
                                                             h["port_length"], h["k_port"]))
    w, d = h["channel_w"], h["channel_d"]
    fre = rect_fre(min(w, d) / max(w, d))
    parts.append(("channel (%g x %g mm, %.0f mm, %d turns)" % (w, d, h["channel_length"], h["channel_turns"]),)
                 + duct(cfg, q_lpm, 2 * w * d / (w + d), w * d, h["channel_length"],
                        h["channel_turns"] * h["k_turn"], fre))
    total = sum(p[1] for p in parts)
    if detail:
        return total, [{"part": p[0], "dp_bar": p[1] / BAR, "v": p[2], "re": p[3]} for p in parts]
    return total


def spindle_branch(cfg, q_lpm):
    s = cfg["hydraulics"]
    return s["spindle_dp_bar"] * BAR * (q_lpm / s["spindle_q_lpm"]) ** 2


def invert(fn, dp, hi=20.0):
    """Flow (l/min) at which a branch has pressure loss dp (Pa)."""
    lo = 0.0
    if dp <= 0:
        return 0.0
    while fn(hi) < dp:
        hi *= 2
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if fn(mid) < dp:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def pump_pressure(pump, q_lpm):
    """Pressure rise (Pa) of a pump at flow q, or None for a fixed-flow pump."""
    if pump["kind"] == "centrifugal":
        x = q_lpm / pump["q_max"]
        return max(0.0, pump["p_max_bar"] * (1 - x * x)) * BAR
    raise ValueError(pump["kind"])


def operating_point(cfg, pump, spindle_valve=True, hose_lengths=None):
    """Flow in each branch, for a pump on the manifold system.

    With the spindle valve, the spindle branch is throttled to its set flow.
    hose_lengths: one hose length (mm) per axis; default all the same."""
    h = cfg["hydraulics"]
    n_axes = h["n_axes"]
    if hose_lengths is None:
        hose_lengths = [h["hose_length"]] * n_axes
    q_sp_set = h["spindle_q_lpm"]

    def flows(dp):
        qa = [invert(lambda q, L=L: axis_branch(cfg, q, L), dp) for L in hose_lengths]
        if spindle_valve:
            qs = min(q_sp_set, invert(lambda q: spindle_branch(cfg, q), dp))
        else:
            qs = invert(lambda q: spindle_branch(cfg, q), dp)
        return qa, qs

    def loop_loss(qt):
        return h["loop_dp_bar"] * BAR * (qt / h["loop_q_lpm"]) ** 2

    if pump["kind"] == "fixed":
        # Positive displacement pump: the flow is set; the pressure follows,
        # up to the relief valve.
        qt = pump["q_lpm"]
        lo, hi = 0.0, pump["relief_bar"] * BAR
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            qa, qs = flows(mid)
            if sum(qa) + qs < qt:
                lo = mid
            else:
                hi = mid
        dp = 0.5 * (lo + hi)
        qa, qs = flows(dp)
        relief = sum(qa) + qs < qt * 0.999
        return {"dp_manifold_bar": dp / BAR, "q_axes": qa, "q_spindle": qs,
                "q_total": sum(qa) + qs, "relief_open": relief,
                "p_pump_bar": (dp + loop_loss(sum(qa) + qs)) / BAR}
    lo, hi = 0.0, pump["p_max_bar"] * BAR
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        qa, qs = flows(mid)
        qt = sum(qa) + qs
        if pump_pressure(pump, qt) - loop_loss(qt) > mid:
            lo = mid
        else:
            hi = mid
    dp = 0.5 * (lo + hi)
    qa, qs = flows(dp)
    qt = sum(qa) + qs
    return {"dp_manifold_bar": dp / BAR, "q_axes": qa, "q_spindle": qs, "q_total": qt,
            "relief_open": False, "p_pump_bar": pump_pressure(pump, qt) / BAR}


def system_curve(cfg, dps_bar, spindle_valve=True):
    """Total flow against manifold pressure (for the chart)."""
    h = cfg["hydraulics"]
    out = []
    for p in dps_bar:
        qa = invert(lambda q: axis_branch(cfg, q), p * BAR)
        qs = invert(lambda q: spindle_branch(cfg, q), p * BAR)
        if spindle_valve:
            qs = min(qs, h["spindle_q_lpm"])
        qt = h["n_axes"] * qa + qs
        out.append({"dp_bar": p, "q_axis": qa, "q_spindle": qs, "q_total": qt,
                    "p_pump_bar": p + h["loop_dp_bar"] * (qt / h["loop_q_lpm"]) ** 2})
    return out
