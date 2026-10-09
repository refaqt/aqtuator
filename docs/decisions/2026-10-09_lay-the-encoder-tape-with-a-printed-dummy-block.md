# 2026-10-09 — Lay the encoder tape with a 3D-printed dummy guide block

- **Date:** 2026-10-09
- **Status:** Accepted

## Context

The steel scale tape of the linear encoder sticks to the side wall of the pocket in the base of
the compact stage. Renishaw lays it with an applicator, a dummy reading head that rides along the
axis and presses the tape down.

[The tape mounting log](../log/2026-10-07_mounting-the-encoder-scale-tape.md) found two problems.
On the real carriage, the applicator sits between two guide blocks, so it cannot reach the end of
the tape and cannot come out while the tape is still in it. There is also very little room to
press the tape down by hand.

The rails cannot take blocks from the end while they are in the base. The rail floor is 420 mm
long and the HIWIN HGR15R rail is 418 mm long, so the pocket walls close both ends of the rail.
Every block must be on the rail before the rail goes into the base.

## Decision

**The applicator is bolted to a 3D-printed dummy guide block. The real guide blocks go on after
the tape is laid.** The order is:

1. Slide the printed dummy block onto the rail next to the tape.
2. Fit that rail in the base, against its alignment tabs, with all its screws.
3. Lay the tape with the applicator on the dummy block, as the Renishaw guide describes.
4. Take the rail out of the base again, and slide the dummy block off its end.
5. Slide the real HIWIN HGL15 guide blocks onto the rail.
6. Fit the rail in the base again, against the same tabs. Then fit the carriage.

The printed block puts the applicator in front of the block, in the direction of laying. The
applicator then reaches the end of the tape before the block reaches the end of the rail.

**Fallback: a dummy rail.** If we do not want to take the real rail off, we fit a dummy rail in
its place for steps 1 to 4. The real rail, with its blocks already on, then goes into the base
only once. The dummy rail must sit on the same floor and tabs as the real rail, and be as
straight. A spare HGR15R rail does this. A printed rail is not likely to be straight enough over
418 mm, so it needs a check first.

## Consequences

- **The tape position depends on how well the rail goes back to the same place.** The applicator
  follows the rail, so the tape follows the rail. Put the tape next to the reference rail. That
  rail lies against two tabs, so it goes back to the same place. Clean the floor and the tabs,
  push the rail against the tabs, and tighten the screws in the same order both times.
- **The printed block must hold the applicator where the real reading head bracket will be.** It
  sets the height of the tape on the wall and the gap to the wall. Check it with the green shim
  from Renishaw before laying. The block must fit the rail with very little play, so it does not
  tilt during the pass. Print a short test piece and try it on the rail first.
- **The real blocks can come off and go on the rail without losing balls.** The HIWIN catalogue
  says the HG series has ball retainers, so the balls stay in the block when it leaves the rail.
  Slide them on straight and slowly, so the seals are not damaged.
- **The tape is open while the rail is out and goes back in.** Cover it with card or a strip of
  paper so a tool cannot scratch it. Fit the datum clamp after 24 hours, as Renishaw asks.
- We still do not know if Renishaw accepts an applicator on a printed block. Ask the Renishaw
  application engineer.
- The dummy carriage plate and the rail-riding saddle from the earlier log are no longer needed.
