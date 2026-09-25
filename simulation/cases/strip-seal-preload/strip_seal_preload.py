"""Bending radius and pull of a 0.25 mm seal strip over four 10 mm rollers.

Python 3 with numpy and scipy:

    pip install numpy scipy
    python3 simulation/cases/strip-seal-preload/strip_seal_preload.py

The layout comes from a sketch of the carriage. The strip lies flat on the
profile. Roller 1 sits above the strip and holds it down. Roller 2 sits below
it in the slot and lifts it by RISE. The strip runs flat across the carriage to
roller 3 and comes back down under roller 4. The sketch draws each ramp as two
arcs of 30 mm radius.

This case answers three questions:

  1. Which radius does the strip really take, and how does the pull change it?
  2. Can EN 1.4301 (AISI 304) replace EN 1.4310 (AISI 301) if the radius stays
     above 30 mm?
  3. How small can the radius go?

Model
-----
The strip is a thin beam under a pull T per mm of width. Its shape is the one
with the lowest energy: bending energy plus the work the pull does when the
path gets longer. The curvature is the exact one, not the small slope version,
because the ramps are steep. The strip may not pass into a roller or below the
profile top. Those are the only things that hold it. Nothing presses it onto
the drawn arcs.

The problem is solved on a grid of points. Each step is a quadratic problem
with bounds, solved by an active set method (points touching a roller or the
profile are held there, the rest are free). The steps repeat until the shape
stops changing.

check_solver() compares the solver with a closed form answer for a strip over
two point supports with no profile under it, and stops if they differ by more
than five percent.
"""

import math

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

# --------------------------------------------------------------------------
# Layout, read off the sketch. Confirm against the CAD model.
# --------------------------------------------------------------------------

ROLLER_D = 10.0      # mm, all four rollers
RISE = 6.0           # mm, strip lifted off the profile top
ARC_R = 30.0         # mm, radius of the two arcs drawn in each ramp
RAMP = 2.0 * math.sqrt(2.0 * ARC_R * RISE / 2.0 - (RISE / 2.0) ** 2)
TOP_SPAN = 119.0     # mm, roller 2 to roller 3
CLEARANCE = 9.75     # mm, room above the flat strip on the carriage
STRIP_WIDTH = 40.0   # mm, only used to turn N per mm into N. Not measured yet
T_STRIP = 0.25       # mm, measured on the old axis
OUTSIDE = 120.0      # mm of strip modelled outside each end of the carriage

# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------


class Strip:
    """Spring strip material. Stresses in MPa.

    sigma_w is the reverse bending fatigue limit (2 million cycles, 50 percent
    survival). For 1.4301 no maker publishes one, so it is a RANGE taken from
    the rule found across twelve IPCO belt grades: 0.32 to 0.48 of Rm.
    """

    def __init__(self, name, E, Rm, Rp02, sigma_w, measured, source):
        self.name = name
        self.E = E
        self.Rm = Rm
        self.Rp02 = Rp02
        self.sigma_w = sigma_w          # (low, high)
        self.measured = measured
        self.source = source


S301 = Strip("EN 1.4310 / AISI 301, 11R51 at Rm 2050", 185000, 2050, 1975,
             (775.0, 775.0), True,
             "Alleima 11R51: 775 MPa measured at 0.25 mm")
S304 = Strip("EN 1.4301 / AISI 304, +C1300 (strongest class)", 179000, 1300,
             760, (0.32 * 1300, 0.48 * 1300), False,
             "EN 10151 Rm 1300-1500 and E; ASTM A666 half hard yield 760 MPa "
             "minimum; no fatigue data published, IPCO ratio 0.32-0.48 Rm")
MATERIALS = (S301, S304)


def stress_at(R, t=T_STRIP, m=S301):
    """Surface bending stress at bending radius R."""
    return m.E * t / (2.0 * R)


def radius_for(sigma, t=T_STRIP, m=S301):
    """Bending radius that gives surface stress sigma."""
    return m.E * t / (2.0 * sigma)


