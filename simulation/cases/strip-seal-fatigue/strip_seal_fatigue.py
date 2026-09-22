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
The strip wraps the outside of a roller, so the neutral axis sits at radius
(D + t) / 2 and the surface bending stress is

    sigma_max = E * t / (D + t)

Sandvik write the same thing as E * t / D for D much larger than t.

Fatigue is driven by the stress AMPLITUDE. The mean stress is a smaller
correction, handled by Goodman. Which amplitude the geometry delivers depends
on whether the strip is bent one way or both ways, and that is the single
largest factor in the whole calculation.
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
    """

    def __init__(self, name, designation, E, Rm, Rp02, sigma_w,
                 stock_0p1, survival, source, note=""):
        self.name = name
        self.designation = designation
        self.E = E                  # MPa
        self.Rm = Rm                # MPa
        self.Rp02 = Rp02            # MPa
        self.sigma_w = sigma_w      # MPa
        self.stock_0p1 = stock_0p1  # is 0.1 mm a standard thickness?
        self.survival = survival
        self.source = source
        self.note = note


MATERIALS = [
    Strip("11R51 cold rolled", "EN 1.4310 / AISI 301", 185000, 2050, 1975, 775,
          True, "50 % at 2e6", "11R51",
          "sigma_w measured at 0.25 mm and Rm 2100; 0.1 mm is likely better"),
    Strip("Hiflex", "UNS S42026, near 1.4031", 210000, 1900, 1500, 920,
          False, "5 % at 2e6", "Hiflex",
          "molybdenum alloyed, stock starts at 0.152 mm"),
    Strip("Springflex cold rolled", "EN 1.4462 duplex", 200000, 1900, 1700, 615,
          False, "50 % at 2e6", "Springflex",
          "best corrosion resistance, sigma_w measured at 0.50 mm"),
    Strip("IPCO 1200SA belt", "EN 1.4310, belt temper", 182000, 1200, 980, 470,
          False, "50 % at 2e6", "IPCO",
          "soft belt temper, kept for contrast only"),
    Strip("IPCO 1850SM belt", "AISI 1065 carbon", 210000, 1800, 1450, 860,
          False, "50 % at 2e6", "IPCO",
          "highest fatigue strength of the belt grades, but it rusts"),
]

DEFAULT = MATERIALS[0]

# 11R51 standard thicknesses at Rm 2050, from the datasheet.
STOCK_MM = (0.03, 0.04, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30)

T_REF = 0.1
N_KNEE = 2.0e6


# --------------------------------------------------------------------------
# Stress and life
# --------------------------------------------------------------------------

def bending_stress(t, D, m=DEFAULT):
    """Peak surface bending stress of a strip of thickness t on diameter D."""
    return m.E * t / (D + t)


def goodman_reversed(amplitude, mean, m=DEFAULT):
    """Equivalent fully reversed amplitude. A compressive mean gets no credit."""
    if mean <= 0.0:
        return amplitude
    if mean >= m.Rm:
        return float("inf")
    return amplitude / (1.0 - mean / m.Rm)


def allowable_peak_one_way(m=DEFAULT):
    """Peak stress allowed when the strip is only ever bent one way.

    The cycle runs 0 -> sigma_max -> 0, so the amplitude is half the peak and
    the mean is the other half. Inverting Goodman for that case gives:

        sigma_peak = 2 * sigma_w / (1 + sigma_w / Rm)

    Alleima publish this same conversion for Hiflex as 620 +/- 620 MPa.
    check_goodman() reproduces it.
    """
    return 2.0 * m.sigma_w / (1.0 + m.sigma_w / m.Rm)


def allowable_peak_both_ways(m=DEFAULT):
    """Peak stress allowed when the strip is bent both ways.

    The amplitude is now the whole peak and the mean is zero, so the published
    reverse bending limit applies directly.
    """
    return m.sigma_w


def cycles_to_failure(sigma_ar, m=DEFAULT):
    """Basquin line through 0.9 * Rm at 1e3 cycles and sigma_w at 2e6."""
    if sigma_ar <= m.sigma_w:
        return float("inf")
    s1 = 0.9 * m.Rm
    slope = math.log10(m.sigma_w / s1) / math.log10(N_KNEE / 1.0e3)
    return 1.0e3 * (sigma_ar / s1) ** (1.0 / slope)


def min_diameter(t, m=DEFAULT, both_ways=True):
    """Smallest roller that keeps the strip below its fatigue limit."""
    allow = allowable_peak_both_ways(m) if both_ways else allowable_peak_one_way(m)
    allow = min(allow, m.Rp02)
    return m.E * t / allow - t


def max_thickness(D, m=DEFAULT, both_ways=True):
    """Thickest strip that stays below the fatigue limit on a given roller."""
    allow = allowable_peak_both_ways(m) if both_ways else allowable_peak_one_way(m)
    allow = min(allow, m.Rp02)
    return D * allow / (m.E - allow)


def check_goodman():
    """Reproduce Alleima's own published Hiflex conversion, 620 +/- 620 MPa."""
    hiflex = next(x for x in MATERIALS if x.name == "Hiflex")
    got = allowable_peak_one_way(hiflex)
    if abs(got - 1240.0) > 1.0:
        raise AssertionError(f"Goodman check failed: {got:.1f} MPa, expected 1240")
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


