<!-- SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

# Forcer water cooling at rated current: results

Case: [`cases/forcer-cooling-thermal/`](../../cases/forcer-cooling-thermal/). All numbers:
[`thermal.json`](thermal.json). Interactive page with the 3D temperature and growth, every input
and the checks: <https://refaqt.github.io/aqtuator/thermal/> (folder
[`simulation/cases/forcer-cooling-thermal-results/`](../../../../../simulation/cases/forcer-cooling-thermal-results/)).

Main case: MAXWELL MK21 at 2.0 A rms without a stop, water at 20 °C, 0.59 l/min per axis (the
recommended pump), still air at 20 °C, base on the machine table.

## Short answer

- **The coil runs 4.7 K over its limit at the full 2.0 A.** Its hottest point settles at
  124.7 °C; the limit is 120 °C. The PTC sensor in the coil switches near 120 °C, so the drive may
  stop the motor after a long time at full current.
- **The cooling works as the data sheet expects.** The water holds the mounting face at 24.5 °C
  on average, about the 25 °C of the data sheet test. 100 K of the 105 K rise sits inside the
  motor (data sheet 0.87 K/W × 116 W). Better cooling cannot fix this.
- **The data sheet rounds the rated current up.** Its 181 N needs 1.957 A. At 1.957 A the coil
  reaches 118.5 °C, 1.5 K under the limit. At 1.8 A it reaches 98.5 °C.
- **Water in → out: 1.8 K** (20.0 → 21.8 °C). The water takes 74 W (64 %) of the 116 W. The base
  takes 35 W into the machine table, and the air 6 W.
- **The printed cooling block does not deform from heat.** Its hottest point is 26.0 °C (31.6 °C
  with every unknown input at its worst). Every SLA resin and FDM filament checked has a heat
  deflection temperature (HDT) of 55 °C or more. Standard resin (Formlabs Grey V5): 71 °C.
- **Pump:** a TEYU CW-5200 chiller with the 4 bar pump option gives 0.59 l/min to each of the six
  axes at 3.1 bar, with a needle valve on the spindle branch. A D5 pump (0.38 bar) is too weak.

## Temperatures, main case

| Part | Lowest | Mean | Highest |
| --- | ---: | ---: | ---: |
| Forcer (coil unit) | 20.7 °C | 95.9 °C | 124.7 °C |
| Forcer mounting face | | 24.5 °C | 43.2 °C |
| Printed cooling block | 20.0 °C | 22.4 °C | 26.0 °C |
| Carriage-bottom | 21.5 °C | 25.1 °C | 27.3 °C |
| Carriage-top | 24.3 °C | 24.5 °C | 25.1 °C |
| Base | 20.3 °C | 21.2 °C | 24.6 °C |
| Magnet track | 20.6 °C | 22.8 °C | 26.6 °C |
| Rails | 20.4 °C | 21.3 °C | 23.1 °C |
| Guide blocks | 23.8 °C | 24.5 °C | 25.8 °C |

The warm-up from a cold start: the coil reaches 63 % of its rise after about 14 minutes and is
within 1 K of its end value after about 70 minutes. It passes the 120 °C limit after about 40 minutes. The base needs about an hour.

## What changes the coil temperature

| Case | Coil |
| --- | ---: |
| Main case | 124.7 °C |
| 1.957 A (181 N) | 118.5 °C |
| 1.8 A (166 N) | 98.5 °C |
| Water in at 15 / 18 / 22 / 25 °C | 120.8 / 123.2 / 126.3 / 128.7 °C |
| Air at 15 / 25 / 30 °C | 121.6 / 127.9 / 131.1 °C |
| Flow 0.2 / 0.3 / 0.5 / 1.0 l/min | 129.8 / 127.2 / 125.1 / 124.0 °C |
| Forcer joint 1 000 / 10 000 W/(m² K) | 128.2 / 123.3 °C |
| Water film × 0.5 / × 2 | 125.5 / 124.3 °C |
| Anodised surfaces | 123.9 °C |
| D5 pump (0.18 l/min) | 130.0 °C |

Each kelvin of colder water gives about 0.8 K at the coil. The other joints (bolts, balls, table,
printed block) change the coil by less than 1 K.

## Thermal growth

Relative to 20 °C everywhere. Two cases bound the unknown stiffness of the forcer joint: the forcer
tied to carriage-bottom, and the forcer free to slide on its screws.

| Result | Forcer tied | Forcer slides |
| --- | ---: | ---: |
| Lift of the carriage-top face | 3.0 µm | 2.5 µm |
| Tilt along / across the travel | 0.5 / −7.8 µrad | −4.6 / −0.8 µrad |
| Flatness change of the top face | 34.7 µm | 2.8 µm |
| Read head against the scale (along the travel) | 11.7 µm | 2.7 µm |
| Motor air gap (mean, closes) | 63 µm | 23 µm |
| Largest extra side load on a guide block | 643 N | 226 N |

The hot steel forcer bends the aluminium carriage like a bimetal strip. How much depends on how
firmly the six M4 screws hold it. The read head movement is a position error that the encoder
cannot see. The air gap stays open (data sheet 0.6 mm, at least 0.45 mm). The guide block loads
are far below C0 = 8 790 N.

## Checks

- Heat balance of every case: within 0.00002 %.
- Water warm-up = heat into the water / (ṁ c), to 0.01 K.
- Motor calibration: 0.867 K/W against the data sheet 0.87 K/W.
- The warm-up ends at the steady coil temperature (124.74 °C).
- The element code gives exact answers on test blocks (slab, free growth, film).
- Mesh check: see the page (section Proof).

## Inputs that are not known

See the [case README](../../cases/forcer-cooling-thermal/README.md). The ones that matter most:
what the data sheet R<sub>TH</sub> is measured to, the forcer joint, the air temperature, the pump
curve between its two published points, and how firmly the forcer holds the carriage (growth only).