def cycles_to_failure(sigma_a, m=S301):
    """Basquin line through 0.9 Rm at 1e3 cycles and sigma_w at 2e6.

    Same line as the strip-seal-fatigue case. Below sigma_w: no limit.
    """
    sw = m.sigma_w[0]
    if sigma_a <= sw:
        return float("inf")
    slope = math.log10(sw / (0.9 * m.Rm)) / math.log10(2.0e6 / 1.0e3)
    return 1.0e3 * (sigma_a / (0.9 * m.Rm)) ** (1.0 / slope)


# --------------------------------------------------------------------------
# Strip shape
# --------------------------------------------------------------------------


def _bounded_qp(H, lb, ub, y):
    """Lowest 0.5 y'Hy with lb <= y <= ub, by an active set method."""
    lo = np.isclose(y, lb)
    hi = np.isclose(y, ub) & ~lo
    for _ in range(1000):
        fixed = lo | hi
        free = ~fixed
        y = np.where(lo, lb, np.where(hi, ub, 0.0))
        Hf = H[free]
        y[free] = spsolve(Hf[:, free].tocsc(), -(Hf[:, fixed] @ y[fixed]))
        g = H @ y
        add_lo = free & (y < lb - 1e-12)
        add_hi = free & (y > ub + 1e-12)
        drop_lo = lo & (g < -1e-9)
        drop_hi = hi & (g > 1e-9)
        if not (add_lo.any() or add_hi.any() or drop_lo.any() or drop_hi.any()):
            return y
        lo = (lo & ~drop_lo) | add_lo
        hi = (hi & ~drop_hi) | add_hi
    raise RuntimeError("contact solver did not settle")


def shape(pull, m=S301, t=T_STRIP, rise=RISE, ramp=RAMP, d=ROLLER_D,
          gap=0.0, profile=True, exact=True, dx=0.05):
    """Shape of the strip centre line under a pull in N per mm of width.

    gap lifts rollers 1 and 4 above the strip, so they no longer pinch it
    against the profile. A very large gap removes them. profile=False takes
    the profile away, so the strip hangs free between the rollers.

    Returns a dict with x, y and the curvature along the strip, plus the
    tightest radius, the roller nearest to it, the point where the strip
    leaves the profile (x = 0 is roller 1), the highest point and the extra
    length the path needs compared with a flat strip.
    """
    EI = m.E * t ** 3 / 12.0
    rho = d / 2.0 + t / 2.0
    x = np.arange(-OUTSIDE, 2 * ramp + TOP_SPAN + OUTSIDE + dx / 2, dx)
    n = len(x)
    rollers = (0.0, ramp, ramp + TOP_SPAN, 2 * ramp + TOP_SPAN)
    lb = np.full(n, 0.0 if profile else -1e3)
    ub = np.full(n, 1e3)
    for k, xc in enumerate(rollers):
        near = np.abs(x - xc) < rho
        dz = np.sqrt(rho ** 2 - (x[near] - xc) ** 2)
        if k in (0, 3):     # above the strip
            ub[near] = np.minimum(ub[near], rho + gap - dz)
        else:               # below the strip
            lb[near] = np.maximum(lb[near], rise - rho + dz)
    for i in (0, 1, n - 2, n - 1):   # the strip is flat far from the carriage
        lb[i] = ub[i] = 0.0
    ub = np.maximum(ub, lb + 1e-9)

    D1 = sp.diags([-np.ones(n - 1), np.ones(n - 1)], [0, 1],
                  shape=(n - 1, n)).tocsr() / dx
    D2 = sp.diags([np.ones(n - 2), -2 * np.ones(n - 2), np.ones(n - 2)],
                  [0, 1, 2], shape=(n - 2, n)).tocsr() / dx ** 2
    P = (sp.diags([np.ones(n - 2), np.ones(n - 2)], [0, 1],
                  shape=(n - 2, n - 1)) * 0.5) @ D1

    y = np.clip(np.interp(x, rollers, [0, rise, rise, 0]), lb, ub)
    for step in range(200):
        s, p = D1 @ y, P @ y
        wb = (1 + p * p) ** -2.5 if exact else np.ones(n - 2)
        wt = 2.0 / (np.sqrt(1 + s * s) + 1) if exact else np.ones(n - 1)
        H = (EI * dx * D2.T @ sp.diags(wb) @ D2
             + pull * dx * D1.T @ sp.diags(wt) @ D1).tocsr()
        new = _bounded_qp(H, lb, ub, y)
        change = np.max(np.abs(new - y))
        y = new if step < 10 else 0.5 * (y + new)
        if change < 1e-5:
            break

    kappa = (D2 @ y) / (1 + (P @ y) ** 2) ** 1.5
    xi, yi = x[1:-1], y[1:-1]
    i = int(np.argmax(np.abs(kappa)))
    s = D1 @ y
    return {
        "x": xi, "y": yi, "kappa": kappa,
        "r_min": 1.0 / abs(kappa[i]),
        "at": 1 + int(np.argmin([abs(xi[i] - xc) for xc in rollers])),
        "lift": float(xi[np.argmax(yi > 1e-3)]),
        "top": float(y.max()),
        "extra": float(np.sum(np.sqrt(1 + s * s) - 1) * dx),
    }


