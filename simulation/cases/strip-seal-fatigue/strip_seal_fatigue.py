"""Fatigue life of a spring steel sealing strip bent over the carriage rollers.

Python 3, standard library only.

    python3 simulation/cases/strip-seal-fatigue/strip_seal_fatigue.py

The stage is sealed by a thin steel strip that lies in a slot. The carriage
carries four rollers that lift the strip, pass under it and lay it back down.
This case answers three questions:

  1. Which strip material and which roller diameter last.
  2. What one carriage pass actually costs the strip.
  3. How to state the life of the seal, given that kilometres of travel do not
     measure it.

Every fatigue number below is measured and published by a strip or belt maker.
None of them is estimated. Sources are listed in `SOURCES` and in the case
README.

Model
-----
Surface bending stress follows from the radius the strip really takes:

    sigma_max = E * t / (2 * R)

If the strip wraps the outside of a roller, R is (D + t) / 2 and this is the
same as E * t / (D + t), which Sandvik write as E * t / D for D much larger
than t. That is the WORST case, not the usual one. A thin strip only takes the
roller radius if something presses it there over an arc. Under light pull it
bridges a small roller and follows its own curve, and then the radius comes
from the layout instead. bending_radius() decides which of the two applies.

Fatigue is driven by the stress AMPLITUDE. The mean stress is a smaller
correction, handled by Goodman. Two things set the amplitude: whether the strip
is bent one way or both ways, and the radius it really takes. Both matter more
than the choice of material.

The fatigue limit itself depends on strip thickness. Thinner strip is stronger,
and the strip makers measure it that way, so fatigue_limit() scales the
published value to the thickness being bought and says when it extrapolates.
"""

import math

SOURCES = {
    "11R51": "Alleima 11R51 strip steel datasheet, 2025-05-09",
    "Hiflex": "Alleima Hiflex compressor valve steel datasheet, 2025-05-09",
    "Springflex": "Alleima Springflex strip steel datasheet, 2025-05-09",
    "IPCO": "IPCO Steel Belt Specifications v0.3 and grade data sheets",
    "EN10151": "EN 10151:2002, stainless steel strip for springs",
    "Sandvik": "Sandvik, The Steel Belt Conveyor, advice for conveyor design",
}


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

class Strip:
    """A strip material with a measured reverse bending fatigue limit.

    sigma_w is the reverse bending stress the strip survives for at least
    2 million cycles. The strip makers all define it that way, but not at the
    same survival rate, so `survival` records which one applies.

    sigma_w is also measured at one thickness, `sigma_w_t`. Thinner strip has a
    higher fatigue limit, so a value read at 0.25 mm understates a 0.1 mm strip.
    `t_exponent` holds that trend where a maker publishes two thicknesses, and
    `t_measured` holds the range they measured, so the report can mark every
    value taken outside it.
    """

    def __init__(self, name, designation, E, Rm, Rp02, sigma_w, sigma_w_t,
                 stock_0p1, survival, source, note="",
                 t_exponent=None, t_measured=None):
        self.name = name
        self.designation = designation
        self.E = E                  # MPa
        self.Rm = Rm                # MPa
        self.Rp02 = Rp02            # MPa
        self.sigma_w = sigma_w      # MPa
        self.sigma_w_t = sigma_w_t  # mm, thickness sigma_w was measured at
        self.stock_0p1 = stock_0p1  # is 0.1 mm a standard thickness?
        self.survival = survival
        self.source = source
        self.note = note
        self.t_exponent = t_exponent    # sigma_w scales as t ** -t_exponent
        self.t_measured = t_measured    # (thinnest, thickest) measured, mm


MATERIALS = [
    Strip("11R51 cold rolled", "EN 1.4310 / AISI 301", 185000, 2050, 1975, 775,
          0.25, True, "50 % at 2e6", "11R51",
          "Alleima publish 775 at 0.25 mm and 630 at 0.50 mm, both at Rm 2100",
          t_exponent=0.299, t_measured=(0.25, 0.50)),
    Strip("Hiflex", "UNS S42026, near 1.4031", 210000, 1900, 1500, 920,
          None, False, "5 % at 2e6", "Hiflex",
          "molybdenum alloyed, stock starts at 0.152 mm"),
    Strip("Springflex cold rolled", "EN 1.4462 duplex", 200000, 1900, 1700, 615,
          0.50, False, "50 % at 2e6", "Springflex",
          "best corrosion resistance, sigma_w measured at 0.50 mm"),
    Strip("IPCO 1200SA belt", "EN 1.4310, belt temper", 182000, 1200, 980, 470,
          None, False, "50 % at 2e6", "IPCO",
          "soft belt temper, kept for contrast only"),
    Strip("IPCO 1850SM belt", "AISI 1065 carbon", 210000, 1800, 1450, 860,
          None, False, "50 % at 2e6", "IPCO",
          "highest fatigue strength of the belt grades, but it rusts"),
]

