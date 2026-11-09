# 2026-11-06 — Preliminary CE assessment of the compact stage

**Role(s):** engineering, safety

## Goal

Niels asked for a first CE check of the compact stage: what must change in the design to make it
safer, which safety features the drive needs, and whether his drive options have them.

## Short answer

- The stage is partly completed machinery. It gets a Declaration of Incorporation and assembly
  instructions. The machinery rules change on 20 January 2027.
- The end stop dampers are too weak for 3 m/s. The payload and the top speed must be fixed.
- The RSF AK MC 15 B read head has no limit outputs in its own manual. The limit switches stay in
  the parts list until this is cleared up.
- Three new hard drive requirements: CE marking (DRV-11), certified Safe Torque Off at SIL 2 /
  PL d (DRV-12), fault stops (DRV-13). Two new preferences (DRV-P4, DRV-P5).
- The Copley XEL fails DRV-12. No drive on the list is confirmed on all three yet.
- Full result: [the CE assessment](../compact-stage-ce-assessment.md).

## Decisions Made

- None. The legal route, the payload and the top speed are for Niels to confirm.

## Next Steps

1. Fix the largest payload and the declared top speed.
2. Ask every drive maker for the Declaration of Conformity and the STO certificate.
3. Add the earth point, cable strain relief and warning sign places to the CAD.

<details>
<summary>Technical notes</summary>

- Drive values were read in the makers' manuals by two research helpers; sources and pages are in
  the technical notes of the CE assessment.
- Mistake rules applied: values from the maker's own documents only, and a whole-repository
  search before removing a bought part (the limit switches appear only in
  `modules/compact-stage/bom/bom.csv`).

</details>