def pull_for_radius(radius, **kw):
    """Pull in N per mm at which the tightest radius equals `radius`.

    More pull gives a tighter bend, so this is the most pull the layout can
    take before the strip goes below that radius.
    """
    lo, hi = 1e-3, 200.0
    if shape(lo, **kw)["r_min"] < radius:
        return 0.0
    for _ in range(30):
        mid = math.sqrt(lo * hi)
        if shape(mid, **kw)["r_min"] > radius:
            lo = mid
        else:
            hi = mid
        if hi / lo < 1.02:
            break
    return math.sqrt(lo * hi)


def check_solver():
    """Compare with the closed form for two point supports and no profile.

    For a strip under pull between point supports, lambda = sqrt(EI / T) and
    beta = L / (2 lambda), the tightest curvature is

        kappa = h sinh(beta) / (2 lambda^2 (beta e^beta - sinh(beta)))
    """
    EI = S301.E * T_STRIP ** 3 / 12.0
    for pull in (10.0, 40.0):
        lam = math.sqrt(EI / pull)
        b = RAMP / (2 * lam)
        want = 2 * lam ** 2 * (b * math.exp(b) - math.sinh(b)) / (RISE * math.sinh(b))
        got = shape(pull, d=0.02, profile=False, exact=False)["r_min"]
        if abs(got / want - 1) > 0.05:
            raise AssertionError(f"solver check failed at {pull} N/mm: "
                                 f"{got:.1f} mm, expected {want:.1f} mm")
    return True


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


def _life(n):
    return "no limit" if n == float("inf") else f"{n:.1e}"