DEFAULT = MATERIALS[0]

# 11R51 standard thicknesses at Rm 2050, from the datasheet.
STOCK_MM = (0.03, 0.04, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30)

T_REF = 0.1
N_KNEE = 2.0e6

# The carriage as drawn in the CAD sketch. All four rollers are the same size.
# The strip leaves the flat, climbs a straight ramp to the top of the carriage,
# runs across it and comes back down, so it turns by the ramp angle at each of
# the four rollers.
#
# RAMP_LENGTH is read off the sketch and has to be confirmed against the model.
# The pull in the strip is not known yet. It is the one input a measurement has
# to supply, which is why the report walks a range instead of giving one answer.
ROLLER_D = 14.0       # mm
RAMP_LENGTH = 38.0    # mm, outer roller to inner roller
RAMP_RISE = 8.38      # mm, height the strip is taken off the flat
STRIP_WIDTH = 40.0    # mm, used only to turn pull per mm into a force
PULL_RANGE = (0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)   # N per mm of width


# --------------------------------------------------------------------------
# Stress and life
# --------------------------------------------------------------------------

def fatigue_limit(t, m=DEFAULT):
    """Reverse bending fatigue limit of a strip of thickness t.

    Thinner strip is stronger. Alleima publish 775 MPa at 0.25 mm and 630 MPa
    at 0.50 mm for the same material at the same strength, which is a power law
    with exponent 0.299. Where a maker gives only one thickness there is no
    trend to follow, so the published value is used unchanged.
    """
    if m.sigma_w_t is None or m.t_exponent is None:
        return m.sigma_w
    return m.sigma_w * (m.sigma_w_t / t) ** m.t_exponent


def extrapolated(t, m=DEFAULT):
    """True when the fatigue limit at t sits outside the measured range."""
    if m.t_measured is None:
        return False
    return not (m.t_measured[0] <= t <= m.t_measured[1])


def bending_stiffness(t, m=DEFAULT):
    """Bending stiffness E*I of the strip, per mm of its width."""
    return m.E * t ** 3 / 12.0


def bending_radius(D, turn, tension, t=T_REF, m=DEFAULT):
    """Radius the strip really takes where it turns by `turn` on a roller.

    `turn` is the change of direction in radians, `tension` the pull in the
    strip in N per mm of width.

    A strip takes the roller radius only if it is pressed onto it over an arc.
    A thin strip under light pull bridges the roller instead: the turn spreads
    over a length sqrt(EI/T) on each side and the tightest radius becomes

        R_free = 2 * sqrt(EI / T) / turn

    The roller is then a floor on the radius, not the answer. Both cases are
    covered by taking whichever radius is larger.
    """
    r_roller = (D + t) / 2.0
    if turn <= 0.0 or tension <= 0.0:
        return float("inf")
    r_free = 2.0 * math.sqrt(bending_stiffness(t, m) / tension) / turn
    return max(r_roller, r_free)


def conforms(D, turn, tension, t=T_REF, m=DEFAULT):
    """True when the strip really wraps the roller at its own radius."""
    return bending_radius(D, turn, tension, t, m) <= (D + t) / 2.0


def tension_to_conform(D, turn, t=T_REF, m=DEFAULT):
    """Pull, in N per mm of width, needed to force the strip onto a roller."""
    if turn <= 0.0:
        return float("inf")
    return bending_stiffness(t, m) / ((D + t) / 2.0 * turn / 2.0) ** 2


def stress_at_radius(R, t=T_REF, m=DEFAULT):
    """Peak surface bending stress of a strip of thickness t at radius R."""
    if R == float("inf"):
        return 0.0
    return m.E * t / (2.0 * R)


def bending_stress(t, D, m=DEFAULT):
    """Worst case: the strip wraps diameter D completely."""
    return m.E * t / (D + t)


def goodman_reversed(amplitude, mean, m=DEFAULT):
    """Equivalent fully reversed amplitude. A compressive mean gets no credit."""
    if mean <= 0.0:
        return amplitude
    if mean >= m.Rm:
        return float("inf")
    return amplitude / (1.0 - mean / m.Rm)


