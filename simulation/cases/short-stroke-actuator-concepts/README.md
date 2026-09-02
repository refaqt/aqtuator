# short-stroke-actuator-concepts

First-order feasibility of three two-sided actuators that fit a **50 × 50 × 20 mm**
envelope, produce **> 200 N**, travel **> 0.1 mm**, and move with **> 10 Hz** bandwidth
at a **BOM below 100 EUR** (feedback sensor excluded — it will be provided).

**Tool:** Python 3, standard library only.

```bash
python3 simulation/cases/short-stroke-actuator-concepts/size_concepts.py
```

Results: [`simulation/results/short-stroke-actuator-concepts/summary.md`](../../results/short-stroke-actuator-concepts/summary.md).

This study sits at the start of the actuator design phase. CAD is still empty
([`cad/README.md`](../../../cad/README.md)). It continues the
[2026-08-24 reluctance investigation](../../../docs/log/2026-08-24_reluctance-actuator-investigation.md)
and uses the measured spindle stiffness of **100 N / 140 µm = 0.71 N/µm**
([2026-01-27](../../../docs/log/2026-01-27_machine-stiffness-measurement.md)).

## What the envelope actually allows

Power is not the problem. Peak mechanical power at 10 Hz, 0.1 mm peak-to-peak, 200 N is
about **1.3 W**. The constraints that bite are **force density**, **two-sidedness**, and
**thermal / reflected inertia**.

A reaction-mass (inertial) shaker in this box is the wrong mental model at 10 Hz:

| Frequency | Proof mass needed for 200 N at ±50 µm |
| --- | ---: |
| 10 Hz | ~1000 kg |
| 100 Hz | ~10 kg |
| 700 Hz (spindle mode in the [2026-05-07 FRF](../../../docs/log/2026-05-07_frf-and-compliance-measurements.md)) | ~0.21 kg |

The whole 50 × 50 × 20 mm envelope in steel is **0.39 kg**. So this device has to be a
**coupling actuator** between two machine parts (or a short-stroke stage), not a 10 Hz
proof-mass damper. At the 700 Hz spindle mode an inertial armature of ~0.2 kg would start
to make sense — that is a different operating point than the 10 Hz floor.

**6-DOF at 200 N per axis does not fit.** Magnetic pressure at 1.2 T is about 0.57 N/mm².
The 50 × 50 mm face is 2500 mm²; even if it were all pole face that is only ~1400 N of
total force budget, with no room for coils or return path. Six axes × 200 N = 1200 N is
already that entire budget. Realistic stretch: **z + rx + ry (piston / tip-tilt) at ~200 N
axial**, with much weaker x / y / rz.

## The three concepts

### 1. PM-biased differential reluctance + flexure guide

Solves the two problems left open on 2026-08-24: lumped Maxwell stress of a few hundred
newtons is available on a 20 × 20 mm pole, but a single gap only attracts. Packaged
continuous force is a different (much smaller) number — see the catalog check below.

```mermaid
flowchart TB
  subgraph envelope["50 x 50 x 20 mm"]
    E["E-core / pot stator<br/>PM in centre leg, coils on outer legs"]
    G1["gap 0.3 mm"]
    ARM["I-armature on steel flexure"]
    G2["gap 0.3 mm"]
    E2["return / second pole"]
    E --- G1 --- ARM --- G2 --- E2
  end
  I["current ±I"] --> E
```

A permanent magnet sets a bias field **B0 ≈ 0.8 T** in two opposing gaps. The coil adds
**±b ≈ 0.4 T**. Net force on the armature is

```text
F = 2 B0 b A / μ0
```

