# 2026-11-24 — Tecnotion motors checked, and LinuxCNC slows down in corners

**Role(s):** engineering, purchasing

## Goal

Tecnotion proposed two linear motors to replace the MAXWELL MK21: the TD82-3 and the TL6N. Check
them, and every other Tecnotion iron core motor, against the milling needs of the QARVE machine.
Answer two questions:

- Can a smaller motor, for example the TD55, replace the MK21?
- Can LinuxCNC slow down by itself in tight corners, so that we need less peak force?

## Work Done

### Short answer

- **Yes, LinuxCNC already slows down in corners.** You set one acceleration limit per axis. In
  every arc and every rounded corner, LinuxCNC lowers the speed so that the sideways acceleration
  stays at 87 % of that limit or less. So the 0.5 mm corner radius does not have to set the motor
  size. The motor sets the acceleration limit, and LinuxCNC adapts the feed in the corner.
- **The peak force of 591 N in the QARVE sheet is too high.** The sheet adds the highest
  acceleration (aluminium roughing) to the highest cutting force (stainless steel roughing). These
  two never happen in the same job. Per job, the highest need is 478 N, in aluminium roughing.
  The MK21 peak force (512 N for 1 s) already covers that.
- **The real weak point of the MK21 is the continuous force**: 181 N against the 228 N cutting
  force of stainless steel roughing.
- **The TD55 is not strong enough.** The TD55-3 gives 106 N continuous and 161 N peak. That is
  less than the cutting force alone. The TD55-6 gives 213 N continuous, 7 % short, and is 159 mm
  long. The TD55-9 gives 319 N but is 223 mm long, 3 mm too long for the QARVE X axis.
- **The TD82-3 is the best fit.** It gives 262 N continuous and is shorter than the MK21 (95 mm).
  It is 7 mm higher (41 mm against 34 mm). With a 0.5 mm corner, LinuxCNC would slow the X axis
  to about 3,700 mm/min in the corner. Aluminium roughing runs at 5,870 mm/min on straight lines.
- **No Tecnotion motor fits the compact stage space** (118 mm long, 86 mm wide, 34 mm high) and
  also gives the MK21 forces. Only the TD55-3 fits that space, and it is far too weak.

### How LinuxCNC handles corners

The motion planner of LinuxCNC knows the acceleration limit of each axis (`MAX_ACCELERATION` in
the INI file). On an arc of radius r, it caps the speed at v = √(0.87 × a_max × r). It keeps the
rest of the acceleration for speeding up and slowing down along the path. Sharp corners between
straight lines get a small blend arc. The size of that arc follows from the path tolerance you
allow with `G64 P`. The same speed cap applies to it.

This was read in the LinuxCNC source code, not in a manual. See the sources below.

LinuxCNC can also scale the feed from an outside signal (adaptive feed, switched on with
`M52 P1`). That is not needed for corners. It could be useful later, for example to lower the
feed when the cutting force is high.

### The QARVE milling needs, per job

Values from the QARVE sheet, tab "System model". Sideways acceleration = feed² / 0.5 mm. The X
axis moves 19 kg with one motor.

| Job | Feed (mm/min) | Acceleration in a 0.5 mm corner (m/s²) | Cutting force (N) | X force needed at full feed (N) |
| --- | ---: | ---: | ---: | ---: |
| Aluminium roughing | 5,869 | 19.1 | 114 | 478 |
| Aluminium finishing | 5,386 | 16.1 | 27 | 333 |
| Stainless steel roughing | 3,937 | 8.6 | 228 | 391 |
| Stainless steel finishing | 2,183 | 2.6 | 83 | 133 |
| Titanium roughing | 3,319 | 6.1 | 111 | 227 |
| Titanium finishing | 2,728 | 4.1 | 54 | 133 |

The sheet uses the in-plane cutting force on one axis. That is on the safe side.

### Motors compared

Tecnotion values come from the Tecnotion iron core brochure, version 1.3. MK21 values come from the
MAXWELL data sheet. The acceleration limit is (peak force − 228 N cutting force) / moving mass. The
moving mass includes the coil unit. The corner feed is the LinuxCNC speed cap in a 0.5 mm arc.

