# 2026-11-19 — Can a Renishaw or Lamotion absolute encoder replace the RSF encoder?

**Role(s):** cad, engineering

## Goal

Check whether the RSF AK MC 15 B read head and its MC 15 MK tape can be swapped for a Renishaw
absolute encoder (RESOLUTE) or a Lamotion absolute encoder (ABS) without a new design. Check whether
the bottom carriage or the base must change. Niels Bosmans asked for this.

## Short answer

- **Both heads fit the present pocket in the bottom carriage, and they touch nothing over the
  full travel.** One change is needed: the two head screw holes move from 3.0 mm to 3.2 mm from
  the step face. Only then is the gap to the tape 0.8 mm, as both makers ask.
- **The base needs no new machining.** The tape centre moves from 34 mm to 31.75 mm on the side
  wall, and the tape start and direction must be set again. These are settings in the base model.
- **The RSF head is not the same as the other two.** All three heads have the same length (36 mm)
  and the same screw pattern (2 × M3, 26 mm apart, 1 mm off-centre, 3 mm from the face that looks
  at the tape). But the RSF head is 3 mm thinner and sits 0.25 mm closer to the tape.
- **The Lamotion ABS head copies the Renishaw RESOLUTE housing.** Size, holes, counterbore and gap
  are the same. Only the depth differs: 18.4 mm against 17.2 mm.

## Work Done

### The three heads side by side

| | RSF AK MC 15 B (now) | Renishaw RESOLUTE | Lamotion ABS |
| --- | --- | --- | --- |
| Length along the travel | 36 mm | 36 mm | 36 mm |
| Size in the screw direction (up and down in the stage) | 13.5 mm | 16.5 mm | 16.5 mm |
| Size away from the tape | 14.8 mm | 17.2 mm | 18.4 mm |
| Gap to the tape | 0.55 ± 0.25 mm | 0.8 ± 0.15 mm | 0.8 ± 0.15 mm |
| Thread in the head | M3 through the full head | M3, counterbored 3 mm deep, at least 5 mm of thread | M3, screw at least 8 mm into the head |
| Cable diameter | 3.7 mm | 4.7 mm | 4.6 mm |
| Smallest fixed cable bend | 8 mm | 10 mm | 45 mm |
| Tape | MC 15 MK, 0.45 × 8 mm, no end clamps | RTLA30-S, 0.4 × 8 mm, datum clamp and end covers | ALZ, 0.4 × 8 mm, two end clamps |
| Tape centre on the base wall | 34 mm | about 32 mm (read the Renishaw drawing) | 31.75 mm |
| Supply voltage | 3.6 to 14 V | 5 V ± 10 % | 5 V ± 10 % |

### Clearance check in FreeCAD

The Lamotion head was placed on the carriage mounting frame of the present assembly. Renishaw has
no model in the parts library, so a stand-in was used: the Lamotion housing cut to the 17.2 mm
Renishaw depth. Both were checked at five carriage positions: the saved position, both damper
contacts, and both full damper presses.

| Point | Holes as they are now (3.0 mm) | Holes moved to 3.2 mm |
| --- | --- | --- |
| Gap from the head to the tape | 0.6 mm, too small | 0.80 mm |
| Head to the second guide rail | 1.0 mm | 1.0 mm |
| Head to the base | 1.0 mm | 1.2 mm |
| Overlap with any other part | none | none |

- The head stays in the 16 mm pocket. It reaches 0.5 mm below the underside of the carriage and
  stays 1.0 mm above the second rail.
- The cable leaves at the same end as the RSF cable.
- The Lamotion end clamps touch nothing. They stay 0.5 mm from the bottom carriage. At the damper
  contacts the head passes over a clamp with 0.7 mm of space.
- **The Lamotion 270 mm tape is long enough only for the normal travel.** Between the clamps,
  242 mm of tape is free. Between the damper contacts, the sensor centre stays 10 mm from each
  clamp. With the dampers fully pressed it comes within 3 mm, so the read window (about 16 mm
  long) runs about 5 mm onto a clamp.
