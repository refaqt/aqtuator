# 2026-10-28 — Seal strip page: the plastic strip on the ceiling is now a short pad

**Role(s):** engineering, simulation, software

## Goal

Niels Bosmans said the seal strip page modelled the plastic strip wrong. It ran along the whole
ceiling from roller 2 to roller 3. He wants a short plastic pad, 10 mm wide, in the middle between
rollers 2 and 3, that pushes the seal strip down. The width must be an input.

## Short answer

- **The page now models a short pad in the middle.** Its width is a new input, 10 mm to start.
  Beside the pad the ceiling is bare aluminium.
- **A 0.5 mm pad does not keep the strip off the aluminium.** At 54 N the strip touches the pad
  edges, the bare ceiling (9 N) and carriage-bottom (8 N). The friction is 8.5 to 9.1 N with PTFE.
  With the old long plastic strip the model gave 2 to 7 N.
- **A thicker pad takes over the ceiling contact.** From 1.5 mm the bare ceiling carries
  nothing at 54 N, and the friction drops to 4.8 to 6.4 N. From about 1.8 mm the pad starts to
  pinch the strip on carriage-bottom.
- **The width matters less than the thickness.** 5 mm or 20 mm wide changes the friction by less
  than 1 N.

## Work Done

- Changed the ceiling in the model: the plastic only covers the set width, centred between
  rollers 2 and 3.
- Added the width input to the page and drew the pad in the middle only.
- The free room under the ceiling is now the smallest gap between rollers 2 and 3, not only at
  the top of the arch.
- Added a check that the pad sits in the middle and is as wide as set.
- Updated the results in the case README.

Full tables: [case README](../../simulation/cases/strip-seal-designer/README.md#results-at-the-defaults).

## Decisions Made

No design decision. The 0.5 mm × 10 mm PTFE pad is only the starting value on the page.

## Open Questions

- **How thick should the pad be?** About 1.5 mm keeps the strip off the bare ceiling at 54 N.
  More than about 1.8 mm pinches the strip. The real tolerance of the carriage gap decides this.

## Next Steps

- [ ] Choose the pad thickness and width, and draw the pad in carriage-top.
