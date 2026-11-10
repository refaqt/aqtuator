"""Crash of the carriage into the end stops: a rigid body on four guide blocks.

The carriage, with everything screwed to it, is one rigid body with six
degrees of freedom (three moves, three turns). It sits on the four guide
blocks, which act as springs across the travel (up/down and sideways) and
hold small moments of their own. Along the travel the blocks roll freely.

The body arrives at the end stops at the speed clamp. Then these forces act:

- the two TA17-7 bumpers (ACE TA force curve over the 7 mm stroke, then a
  steep rise when the tube is flat, in series with the pocket wall of the
  base from the stress analysis);
- the metal hit of the carriage-bottom end face on the base end wall, after
  the gap that is left when the bumpers are fully in. The base side follows
  the force-displacement curve from the stress analysis, with plastic
  deformation. The carriage is taken as rigid there;
- the motor thrust (670 N towards the wall, if the drive keeps pushing);
- the magnetic pull of the forcer and gravity.

All internal units are SI (m, kg, N, s). Inputs in case.toml are in mm.
This file only needs numpy. Run evaluate.py to produce the results.
"""

import math

import numpy as np

G = 9.80665


def box_inertia(m, size_mm):
    a, b, c = (s * 1e-3 for s in size_mm)
    return np.diag([m * (b * b + c * c) / 12.0, m * (a * a + c * c) / 12.0, m * (a * a + b * b) / 12.0])


class Part:
    """A point mass with its own inertia, at a position in the assembly (m)."""

    def __init__(self, name, mass, com_mm, size_mm, group="carriage"):
        self.name = name
        self.mass = float(mass)
        self.com = np.array(com_mm, dtype=float) * 1e-3
        self.inertia = box_inertia(self.mass, size_mm)
        self.group = group


def combine(parts):
    m = sum(p.mass for p in parts)
    com = sum(p.mass * p.com for p in parts) / m
    J = np.zeros((3, 3))
    for p in parts:
        r = p.com - com
        J += p.inertia + p.mass * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    return m, com, J


def stage_parts(cfg, moving_only=False):
    parts = [Part(p["name"], p["mass"], p["com"], p["size"]) for p in cfg["moving"]]
    if not moving_only:
        parts += [Part(p["name"], p["mass"], p["com"], p["size"], group="fixed") for p in cfg["fixed"]]
    return parts


def payload_part(cfg, mass, h_mm):
    g = cfg["geometry"]
    if mass <= 0:
        return []
    fx, fy = cfg["table"]["footprint"]
    com = [g["x_carriage_centre"], g["y_carriage_centre"], g["carriage_top_plane"] + h_mm]
    return [Part("payload", mass, com, [fx, fy, 2.0 * h_mm], group="payload")]


def cross_stage_parts(cfg, carriage_pos_mm=0.0):
    """A second stage, turned by 90 degrees, on the carriage top.

    Upper coordinates (xu along its travel, yu across) map to the lower
    stage as: x = xc + (yu - 105), y = yc + offset + (xu - 220), z = 60 + zu.
    """
    g = cfg["geometry"]
    xc, yc, zt = g["x_carriage_centre"], g["y_carriage_centre"], g["carriage_top_plane"]
    off = cfg["cross_stage"]["offset_y"]
    shift = 220.0 - g["x_carriage_centre"] + carriage_pos_mm  # upper carriage along its travel
    out = []
    for p in cfg["moving"] + cfg["fixed"]:
        xu, yu, zu = p["com"]
        moving = p in cfg["moving"]
        if moving:
            xu += shift
        sx, sy, sz = p["size"]
        out.append(Part("upper " + p["name"], p["mass"],
                        [xc + (yu - 105.0), yc + off + (xu - 220.0), zt + zu], [sy, sx, sz],
                        group="upper-carriage" if moving else "upper-fixed"))
    return out


