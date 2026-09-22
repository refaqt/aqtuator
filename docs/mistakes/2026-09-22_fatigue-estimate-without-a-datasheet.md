# 2026-09-22 — Gave a fatigue life from textbook constants, and got it wrong three times

## What happened

The question was how long a 0.1 mm spring steel sealing strip lasts when the carriage
rollers bend it. Three answers were given before the right one.

**First answer, too pessimistic by about forty times.** It used generic steel constants
from a textbook: a tensile strength of 1800 MPa, a modulus of 195 GPa and an assumed
fatigue exponent. It reported 7,300 cycles for a 14 mm roller. The supplier data sheet for
the real material gives about 290,000 for the same geometry.

Two inputs were wrong. Strip of 0.1 mm is not sold at 1800 MPa, it is sold at 2050 MPa,
because thin strip work hardens more during rolling. And cold rolled austenitic stainless
has a modulus of 185 GPa, not 195. Both errors pushed the answer the same way.

**Second answer, wrong in the other direction.** It assumed the strip is bent in one
direction only. The carriage has four rollers and bends the strip up, down, down and up, so
the stress swing is twice as large as assumed. The recommendation moved from 17 mm rollers
to 24 mm once the real layout was counted.

**Third answer, too pessimistic again, and this time it nearly changed the machine.** It
treated the roller diameter as the bending radius, so a 14 mm roller was reported at
1312 MPa and 19,000 crossings, and the design was told to fit 60 mm rollers above the
carriage. A strip only takes the roller radius if something presses it there. In the
carriage as drawn the strip turns about twelve degrees at each roller, and forcing a 0.1 mm
strip onto a 14 mm roller at that angle would need about 1,050 N of pull on a 40 mm strip.
The strip bridges the roller, the real stress is 57 to 362 MPa, and the 14 mm rollers were
never a problem.

The same answer also read the fatigue limit at 0.25 mm and applied it to a 0.1 mm strip,
although the maker publishes two thicknesses and their own trend gives about 1019 MPa at
0.1 mm instead of 775 MPa.

## Why it went wrong

The first error is the same one as
[the pole-face Maxwell stress entry](2026-09-02_maxwell-stress-as-device-force-density.md):
a lumped formula with assumed constants was reported as an answer before any supplier data
sheet was opened. The prevention rule written then was about force density, so it did not
fire for a fatigue question. The rule was too narrow.

The second error came from answering before the arrangement was known. The load case was
assumed rather than asked about. A sentence asking how the strip is routed would have
caught it, and the user had to catch it instead.

The third error is the second one again, one level deeper. The arrangement was asked about
and the roller count was right, but the geometry that makes the strip take a radius was
still assumed. A drawing of the carriage settled it in one look, and the user had to supply
that drawing too. The lesson is not about rollers. It is that a formula input which names a
part, such as "the roller diameter", quietly smuggles in a physical claim about what that
part does to the material.

## Prevention rule

**Before quoting any number that describes how a real part behaves, open a supplier data
sheet or a standard for the actual material, in the actual size.** This covers fatigue
life, force density, stiffness, strength and thermal limits. A textbook formula with
assumed constants gives the shape of the answer, never the value. If no data sheet can be
found, say the number is an estimate and give the range it could take, before giving the
number.

**Watch for size and temper in particular.** Thin strip, thin wire and small parts are
often much stronger than the bulk grade, and sometimes much weaker. A figure taken from a
grade table is not a figure for the size being bought.

**Before calculating a load, state the load case back and ask if it is right.** How many
times per pass, in which direction, and with what mean value. Getting the material right
does not help if the loading is wrong.

**A contact radius is not a bending radius.** Before putting any radius into a stress
formula, say what makes the part take that radius, and check that the force to do so
exists. A roller, a pin, a former or a fold line sets a lower limit on the radius. It sets
the actual radius only when something presses the material onto it hard enough. Work out
that force and compare it with the force the design really has.

**Ask for the drawing before the third answer, not after.** Two wrong answers in a row on
the same question mean the geometry is not understood. Ask to see it.

## Related

- [Treated pole-face Maxwell stress as packaged force density](2026-09-02_maxwell-stress-as-device-force-density.md)
- [Treated analogWrite ISR unsafety as settled too early](2026-03-31_analogwrite-isr-conclusion-premature.md)
- [Strip seal material and roller size](../decisions/2026-09-22_strip-seal-material-and-roller-size.md)
- [`simulation/cases/strip-seal-fatigue/`](../../simulation/cases/strip-seal-fatigue/)
