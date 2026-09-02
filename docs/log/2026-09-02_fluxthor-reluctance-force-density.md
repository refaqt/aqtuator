# 2026-09-02 — Fluxthor reluctance force density vs our Maxwell sizing

**Role(s):** engineering, simulation

## Goal

Check why [Fluxthor Atlas](https://www.fluxthor.com/products/reluctance-actuator)
continuous force is much lower than the 204 N we sized for a 50 × 50 × 20 mm PM-biased
reluctance puck
([short-stroke concepts](../../simulation/cases/short-stroke-actuator-concepts/),
[morning log](2026-09-02_short-stroke-actuator-concepts.md)).

## Work Done

- Pulled Atlas (pure reluctance), Rhino (hybrid / PM-biased), and Hercules (reluctance
  tuning) datasheets from fluxthor.com. Atlas is their high-force line; Rhino/Hercules
  trade force for motor constant and thermal stability. Same 30 / 40 / 60 / 100 mm family,
  40–70 mm thick, flexure-guided mover, stroke 100–1000 µm.
- Re-ran the lumped sizer with two-gap MMF, magnetic negative stiffness, and a catalog
  table. Script:
  [`simulation/cases/short-stroke-actuator-concepts/size_concepts.py`](../../simulation/cases/short-stroke-actuator-concepts/size_concepts.py).

## Findings

Fluxthor is not a low-force-density company. They advertise "highest force density of
all electromagnetic actuators." Their *packaged continuous* density is still only
**0.25–0.41 N/cm³** (Atlas). We quoted **4.1 N/cm³**. That is a 10× gap in the quantity
being named, not a 10× error in Maxwell's equations.

| | Our sizing | Fluxthor Atlas (peak of line) | Atlas scaled to 50 cm³ |
| --- | ---: | ---: | ---: |
| Envelope | 50 × 50 × 20 mm (50 cm³) | 100 × 100 × 70 mm (700 cm³) | 50 cm³ |
| Force | 204 N pole-face Maxwell | 286 N continuous | ~20 N continuous |
| N/cm³ | 4.1 | 0.41 | 0.41 |
| Current at that force | 1.4 A | 8.2 A (RA100) / 0.44 A (RA40) | — |

Closest volume: Atlas-RA30 is 36 cm³ and 9 N at 100 µm stroke — same stroke class as
ours, 0.25 N/cm³. Closest footprint: Atlas-RA40 is 40 × 40 × 50 mm and 32 N.

Rhino (the topology we actually sized — PM bias + coils + compliant mechanism) is
*weaker* than Atlas at the same size (HRA40: ±21 N) with a much higher Km (468 N/A,
45 mA at rated force). They are not maximising force. They are selling nanometer-stable,
near-zero-heat stages for semiconductor and optics. Atlas is the "high force" product
and still sits at ~0.4 N/cm³.

**What was wrong in our reasoning**

1. **Maxwell pressure on an assumed pole was treated as device force density.**
   1.2 T is 0.57 MPa = 57 N/cm² of pole face. A 20 × 20 mm pole in a 50 × 50 mm face
   is already only 16 % fill. Catalog density divides by the whole module after housing,
   return iron, coil, magnet, and flexure, at a thermally safe current, not at Bsat.
2. **Continuous vs peak, and thermal class.** 1.4 A in 0.4 mm wire is ~11 A/mm² and
   ~3 W. Fine on a mill; fatal for a lithography stage. Fluxthor's I_cont on Rhino-HRA40
   is 45 mA. Running Atlas hotter would raise force (F ∝ I² on the pure-reluctance
   line, until saturation). It would not give 4 N/cm³ packaged.
3. **Negative stiffness vs "flexure much softer than the machine."** Those two
   requirements fight. `k_mag ≈ 2F/g ≈ 1.4 N/µm` > `k_machine = 0.71 N/µm`, so the
   armature snaps in unless the flexure (or a loop) stabilises it. Fluxthor's product
   *is* that compliant mechanism. A snap-in-safe flexure leaves ~107 N of the 204 N
   at the spindle — before leakage.
4. **Ampère's law counted one gap.** Control flux crosses both 0.3 mm gaps: 191 At
   needed, 140 At in the coil. The original "PASS" used 96 At.
5. **20 mm height.** Their shortest pack is 40 mm. The extra length is coil window and
   flexure. A 20 mm puck is a worse packing problem than their cubes, not a better one.

Literature in the same family (Cigarini / Ito / Schitter 2019; Swank TU Delft 2023,
the Fluxthor research line) reports HRA force density up to ~10× a voice coil *on the
magnetic circuit*, with a large negative stiffness and FEA correction factors on the
lumped model. That matches "Maxwell is high, the box is not."

**What to believe for AQTUATOR**

- 204 N: upper bound on unsaturated pole-face force, not a spec.
- Catalog-like continuous in this box: ~20 N.
- Honest custom mill puck (hotter, shorter gap, less precision flexure): tens of
  newtons continuous; ~100 N as a short-duty stretch after the flexure tax.
- If 200 N must hold in 50 × 50 × 20 mm: flextensional piezo (Cedrat APA40SM is 260 N
  in a smaller box, stroke 54 µm) is the only concept with a commercial analogue.

## Decisions

- Stop treating the reluctance concept as a 200 N continuous pass.
- Keep 204 N only as a pole-face ceiling in the sizer.
- Catalog table lives in `size_concepts.py` so the comparison cannot drift from the
  write-up.

## Open Questions

- Can a mill-duty puck (few watts, no nanometer thermal budget) close much of the 10×
  gap without growing the 20 mm height?
- Is the 200 N target still required once delivered reluctance force is ~20–100 N?
- Closed-loop current/position control instead of a stiff flexure: would that return
  the flexure tax, at the cost of always-on control and snap-in on fault?

## Next Steps

- Freeze force target against the catalog-adjusted range before CAD.
- If reluctance is still the first experiment: E-I puck to measure F(I,g), k_mag, and
  heat — do not size the flexure as "much softer than the machine."
- Mistake logged:
  [2026-09-02 Maxwell stress as device force density](../mistakes/2026-09-02_maxwell-stress-as-device-force-density.md).