def pass_history(d_outer, d_inner, t=T_REF, m=DEFAULT, repeats=8):
    """Stress at the critical surface for `repeats` carriage passes.

    The four rollers bend the strip up, down, down and up, and the strip runs
    straight between them, so the curvature returns to zero in between.
    Rollers 1 and 4 sit inside the slot and use d_outer. Rollers 2 and 3 sit
    above the carriage and use d_inner.
    """
    s1 = bending_stress(t, d_outer, m)
    s2 = bending_stress(t, d_inner, m)
    one = [0.0, +s1, 0.0, -s2, 0.0, -s2, 0.0, +s1, 0.0]
    return one * repeats


def _counted(d_outer, d_inner, t, m, repeats):
    """Cycles found in `repeats` passes, keyed by (amplitude, mean)."""
    out = {}
    for rng, mean, count in rainflow(pass_history(d_outer, d_inner, t, m, repeats)):
        key = (round(rng / 2.0, 1), round(mean, 1))
        out[key] = out.get(key, 0.0) + count
    return out


def cycles_per_pass(d_outer, d_inner, t=T_REF, m=DEFAULT, repeats=8):
    """Cycles that one carriage pass adds, keyed by (amplitude, mean).

    Counting a repeating history leaves a residue of half cycles at the ends,
    which would be charged to whichever pass happens to be last. Counting
    `repeats` and `repeats + 1` passes and taking the difference cancels that
    residue exactly, because the extra pass adds one block of closed cycles
    and nothing else.
    """
    more = _counted(d_outer, d_inner, t, m, repeats + 1)
    less = _counted(d_outer, d_inner, t, m, repeats)
    out = {}
    for key in set(more) | set(less):
        n = more.get(key, 0.0) - less.get(key, 0.0)
        if n > 1e-9:
            out[key] = n
    return out


def damage_per_pass(d_outer, d_inner, t=T_REF, m=DEFAULT, repeats=8):
    """Miner damage for one carriage pass, plus the cycles it breaks into."""
    breakdown = cycles_per_pass(d_outer, d_inner, t, m, repeats)
    total = 0.0
    for (amp, mean), count in breakdown.items():
        nf = cycles_to_failure(goodman_reversed(amp, mean, m), m)
        if nf != float("inf"):
            total += count / nf
    return total, breakdown