def allowable_peak_one_way(t=T_REF, m=DEFAULT):
    """Peak stress allowed when the strip is only ever bent one way.

    The cycle runs 0 -> sigma_max -> 0, so the amplitude is half the peak and
    the mean is the other half. Inverting Goodman for that case gives:

        sigma_peak = 2 * sigma_w / (1 + sigma_w / Rm)

    Alleima publish this same conversion for Hiflex as 620 +/- 620 MPa.
    check_goodman() reproduces it.
    """
    sw = fatigue_limit(t, m)
    return 2.0 * sw / (1.0 + sw / m.Rm)


def allowable_peak_both_ways(t=T_REF, m=DEFAULT):
    """Peak stress allowed when the strip is bent both ways.

    The amplitude is now the whole peak and the mean is zero, so the published
    reverse bending limit applies directly.
    """
    return fatigue_limit(t, m)


def cycles_to_failure(sigma_ar, t=T_REF, m=DEFAULT):
    """Basquin line through 0.9 * Rm at 1e3 cycles and sigma_w at 2e6."""
    sw = fatigue_limit(t, m)
    if sigma_ar <= sw:
        return float("inf")
    s1 = 0.9 * m.Rm
    slope = math.log10(sw / s1) / math.log10(N_KNEE / 1.0e3)
    return 1.0e3 * (sigma_ar / s1) ** (1.0 / slope)


def min_diameter(t, m=DEFAULT, both_ways=True):
    """Smallest FULLY WRAPPED roller that stays below the fatigue limit.

    This is the worst case. A roller the strip only bridges may be smaller.
    """
    allow = (allowable_peak_both_ways(t, m) if both_ways
             else allowable_peak_one_way(t, m))
    allow = min(allow, m.Rp02)
    return m.E * t / allow - t


def max_thickness(D, m=DEFAULT, both_ways=True, t=T_REF):
    """Thickest strip that stays below the fatigue limit on a wrapped roller.

    The allowable stress itself depends on thickness, so this is solved by
    repeating the step until the answer stops moving. `t` is only the starting
    guess.
    """
    for _ in range(50):
        allow = (allowable_peak_both_ways(t, m) if both_ways
                 else allowable_peak_one_way(t, m))
        allow = min(allow, m.Rp02)
        nxt = D * allow / (m.E - allow)
        if abs(nxt - t) < 1e-9:
            return nxt
        t = nxt
    return t


def check_goodman():
    """Reproduce Alleima's own published Hiflex conversion, 620 +/- 620 MPa."""
    hiflex = next(x for x in MATERIALS if x.name == "Hiflex")
    got = allowable_peak_one_way(T_REF, hiflex)
    if abs(got - 1240.0) > 1.0:
        raise AssertionError(f"Goodman check failed: {got:.1f} MPa, expected 1240")
    return got


def check_radius_model():
    """The radius model must contain the old full wrap formula as its limit.

    Pressed hard enough, the strip takes the roller radius and the stress must
    match E * t / (D + t) exactly. If it does not, the two models disagree.
    """
    D, turn = 14.0, math.radians(30.0)
    hard = 100.0 * tension_to_conform(D, turn)
    got = stress_at_radius(bending_radius(D, turn, hard))
    want = bending_stress(T_REF, D)
    if abs(got - want) > 0.5:
        raise AssertionError(
            f"radius model failed: {got:.1f} MPa, expected {want:.1f}")
    if not conforms(D, turn, hard):
        raise AssertionError("radius model failed: no wrap at high tension")
    if conforms(D, turn, 0.01 * tension_to_conform(D, turn)):
        raise AssertionError("radius model failed: wrap at low tension")
    return got


# --------------------------------------------------------------------------
# Cycle counting
# --------------------------------------------------------------------------

def turning_points(series):
    """Drop every point that is not a reversal.

    Consecutive equal values must be collapsed first. The strip returns to
    zero stress between every roller, so a history built from several passes
    holds runs of equal values, and a run would otherwise hide the reversal
    that follows it.
    """
    pts = [series[0]]
    for value in series[1:]:
        if value != pts[-1]:
            pts.append(value)
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        if (pts[i] - pts[i - 1]) * (pts[i + 1] - pts[i]) < 0.0:
            out.append(pts[i])
    out.append(pts[-1])
    return out