- **A 290 mm Lamotion tape covers the full travel.** With each clamp 10 mm further out, nothing
  touches and the sensor centre stays 13 mm from each clamp at full press.

## Decisions Made

No decision yet. The RSF encoder stays in the stage. This entry shows what a swap would cost.

## Open Questions

- Where exactly is the optical centre of the Renishaw head across its 16.5 mm width? This sets
  the tape height on the base.
- What shock does the Lamotion head allow? The Renishaw head allows 1000 m/s² for 6 ms, the same
  as the RSF value used in the crash study.

## Next Steps

If a swap is chosen:

1. In the bottom carriage, move the two head screw holes from 3.0 mm to 3.2 mm.
2. In the base, set the tape centre to 31.75 mm (Lamotion) or to the Renishaw value. Set the tape
   start and the tape direction again.
3. Make the cable slot in the bottom carriage and the read head cable clamp wider for the 4.6 to
   4.7 mm cable. Check that the cable path allows the 45 mm bend of the Lamotion cable.
4. Use M3 × 18 screws for the head.
5. For Lamotion, order a 290 mm tape if the encoder must read with the dampers fully pressed.
6. Both heads fail the head width limit of the encoder requirements (16.5 mm against less than
   15 mm). Lamotion also fails the height limit (18.4 mm against less than 18 mm). Change the
   requirements, or accept these failures.
7. Update the stage architecture, the bill of materials and the drive requirements in the same
   change, so they all name the new encoder.

<details>
<summary>Technical notes</summary>

- Sources: Renishaw RESOLUTE data sheet
  ([PDF](https://www.renishaw.com/media/pdf/en/519451ac9986446394a06d0f8f236688.pdf)), page 11
  (installation drawing) and the specification pages (scale form, cable, shock, mass). RSF and
  Lamotion values from the stoq parts library rows and from
  [the Lamotion fit of 20 October](2026-10-20_encoder-in-the-compact-stage-assembly.md) and
  [the RSF swap of 27 October](2026-10-27_rsf-encoder-in-the-compact-stage.md).
- The check ran headless in FreeCAD 1.1.3 on a scratch copy of `compact-stage.FCStd`. The stoq
  files came from the pinned commit `537fce1`. Nothing in the repository was changed or saved.
- Joint rule: taken from the present `Fixed_readhead` joint (carriage `IF_readhead_mount`, head
  frame, 180° about Z, plus a 180° flip about X because the RSF `IF_mount_top` points out of the
  head). The rule reproduced the saved RSF placement exactly. The Lamotion `IF_mount_side` points
  into the head, so it is placed without the X flip.
- Lamotion sensor line with the present holes: x = 219.582, y = 17.2, z = 31.75 mm. Head bounding
  box x 183.51 … 237.58, y 18.00 … 36.40, z 23.50 … 40.00.
- Positions: carriage moved by −109.603, −102.603, 0, +119.397 and +126.397 mm along x.
- Overlap test: `common().Volume` and `distToShape()` against every link. Fixed parts were checked
  at all five positions. Moving parts were checked once.
- The sealing strip is drawn bent around the carriage in its saved position, so it was only
  checked there. It does not touch the head. Its top is at the same height for all three heads.
- Lamotion tape and clamps: placed with `IF_head` on the head `IF_scale` (holes at 3.2 mm), and
  centred on the sensor path. Tape x 92.98 … 362.98 mm, clamps x 74.98 … 380.98 mm. The 290 mm
  case was tested by moving each clamp solid 10 mm outwards. The tape solid itself stayed 270 mm.
- Read window length (about 16 mm) from
  [the guide block log of 22 October](2026-10-22_guide-blocks-10-mm-closer.md).
- The check script was a one-off in the session scratch folder. It is not kept in the repository.
- Mistake rules checked:
  [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md)
  (every size read in the maker's own drawing),
  [drive check used the old encoder](../mistakes/2026-11-04_drive-check-used-the-old-encoder.md)
  (step 7 above), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md).

</details>
