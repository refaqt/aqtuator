# 2026-09-02 — Short-stroke actuator concepts

**Role(s):** engineering, hardware, simulation

## Goal

Find three low-cost, two-sided, high-force, short-stroke actuator ideas that fit
50 × 50 × 20 mm, with a first-order feasibility check against > 200 N, > 0.1 mm travel,
> 10 Hz, and BOM < 100 EUR (sensor provided).

## Work Done

- First-order sizing of three concepts. Script and write-up:
  [`simulation/cases/short-stroke-actuator-concepts`](../../simulation/cases/short-stroke-actuator-concepts/).
  Numbers:
  [`simulation/results/short-stroke-actuator-concepts/summary.md`](../../simulation/results/short-stroke-actuator-concepts/summary.md).
- Plant load used: measured spindle stiffness 100 N / 140 µm = 0.71 N/µm
  ([2026-01-27](2026-01-27_machine-stiffness-measurement.md)).
- Starting point for idea 1: [2026-08-24 reluctance note](2026-08-24_reluctance-actuator-investigation.md).

## Findings

Power is not the problem (~1.3 W peak at 10 Hz, 0.1 mm peak-to-peak, 200 N). Force
density, two-sidedness, and heat or reflected inertia are what bite.

This envelope cannot be a 10 Hz reaction-mass shaker:

| Frequency | Proof mass needed for 200 N at ±50 µm |
| --- | ---: |
| 10 Hz | ~1000 kg |
| 100 Hz | ~10 kg |
| 700 Hz (spindle mode, [2026-05-07](2026-05-07_frf-and-compliance-measurements.md)) | ~0.21 kg |

The whole 50 × 50 × 20 mm envelope in steel is 0.39 kg. The device has to be a coupling
actuator between two machine parts (or a short-stroke stage). At the 700 Hz spindle mode
an inertial armature of ~0.2 kg would start to make sense — that is a different operating
point than the 10 Hz floor.

**6-DOF at 200 N per axis does not fit.** Magnetic pressure at 1.2 T is about 0.57 N/mm².
The 50 × 50 mm face is 2500 mm²; even if it were all pole face that is only ~1400 N of
total force budget. Six axes × 200 N = 1200 N is already that entire budget. Realistic
stretch: z + rx + ry (piston / tip-tilt) at ~200 N axial, with much weaker x / y / rz.

### 1. PM-biased differential reluctance + flexure guide

Makes the 2026-08-24 reluctance idea two-sided. Magnet sets ~0.8 T in two opposing 0.3 mm
gaps; coil adds ±0.4 T. Net force linear in current to first order.

- Force: 204 N with a 20 × 20 mm pole
- Travel: 0.4 mm in that gap stack-up
- Coil: ~100 amp-turns, ~3 W
- Resonance vs machine (80 g armature): ~480 Hz
- BOM: ~€55 (laminations, magnet wire, N42, laser-cut flexure, H-bridge)
- 20 mm height is tight (~2 mm spare)
- Laminate the iron if we later care about the 700 Hz spindle mode
- 3-DOF stretch: three 120° stator sectors for z + rx + ry at ~200 N axial; rim poles for
  x/y/rz would be tens of newtons, not 200 N

### 2. Flextensional multilayer piezo

Cheap 10 × 10 × 18 mm stack: ~20 µm free, ~3200 N blocking. Steel diamond shell at 6× and
~60 % hinge efficiency, stack preloaded, drive biased around mid-stroke (0–150 V).

- Two-sided force: ~250 N (preloaded)
- Travel: ~120 µm
- Resonance vs machine: ~390 Hz
- BOM: ~€90; the 150 V driver is the item that can slip over €100
- Catalogue analogue: Cedrat APA40SM — 54 µm, 260 N, 15 × 27 × 12 mm. Force and envelope
  proven; stroke about 2× short of 0.1 mm. Catalogue parts that do both 0.1 mm and 200 N
  are either too long or several thousand euros.
- 3-DOF stretch: three shells do not sit in 50 × 50 mm

### 3. Lorentz voice coil + 7:1 flexure lever

Bare Lorentz in this volume is ~15 N continuous / ~35 N peak. Lever brings that up.

- Force: ~250 N peak / ~100 N continuous — 200 N is peak-duty only
- Travel: 0.1 mm (coil stroke 0.7 mm)
- Reflected mass ~2.6 kg → ~84 Hz vs the machine: enough for 10 Hz, not for a 700 Hz
  spindle mode
- BOM: ~€70
- Naturally two-sided; reuses current-loop hardware

Rotary BLDC + 50 µm eccentric looks cheaper (only 10 mNm, a ~€15 drone motor) but fails
bandwidth: that crank reflects ~600 kg and resonates near 5 Hz. Do not take that shortcut.

### Not worth prototyping here

Bare voice coil (no lever), SMA, pneumatics, Terfenol-D, off-the-shelf linear motors.

## Decisions

- First prototype: idea 1 (reluctance). Idea 2 if the plant pole must sit well above
  100 Hz. Idea 3 only as a peak-duty linear option that reuses current-loop hardware.
- If 10 Hz is only a minimum and the real target is the 700 Hz spindle mode: drop idea 3;
  keep idea 1 laminated, or idea 2.
- Aim for a piston / tip-tilt puck, not a hexapod in this box.

## Open Questions

- Is 10 Hz the real operating band, or only a minimum, with the 700 Hz spindle mode as
  the actual target?
- Where does the 50 × 50 × 20 mm package sit on the machine? Non-collocated moment load
  was the other problem on 2026-08-24.
- Is 0.1 mm peak-to-peak or ±0.1 mm?

## Next Steps

- Freeze 1-DOF vs 3-DOF (z/rx/ry) before CAD.
- Magnetic circuit sketch and flexure stress for idea 1.
- Declare the force / stroke / envelope numbers in `architecture/` SysML so later
  measurement summaries can cite them.