def rainflow(series):
    """Three point rainflow counting, ASTM E1049.

    Yields (range, mean, count). The residue left on the stack is returned as
    half cycles, which is why a repeating history should be fed in several
    times and the result divided by the number of repeats.
    """
    stack = []
    cycles = []
    for point in turning_points(series):
        stack.append(point)
        while len(stack) >= 3:
            r_old = abs(stack[-2] - stack[-3])
            r_new = abs(stack[-1] - stack[-2])
            if r_new < r_old:
                break
            cycles.append((r_old, (stack[-3] + stack[-2]) / 2.0, 1.0))
            del stack[-3:-1]
    for i in range(len(stack) - 1):
        cycles.append((abs(stack[i + 1] - stack[i]),
                       (stack[i] + stack[i + 1]) / 2.0, 0.5))
    return cycles


def pass_history(s_outer, s_inner, repeats=8):
    """Stress at the critical surface for `repeats` carriage passes.

    The four rollers bend the strip up, down, down and up, and the strip runs
    straight between them, so the curvature returns to zero in between.
    Rollers 1 and 4 sit inside the slot and reach s_outer. Rollers 2 and 3 sit
    above the carriage and reach s_inner.
    """
    one = [0.0, +s_outer, 0.0, -s_inner, 0.0, -s_inner, 0.0, +s_outer, 0.0]
    return one * repeats


def wrapped_stresses(d_outer, d_inner, t=T_REF, m=DEFAULT):
    """Peak stresses for the worst case, where both rollers are fully wrapped."""
    return bending_stress(t, d_outer, m), bending_stress(t, d_inner, m)


def layout_stresses(d_outer, d_inner, turn_outer, turn_inner, tension,
                    t=T_REF, m=DEFAULT):
    """Peak stresses for a real layout, where the strip may bridge a roller."""
    return (stress_at_radius(bending_radius(d_outer, turn_outer, tension, t, m), t, m),
            stress_at_radius(bending_radius(d_inner, turn_inner, tension, t, m), t, m))


def _counted(s_outer, s_inner, repeats):
    """Cycles found in `repeats` passes, keyed by (amplitude, mean)."""
    out = {}
    for rng, mean, count in rainflow(pass_history(s_outer, s_inner, repeats)):
        key = (round(rng / 2.0, 1), round(mean, 1))
        out[key] = out.get(key, 0.0) + count
    return out


def cycles_per_pass(s_outer, s_inner, repeats=8):
    """Cycles that one carriage pass adds, keyed by (amplitude, mean).

    Counting a repeating history leaves a residue of half cycles at the ends,
    which would be charged to whichever pass happens to be last. Counting
    `repeats` and `repeats + 1` passes and taking the difference cancels that
    residue exactly, because the extra pass adds one block of closed cycles
    and nothing else.
    """
    more = _counted(s_outer, s_inner, repeats + 1)
    less = _counted(s_outer, s_inner, repeats)
    out = {}
    for key in set(more) | set(less):
        n = more.get(key, 0.0) - less.get(key, 0.0)
        if n > 1e-9:
            out[key] = n
    return out


def damage_per_pass(s_outer, s_inner, t=T_REF, m=DEFAULT, repeats=8):
    """Miner damage for one carriage pass, plus the cycles it breaks into."""
    breakdown = cycles_per_pass(s_outer, s_inner, repeats)
    total = 0.0
    for (amp, mean), count in breakdown.items():
        nf = cycles_to_failure(goodman_reversed(amp, mean, m), t, m)
        if nf != float("inf"):
            total += count / nf
    return total, breakdown


def passes_to_failure(s_outer, s_inner, t=T_REF, m=DEFAULT):
    """Carriage crossings of one point of the strip before a crack starts."""
    if s_outer >= m.Rp02 or s_inner >= m.Rp02:
        return 0.0  # the strip takes a permanent set and stops sealing
    d, _ = damage_per_pass(s_outer, s_inner, t, m)
    return float("inf") if d == 0.0 else 1.0 / d


def passes_wrapped(d_outer, d_inner, t=T_REF, m=DEFAULT):
    """Crossings for the worst case, where both rollers are fully wrapped."""
    return passes_to_failure(*wrapped_stresses(d_outer, d_inner, t, m), t, m)


def travel_km(passes, stroke_m):
    """Travel before failure for a machine that repeats one stroke.

    A point is loaded once per crossing. One back and forth over a stroke s is
    2s of travel and gives two crossings, so one crossing costs s of travel.
    """
    if passes == float("inf"):
        return float("inf")
    return passes * stroke_m / 1000.0


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def _f(v, unit=""):
    if v == float("inf"):
        return "unlimited"
    if v == 0.0:
        return "SET"
    return f"{v:.1e}{unit}"


