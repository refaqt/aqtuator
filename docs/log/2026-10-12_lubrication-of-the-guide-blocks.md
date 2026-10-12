# 2026-10-12 — Lubrication of the guide blocks

**Role(s):** engineering, cad, purchasing

## Goal

Decide how the four HIWIN HGL15 guide blocks of the compact stage get their lubricant. The
questions were: do the blocks need lubricant all the time, do we need tubes to every block, and
can one input feed all four blocks.

## Work Done

- **The blocks do not need a constant flow of lubricant.** Rolling guides need a small amount of
  grease or oil at long intervals. The HIWIN catalogue asks for "adequate lubrication" and never
  for a constant flow.
- **HIWIN sells a long-term lubrication unit (E2) that can make the blocks last their whole life
  without new grease.** It is an oil tank on one end of the block. For size 15, the catalogue
  gives up to 10,000 km of travel with one unit, and up to 20,000 km with a unit on each end. It
  works from −10 °C to +60 °C and in any mounting position.
- **The E2 unit is not in our design yet.** The part number in the parts list ends in "+E2", but
  neither the HIWIN CAD file nor our assembly has the unit. Our own block model can draw it, but
  the unit is switched off there.
- **One plain manifold with one input and four outputs is not a good way to feed four blocks.**
  Grease takes the easiest path, so one block gets almost all of it and another may get none,
  without any warning. If we ever need lubrication lines, there are two good options. The first is
  one line per block to a plate with four grease nipples. The second is a progressive distributor
  (a metering block), which pushes a fixed amount to each output in turn.

## Decisions Made

These choices are proposed. They wait for answers from HIWIN (see Open Questions).

1. **Each block gets one E2 unit, on the inner end, between the two blocks on the same rail.**
   On that end it does not shorten the stroke.
2. **The blocks are greased once, when they are slid onto the rail. No lubrication tubes run to
   the blocks.** This fits the assembly order in
   [the encoder tape decision](../decisions/2026-10-09_lay-the-encoder-tape-with-a-printed-dummy-block.md):
   every block goes onto its rail before the rail goes into the base.
3. **After the first greasing, the grease nipple may be replaced by an M4 plug screw.** Grease
   first, with the nipple in place, and push each block over its full stroke a few times. Then
   fit the plug, if the nipple is in the way. If the nipple fits in the gap, it can stay.

## Open Questions

- Does a block with an E2 unit still need grease at assembly? Which grease mixes safely with the
  oil in the tank (HIWIN SHC 636)? The catalogue does not say.
- Is HGL15CAZBC available with one E2 unit, and on which end does the unit go? Is the grease
  nipple on the block or on the E2 unit?
- Is 10,000 km of travel enough for the life of the stage? This needs an estimate of how far the
  stage travels each year. Example with made-up numbers: an average speed of 0.1 m/s over
  2,000 running hours a year gives about 720 km a year, so 10,000 km would last about 14 years.
- If the stage mostly makes short, fast movements, the oil only reaches the part of the rail
  that the block passes over. HIWIN sells a grease for this case (G06). A regular full stroke may
  still be needed.

## Next Steps

1. Ask HIWIN the questions above.
2. Estimate the yearly travel of the stage and compare it with 10,000 km.
3. In the CAD, add the E2 unit on the inner end of each block. Check the gap between the two
   blocks on each rail (at least 28 mm) and the space under the carriage plate.

<details>
<summary>Technical notes</summary>

- Source: HIWIN linear guideways catalogue GW-13-1-EN-2606-K, in
  `modules/stoq/modules/hiwin/docs/datasheets/`. Section 2.6.2 and 2.6.3 (page 17),
  order code (page 35), table 3.13 (page 47), section 4.1 and 4.2 (pages 162 and 163).
- Table 3.13 for HG_15C: E2 unit W = 32.4 mm, H = 19.5 mm, T = 12.5 mm, V = 3.0 mm. Block length
  with one unit is 75.4 mm with standard seals (SS) and 80.5 mm with ZZ seals. The bare block is
  61.4 mm, so each block gets 14 mm longer with standard seals.
- The lubrication threads on the side and the end of HG_15 blocks are M4 (table 4.1). The grease
  nipple sticks out 5.3 mm (G in `HGL15CAZBC+E2.params.csv`).
- Our own block model in the parts library has `E2_units = 0`. Its note says the unit goes at the
  nipple end when it is set to 1. The parts library is a separate repository, so it was not
  changed in this entry.
- The catalogue does not give a relubrication interval or a grease amount. HIWIN puts these in
  its "Linear guideways" assembly instructions on hiwin.de.
- Mistake rule checked: [fatigue estimate without a data sheet](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md).
  All part numbers here come from the HIWIN catalogue. The yearly travel is a made-up example and
  is marked as such.

</details>
