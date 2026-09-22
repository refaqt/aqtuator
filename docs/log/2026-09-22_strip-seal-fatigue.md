# 2026-09-22 — How long the seal strip lasts, and how to say it

**Role(s):** engineering, simulation

> Superseded later the same day. The roller sizes below are too large, because the model
> treated the roller diameter as the bending radius. See
> [The seal strip rollers were never the problem](2026-09-22_strip-seal-bending-radius.md).

## Goal

Decide the material and the roller size for the spring steel strip that seals the linear
stages, and find an honest way to state how long that strip lasts.

## Work Done

- Built a model of the seal strip under the carriage rollers, in
  [`simulation/cases/strip-seal-fatigue/`](../../simulation/cases/strip-seal-fatigue/).
  It uses measured fatigue data from strip and belt makers, not textbook constants.
- Collected that data. Alleima publish a fatigue limit for EN 1.4310 by thickness and
  strength, and for two other strip materials. IPCO publish one for twelve steel belt
  grades. Across all twelve the fatigue limit sits between 0.32 and 0.48 of the tensile
  strength, which is a useful rule when nothing better exists.
- Counted what one carriage pass really costs, using the rainflow method. The four rollers
  bend the strip up, down, down and up, and that adds up to **one full reversal per pass**,
  not four and not one per roller.
- Found that the roller layout matters more than the material. Bending the strip both ways
  over the same roller is about fifteen times more damaging than bending it one way.
- Found a cheap fix. The two rollers above the carriage have room that the two in the slot
  do not. Opening only those two to 60 mm turns the reversal back into a one-way bend and
  reaches unlimited life with the 20 mm rollers already in the design.
- Showed why travel in kilometres cannot state the life of the seal, and what to state
  instead.
- Read the coolant data sheet. SAMNOS AL is water based at pH 7.4, used as minimum quantity
  lubrication. That matters, because every published fatigue value is measured in dry air.

## Decisions Made

Recorded in
[Strip seal material and roller size](../decisions/2026-09-22_strip-seal-material-and-roller-size.md),
status proposed until the CAD confirms the space.

- The strip is EN 1.4310 cold rolled to 2050 MPa, with rounded edges called out on the
  drawing.
- The seal is designed to last without a limit. Either all four rollers at 24 mm, or 20 mm
  in the slot with 60 mm above the carriage.
- Life is stated as crossings of the carriage over one point of the strip, never as
  kilometres.

## Mistakes

Two wrong answers were given before the right one, and both are recorded in
[the mistake entry](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md). The
prevention rule from the September force density entry was written too narrowly to catch
the first one, and has now been widened to cover any number that describes how a real part
behaves.

## Next Steps

- [ ] Check the CAD for room above the carriage. Rollers of 60 mm need height that the
      current design may not have. Until that is checked the decision stays proposed.
- [ ] Ask HPM Technologie for the chloride content of SAMNOS AL. It is not on the data
      sheet, and it decides whether EN 1.4310 is good enough or whether a molybdenum
      alloyed stainless is needed.
- [ ] Run a bend test with the real strip, the real roller and the real coolant. The
      unlimited life claim rests on dry air data and is not yet proven wet.
- [ ] Confirm that the strip really runs straight between rollers. The cycle count assumes
      it does. If the strip stays curved between two close rollers, the count changes.
- [ ] Watch the parking position. Where the carriage stands overnight the strip stays bent
      and will slowly take a permanent kink.

<details>
<summary>Checks</summary>

The model runs on Python 3 with the standard library only, matching the other cases in
`simulation/cases/`.

Two self-checks run inside it. The Goodman mean stress step is checked against a figure
Alleima publish for their Hiflex material, 620 ± 620 MPa: the script computes 1240 MPa and
stops if it does not match. The rainflow counter was written from scratch to avoid a
dependency, then compared against the `rainflow` package version 3.2.0 on five roller
layouts. Ranges, means and counts match exactly on all five.

Writing the rainflow counter surfaced one bug. The first version did not collapse runs of
equal values before looking for reversals, and the strip returns to zero stress between
every roller, so whole reversals were being hidden. Fixed and re-checked. A second, smaller
problem was the residue of half cycles left at the ends of a repeating history, which was
charged to whichever pass happened to be last. Counting N and N + 1 passes and taking the
difference cancels it exactly.

`bash doqs.sh check` was not run in this session. Nothing here touches CAD, parameters, a
bill of materials or a licence folder, but the check should still run before merge.

</details>
