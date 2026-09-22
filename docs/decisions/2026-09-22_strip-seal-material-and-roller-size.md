# 2026-09-22 — Strip seal material and roller size

- **Date:** 2026-09-22
- **Status:** Proposed

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

**3. The seal is designed to last without a limit, not to a replacement interval.**

Two layouts reach that with 0.1 mm strip. Either all four rollers at 24 mm, or rollers 1
and 4 kept at 20 mm with rollers 2 and 3 opened to 60 mm. The second is preferred, because
the two rollers above the carriage have room and the two inside the slot do not.

Rollers of 14 mm are rejected for 0.1 mm strip. No roller layout rescues them, and the
strip would have to drop to 0.05 mm.

**4. The life of the seal is stated as crossings of the carriage over one point of the
strip, never as kilometres of travel.**

Travel before failure is the number of crossings multiplied by the stroke the machine
repeats. The same strip lasts twenty times further on a long stroke than on a short one, so
a kilometre figure measures the duty cycle rather than the strip. Where a design does last
without a limit, no figure is needed at all.

## Consequences

**The carriage grows above the strip and not inside the slot.** Opening rollers 2 and 3 to
60 mm needs height over the carriage. That is a real cost, and it has to be checked against
the CAD before this decision moves from proposed to accepted.

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
between rollers and returns to zero curvature. If rollers sit close enough that the strip
stays curved between them, the count changes. This should be confirmed against the CAD or a
photograph of the strip under load.