def main():
    check_solver()
    print("Solver check against the closed form for point supports: passed.\n")

    print("=" * 76)
    print("1. The radius each material needs, 0.25 mm strip")
    print("=" * 76)
    print("\nThe strip is bent up, down, down and up at each carriage pass, so")
    print("the stress swings fully both ways. The tightest radius sets it.\n")
    print(f"{'material':<48} {'no limit':>12} {'no set':>9}")
    print("-" * 72)
    for m in MATERIALS:
        lo, hi = m.sigma_w
        r_fat = (f"{radius_for(lo, m=m):.0f} mm" if lo == hi else
                 f"{radius_for(hi, m=m):.0f}-{radius_for(lo, m=m):.0f} mm")
        print(f"{m.name:<48} {r_fat:>12} "
              f"{radius_for(m.Rp02, m=m):>6.1f} mm")
    print("\n'no limit' is the smallest radius with no fatigue limit reached")
    print("(50 percent survival at 2 million crossings). 'no set' is the")
    print("smallest radius before the strip takes a permanent bend.")
    for m in MATERIALS:
        print(f"\n{m.name}, stress at {ARC_R:.0f} mm: "
              f"{stress_at(ARC_R, m=m):.0f} MPa. Source: {m.source}.")

    print("\n" + "=" * 76)
    print("2. The layout as drawn: what the pull does")
    print("=" * 76)
    print(f"\nRollers {ROLLER_D:.0f} mm, rise {RISE:.1f} mm, ramp {RAMP:.1f} mm. "
          f"Roller 1 pinches the")
    print("strip against the profile top.\n")
    print(f"{'pull':>11} {'on 40 mm':>9} {'tightest R':>11} {'where':>12} "
          f"{'highest':>8} {'extra length':>13}")
    print("-" * 70)
    for pull in (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
        r = shape(pull)
        where = f"roller {r['at']}"
        print(f"{pull:>6.1f} N/mm {pull * STRIP_WIDTH:>7.0f} N {r['r_min']:>8.1f} mm "
              f"{where:>12} {r['top']:>5.1f} mm {r['extra']:>10.2f} mm")
    print(f"\nHighest is the top of the strip above the profile. The strip may")
    print(f"rise {RISE + CLEARANCE:.2f} mm before it touches the carriage.")
    print("More pull always makes the bend tighter. Pull does not create the")
    print("drawn 30 mm arcs. The strip is stiff enough to spread the bend by")
    print("itself, and pull pulls it back into the rollers.")
    p30 = pull_for_radius(ARC_R)
    print(f"\nMost pull that keeps the tightest radius above {ARC_R:.0f} mm: "
          f"{p30:.2f} N/mm,")
    print(f"which is {p30 * STRIP_WIDTH:.0f} N on a {STRIP_WIDTH:.0f} mm strip.")

    print("\n" + "=" * 76)
    print("3. The pull that comes from fixing both ends")
    print("=" * 76)
    extra = shape(p30)["extra"]
    print(f"\nOver the carriage the path is {extra:.2f} mm longer than a flat strip.")
    print("If both ends are screwed down, that length has to come from")
    print("stretching the strip, and the stretch adds pull on top of any")
    print("preload:\n")
    print(f"{'free strip length':>18} {'extra pull':>12}")
    print("-" * 32)
    for length in (500, 1000, 2000):
        dT = S301.E * T_STRIP * extra / length
        print(f"{length:>15} mm {dT:>8.0f} N/mm")
    lo = S301.E * T_STRIP * extra / 2000 / p30
    hi = S301.E * T_STRIP * extra / 500 / p30
    print(f"\nThat is {lo:.0f} to {hi:.0f} times more than the {p30:.2f} N/mm "
          f"the radius allows.")
    print("A strip fixed hard at both ends is pulled into the rollers by the")
    print("carriage itself. One end needs a soft spring with a few mm of travel,")
    print("so the pull stays near the preload wherever the carriage stands.")

    print("\n" + "=" * 76)
    print("4. Layout changes that open the bend")
    print("=" * 76)
    print(f"\nPull {p30:.2f} N/mm unless stated.\n")
    print(f"{'change':<44} {'tightest R':>11} {'highest':>9} {'lifts off':>10}")
    print("-" * 77)
    cases = (
        ("as drawn", {}),
        ("rollers 1 and 4 lifted 0.5 mm off the strip", {"gap": 0.5}),
        ("rollers 1 and 4 lifted 1.0 mm off the strip", {"gap": 1.0}),
        ("ramp 1.5 times longer", {"ramp": 1.5 * RAMP}),
        ("rise 4 mm instead of 6 mm", {"rise": 4.0}),
    )
    for label, kw in cases:
        r = shape(p30, **kw)
        print(f"{label:<44} {r['r_min']:>8.1f} mm {r['top']:>6.1f} mm "
              f"{r['lift']:>7.1f} mm")
    print("\nLifts off is where the strip leaves the profile, measured from")
    print(f"roller 1. The carriage end sits about {ROLLER_D / 2 + 5:.0f} mm "
          "before roller 1.")
    print("Rollers 1 and 4 pinch the strip flat against the profile. That")
    print("acts like a clamp and forces the whole bend to start at one point.")
    print("Lifted rollers let the bend start earlier, but the strip then")
    print("leaves the profile outside the carriage. The magnets that hold the")
    print("strip down are not in the model, and they shorten that length.")

    print("\n" + "=" * 76)
    print("5. Going below 30 mm with 11R51, 0.25 mm")
    print("=" * 76)
    print(f"\n{'radius':>8} {'stress':>9} {'crossings':>11}")
    print("-" * 31)
    for R in (40, 35, 30, 27.5, 25, 22.5, 20, 15, 12):
        s = stress_at(R)
        print(f"{R:>5.1f} mm {s:>5.0f} MPa {_life(cycles_to_failure(s)):>11}")
    print("\nOne crossing is one pass of the carriage over one point of the strip.")
    print("Thinner strip moves every radius down in proportion. At 0.10 mm the")
    print("no limit radius is about 9 mm (see the strip-seal-fatigue case).")


if __name__ == "__main__":
    main()
