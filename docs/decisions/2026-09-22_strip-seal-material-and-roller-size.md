# 2026-09-22 — Strip seal material and roller size

- **Date:** 2026-09-22
- **Status:** Proposed
- **Revised:** 2026-09-22, after the carriage drawing showed how gently the strip turns

## Context

The linear stages are sealed by a thin spring steel strip lying in a slot. The carriage
carries four rollers that lift the strip, pass under it and lay it back down. The first
roller bends the strip up, the second flattens it above the carriage, the third starts it
down and the fourth lays it flat again.

The packaging is tight. The first design fits 20 mm rollers with difficulty, and smaller
rollers would help the rest of the carriage. Smaller rollers bend the strip harder, so the
question was how much life a smaller roller costs.

Two things made the first answer wrong, and they are recorded in
[the mistake entry for this work](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md).
The first estimate used textbook constants and was too pessimistic by about forty times.
The second estimate assumed the strip is bent one way only, which this carriage does not do.

No maker of linear stages publishes fatigue data for a cover strip. HIWIN sell the strip
deflection as a spare part and say nothing about how long the strip lasts. Strip makers and
steel belt makers do publish measured fatigue data, and that is what this decision rests on.

**The first version of this decision asked for rollers that are not needed.** Two things
were wrong with it, and the carriage drawing brought both to light.

The model treated the roller diameter as the bending radius. A strip only takes the roller
radius if something presses it there. In the carriage as drawn the strip turns about twelve
degrees at each roller, and forcing a 0.1 mm strip onto a 14 mm roller at that angle would
need about 1,050 N of pull on a 40 mm strip. The strip bridges the roller instead, and the
bending stress is a few hundred MPa rather than the 1312 MPa first reported.

The fatigue limit was also read at the wrong thickness. Alleima measure 775 MPa at 0.25 mm
and 630 MPa at 0.50 mm. Our strip is 0.1 mm, and thinner strip is stronger. Their own trend
gives about 1019 MPa at 0.1 mm.

The work is in
[`simulation/cases/strip-seal-fatigue/`](../../simulation/cases/strip-seal-fatigue/).

## Decision

**1. The strip is EN 1.4310 (AISI 301), cold rolled to a tensile strength of 2050 MPa.**

Alleima 11R51 is one source. Any supplier working to EN 10151 can match it. At 0.1 mm this
temper is the only one on offer, because thin strip work hardens more during rolling, so
the strong material comes for free.

It beats the alternatives for a reason worth keeping in mind: its modulus is the lowest of
the group at 185 GPa, and bending stress is proportional to modulus. A harder steel with a
higher modulus does no better.

**2. The strip is specified with rounded edges, and that goes on the drawing.**

At this strength the strip stretches by only 0.5 percent before it breaks. It is strong but
not forgiving. Cracks start at edge damage, and the strip maker states that rounding the
edges gives a large increase in fatigue life. A sheared edge can cost a factor of ten.

**3. The rollers stay at 14 mm. The ramp length is what the design controls, not the
roller diameter.**

The strip must not turn by more than about fifteen degrees at any roller. That is what the
ramp length and the lift height decide. At twelve degrees the bending stress stays between
57 and 362 MPa across the whole plausible range of strip pull, against a fatigue limit of
about 1019 MPa. HIWIN reach the same place with no rollers at all, by adding 30 to 70 mm of
carriage length per end depending on axis size.

Two conditions keep this true, and both must be checked on the built carriage:

- The strip is not pressed onto any roller by a counter surface or a hold-down.
- The pull in the strip stays well under 26 N per mm of width, which is 1,050 N on a 40 mm
  strip. Nothing about a magnet held cover strip approaches that, but it has to be measured
  rather than assumed.

If either fails, the strip wraps the roller. The worst case table then applies, and 14 mm
gives 79,000 crossings while 20 mm reaches the fatigue limit.

**4. The seal is a wear part with a stated interval, not a part designed to last without a
limit.**

This follows what every maker does. HIWIN sell the cover strip by the metre in 3 m and 6 m
lengths, and their instruction is to change it "as soon as there are any signs of rippling
and it can no longer be held in position by the magnetic strips". They also say it wears by
rubbing. Parker reject a band for nicks, kinks and edge damage.

So the strip is replaced on inspection, on these three signs:

- The strip ripples and the magnets no longer hold it flat.
- The edge is nicked or kinked.
- Rubbing has worn a visible track.

**5. Where a number is needed, the life of the seal is stated as crossings of the carriage
over one point of the strip, never as kilometres of travel.**

Travel before failure is the number of crossings multiplied by the stroke the machine
repeats. The same strip lasts twenty times further on a long stroke than on a short one, so
a kilometre figure measures the duty cycle rather than the strip.

## Consequences

**The carriage grows in length, not in height.** The earlier version asked for 60 mm
rollers above the carriage. It no longer does. What the carriage needs is a ramp long
enough to keep the turn shallow, which is length at each end. That is the same trade every
maker of these axes has made.

**One number now carries the whole decision.** It is the radius the strip really takes at a
roller. Measure it on the built carriage with a radius gauge or a photograph against a
scale. Until that is measured this decision stays proposed.

**Corrosion becomes the open risk instead of fatigue.** Every fatigue value used here is
measured in dry air, and the strip makers say so. The stage runs SAMNOS AL, a water based
coolant at pH 7.4, applied as minimum quantity lubrication. In a wet environment many
steels lose the fatigue limit, so "lasts without a limit" is not yet proven for this
machine. EN 1.4310 is also the weakest common stainless against pitting: about 17 percent
chromium and no molybdenum.

Two things close that gap. The chloride content of the coolant, which is not on its data
sheet and has to be asked for, and a bend test with the real strip and the real coolant. If
chloride turns out to be high, the alternatives are a molybdenum alloyed stainless valve
steel, or duplex EN 1.4462 at the cost of much larger rollers.

**Parking position needs watching.** Where the carriage stands still for hours, a piece of
strip stays bent under a roller. That is sustained stress, not a fatigue cycle, and it makes
the strip take a slow permanent bend. EN 1.4310 relaxes more than duplex or 17-7 PH. If the
machine parks in the same place every night, check that spot for a kink.

**One geometric assumption is unchecked.** The cycle count assumes the strip runs straight
between rollers and returns to zero curvature. The carriage drawing supports this: the
strip runs straight up the ramp and straight across the carriage, and turns only at the
rollers. It still deserves a photograph of the strip under load, because a strip that stays
curved between two close rollers would change the count.

**The fatigue limit at 0.1 mm is extrapolated.** Alleima measure down to 0.25 mm only. The
1019 MPa figure extends their own trend past that, and three questions have gone to them:
whether there is measured data at 0.1 mm, what the value is along the rolling direction
rather than across it, and what the value is at a lower survival rate than 50 percent. The
decision does not depend on the answers, because the strip is far below the limit either
way, but the number quoted in the results does.