class BumperLaw:
    """Force of one TA17-7 against its compression (m -> N), loading branch."""

    def __init__(self, cfg, solid_stiffness=None, rate=1.0, pocket_curve=None):
        b = cfg["bumper"]
        self.s = b["stroke"] * 1e-3
        n = b["curve_exponent"]
        self.n = n
        integral = 1.0 - 1.0 / (1.0 + n)
        self.f_full = rate * b["energy_per_stroke"] / (self.s * integral)
        self.k_solid = (solid_stiffness or b["solid_stiffness"]) * 1e3  # N/mm -> N/m
        self.absorbed = b["absorbed"]
        # Past the stroke: the flat elastomer and the pocket wall in series.
        # pocket_curve: (force for both bumpers in N, wall displacement in m).
        e_tab = [0.0]
        f_tab = [self.f_full]
        if pocket_curve is not None:
            pf, pd = pocket_curve

            def wall(f_one):
                return float(np.interp(2.0 * f_one, pf, pd))
        else:
            def wall(f_one):
                return 0.0
        w0 = wall(self.f_full)
        for f in np.linspace(self.f_full, self.f_full + 60000.0, 600)[1:]:
            e_tab.append((f - self.f_full) / self.k_solid + wall(f) - w0)
            f_tab.append(f)
        self.e_tab = np.array(e_tab)
        self.f_tab = np.array(f_tab)

    def load(self, d):
        if d <= 0.0:
            return 0.0
        if d <= self.s:
            return self.f_full * (1.0 - (1.0 - d / self.s) ** self.n)
        e = d - self.s
        if e <= self.e_tab[-1]:
            return float(np.interp(e, self.e_tab, self.f_tab))
        slope = (self.f_tab[-1] - self.f_tab[-2]) / (self.e_tab[-1] - self.e_tab[-2])
        return float(self.f_tab[-1] + slope * (e - self.e_tab[-1]))

    def work(self, d):
        x = np.linspace(0.0, d, 400)
        return float(np.trapezoid([self.load(v) for v in x], x))


class MetalLaw:
    """Force of the end wall against the carriage end (m -> N).

    Loading follows the curve from the stress analysis. Unloading follows the
    first elastic slope, so the plastic part stays as a lasting dent.
    """

    def __init__(self, band_curve):
        f, d = band_curve
        self.f = np.concatenate([[0.0], np.asarray(f, float)])
        self.d = np.concatenate([[0.0], np.asarray(d, float)])
        self.k_el = self.f[1] / self.d[1]

    def load(self, d):
        if d <= 0.0:
            return 0.0
        if d <= self.d[-1]:
            return float(np.interp(d, self.d, self.f))
        slope = (self.f[-1] - self.f[-2]) / (self.d[-1] - self.d[-2])
        return float(self.f[-1] + slope * (d - self.d[-1]))