| Motor | Continuous force (N) | Peak force (N) | Length × width × height (mm) | Continuous force ≥ 228 N | X acceleration limit (m/s²) | X corner feed (mm/min) |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| MAXWELL MK21 | 181 | 512 (1 s) | 118 × 86 × 34 | No | 14.1 | 4,700 |
| Tecnotion TD55-3 | 106 | 161 | 95 × 55 × 32.1 | No | none | none |
| Tecnotion TD55-6 | 213 | 323 | 159 × 55 × 32.1 | No | 4.8 | 2,700 |
| Tecnotion TD55-9 | 319 | 484 | 223 × 55 × 32.1 | Yes | 12.6 | 4,400 |
| Tecnotion TD82-3 | 262 | 403 | 95 × 82 × 41 | Yes | 8.7 | 3,700 |
| Tecnotion TD82-6 | 524 | 805 | 159 × 82 × 41 | Yes | 27.3 | 6,500 |
| Tecnotion TL6N | 200 | 400 | 146 × 80 × 40 | No | 8.4 | 3,600 |
| Tecnotion TL9N | 300 | 600 | 194 × 80 × 40 | Yes | 17.7 | 5,300 |

Notes on the table:

- Tecnotion gives the peak force for a coil temperature rise of 6 K/s. From 25 °C to 105 °C that
  is more than 10 s. A corner takes a few milliseconds, so the peak time is never the limit.
- Tecnotion gives the continuous force with the coils at 105 °C (TD) or 100 °C (TL) and the
  mounting surface at 20 °C. MAXWELL uses 120 °C. Tecnotion says the two sets of numbers are not
  defined the same way. All Tecnotion values are ±10 %.
- The QARVE sheet allows a coil unit of up to 220 mm on X, 407 mm on Y and 270 mm on Z. The
  compact stage allows 118 mm.
- The 0.5 mm corner radius is a strict case. With a 10 mm cutter, the tool centre goes around an
  outside corner of the part on a 5 mm radius. There the sideways acceleration is ten times lower.

### Where the offer is

The prices and the Tecnotion comparison are in the private purchasing database:
[comparison PDF in maqers](https://github.com/refaqt/maqers/blob/main/documents/tecnotion/2026-11-23_motor-comparison-tecnotion-vs-maxwell-mk21.pdf).
Tecnotion asked to continue through its partner Eltrex.

## Decisions Made

- None yet. The motor choice for QARVE stays open.

## Open Questions

- Can the QARVE axes accept a motor that is 7 mm higher than the MK21? If yes, the TD82-3 fits
  all needs except full feed in 0.5 mm corners.
- Is a corner feed of about 3,700 mm/min on X acceptable for aluminium roughing? Lower feed in
  the corner also lowers the chip thickness there.
- Should the QARVE sheet check the peak force per job, instead of the highest acceleration plus
  the highest cutting force?
- The TD55 price was not asked. It is only worth asking if the stainless steel roughing job gets
  about 7 % lighter (TD55-6).

## Next Steps

- Fix the peak force formula in the QARVE sheet, so that it checks each job on its own.
- Ask Eltrex for the TD82-3 lead time and the price for 2 sets.

<details>
<summary>Sources and calculation</summary>

- Tecnotion, iron core brochure (English, version 1.3), received by email on 2026-11-23: TD55 table
  page 12 and drawing page 13 (mounting height 32.1 mm, width 55 mm); TD82 table page 14 and drawing
  page 15 (mounting height 41 mm); TL table page 20.
- Tecnotion comparison "Motor Comparison Tecnotion vs Maxwell MK21", 2026-11-23, in maqers at
  `documents/tecnotion/2026-11-23_motor-comparison-tecnotion-vs-maxwell-mk21.pdf`.
- LinuxCNC source, branch `master`, read on 2026-11-24:
  [`src/emc/tp/tc.c`](https://github.com/LinuxCNC/linuxcnc/blob/master/src/emc/tp/tc.c),
  function `tcUpdateArcLimits`: `v_max_cutoff = pmSqrt(a_n_max_cutoff * radius)` with
  `a_n_max_cutoff = BLEND_ACC_RATIO_NORMAL * a_max`.
  [`src/emc/tp/blendmath.h`](https://github.com/LinuxCNC/linuxcnc/blob/master/src/emc/tp/blendmath.h):
  `BLEND_ACC_RATIO_TANGENTIAL 0.5`, so `BLEND_ACC_RATIO_NORMAL` = √(1 − 0.25) = 0.866.
- QARVE sheet, tab "System model": the X axis peak force is
  `max(B311, B313 + B314)`. B313 is the highest feed acceleration of all jobs times the mass. B314
  is the highest cutting force of all jobs. They come from different jobs.
- Masses used: X 19 kg, Y 29 kg on two motors, plus the coil unit mass. The Y axis gives a higher
  corner feed than X for every motor.

</details>
