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
- **The TD55 cannot do all jobs at full rate.** The TD55-3 gives 106 N continuous and 161 N
  peak. That is less than the 228 N cutting force of stainless steel roughing. The TD55-6 gives
  213 N continuous, 7 % short, but it is 159 mm long. The TD55-9 gives 319 N but is 223 mm long.
- **The TD82-3 is out.** It gives 262 N continuous and is shorter than the MK21 (95 mm), but it
  is 41 mm high. The MK21 height of 34 mm is the maximum for now. The TL6N (40 mm) is out for the
  same reason.
- **If we accept less force, the TD55-3 fits.** It is the strongest Tecnotion motor that fits in
  the MK21 space. It gives 59 % of the MK21 continuous force and 31 % of its peak force. The
  machine then needs limits: stainless steel roughing at about half the material removal rate,
  and a lower feed in tight corners. See the update below.

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

### Update: motors that fit in the MK21 space, with less force

Limits: coil unit at most 118 mm long and 86 mm wide, and at most 34 mm from the mounting
surface of the magnet plate to the top of the coil unit. Longer magnet plates are fine.

| Motor | Length × width × height (mm) | Continuous force (N) | Peak force (N) | Fits |
| --- | --- | ---: | ---: | --- |
| MAXWELL MK21 | 118 × 86 × 34 | 181 | 512 | Reference |
| Tecnotion TD55-3 | 95 × 55 × 32.1 | 106 | 161 | Yes |
| Tecnotion TD36-6 | 113 × 36 × 24.8 | 72 | 149 | Yes |
| Tecnotion TD36-3 | 65 × 36 × 24.8 | 40 | 75 | Yes, but very weak |
| Tecnotion TD55-6 | 159 × 55 × 32.1 | 213 | 323 | No, too long |
| Tecnotion TM3, TMX3 | 93 × 50 × 40 | 60 to 71 | 105 to 124 | No, too high |
| Tecnotion TD82-3 | 95 × 82 × 41 | 262 | 403 | No, too high |
| Tecnotion TL6N | 146 × 80 × 40 | 200 | 400 | No, too long and too high |

The TD36 series is rated for 230 V AC (325 V DC) at most. That matches a drive on 230 V AC, but
leaves no margin. The TD55 is rated for 480 V AC.

What the TD55-3 means for each milling job. The cutting force is cut back to 106 N, the continuous
force, by lowering the material removal rate. The rest of the peak force (161 N) is left for
acceleration. The corner feed is the speed LinuxCNC allows in a 0.5 mm arc.

| Job | Material removal rate | X corner feed (mm/min) | Normal feed (mm/min) |
| --- | ---: | ---: | ---: |
| Aluminium roughing | 93 % | 2,100 | 5,869 |
| Aluminium finishing | 100 % | 3,300 | 5,386 |
| Stainless steel roughing | 47 % | 2,100 | 3,937 |
| Stainless steel finishing | 100 % | 2,500 | 2,183 (no slowdown) |
| Titanium roughing | 96 % | 2,100 | 3,319 |
| Titanium finishing | 100 % | 2,900 | 2,728 (no slowdown) |

The Y axis has two motors and does a little better. For comparison: with the MK21, stainless
steel roughing also needs a limit, at 79 % of the material removal rate, and the other jobs keep
almost full feed in the corner.

So the TD55-3 works if we accept about half the material removal rate in stainless steel
roughing, and a corner feed of about 2,000 to 3,300 mm/min. The slowdown only lasts while the
tool is in the corner. The TD36-6 is weaker on every point and is not worth it.

### Update: the peak force formula in the QARVE sheet

The new rule checks each job on its own: peak force = moving mass × corner acceleration of that
job + cutting force of that same job. The highest of these, and the rapid moves, sets the peak
force.

Why this is the worst case, kept simple:

- In a corner, the motor must pull the tool towards the centre of the arc.
- In an outside corner, the part is on the inside of the arc. The cutting force pushes the tool
  away from the part, so outwards. The motor must beat both: the forces add up.
- In an inside corner, the part is on the outside of the arc. The cutting force pushes the tool
  towards the centre. It helps the motor, so the forces partly cancel.
- So the formula adds the full in-plane cutting force to the corner force. That covers the
  outside corner, and it is on the safe side for the inside corner. It needs no force directions.
- It still uses the 0.5 mm radius. In an outside corner, the tool centre runs on a radius at
  least as large as the tool radius, so this is extra margin.

With the new rule the peak force drops from 591 N to 478 N on X, and from 505 N to 392 N per motor
on Y. On Z it goes from 332 N to 302 N.

### Where the offer is

The prices and the Tecnotion comparison are in the private purchasing database:
[comparison PDF in maqers](https://github.com/refaqt/maqers/blob/main/documents/tecnotion/2026-11-23_motor-comparison-tecnotion-vs-maxwell-mk21.pdf).
Tecnotion asked to continue through its partner Eltrex.

## Decisions Made

- None yet. The motor choice for QARVE stays open.

## Open Questions

- Is about half the material removal rate in stainless steel roughing acceptable with the TD55-3?
- Is a corner feed of about 2,000 to 3,300 mm/min acceptable? Lower feed in the corner also
  lowers the chip thickness there.

## Next Steps

- Put the new peak force formulas in the QARVE sheet (cells B294, B316 and B331 of the tab
  "System model"). The formulas are below.
- Ask Eltrex for a TD55-3 price, the lead time and the price for 2 sets.
- Check the TD55-3 force against speed in the Tecnotion simulation tool, at our bus voltage.

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
- Heights from the brochure drawings: TD36 24.8 mm (page 11), TD55 32.1 mm (page 13), TD82 41 mm
  (page 15), TM and TMX 40 mm (pages 17 and 19). TD36 table on page 10, TMX table on page 18.
- New formulas for the tab "System model". Each job block is 39 rows apart: corner acceleration in
  B41, B80, B119, B158, B197, B236; in-plane cutting force in B32, B71, B110, B149, B188, B227;
  axial force in B33, B72, B111, B150, B189, B228.
  - B316, X-axis motor peak force:
    `=MAX($B$311, $B$308*B41+B32, $B$308*B80+B71, $B$308*B119+B110, $B$308*B158+B149, $B$308*B197+B188, $B$308*B236+B227)`
  - B331, Y-axis motor peak force (per motor, two motors):
    `=MAX($B$327/2, $B$325*B41/2+B32, $B$325*B80/2+B71, $B$325*B119/2+B110, $B$325*B158/2+B149, $B$325*B197/2+B188, $B$325*B236/2+B227)`
  - B294, Z-axis motor peak force:
    `=MAX($B$290, $B$287*B41+B33, $B$287*B80+B72, $B$287*B119+B111, $B$287*B158+B150, $B$287*B197+B189, $B$287*B236+B228)`

</details>
