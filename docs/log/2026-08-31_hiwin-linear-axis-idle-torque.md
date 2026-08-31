# 2026-08-31 — Hiwin linear axis idle torque

**Role(s):** engineering

**Source:** [HIWIN Catalogue — Linear Axes and Linear Axis Systems](https://narvija.com/wp-content/uploads/2025/07/HIWIN-CATALOGUE-LINEAR-AXES-AND-LINEAR-AXIS-SYSTEMS.pdf) (HX series; same document as `g:\Shared drives\9 - Purchases\Suppliers\HIWIN\documentation\HIWIN-CATALOGUE-LINEAR-AXES-AND-LINEAR-AXIS-SYSTEMS.PDF`)

## What idle torque is

In the HX catalog, **idle torque** (`Mleer` / `Midle`, German *Leerlaufdrehmoment*) is the **no-load running friction torque** of the complete axis module: the drive torque needed to keep the axis moving at **constant speed with no external payload**, beyond the axis's own moving parts (carriage, belt or ballscrew, bearings, seals, cover strip, etc.).

It is **not** motor cogging, external load, or inertia during acceleration.

## How it is used in sizing

Section 3 (*Calculation basis*) adds idle torque as a fixed term when sizing motor and gearbox:

- **Full dynamic sizing:** `MA = Mdyn + Mstat + Mleer`
  - `Mdyn` — acceleration / inertia
  - `Mstat` — gravity when the axis is not horizontal
  - `Mleer` — idle torque (from technical data tables)

- **Constant-velocity case** (assembly manual simplification): `MA = Mload + Midle`

The catalog does **not** provide a formula to calculate `Mleer`; look it up in the per-axis **Mechanical properties** tables as **Idle torque at 0-stroke [Nm]**.

## Physical origin

The linear-axes catalog lists idle torque as tabulated constants and does not break out each contributor. Physically it is the sum of **internal friction losses** when the axis runs unloaded:

| Source | Notes |
| --- | --- |
| Linear guideway friction | Carriage blocks on HIWIN profile rails (incl. SynchMotion preload) |
| Drive element friction | Ballscrew preload + seals (HM-S / HT-S); belt tension + pulley bearings (HM-B / HT-B) |
| Cover strip | Steel cover sliding in the profile — idle torque is **higher with cover** |
| Support / end bearings | Ballscrew support bearings; belt idler / tensioner bearings |
| Seals, wipers, lubricant drag | Rolling-contact seals and grease-film resistance |

Hiwin publishes these as **empirically measured constants** per axis size and variant, not as a user-calculated quantity in this catalog.

For ballscrew-driven axes, a large share comes from the integrated HIWIN ballscrew. The separate **Ballscrews** catalog defines idle torque as preload friction between nut and shaft plus sealing-element friction (measured at constant speed, typically 100 rpm, per DIN ISO 3408).

## Evidence in catalog tables

Idle torque varies systematically with configuration, which confirms it is friction-dominated:

- **Cover strip:** HM060B — 0.47 Nm (no cover) vs 0.80 Nm (with cover)
- **Axis size:** HM040B ≈ 0.15 Nm → HM120B ≈ 3.10 Nm
- **Ballscrew lead:** HM080S — 0.35 Nm (5 mm lead) vs 0.52 Nm (20 mm lead)

## Practical takeaway

Use the **Idle torque at 0-stroke** value from the Mechanical properties table for the exact order code (size, carriage type, cover option, spindle pitch if applicable). Include it in motor/gearbox sizing so losses that exist even at zero payload are not ignored.