def passes_to_failure(d_outer, d_inner, t=T_REF, m=DEFAULT):
    """Carriage crossings of one point of the strip before a crack starts."""
    if bending_stress(t, d_outer, m) >= m.Rp02:
        return 0.0  # the strip takes a permanent set and stops sealing
    d, _ = damage_per_pass(d_outer, d_inner, t, m)
    return float("inf") if d == 0.0 else 1.0 / d


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
          f"{check_goodman():.0f} MPa, expected 1240 MPa. Passed.\n")

    print("=" * 76)
    print("1. Materials, and the smallest roller each one allows at 0.1 mm")
    print("=" * 76)
    print(f"\n{'material':<23} {'designation':<24} {'0.1mm':<6} "
          f"{'one way':>9} {'both ways':>10}")
    print("-" * 76)
    for m in sorted(MATERIALS, key=lambda x: min_diameter(T_REF, x)):
        print(f"{m.name:<23} {m.designation:<24} "
              f"{'yes' if m.stock_0p1 else 'no':<6} "
              f"{min_diameter(T_REF, m, False):>6.1f} mm {min_diameter(T_REF, m):>7.1f} mm")
    print("\n  'one way' is a strip only ever bent in one direction.")
    print("  'both ways' is the four roller layout on this stage.")

    m = DEFAULT
    print("\n" + "=" * 76)
    print(f"2. What one carriage pass costs, {m.designation} at 0.1 mm")
    print("=" * 76)
    _, br = damage_per_pass(20.0, 20.0)
    print(f"\nFour rollers at 20 mm. Peak bending stress "
          f"{bending_stress(T_REF, 20.0):.0f} MPa. Rainflow of one pass:\n")
    for (amp, mean), n in sorted(br.items(), key=lambda x: -x[0][0]):
        sar = goodman_reversed(amp, mean)
        print(f"   {n:>4.2f} cycle  amplitude {amp:>6.0f}  mean {mean:>7.0f}"
              f"  -> reversed {sar:>6.0f} MPa, life {_f(cycles_to_failure(sar))}")
    print("\n   One pass is one full reversal. Not four, and not one per roller.")
    print("   Passing through zero between rollers resets nothing: rainflow")
    print("   closes the loop between the highest and the lowest point.")

    print("\n" + "=" * 76)
    print("3. Life against roller size, four equal rollers, 0.1 mm strip")
    print("=" * 76)
    print(f"\n{'D [mm]':>7} {'stress':>8} {'/Rp0.2':>8} {'passes':>12}")
    print("-" * 38)
    for D in range(14, 26, 2):
        s = bending_stress(T_REF, float(D))
        print(f"{D:>7} {s:>7.0f} {s/m.Rp02:>8.2f} "
              f"{_f(passes_to_failure(float(D), float(D))):>12}")

    print("\n" + "=" * 76)
    print("4. The cheap fix: open rollers 2 and 3, keep 1 and 4 tight")
    print("=" * 76)
    print(f"\n{'1 and 4':>9} {'2 and 3':>9} {'passes':>12} {'gain':>7}")
    print("-" * 40)
    for outer, inner in ((14, 14), (14, 60), (20, 20), (20, 40), (20, 60), (24, 24)):
        p = passes_to_failure(float(outer), float(inner))
        base = passes_to_failure(float(outer), float(outer))
        gain = "-" if p == float("inf") or base in (0.0, float("inf")) \
            else f"{p/base:.0f}x"
        print(f"{outer:>7} mm {inner:>7} mm {_f(p):>12} {gain:>7}")
    print("\n   Opening only the two rollers above the carriage turns the")
    print("   reversal back into a one way bend, because the downward peak")
    print("   shrinks while the upward peak stays.")

    print("\n" + "=" * 76)
    print("5. Designs that need no life figure at all")
    print("=" * 76)
    print(f"\n{'D [mm]':>8} {'t needed':>11} {'order':>10}")
    print("-" * 31)
    for D in (14, 16, 18, 20, 22, 24):
        t = max_thickness(float(D))
        fits = [x for x in STOCK_MM if x <= t]
        print(f"{D:>6} mm {t:>9.3f} mm "
              f"{(f'{max(fits):.2f} mm' if fits else 'none'):>10}")

    print("\n" + "=" * 76)
    print("6. Why travel in kilometres does not measure this")
    print("=" * 76)
    strokes = (0.05, 0.10, 0.20, 0.50, 1.00)
    print(f"\n{'rollers':>9} {'passes':>11}" +
          "".join(f" {s*1000:>7.0f} mm" for s in strokes))
    print("-" * (21 + 11 * len(strokes)))
    for D in (14, 18, 20, 22, 24):
        p = passes_to_failure(float(D), float(D))
        row = f"{D:>7} mm {_f(p):>11}"
        for s in strokes:
            v = travel_km(p, s)
            row += f" {('unlimited' if v == float('inf') else f'{v:,.0f} km'):>10}"
        print(row)
    print("\n   Headings are the stroke the carriage repeats. The same strip")
    print("   lasts twenty times further on a long stroke than a short one,")
    print("   so a bare kilometre figure describes the duty cycle, not the")
    print("   strip. State crossings of one point instead:")
    print("\n       travel [m] = passes to failure x stroke [m]")
    print("\n   For a mixed duty cycle add up the damage at the busiest point")
    print("   and replace the strip when the sum reaches 1.")


if __name__ == "__main__":
    main()