def main():
    print(f"Goodman self-check against the published Hiflex figure: "
          f"{check_goodman():.0f} MPa, expected 1240 MPa. Passed.")
    print(f"Radius self-check, strip pressed hard onto a 14 mm roller: "
          f"{check_radius_model():.0f} MPa, matches E*t/(D+t). Passed.\n")

    m = DEFAULT
    turn = math.atan(RAMP_RISE / RAMP_LENGTH)

    print("=" * 76)
    print("1. The fatigue limit depends on how thin the strip is")
    print("=" * 76)
    print(f"\n{m.name}, {m.designation}. {m.note}.")
    print(f"\n{'thickness':>10} {'fatigue limit':>14}   source")
    print("-" * 52)
    for t in (0.50, 0.25, 0.15, 0.10, 0.08, 0.05):
        tag = "extrapolated" if extrapolated(t, m) else "measured"
        print(f"{t:>8.2f} mm {fatigue_limit(t, m):>11.0f} MPa   {tag}")
    print("\n   The old version of this case used 775 MPa, the value at")
    print("   0.25 mm, for a 0.1 mm strip. That understates the strip.")
    print("   Everything below 0.25 mm is an extrapolation of the maker's own")
    print("   trend and has to be confirmed with them before it is relied on.")

    print("\n" + "=" * 76)
    print("2. Does the strip really wrap the rollers?")
    print("=" * 76)
    print(f"\nRollers {ROLLER_D:.0f} mm. Ramp {RAMP_LENGTH:.0f} mm long and "
          f"{RAMP_RISE:.2f} mm high, so the strip")
    print(f"turns {math.degrees(turn):.1f} degrees at each roller.")
    need = tension_to_conform(ROLLER_D, turn)
    print(f"\nPull needed before the strip takes the roller radius: "
          f"{need:.1f} N per mm")
    print(f"of width, which is {need * STRIP_WIDTH:,.0f} N on a "
          f"{STRIP_WIDTH:.0f} mm strip.")
    print(f"\n{'pull':>9} {'radius':>10} {'stress':>9} {'wraps?':>8} "
          f"{'share of limit':>15}")
    print("-" * 55)
    sw = fatigue_limit(T_REF, m)
    for pull in PULL_RANGE:
        r = bending_radius(ROLLER_D, turn, pull)
        s = stress_at_radius(r)
        print(f"{pull:>6.2f} N/mm {r:>7.1f} mm {s:>6.0f} MPa "
              f"{('yes' if conforms(ROLLER_D, turn, pull) else 'no'):>8} "
              f"{s / sw:>15.2f}")
    print(f"\n   Share of limit is against {sw:.0f} MPa. A strip held by")
    print("   magnets or a light clamp sits at the top of this table, far")
    print("   below the limit. The roller diameter only starts to matter")
    print("   once the strip is pulled hard enough to wrap it.")

    print("\n" + "=" * 76)
    print("3. What one carriage pass costs, for the layout as drawn")
    print("=" * 76)
    for pull in (0.2, 2.0):
        so, si = layout_stresses(ROLLER_D, ROLLER_D, turn, turn, pull)
        p = passes_to_failure(so, si)
        print(f"\nPull {pull:.1f} N per mm, peak stress {so:.0f} MPa, "
              f"crossings {_f(p)}")
        _, br = damage_per_pass(so, si)
        for (amp, mean), n in sorted(br.items(), key=lambda x: -x[0][0]):
            sar = goodman_reversed(amp, mean)
            print(f"   {n:>4.2f} cycle  amplitude {amp:>6.0f}  mean {mean:>7.0f}"
                  f"  -> reversed {sar:>6.0f} MPa, life {_f(cycles_to_failure(sar))}")
    print("\n   One pass is one full reversal. Not four, and not one per")
    print("   roller. Passing through zero between rollers resets nothing:")
    print("   rainflow closes the loop between the highest and lowest point.")
    print("   That part of the old model was right and has not changed.")

    print("\n" + "=" * 76)
    print("4. Worst case: what if the strip did wrap every roller")
    print("=" * 76)
    print(f"\n{'D [mm]':>7} {'stress':>8} {'/Rp0.2':>8} {'crossings':>12}")
    print("-" * 38)
    for D in range(14, 26, 2):
        s = bending_stress(T_REF, float(D))
        print(f"{D:>7} {s:>7.0f} {s / m.Rp02:>8.2f} "
              f"{_f(passes_wrapped(float(D), float(D))):>12}")
    print(f"\n   This is the table the old version reported as the answer.")
    print("   It applies only to a strip pulled hard onto its rollers.")
    print("   Permanent set is never the limit: even 14 mm reaches only two")
    print("   thirds of the proof strength.")
    print(f"\n   A thinner strip is the other way out of the same corner:")
    print(f"\n   {'D [mm]':>8} {'t needed':>11} {'order':>10}")
    print("   " + "-" * 31)
    for D in (14, 18, 20, 24):
        need = max_thickness(float(D))
        fits = [x for x in STOCK_MM if x <= need]
        print(f"   {D:>6} mm {need:>9.3f} mm "
              f"{(f'{max(fits):.2f} mm' if fits else 'none'):>10}")
    print("\n   Thinner strip helps twice over: less thickness in the stress,")
    print("   and a higher fatigue limit. It also dents more easily, and")
    print("   denting is what ends a cover strip in the field.")

    print("\n" + "=" * 76)
    print("5. The cheap fix, if the strip ever does wrap")
    print("=" * 76)
    print(f"\n{'1 and 4':>9} {'2 and 3':>9} {'crossings':>12} {'gain':>7}")
    print("-" * 42)
    for outer, inner in ((14, 14), (14, 40), (14, 60), (20, 20), (20, 40), (24, 24)):
        p = passes_wrapped(float(outer), float(inner))
        base = passes_wrapped(float(outer), float(outer))
        gain = "-" if outer == inner or p == float("inf") \
            or base in (0.0, float("inf")) else f"{p / base:.0f}x"
        print(f"{outer:>7} mm {inner:>7} mm {_f(p):>12} {gain:>7}")
    print("\n   Opening only the two rollers above the carriage turns the")
    print("   reversal back into a one way bend, because the downward peak")
    print("   shrinks while the upward peak stays. A longer ramp does the")
    print("   same job without the height, by lowering the turn angle.")

    print("\n" + "=" * 76)
    print("6. Materials, on a fully wrapped roller at 0.1 mm")
    print("=" * 76)
    print(f"\n{'material':<23} {'designation':<24} {'0.1mm':<6} "
          f"{'one way':>9} {'both ways':>10}")
    print("-" * 76)
    for x in sorted(MATERIALS, key=lambda y: min_diameter(T_REF, y)):
        print(f"{x.name:<23} {x.designation:<24} "
              f"{'yes' if x.stock_0p1 else 'no':<6} "
              f"{min_diameter(T_REF, x, False):>6.1f} mm "
              f"{min_diameter(T_REF, x):>7.1f} mm")
    print("\n   Only 11R51 has a published thickness trend, so only its")
    print("   figures are corrected to 0.1 mm. The others are quoted at the")
    print("   thickness their maker measured, which flatters 11R51's rivals.")

    print("\n" + "=" * 76)
    print("7. Why travel in kilometres does not measure this")
    print("=" * 76)
    strokes = (0.05, 0.10, 0.20, 0.50, 1.00)
    print(f"\n{'rollers':>9} {'crossings':>11}" +
          "".join(f" {s * 1000:>7.0f} mm" for s in strokes))
    print("-" * (21 + 11 * len(strokes)))
    for D in (14, 18, 20, 22, 24):
        p = passes_wrapped(float(D), float(D))
        row = f"{D:>7} mm {_f(p):>11}"
        for s in strokes:
            v = travel_km(p, s)
            row += f" {('unlimited' if v == float('inf') else f'{v:,.0f} km'):>10}"
        print(row)
    print("\n   Headings are the stroke the carriage repeats. The same strip")
    print("   lasts twenty times further on a long stroke than a short one,")
    print("   so a bare kilometre figure describes the duty cycle, not the")
    print("   strip. State crossings of one point instead:")
    print("\n       travel [m] = crossings to failure x stroke [m]")
    print("\n   For a mixed duty cycle add up the damage at the busiest point")
    print("   and replace the strip when the sum reaches 1.")
    print("\n   None of this covers the two things that actually end the life")
    print("   of a cover strip in the field: it ripples until the magnets no")
    print("   longer hold it flat, and it wears by rubbing. Treat the strip")
    print("   as a wear part and inspect it, rather than trusting a number.")


if __name__ == "__main__":
    main()
