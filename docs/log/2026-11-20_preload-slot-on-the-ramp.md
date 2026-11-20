# 2026-11-20 — Preload slot: the screw touches only the outer edge of the strip

**Role(s):** cad

> **Replaced the same day.** This 8.5 mm slot opened the base cavity. See
> [the sealed preload log](2026-11-20_preload-on-the-ramp-sealed.md).

## Goal

With the new end clamp, the ISO 10642 M4 preload screw sits on the ramp, where the strip slopes
about 13.5°. Its cone touched the inner edge of the 5 mm strip hole first, so tightening it would
loosen the strip. Niels Bosmans asked to make the hole a slot that touches only at the outside,
to check that it touches at the right spot, and to give the screw enough room to sink.

## Short answer

- **A slot solves it, but only if it is wider than the head.** A 5 mm wide slot does not help: the
  cone then catches the long sides of the slot, where the strip is higher. From about 7 mm wide,
  the first contact is the outer edge.
- **The strip now has a slot 8.5 mm wide and 1 mm long towards the middle.** Its outer edge is
  2.15 mm from the screw axis along the strip, as before.
- **The cone touches the right spot.** In the assembly the first contact is at x = 4.39 mm, on the
  middle line of the strip: the outer edge of the slot, 2.1 mm outside the screw axis.
- **The screw can sink 1.32 mm after the first contact** before the head reaches the base. The
  pull of 270 N needs only about 0.1 mm per end, plus the hole tolerances. Nothing else on the
  strip touches the head over 1.4 mm of travel.
- **The base counterbore is now 9 mm, shifted 1.5 mm towards the middle.** Its outer edge stays
  3 mm from the axis, so the strip is still supported up to 0.85 mm from the slot edge. Its depth
  is the same, 2.48 mm.

## What changed

- Parameters: `strip_preload_hole_d` is now 8.5 mm, the slot width. New `strip_preload_slot_l`
  = 1 mm.
- Strip build script: the preload hole is a slot, cut square to the strip on the ramp. The flat
  strip has the same slot, fully constrained. The outer arc centre is 8.21 mm from the strip end
  on the flat strip.
- Base: `preload_counterbore_d` = 9 mm, new `preload_counterbore_out` = 3 mm. The counterbore
  sketch places each circle `preload_counterbore_d / 2 - preload_counterbore_out` from the screw
  axis, towards the middle.
- Assembly: the preload screws rest at the first contact, head top at z = 41.29 mm.
- Architecture note, bill of materials and the end clamp decision describe the slot.

## How the size was found

A short calculation over the strip surface on the ramp gave the first contact of the cone for
slot widths from 5 to 10 mm and lengths from 0 to 4 mm. It then pushed the strip outwards with
the cone and looked for any second contact. Width decides, length hardly matters:

| Slot width | First contact | Travel before a second contact on the strip |
| --- | --- | --- |
| 5 mm | side of the slot, towards the middle | none |
| 6 mm | side of the slot, near the outer edge | 0.02 mm |
| 7 mm | outer edge | 0.58 mm |
| 8 mm | outer edge | 1.09 mm |
| 8.5 mm, 1 mm long | outer edge | more than 2.5 mm |

Then the same check for the base: with the counterbore outer edge 3 mm from the axis, the head
reaches the base wall and the counterbore floor at about the same travel (1.39 mm by calculation,
1.32 mm in the CAD).

## Checks

- Strip, flat and bent, is one valid solid each. Both sketches are fully constrained.
- In the assembly: the first contact is at the outer edge on both ends. No overlap of the strip
  with the base or the screws.
- `doqs check`: all gates pass.

## Open questions

- The cone touches the strip at one point. Whether a 0.15 mm strip edge takes the side force of
  the screw without bending into the counterbore is not checked. A test on a strip sample would
  show it.

<details>
<summary>Technical notes</summary>

- The bent slot is cut as 21 cylinders square to the strip along the slot. The overlapping
  cylinders left a sliver with no volume at one end; the build now keeps only the strip solid.
- The generated `cad/params.csv` is stale and still has the old 5 mm hole. The build was run with
  the values from `cad/params/default.csv`.
- The preload screw joints moved to the M4 hole edges in the counterbore floor, because the old
  counterbore edge is gone.

</details>
