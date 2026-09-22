# 2026-09-22 — The seal strip rollers were never the problem

**Role(s):** engineering, simulation

## Goal

Check the seal strip calculation made earlier the same day. It said the 14 mm rollers in
the design are too small, and asked for 60 mm rollers above the carriage. That did not
match a competitor's product, which clearly uses smaller rollers.

## Work Done

- Read the carriage drawing. The strip climbs a ramp about 38 mm long and 8.38 mm high, so
  it turns only about twelve degrees at each roller.
- Found the error that mattered. The model treated the roller diameter as the bending
  radius. A strip only takes the roller radius if something presses it there. At twelve
  degrees, forcing a 0.1 mm strip onto a 14 mm roller would need about 1,050 N of pull on a
  40 mm strip. The strip bridges the roller instead, and the bending stress is 57 to
  362 MPa rather than the 1312 MPa first reported.
- Found a second, smaller error. The fatigue limit was read at 0.25 mm and used for a
  0.1 mm strip. Alleima publish two thicknesses, and their own trend gives about 1019 MPa
  at 0.1 mm instead of 775 MPa.
- Checked how other makers do it. HIWIN use no rollers at all. They lift the strip with
  plastic sliding guides and add 30 to 70 mm of carriage length per end, depending on axis
  size, to spread the turn. An SMC patent says in its description of earlier designs that a
  seal band guided by guide rollers is flattened by them.
- Found what actually ends the life of a cover strip. HIWIN tell the user to change it when
  it ripples and the magnets no longer hold it flat, and they say it wears by rubbing.
  Parker reject a band for nicks, kinks and edge damage. None of them replace it because it
  cracked.
- Rebuilt the model around the radius the strip really takes, with the roller as a floor on
  that radius and the old formula kept as the worst case.

## Decisions Made

Recorded in
[Strip seal material and roller size](../decisions/2026-09-22_strip-seal-material-and-roller-size.md),
which was revised rather than replaced. Status stays proposed.

- The 14 mm rollers stay. The carriage grows in length, not in height.
- What the design controls is the turn angle at each roller, which must stay under about
  fifteen degrees. The ramp length and the lift height set it.
- The seal is a wear part replaced on inspection, not a part designed to last without a
  limit. The three signs to replace it are written down.

## Mistakes

A third wrong answer on the same question, added to
[the mistake entry](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md). The
new prevention rule: a contact radius is not a bending radius. Before putting a radius into
a stress formula, say what makes the part take that radius and check that the force to do
so exists. A second rule was added too: after two wrong answers on the same question, ask
for the drawing.

## Next Steps

- [ ] Measure the radius the strip really takes at a roller on the built carriage, with a
      radius gauge or a photograph against a scale. The whole revision rests on this one
      number.
- [ ] Confirm the 38 mm ramp length against the CAD model. It was read off a sketch.
- [ ] Measure the pull in the strip. The results walk a range because this is unknown.
- [ ] Ask Alleima three questions: is there measured fatigue data at 0.1 mm, what is the
      value along the rolling direction rather than across it, and what is the value at a
      lower survival rate than 50 percent.
- [ ] Ask HPM Technologie for the chloride content of SAMNOS AL. Still open from the
      earlier entry, and still the largest untested risk.
- [ ] Run a bend test with the real strip, the real roller and the real coolant.
- [ ] Watch the parking position for a permanent kink.

<details>
<summary>Checks</summary>

The model runs on Python 3 with the standard library only, matching the other cases in
`simulation/cases/`.

Three self-checks now run inside it. The Goodman step is checked against a figure Alleima
publish for their Hiflex material, 620 ± 620 MPa: the script computes 1240 MPa and stops if
it does not match. A new radius check presses the strip onto a 14 mm roller with a hundred
times the pull needed to make it conform, and requires the result to equal `E*t/(D+t)`
exactly; it also requires no wrap at a hundredth of that pull. This proves the new radius
model contains the old full wrap formula as its limiting case. The rainflow counter is
unchanged and was compared against the `rainflow` package version 3.2.0 on five roller
layouts when it was written.

The cycle count is unchanged: one carriage pass is still one full reversal. Only the size
of that reversal changed.

`bash doqs.sh check` was not run in this session. Nothing here touches CAD, parameters, a
bill of materials or a licence folder, but the check should still run before merge.

</details>
