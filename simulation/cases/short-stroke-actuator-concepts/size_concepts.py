"""First-order sizing for three 50 x 50 x 20 mm short-stroke actuator concepts.

Run from the repository root:

    python simulation/cases/short-stroke-actuator-concepts/size_concepts.py

The models are lumped and conservative. They answer "does the physics fit
the box?" — not a detailed magnetic/FEA design. Numbers feed
``simulation/results/short-stroke-actuator-concepts/summary.md``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

MU0 = 1.25663706212e-6  # H/m
PI = math.pi


@dataclass(frozen=True)
class Requirements:
    force_n: float = 200.0
    stroke_m: float = 100e-6  # total travel (peak-to-peak)
    bandwidth_hz: float = 10.0
    width_m: float = 50e-3
    depth_m: float = 50e-3
    height_m: float = 20e-3
    bom_eur: float = 100.0
    # Closed-loop plant should sit several times above the spec.
    bandwidth_margin: float = 3.0


@dataclass
class Check:
    name: str
    value: str
    required: str
    passed: bool
    note: str = ""


@dataclass
class Concept:
    slug: str
    title: str
    checks: list[Check] = field(default_factory=list)
    extras: dict[str, str] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


def _fmt(value: float, unit: str, digits: int = 3) -> str:
    return f"{value:.{digits}g} {unit}"


def _check(name: str, value: float, required: float, unit: str, ge: bool = True, note: str = "") -> Check:
    passed = value >= required if ge else value <= required
    cmp = ">=" if ge else "<="
    return Check(name, _fmt(value, unit), f"{cmp} {_fmt(required, unit)}", passed, note)


def reaction_mass_kg(req: Requirements, freq_hz: float) -> float:
    """Proof mass needed to produce req.force_n at freq_hz within req.stroke_m.

    x = a / omega^2, F = m a  =>  m = F / (omega^2 x)
    Stroke here is peak (half of peak-to-peak) because a sine of amplitude A
    has peak displacement A.
    """
    omega = 2 * PI * freq_hz
    peak = req.stroke_m / 2.0
    return req.force_n / (omega * omega * peak)


def envelope_steel_mass_kg(req: Requirements) -> float:
    volume = req.width_m * req.depth_m * req.height_m
    return 7800.0 * volume


def concept_reluctance(req: Requirements) -> Concept:
    """PM-biased differential reluctance with a flexure-guided armature.

    Two opposing gaps, bias B0 from a permanent magnet, control field ±b from
    a coil. Net force is linear in b to first order:

        F = 2 * B0 * b * A / mu0

    That F is unsaturated Maxwell force on the assumed pole face — not a
    packaged continuous rating. See format_catalog_report() and
    docs/log/2026-09-02_fluxthor-reluctance-force-density.md.
    """
    pole_a = 20e-3 * 20e-3  # m^2, one gap
    b0 = 0.80  # T, PM bias in the gap
    b_ctrl = 0.40  # T, coil-produced field
    g0 = 0.30e-3  # m, nominal gap (travel + residual)
    n_turns = 100
    i_peak = 1.4  # A

    force = 2.0 * b0 * b_ctrl * pole_a / MU0
    stroke = 2.0 * (g0 - 0.10e-3)  # leave 0.10 mm residual per side
    # Control flux crosses both gaps in series. The original one-gap MMF
    # (b*g/mu0 ≈ 96 At) under-counted Ampère's law by 2×.
    mmf_needed_one_gap = b_ctrl * g0 / MU0
    mmf_needed = 2.0 * mmf_needed_one_gap
    mmf_have = n_turns * i_peak

    # Inductance of one gap winding, current-control voltage at 10 Hz and 100 Hz.
    inductance = n_turns**2 * MU0 * pole_a / g0
    i_amp = i_peak
    v_l_10 = inductance * (2 * PI * 10.0 * i_amp)
    v_l_100 = inductance * (2 * PI * 100.0 * i_amp)

    # Mean turn length ~ 4*25 mm; 0.4 mm Cu.
    mean_turn_m = 0.10
    copper_resistivity = 1.7e-8
    wire_area = PI * (0.20e-3) ** 2
    resistance = copper_resistivity * n_turns * mean_turn_m / wire_area
    p_copper = i_peak**2 * resistance

    # Bandwidth vs the measured spindle stiffness (100 N / 140 um, 2026-01-27),
    # not vs a stiff flexure. A force actuator should be softer than the machine.
    k_machine = 100.0 / 140e-6
    m_arm = 0.08
    f_mech = (1.0 / (2.0 * PI)) * math.sqrt(k_machine / m_arm)

    # Pure-reluctance negative stiffness scale: k ≈ 2 F / g. PM bias can reduce
    # this, but not below the same order. Open-loop snap-in unless k_flex +
    # k_machine > |k_mag|.
    k_mag = 2.0 * force / g0
    k_flex_min = max(0.0, k_mag - k_machine)
    force_after_flexure = force / (1.0 + k_flex_min / k_machine) if k_machine else 0.0

    height_stack = 3.0e-3 + 8.0e-3 + g0 + 4.0e-3 + 2.5e-3  # backiron, window, gap, I-bar, flexure
    bom = 55.0
    envelope_cm3 = req.width_m * req.depth_m * req.height_m * 1e6

    checks = [
        _check("force (pole-face Maxwell)", force, req.force_n, "N", note="unsaturated, assumed 20x20 mm pole"),
        _check("stroke", stroke, req.stroke_m, "m", note="two-sided gap, 0.10 mm residual"),
        _check("mech resonance", f_mech, req.bandwidth_hz * req.bandwidth_margin, "Hz"),
        _check("envelope height", height_stack, req.height_m, "m", ge=False),
        _check("coil MMF (two gaps)", mmf_have, mmf_needed, "At", note=f"one-gap figure was {mmf_needed_one_gap:.0f} At"),
        _check("BOM", bom, req.bom_eur, "EUR", ge=False),
    ]
    return Concept(
        slug="pm-differential-reluctance",
        title="PM-biased differential reluctance + flexure guide",
        checks=checks,
        extras={
            "pole area": _fmt(pole_a * 1e6, "mm^2"),
            "B0 / b": f"{b0:g} T / {b_ctrl:g} T",
            "NI needed / have": f"{mmf_needed:.0f} At / {mmf_have:.0f} At",
            "L (one coil)": _fmt(inductance * 1e3, "mH"),
            "R coil": _fmt(resistance, "ohm"),
            "P copper at Ipeak": _fmt(p_copper, "W"),
            "V_L at 10 Hz": _fmt(v_l_10, "V"),
            "V_L at 100 Hz": _fmt(v_l_100, "V"),
            "k_machine (measured)": _fmt(k_machine / 1e6, "N/um"),
            "k_mag (≈2F/g)": _fmt(k_mag / 1e6, "N/um"),
            "k_flex to avoid snap-in": _fmt(k_flex_min / 1e6, "N/um"),
            "F to machine after that flexure": _fmt(force_after_flexure, "N"),
            "envelope force density": _fmt(force / envelope_cm3, "N/cm^3"),
            "6-DOF stretch": "3-sector puck: z + rx + ry at ~200 N; x/y/rz at much lower force",
        },
    )


def concept_piezo_flextensional(req: Requirements) -> Concept:
    """Multilayer PZT stack in a steel flextensional (diamond / APA-like) shell.

    Work is roughly conserved: F_block * free_stroke is invariant under an
    ideal lever. Hinge compliance is modelled as 60 % force efficiency.
    """
    stack_free = 20e-6  # m, 10 x 10 x 18 mm class stack at 150 V
    stack_block = 3200.0  # N
    amp = 6.0
    efficiency = 0.60  # flexure hinge loss
    stroke = stack_free * amp
    force = stack_block / amp * efficiency

    # Bias around mid-stroke so the preloaded shell can push and pull.
    preload = 250.0  # N at the output
    stack_preload = preload * amp
    bidirectional_force = min(force, preload)

    k_machine = 100.0 / 140e-6
    m_out = 0.12  # shell + platen
    f_mech = (1.0 / (2.0 * PI)) * math.sqrt(k_machine / m_out)
    k_out = force / (stroke / 2.0) if stroke else 0.0

    # Envelope: diamond ~ 48 x 18 x 18 mm plus 2 mm platen. Fits 50 x 50 x 20.
    length_mm = 48.0
    height_mm = 18.0
    width_mm = 18.0

    cap = 4.5e-6  # F, typical 10 x 10 x 18 mm
    v_drive = 150.0
    # Dissipative charge/discharge, no energy recovery.
    p_avg_10 = cap * v_drive**2 * 10.0 / 2.0
    p_avg_200 = cap * v_drive**2 * 200.0 / 2.0

    bom = 90.0  # cheap stack + laser-cut shell + DIY 150 V driver

    checks = [
        _check("force (preloaded, two-sided)", bidirectional_force, req.force_n, "N"),
        _check("stroke", stroke, req.stroke_m, "m", note=f"amplification {amp:g} x"),
        _check("mech resonance", f_mech, req.bandwidth_hz * req.bandwidth_margin, "Hz"),
        _check("envelope length", length_mm, 50.0, "mm", ge=False),
        _check("envelope height", height_mm, 20.0, "mm", ge=False),
        _check("envelope width", width_mm, 50.0, "mm", ge=False),
        _check("stack preload vs blocking", stack_block, stack_preload, "N"),
        _check("BOM", bom, req.bom_eur, "EUR", ge=False),
    ]
    return Concept(
        slug="flextensional-piezo",
        title="Flextensional multilayer piezo",
        checks=checks,
        extras={
            "stack": "10 x 10 x 18 mm, ~20 um free, ~3200 N blocking",
            "amplification": f"{amp:g} x at {efficiency:.0%} hinge efficiency",
            "output stiffness": _fmt(k_out / 1e6, "N/um"),
            "P avg at 10 Hz (lossy drive)": _fmt(p_avg_10, "W"),
            "P avg at 200 Hz (lossy drive)": _fmt(p_avg_200, "W"),
            "commercial analogue": "Cedrat APA40SM: 54 um, 260 N, 15 x 27 x 12 mm (stroke short of 0.1 mm)",
            "6-DOF stretch": "three 120 deg stacks -> z/rx/ry; 50 x 50 x 20 mm is tight for three shells",
        },
    )


def concept_lorentz_lever(req: Requirements) -> Concept:
    """Moving-coil Lorentz motor with a flexure lever.

    Continuous Lorentz force in this volume is tens of newtons. A lever of
    ratio n trades coil stroke for output force.
    """
    b_gap = 0.85  # T
    j_peak = 12e6  # A/m^2, short-duty
    j_cont = 5e6
    copper_volume = 3.5e-6  # m^3, ~3.5 cm^3 in a 4 mm gap window
    n_lever = 7.0

    f_coil_peak = j_peak * copper_volume * b_gap
    f_coil_cont = j_cont * copper_volume * b_gap
    f_out_peak = f_coil_peak * n_lever
    f_out_cont = f_coil_cont * n_lever
    stroke_coil = req.stroke_m * n_lever
    gap_needed = stroke_coil + 0.40e-3  # mechanical clearance

    m_coil = copper_volume * 8960.0 + 0.02  # copper + former
    m_out = m_coil * n_lever**2 + 0.05  # reflected + lever
    k_machine = 100.0 / 140e-6
    f_mech = (1.0 / (2.0 * PI)) * math.sqrt(k_machine / m_out)
    k_out = k_machine

    # Rotary-eccentric alternative, for the extras table.
    j_rotor = 1.5e-6  # kg m^2, 2207-class
    r_ecc = req.stroke_m / 2.0  # direct 50 um crank radius
    m_reflected_rotary = j_rotor / (r_ecc**2)
    f_rotary = (1.0 / (2.0 * PI)) * math.sqrt(k_out / m_reflected_rotary)
    t_rotary = req.force_n * r_ecc

    height_mm = 4.0 + 4.0 + 4.0 + 5.0  # magnet, gap/coil, magnet, return+flexure
    bom = 70.0

    checks = [
        _check("force peak", f_out_peak, req.force_n, "N", note=f"lever {n_lever:g}:1, short duty"),
        _check("coil stroke vs 20 mm box", stroke_coil, req.height_m, "m", ge=False),
        _check("airgap fits height", gap_needed, 5.0e-3, "m", ge=False),
        _check("mech resonance", f_mech, req.bandwidth_hz * req.bandwidth_margin, "Hz"),
        _check("envelope height", height_mm * 1e-3, req.height_m, "m", ge=False),
        _check("BOM", bom, req.bom_eur, "EUR", ge=False),
    ]
    return Concept(
        slug="lorentz-flexure-lever",
        title="Lorentz voice coil + flexure lever",
        checks=checks,
        extras={
            "coil peak / cont": f"{f_coil_peak:.0f} N / {f_coil_cont:.0f} N",
            "output peak / cont": f"{f_out_peak:.0f} N / {f_out_cont:.0f} N",
            "continuous 200 N": "NO — natural cooling in this volume; short-duty / chatter bursts only",
            "coil stroke": _fmt(stroke_coil * 1e3, "mm"),
            "reflected moving mass": _fmt(m_out, "kg"),
            "rotary eccentric T": _fmt(t_rotary * 1e3, "mNm"),
            "rotary reflected mass": _fmt(m_reflected_rotary, "kg"),
            "rotary resonance vs k_out": _fmt(f_rotary, "Hz"),
            "6-DOF stretch": "3-4 coils under a flexure platen for z/rx/ry; laterals starve for copper",
        },
    )


# Fluxthor catalog, 2026-09-02, https://www.fluxthor.com/products/reluctance-actuator
# and https://www.fluxthor.com/products/hybrid-reluctance-actuator
# Hercules (reluctance-tuning) shares the Rhino force / Km table.
FLUXTHOR_ATLAS = (
    # name, w_mm, d_mm, h_mm, F_N, Km_N_per_A, stroke_um, m_g
    ("Atlas-RA30", 30, 30, 40, 9.0, 29.0, 100, 33),
    ("Atlas-RA40", 40, 40, 50, 32.0, 73.0, 200, 52),
    ("Atlas-RA60", 60, 60, 60, 75.0, 56.0, 500, 89),
    ("Atlas-RA100", 100, 100, 70, 286.0, 35.0, 1000, 235),
)
FLUXTHOR_RHINO = (
    ("Rhino-HRA30", 30, 30, 40, 7.0, 245.0, 100, 36),
    ("Rhino-HRA40", 40, 40, 50, 21.0, 468.0, 200, 51),
    ("Rhino-HRA60", 60, 60, 60, 24.0, 224.0, 500, 99),
    ("Rhino-HRA100", 100, 100, 70, 57.0, 131.0, 1000, 210),
)


def _catalog_row(name: str, w: float, d: float, h: float, force: float, km: float, stroke_um: float, mass_g: float) -> dict[str, float | str]:
    vol_cm3 = (w * d * h) / 1000.0
    i_cont = force / km if km else 0.0
    return {
        "name": name,
        "envelope": f"{w:.0f}x{d:.0f}x{h:.0f} mm",
        "vol_cm3": vol_cm3,
        "force": force,
        "n_per_cm3": force / vol_cm3,
        "km": km,
        "i_cont": i_cont,
        "stroke_um": stroke_um,
        "mass_g": mass_g,
    }


def format_catalog_report(req: Requirements) -> str:
    """Compare pole-face Maxwell sizing with Fluxthor packaged continuous ratings."""
    envelope_cm3 = req.width_m * req.depth_m * req.height_m * 1e6
    pole_a = 20e-3 * 20e-3
    b0, b_ctrl = 0.80, 0.40
    our_force = 2.0 * b0 * b_ctrl * pole_a / MU0
    our_density = our_force / envelope_cm3
    pressure_12t = (1.2**2) / (2.0 * MU0)  # Pa

    lines = [
        "Fluxthor catalog check (packaged continuous force)",
        "-------------------------------------------------",
        "Source: fluxthor.com Atlas (pure reluctance) and Rhino (PM-biased hybrid),",
        "2026-09-02. Same envelope family as Hercules (reluctance tuning).",
        "",
        f"  our envelope                 {envelope_cm3:.0f} cm^3",
        f"  our pole-face Maxwell force  {our_force:.0f} N  ({our_density:.2f} N/cm^3)",
        f"  magnetic pressure at 1.2 T   {pressure_12t/1e6:.2f} MPa  ({pressure_12t/1e4:.0f} N/cm^2 of pole)",
        "",
        "  model          envelope         vol    F_cont   N/cm^3    Km     I_cont  stroke",
        "  -------------- ---------------- ------ -------- --------- ------ ------- ------",
    ]
    for row_src in (*FLUXTHOR_ATLAS, *FLUXTHOR_RHINO):
        r = _catalog_row(*row_src)
        lines.append(
            f"  {r['name']:<14} {r['envelope']:<16} {r['vol_cm3']:5.0f} "
            f"{r['force']:7.0f} N {r['n_per_cm3']:7.2f}  {r['km']:5.0f} "
            f"{r['i_cont']:6.3f} A {r['stroke_um']:5.0f} um"
        )

    atlas_density = max(float(_catalog_row(*row)["n_per_cm3"]) for row in FLUXTHOR_ATLAS)
    rhino40 = _catalog_row(*FLUXTHOR_RHINO[1])
    scaled_atlas = atlas_density * envelope_cm3
    lines.extend(
        [
            "",
            f"  Atlas peak catalog density     {atlas_density:.2f} N/cm^3  (~{our_density/atlas_density:.0f} x below our Maxwell figure)",
            f"  that density in our 50 cm^3    {scaled_atlas:.0f} N continuous",
            f"  Rhino-HRA40 Km / I_cont        {rhino40['km']:.0f} N/A / {rhino40['i_cont']:.3f} A  (precision thermal, not saturation)",
            "  20 mm height vs their 40-70 mm  they spend the extra length on coil + compliant guide",
            "",
            "  The Maxwell number is an upper bound on pole-face pressure. A packaged, thermally",
            "  rated, flexure-guided device lands near 0.3-0.4 N/cm^3. 200 N continuous in this",
            "  box is not supported by the catalog. A mill can run hotter than a lithography",
            "  stage, so we can beat Fluxthor's *rating*, not their physics.",
            "",
        ]
    )
    return "\n".join(lines)


def format_report(req: Requirements, concepts: list[Concept]) -> str:
    steel = envelope_steel_mass_kg(req)
    lines = [
        "Short-stroke actuator concept sizing",
        "====================================",
        "",
        "Requirements",
        f"  force        {req.force_n:g} N, two-sided",
        f"  travel       {req.stroke_m * 1e3:g} mm peak-to-peak",
        f"  bandwidth    > {req.bandwidth_hz:g} Hz (plant margin {req.bandwidth_margin:g} x)",
        f"  envelope     {req.width_m*1e3:g} x {req.depth_m*1e3:g} x {req.height_m*1e3:g} mm",
        f"  BOM          < {req.bom_eur:g} EUR (sensor excluded)",
        "",
        "Inertial (reaction-mass) sanity check",
        f"  steel mass of the whole envelope     {steel:.2f} kg",
        f"  proof mass needed at {req.bandwidth_hz:g} Hz     {reaction_mass_kg(req, req.bandwidth_hz):.0f} kg",
        f"  proof mass needed at 100 Hz          {reaction_mass_kg(req, 100.0):.2f} kg",
        f"  proof mass needed at 700 Hz          {reaction_mass_kg(req, 700.0):.3f} kg",
        "  => 10 Hz / 0.1 mm / 200 N cannot be a proof-mass shaker in this box.",
        "     Treat the device as a coupling actuator between two structures.",
        "",
    ]
    for concept in concepts:
        flag = "PASS" if concept.passed else "FAIL"
        lines.append(f"{concept.title}  [{flag}]")
        lines.append("-" * len(concept.title))
        for chk in concept.checks:
            mark = "ok" if chk.passed else "NO"
            extra = f"  ({chk.note})" if chk.note else ""
            lines.append(f"  [{mark}] {chk.name}: {chk.value}  (need {chk.required}){extra}")
        if concept.extras:
            lines.append("  extras:")
            for key, val in concept.extras.items():
                lines.append(f"    {key}: {val}")
        lines.append("")
    lines.append(format_catalog_report(req))
    return "\n".join(lines)


def main() -> int:
    req = Requirements()
    concepts = [
        concept_reluctance(req),
        concept_piezo_flextensional(req),
        concept_lorentz_lever(req),
    ]
    print(format_report(req, concepts))
    failed = [c.slug for c in concepts if not c.passed]
    if failed:
        print("Failed concepts:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
