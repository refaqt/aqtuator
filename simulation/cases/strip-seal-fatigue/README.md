# strip-seal-fatigue

How long a spring steel sealing strip lasts when the carriage rollers bend it, which
material to buy, and how to state the life of the seal in a way a customer can use.

**Tool:** Python 3, standard library only.

```bash
python3 simulation/cases/strip-seal-fatigue/strip_seal_fatigue.py
```

Results: [`simulation/results/strip-seal-fatigue/summary.md`](../../results/strip-seal-fatigue/summary.md).

The choice this case supports is recorded in
[2026-09-22 Strip seal material and roller size](../../../docs/decisions/2026-09-22_strip-seal-material-and-roller-size.md).

## The arrangement

A thin steel strip lies in a slot and seals it. The carriage carries four rollers. The
first lifts the strip, the second flattens it above the carriage, the third starts it
down again and the fourth lays it back in the slot. Between rollers the strip is straight.

So one point of the strip is bent up, down, down and up each time the carriage passes.

## What the model does

**Bending stress.** The surface stress follows from the radius the strip really takes:

```
sigma_max = E * t / (2 * R)
```

If the strip wraps the roller, `R` is `(D + t) / 2` and this is the same as `E * t / (D + t)`.
Sandvik write that as `E * t / D` when the roller is much larger than the strip. It is the
worst case, not the usual one. See the next section.

**The fatigue limit depends on thickness.** Alleima publish 775 MPa at 0.25 mm and 630 MPa
at 0.50 mm for the same material at the same strength. Thinner strip is stronger. The model
scales the published value to the thickness being bought and marks every value taken below
0.25 mm as extrapolated, because that is past the thinnest strip they measured.

**Mean stress.** Fatigue is driven by the size of the stress swing. The average stress is
a smaller correction, handled by the Goodman relation. The script checks its own Goodman
step against a figure Alleima publish for one of their materials, and refuses to run if it
does not match.

**Cycle counting.** The four bends are counted by the rainflow method, which is the
standard way to find how many load cycles an irregular stress history contains. The strip
returning to zero stress between two rollers does not end a cycle. What counts is the
distance from the highest stress to the lowest.

The result is simple: **one carriage pass equals one full reversal** at the peak bending
stress, plus two smaller cycles that are below the fatigue limit and do no damage.

## When a strip wraps a roller, and when it bridges it

A strip takes the roller radius only if something presses it onto the roller over an arc.
A thin strip under light pull does not. The turn spreads over a length `sqrt(EI / T)` on
each side of the roller, where `T` is the pull per mm of strip width, and the tightest
radius becomes

```
R_free = 2 * sqrt(EI / T) / turn angle
```

The roller is then a floor on the radius, not the answer, so the model takes whichever of
the two radii is larger.

For the carriage as drawn this settles the question. The strip turns about 12 degrees at
each roller. Forcing a 0.1 mm strip onto a 14 mm roller at that angle needs about 1,050 N
of pull on a 40 mm strip. A cover strip held by magnets or a light clamp carries a small
fraction of that, so it bridges, and the real bending stress is a few hundred MPa instead
of 1312 MPa.

The design variable is therefore the **turn angle**, which comes from the ramp length and
the lift height, not the roller diameter. HIWIN reach the same place from the other
direction: they use no rollers at all, and add 30 to 70 mm of carriage length per end,
depending on axis size, to spread the turn.

## Why the roller layout matters more than the material

A strip bent in one direction only swings by half the peak stress. A strip bent both ways
swings by the whole peak stress. The swing doubles, and the swing is what breaks things.
For the same roller, bending both ways is roughly fifteen times more damaging.

This gives a cheap fix. Rollers 2 and 3 sit above the carriage, where there is usually
more room than inside the slot. Making only those two larger shrinks the downward peak and
turns the reversal back into a one-way bend.

## Sources

Every fatigue number in the script is measured and published by a strip or belt maker.
None is estimated.

| Source | What it gives |
| --- | --- |
| Alleima 11R51 data sheet, 2025-05-09 | EN 1.4310: strength by thickness, reverse bending fatigue limit, modulus |
| Alleima Hiflex data sheet, 2025-05-09 | A molybdenum alloyed stainless valve steel, and a published mean stress conversion |
| Alleima Springflex data sheet, 2025-05-09 | EN 1.4462 duplex, for comparison on corrosion |
| IPCO Steel Belt Specifications v0.3 | Fatigue limit of twelve belt grades. All sit between 0.32 and 0.48 of tensile strength |
| Sandvik, The Steel Belt Conveyor | The drum diameter rule for belts, and the bending stress formula |
| EN 10151:2002 | Tensile classes of strip for springs, and how tightly each class may be bent |
| HIWIN HT-L assembly instructions, HTL-01-7-EN-2306-MA | How the cover strip is deflected, how it is replaced, and what triggers replacement |
| HIWIN linear axes catalogue HX-06-5-EN-2608-K | The length the cover strip deflection adds to the carriage, per axis size |
| US 6,092,456 | States that a seal band guided by guide rollers is flattened by them |
| US 6,629,779 | A cover band lifted so that its bending line runs free, without touching the slide |

## Three limits the numbers do not cover

**Fatigue is not what ends the life of a cover strip.** HIWIN tell the user to change it
"as soon as there are any signs of rippling and it can no longer be held in position by the
magnetic strips", and they say it wears by rubbing. Parker reject a band for nicks, kinks
and edge damage. The calculation in this case proves that fatigue is not the limit. It does
not predict when the strip stops sealing.


**The published fatigue values are for dry air.** Alleima and IPCO both say so, and the
Sandvik drum sizes assume no corrosion. The stage runs with a water based coolant, so a
bend test with the real strip and the real coolant is still needed before the unlimited
life claim can be relied on.

**Forming is not the limit.** EN 10151 allows this strip to be bent ninety degrees around
a radius of three times its thickness, which is 0.3 mm. The rollers are far larger than
that, so the strip will never crack on a single bend. Only fatigue and permanent set
matter.