class CrashModel:
    def __init__(self, cfg, parts, fem=None, solid_stiffness=None, rate=1.0,
                 push=True, speed=None):
        self.cfg = cfg
        g = cfg["geometry"]
        gd = cfg["guides"]
        self.parts = parts
        self.m, self.com, self.J = combine(parts)
        self.Jinv = np.linalg.inv(self.J)
        self.speed = speed if speed is not None else cfg["crash"]["speed_clamp"]
        self.push = push
        self.f_motor = cfg["crash"]["motor_force"]
        mm = 1e-3
        # Points relative to the centre of mass (m).
        self.r_bump = [np.array([g["bumper_tip_x"], y, g["bumper_z"]]) * mm - self.com for y in g["bumper_y"]]
        zc = 0.5 * sum(g["metal_band_z"])
        self.r_end = np.array([g["carriage_end_x"], g["y_carriage_centre"], zc]) * mm - self.com
        self.r_blocks = [np.array([x, y, g["block_z"]]) * mm - self.com for x in g["block_x"] for y in g["block_y"]]
        self.r_forcer = np.array(g["forcer_force_point"]) * mm - self.com
        self.r_head = np.array(g["read_head"]) * mm - self.com
        self.kz = gd["k_radial"] * 1e3
        self.ky = gd["k_lateral"] * 1e3
        L = gd["ball_track_length"] * mm
        w = gd["ball_row_width"] * mm
        # Own moment stiffness of one block (N m/rad): roll, pitch, yaw.
        self.k_own = np.array([self.kz * w * w / 12.0, self.kz * L * L / 12.0, self.ky * L * L / 12.0])
        pocket_curve = None
        band_curve = None
        if fem is not None:
            cv = [c for c in fem["pocket"]["curve"] if c["force"] > 0]
            pocket_curve = ([0.0] + [c["force"] for c in cv], [0.0] + [c["displacement"] * mm for c in cv])
            cv = [c for c in fem["band"]["curve"] if c["force"] > 0]
            band_curve = ([c["force"] for c in cv], [c["displacement"] * mm for c in cv])
        self.bumper = BumperLaw(cfg, solid_stiffness, rate, pocket_curve)
        self.metal = MetalLaw(band_curve) if band_curve else None
        self.gap = (cfg["bumper"]["stroke"] + cfg["metal_contact"]["gap_after_stroke"]) * mm
        # Constant forces: gravity on every part, magnetic pull on the forcer.
        self.f_const = np.array([0.0, 0.0, -self.m * G])
        self.m_const = np.zeros(3)
        for p in parts:
            r = p.com - self.com
            self.m_const += np.cross(r, np.array([0.0, 0.0, -p.mass * G]))
        fmag = np.array([0.0, 0.0, -cfg["magnet"]["attraction"]])
        self.f_const += fmag
        self.m_const += np.cross(self.r_forcer, fmag)
        self.u_static = self.static_offset()

    # Block springs -------------------------------------------------------
    def block_forces(self, u, th):
        out = []
        for r in self.r_blocks:
            d = u + np.cross(th, r)
            out.append(np.array([0.0, -self.ky * d[1], -self.kz * d[2]]))
        return out

    def static_offset(self):
        """Spring set under gravity and the magnetic pull (6 x 6 linear solve)."""
        K = np.zeros((6, 6))
        for k in range(6):
            q = np.zeros(6)
            q[k] = 1e-6
            F, M = self.spring_wrench(q[:3], q[3:])
            K[:, k] = -np.concatenate([F, M]) / 1e-6
        # Along x the blocks roll: keep x free of springs, fix it to zero.
        K[0, 0] = 1.0
        rhs = np.concatenate([self.f_const, self.m_const])
        rhs[0] = 0.0
        return np.linalg.solve(K, rhs)

    def spring_wrench(self, u, th):
        F = np.zeros(3)
        M = -self.k_own * th * len(self.r_blocks)
        for r, f in zip(self.r_blocks, self.block_forces(u, th)):
            F += f
            M += np.cross(r, f)
        return F, M

    # Equations of motion ------------------------------------------------
    def prepare(self):
        """Linear spring matrix and plain numbers for a fast inner loop."""
        K = np.zeros((6, 6))
        for k in range(6):
            q = np.zeros(6)
            q[k] = 1.0
            F, M = self.spring_wrench(q[:3], q[3:])
            K[:, k] = np.concatenate([F, M])
        self.K6 = K
        self.c6 = np.concatenate([self.f_const, self.m_const])
        if self.push:
            r = self.r_forcer
            f = -self.f_motor
            self.c6 = self.c6 + np.array([f, 0.0, 0.0, 0.0, r[2] * f, -r[1] * f])
        self.minv = np.concatenate([np.full(3, 1.0 / self.m), np.zeros(3)])
        # Fastest natural frequency, for the time step.
        Mm = np.zeros((6, 6))
        Mm[:3, :3] = self.m * np.eye(3)
        Mm[3:, 3:] = self.J
        kmax = np.max(np.abs(np.linalg.eigvals(np.linalg.solve(Mm, -K))))
        k_contact = 2 * self.bumper.k_solid
        if self.metal is not None:
            k_contact += self.metal.k_el
        self.w_max = math.sqrt(max(kmax, k_contact / self.m * 3.0))

    def contact(self, y, state):
        """Generalised force (6) of the bumpers and of the metal hit."""
        ux, thy, thz = y[0], y[4], y[5]
        vx, wy, wz = y[6], y[10], y[11]
        g = np.zeros(6)
        fb = []
        for i, r in enumerate(self.r_bump):
            d = -(ux + thy * r[2] - thz * r[1])
            dv = -(vx + wy * r[2] - wz * r[1])
            f = self.bumper.load(d)
            if dv < 0.0 or state["bump_unloading"][i]:
                f *= (1.0 - self.bumper.absorbed)
            g[0] += f
            g[4] += r[2] * f
            g[5] -= r[1] * f
            fb.append(f)
        fm = 0.0
        if self.metal is not None:
            r = self.r_end
            d = -(ux + thy * r[2] - thz * r[1]) - self.gap
            if d > 0.0 or state["metal_peak"] > 0.0:
                pk = state["metal_peak"]
                if d >= pk:
                    fm = self.metal.load(d)
                else:
                    fm = max(0.0, self.metal.load(pk) - self.metal.k_el * (pk - d))
            g[0] += fm
            g[4] += r[2] * fm
            g[5] -= r[1] * fm
        return g, fb, fm

    def accel(self, y, state):
        q = y[:6]
        gen = self.c6 + self.K6 @ q
        g, fb, fm = self.contact(y, state)
        gen = gen + g
        a = gen[:3] / self.m
        al = self.Jinv @ gen[3:]
        return a, al, fb, fm

    def deriv(self, y, state):
        a, al, _, _ = self.accel(y, state)
        return np.concatenate([y[6:12], a, al])

    def run(self, t_end=0.06, dt=None, every=None):
        self.prepare()
        if dt is None:
            dt = min(2e-6, 0.25 / self.w_max)
        if every is None:
            every = max(1, int(2e-6 / dt))
        y = np.zeros(12)
        y[0:6] = self.u_static
        y[0] = 0.0
        y[6] = -self.speed
        state = {"bump_unloading": [False, False], "metal_peak": 0.0}
        rec = {k: [] for k in ("t", "u", "th", "v", "w", "a", "al", "fb", "fm", "blocks")}
        t = 0.0
        n = int(t_end / dt)
        left_contact = None
        for i in range(n):
            k1 = self.deriv(y, state)
            k2 = self.deriv(y + 0.5 * dt * k1, state)
            k3 = self.deriv(y + 0.5 * dt * k2, state)
            k4 = self.deriv(y + dt * k3, state)
            y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
            t += dt
            # Hysteresis state: a bumper unloads once it moves back.
            for j, r in enumerate(self.r_bump):
                dv = -(y[6] + y[10] * r[2] - y[11] * r[1])
                if dv < 0.0:
                    state["bump_unloading"][j] = True
            if self.metal is not None:
                r = self.r_end
                d = -(y[0] + y[4] * r[2] - y[5] * r[1]) - self.gap
                state["metal_peak"] = max(state["metal_peak"], d)
            if i % every == 0 or i == n - 1:
                a, al, fb, fm = self.accel(y, state)
                rec["t"].append(t)
                rec["u"].append(y[0:3].copy())
                rec["th"].append(y[3:6].copy())
                rec["v"].append(y[6:9].copy())
                rec["w"].append(y[9:12].copy())
                rec["a"].append(a)
                rec["al"].append(al)
                rec["fb"].append(list(fb))
                rec["fm"].append(fm)
                rec["blocks"].append(self.block_forces(y[0:3], y[3:6]))
            # Stop some time after the body left the bumpers, or when it
            # rests against them with the motor pushing.
            d_tip = -(y[0])
            if left_contact is None and y[6] > 0 and d_tip <= 0:
                left_contact = t
            if left_contact is not None and t > left_contact + 0.002:
                break
            if self.push and abs(y[6]) < 1e-3 and t > 0.02 and abs(y[6] - rec["v"][-1][0]) < 1e-5:
                break
        for k in rec:
            rec[k] = np.array(rec[k])
        rec["metal_peak"] = state["metal_peak"]
        return rec


