# ADR — The cooling block runs to the side face and holds two Festo fittings

- **Date:** 2026-11-09
- **Status:** Proposed. Niels Bosmans asked for this change and approved the sketch on
  2026-11-09. Not yet printed or tested.
- **Replaces part of:** [2026-11-06 forcer cooling](2026-11-06_forcer-cooling-sealed-with-standard-o-rings.md)
  (the printed hose barbs, the hose slot and the side cable clamp).

Write this file in B2 English. Follow `.agents/rules/communication.md`.

## Context

The first cooling block (2026-11-06) ended at the motor cable opening. Two hose barbs were
printed on it, and the hoses ran in their own slot to the side face. A large printed clamp
outside the side face held the hoses and both cables. Niels asked for:

- standard screwed-in Festo fittings instead of printed barbs, with 2 mm of resin around each
  tapped thread;
- a block that runs all the way to the side face, in one pocket with smooth curves;
- four screws, all on the centre line of the block;
- small clamps for the motor cable and the read head cable, pressed by carriage-top, instead of
  the side clamp.

## Decision

- **Block.** One pocket, 5 mm deep: a wide part over the channel ends and a 12 mm arm to the side
  face. The four bends of the arm have a 10 mm radius. The arm crosses over the motor cable where
  the cable comes up through the carriage. Outside the side face, a head of 9 × 20 mm holds the
  two fittings.
- **Fittings.** Two Festo NPQH-D-M5-Q4-P10 (578334), rated for water up to 0.6 MPa at 0–50 °C.
  They sit 11 mm apart. The hex is 9 mm across flats and 10.4 mm across corners, so a spanner
  does not fit between them. The fitting also has an internal 2.5 mm hex, so a hex key tightens
  it (1 Nm). The M5 threads are tapped 5 mm deep in the print, with 2 mm of resin around each.
- **Motor cable.** The cable must stay under the block where it comes up. The motor cable slot is
  5 mm deeper over 45° of its bend, starting 5° into the bend. Both ends of the deeper part are
  half circles of the slot width, so a mill can cut it. The start keeps 2.8 mm away from the step
  in the underside of carriage-bottom.
- **Print base.** The top of the block and of the head is one flat face. The block is printed
  with that face on the build plate. The head hangs down outside the side face, so the M5
  threads sit 2.6 mm lower than the passages. A short drop in the head joins them.
- **Screws.** Three ISO 10642 M2.5 screws from below: two M2.5 × 6 in the wide part, one
  M2.5 × 8 near the side face (at x = 198 mm). After review, the two screws near the side face
  became one.
- **Cable clamps.** One clamp for each cable, in the end of its own cable slot, flush with the
  side face, so it also closes the slot against dirt. Each clamp has two printed halves with a
  half-round groove and square corners. Each half is 0.1 mm narrower than the slot on each side
  (motor 8.8 mm, read head 5.8 mm). With both halves on the cable, the stack is 0.2 mm higher
  than the slot is deep. Beside the motor cable, only 0.25 mm of resin is left at the split line;
  Niels accepted this.

## Consequences

- The cooling block, both clamps and the pocket in carriage-bottom are parametric. They all read
  the same parameters in `modules/compact-stage/cad/params/default.csv`.
- The hose slot and the two M3 holes for the old side clamp are gone from carriage-bottom.
- The motor cable must lie low in its bend, under the block. Check this with the real cable.
- The screw near the side face has only 2.3 mm of thread in the resin. Test the pull-out
  strength on the first print.