With **A = 20 × 20 mm** that is **204 N** of *unsaturated pole-face Maxwell force*,
linear in current to first order, and **two-sided**. That is not a packaged continuous
rating — see [Fluxthor catalog check](#fluxthor-catalog-vs-our-maxwell-number). Nominal
gap 0.3 mm leaves **0.4 mm** of two-sided travel before a 0.10 mm residual.

Control flux crosses **both** gaps, so Ampère's law needs **~191 At**, not the original
one-gap 96 At. 100 turns at 1.4 A is only 140 At (about 3 W copper) — short. Current-mode
drive at 24 V still has headroom at 100 Hz (`V_L ≈ 15 V`).

The flexure takes lateral loads and sets a well-defined gap. Magnetic negative stiffness
is **~1.4 N/µm** (`2F/g`), larger than the measured machine stiffness of **0.71 N/µm**.
A flexure stiff enough to stop snap-in (`k_flex ≳ 0.64 N/µm`) is no longer "much softer
than the machine": only **~107 N** of the 204 N then reaches the structure. Against
0.71 N/µm and an 80 g armature the mechanical resonance is **~480 Hz**.

**BOM (order-of-magnitude):** EI laminations or water-jet SiFe €10, magnet wire €5, N42
magnets €10, laser-cut spring-steel flexure €20, H-bridge €10, housing/fasteners €10.
**~€55.** Laminations (or ferrite, at the cost of lower Bsat) are required if the
actuator is later used near the 700 Hz spindle mode; at 10 Hz even solid iron would
mostly work.

**6-DOF stretch:** sector the stator into three 120° poles. The same puck then does
**z, rx, ry**. Rim poles for x/y/rz are possible but starve for area in 20 mm height —
expect tens of newtons, not 200 N.

**Main risks:** the 204 N figure is pole-face pressure, not device force (Fluxthor Atlas
is ~0.4 N/cm³ packaged, ~10× lower); negative stiffness vs flexure tax; two-gap MMF
shortfall; force ~ 1/gap² if the PM bias is uneven; eddy currents in solid iron; the
20 mm stack-up (back iron + window + gap + armature + flexure) has only ~2 mm of spare.

### 2. Flextensional multilayer piezo

A cheap 10 × 10 × 18 mm PZT stack gives ~**20 µm** free stroke and ~**3200 N** blocking.
A steel diamond / APA-style shell of amplification **6×** and ~60 % hinge efficiency
converts that to **~120 µm** travel and **~250 N** two-sided once the shell preloads the
stack and the drive is biased around mid-stroke (0–150 V around ~90 V).

```mermaid
flowchart LR
  V["0 to 150 V"] --> S["PZT stack<br/>10 x 10 x 18 mm"]
  S -->|"20 um, 3200 N"| F["steel flextensional shell<br/>~6x, preload"]
  F -->|"120 um, ~250 N"| OUT["output faces"]
```

This is the same topology as a Cedrat APA. The closest catalogue part that already fits
the box is the **APA40SM**: 54 µm, 260 N, 15 × 27 × 12 mm — force and envelope are
proven, stroke is about 2× short of 0.1 mm. A custom lower-amplification shell around a
taller stack closes that gap. Parts that do 0.1 mm and 200 N in the catalogue
(APA100M, APA120ML) are either 55 mm long or several thousand euros.

Mechanical resonance against the machine stiffness is **~390 Hz**. The piezo itself
resonates in the kilohertz. Lossy 150 V drive is ~0.5 W at 10 Hz and ~10 W at 200 Hz;
a recovering class-D stage is nicer but not required for the 10 Hz floor.

**BOM:** Chinese 10 × 10 × 18 mm stack €20–40 (PI-grade is €400 and blows the budget),
laser-cut stainless shell €20, DIY 150 V amplifier (boost + HV op-amp) €25–40.
**~€90**, with the driver as the item that can slip over €100.

**6-DOF stretch:** three stacks at 120° under a triangular platen give z/rx/ry. Three
flextensional shells do not sit comfortably in 50 × 50 mm; three bare 10 mm stacks would
fit in height but only deliver ~20 µm.

**Main risks:** stack tension (must stay preloaded under 200 N external load), hinge
fatigue, hysteresis/creep (the provided sensor closes that loop), HV safety, driver cost.

### 3. Lorentz voice coil + flexure lever

A Lorentz motor is naturally two-sided and linear, but **F = J V_cu B** in this volume
is only **~15 N continuous / ~35 N peak** of coil force. A **7:1** flexure lever brings
the output to **~250 N peak / ~100 N continuous**. Coil stroke is 0.7 mm, which still
fits a 1 mm airgap inside 20 mm.

```mermaid
flowchart LR
  I["current ±I"] --> C["moving coil in 0.85 T gap"]
  C -->|"~35 N peak, 0.7 mm"| L["flexure lever 7:1"]
  L -->|"~250 N peak, 0.1 mm"| OUT["output"]
```

Reflected coil mass is ~2.6 kg. Against 0.71 N/µm that is **~84 Hz** — enough for the
10 Hz spec with a 3× margin, not enough to sit under a 700 Hz spindle mode. Continuous
200 N is **not** available with natural cooling; this concept is a **short-duty / chatter
burst** actuator.

A **rotary BLDC + 50 µm eccentric** looks attractive on torque (only 10 mNm) and cost
(a 2207 motor is ~€15, and the project already has ODrive current loops). It fails
bandwidth: rotor inertia reflected through a 50 µm crank is ~**600 kg**, resonance
~**5 Hz**. A larger crank plus a second-stage lever does not remove the J / r² problem
unless the motor is a large-diameter pancake with r_out ≳ 1 mm and ~0.2 N·m — then the
package is the whole 50 mm and height is gone. Do not pick the rotary-eccentric shortcut
unless the 10 Hz floor is the actual operating frequency and inertia is modelled in FEA.

**BOM:** N52 magnets €20, coil €8, steel flexure lever €20, H-bridge or existing ODrive
€10, return iron €10. **~€70.**

**6-DOF stretch:** three or four coils under a flexure platen for z/rx/ry. Lateral
Lorentz channels have even less copper. Same 6-DOF budget problem as the others.

**Main risks:** thermal (200 N is peak-only), flexure lever compliance eating stroke,
84 Hz plant pole if anyone later wants mid-band chatter control.

## Comparison

| | Reluctance | Flextensional piezo | Lorentz + lever |
| --- | --- | --- | --- |
| Two-sided | yes, with PM bias + two gaps | yes, with preload + bias voltage | native |
| Force | 204 N pole-face Maxwell; ~107 N after snap-in flexure; catalog-like continuous ~20 N | ~250 N (preloaded); Cedrat APA40SM is a real 260 N part | 250 N peak / 100 N cont. |
| Travel | 0.4 mm in a 0.3 mm gap stack-up | 0.12 mm at 6× | 0.1 mm (coil 0.7 mm) |
| Plant resonance vs machine | ~480 Hz | ~390 Hz | ~84 Hz |
| BOM | ~€55 | ~€90, driver-sensitive | ~€70 |
| 6-DOF in-box | best path: 3-sector z/rx/ry | three shells do not fit | 3 coils for z/rx/ry |
| Why pick it | still the magnetic-pressure ceiling; not a 200 N continuous spec | only concept with a catalog analogue at ~200 N | linearity, reuse of current-loop hardware |

## Rejected at this envelope

- **Bare voice coil (no lever):** ~30–70 N peak, not 200 N.
- **Rotary eccentric / cam without a large crank radius:** reflected inertia kills >10 Hz.
- **SMA wire:** 10 Hz is the cooling limit, hysteresis, poor for closed-loop force.
- **Pneumatic / hydraulic servo:** valve cost and seals blow the BOM; compressibility
  fights 10 Hz in a long line (a sealed hydrostatic lever might work, but not as a first
  prototype).
- **Terfenol-D / magnetostriction:** piezo-like stroke, magnet-like BOM, worse supply.
- **Off-the-shelf linear motors:** the [2026-04-21 supplier look](../../../docs/log/2026-04-21_linear-motor-suppliers.md)
  is a different size and cost class.

## Fluxthor catalog vs our Maxwell number

Fluxthor (TU Delft spin-out) sells packaged reluctance actuators with a compliant
guide: [Atlas](https://www.fluxthor.com/products/reluctance-actuator) (pure reluctance,
their high-force line), [Rhino](https://www.fluxthor.com/products/hybrid-reluctance-actuator)
(PM-biased hybrid, same topology as concept 1), and Hercules (reluctance tuning; same
force table as Rhino). Numbers captured 2026-09-02.

| Model | Envelope | Volume | Continuous force | N/cm³ | Km | I at F_cont | Stroke |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Atlas-RA30 | 30 × 30 × 40 mm | 36 cm³ | 9 N | 0.25 | 29 N/A | 0.31 A | 100 µm |
| Atlas-RA40 | 40 × 40 × 50 mm | 80 cm³ | 32 N | 0.40 | 73 N/A | 0.44 A | 200 µm |
| Atlas-RA60 | 60 × 60 × 60 mm | 216 cm³ | 75 N | 0.35 | 56 N/A | 1.34 A | 500 µm |
| Atlas-RA100 | 100 × 100 × 70 mm | 700 cm³ | 286 N | 0.41 | 35 N/A | 8.2 A | 1000 µm |
| Rhino-HRA40 | 40 × 40 × 50 mm | 80 cm³ | ±21 N | 0.26 | 468 N/A | 45 mA | ±200 µm |
| **Our Maxwell sizing** | **50 × 50 × 20 mm** | **50 cm³** | **204 N** | **4.1** | ~150 N/A at 1.4 A | **1.4 A** | 400 µm |

Atlas, their "highest force density" product, sits at **0.25–0.41 N/cm³**. Scaled to our
50 cm³ that is **~20 N** continuous. We were **10×** high because we compared different
quantities:

1. **Pole-face Maxwell stress vs packaged continuous force.** 1.2 T is 0.57 MPa =
   57 N/cm² of *pole*. A 20 × 20 mm pole in a 50 × 50 × 20 mm box already uses only 16 %
   of the face; the rest is return iron, coil, magnet, flexure, housing. Catalog density
   divides force by the *whole* module, thermally derated, after the compliant mechanism.
2. **Thermal class.** Rhino has a *better* motor constant than Atlas (468 vs 73 N/A) and
   *lower* continuous force, because I_cont is 45 mA. They sell nanometer-stable stages
   (semiconductor, optics). Atlas-RA40 at 0.44 A is still a precision rating, not
   saturation. A mill can dump a few watts; they cannot. We can beat their *rating*.
   We do not beat Maxwell's equations.
3. **Negative stiffness / flexure tax.** Reluctance force grows as the gap closes
   (`k_mag ≈ 2F/g ≈ 1.4 N/µm`). That is stiffer than the machine (0.71 N/µm), so the
   armature snaps in unless the flexure (or a closed loop) stabilises it. Fluxthor's
   product *is* that compliant mechanism plus "reluctance tuning." A flexure that
   cancels snap-in is not << k_machine, so a large fraction of F never reaches the
   spindle. Delivered force ~107 N even before leakage and heat.
4. **Lumped circuit was optimistic.** Control MMF was counted across one gap (96 At)
   instead of two (191 At). Leakage, fringing, return-path saturation, and PM operating
   point are the usual next factor of two in MEC vs FEA (Cigarini 2019, Swank 2023).
5. **20 mm is the hard dimension.** Their shortest pack is 40 mm. The extra length is
   coil window and flexure. A 20 mm puck starves copper or pole, or both.

**What to believe for this mill:** 204 N remains a useful *upper bound* on pole-face
pressure. A custom coupling puck that runs hotter and at a shorter gap than Atlas can
beat 20 N — perhaps tens of newtons continuous, around 100 N as a hot / short-duty
stretch after the flexure tax. **200 N continuous in 50 × 50 × 20 mm is not a
catalog-supported spec.** Concept 2 (flextensional piezo) is the only idea with a
commercial analogue already at ~200 N in a similar box (APA40SM: 260 N, 54 µm).

Write-up of the check: [`docs/log/2026-09-02_fluxthor-reluctance-force-density.md`](../../../docs/log/2026-09-02_fluxthor-reluctance-force-density.md).

## Suggested first prototype

Do not take 200 N reluctance as a spec. If the force target stays at 200 N, **concept 2**
is the only path with a catalog analogue in this envelope (stroke still short of 0.1 mm).
Build **concept 1** only as a magnetic-circuit experiment: an E-I puck to measure real
force, negative stiffness, and heat in 20 mm — expect tens of newtons continuous, not
204 N. Use the provided sensor from day one. Keep concept 3 as the linear / ODrive-reuse
peak-duty option.