def block_check(cfg, model, rec):
    """Peak loads on each block, and the HIWIN static safety factors."""
    gd = cfg["guides"]
    c0 = gd["c0"]
    m0 = np.array([gd["m0x"], gd["m0y"], gd["m0z"]]) * 1e-3  # N m
    th = rec["th"]
    own = np.abs(th) * model.k_own  # moments of one block, roll / pitch / yaw
    out = []
    for b in range(4):
        fy = np.abs(rec["blocks"][:, b, 1])
        fz = np.abs(rec["blocks"][:, b, 2])
        p_force = fy + fz  # HIWIN: radial plus lateral
        p_eq = p_force + c0 * (own[:, 0] / m0[0] + own[:, 1] / m0[1] + own[:, 2] / m0[2])
        k = int(np.argmax(p_eq))
        out.append({
            "block": b,
            "fz_max": float(fz.max()),
            "fy_max": float(fy.max()),
            "moment_roll_max": float(own[:, 0].max()),
            "moment_pitch_max": float(own[:, 1].max()),
            "moment_yaw_max": float(own[:, 2].max()),
            "p_eq_max": float(p_eq[k]),
            "fsl": float(c0 / p_eq[k]) if p_eq[k] > 0 else float("inf"),
            "fz_static": float(fz[0]),
        })
    return out


def point_accel(rec, r):
    return rec["a"] + np.cross(rec["al"], r)


def pulse_width(t, a, frac=0.5):
    """Time the signal stays above frac x its peak (longest stretch)."""
    peak = a.max()
    if peak <= 0:
        return 0.0
    above = a >= frac * peak
    best = cur = 0.0
    for i in range(1, len(t)):
        if above[i]:
            cur += t[i] - t[i - 1]
            best = max(best, cur)
        else:
            cur = 0.0
    return best


def one_dof_check(cfg, mass=5.0, speed=2.0):
    """The damper-sizing page case: 5 kg, 2 m/s, motor off, two bumpers.

    Returns the compression (mm) and the peak force of both bumpers (N).
    """
    law = BumperLaw(cfg)
    x, v, dt = 0.0, speed, 1e-6
    fpk = 0.0
    while v > 0:
        f = 2.0 * law.load(x)
        fpk = max(fpk, f)
        v -= f / mass * dt
        x += v * dt
    return x * 1e3, fpk
