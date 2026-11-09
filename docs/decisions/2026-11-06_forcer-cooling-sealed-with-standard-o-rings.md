# ADR — The forcer cooling is sealed with standard O-rings and a printed block

- **Date:** 2026-11-06
- **Status:** Partly replaced by [2026-11-09](2026-11-09_cooling-block-to-the-edge-with-festo-fittings.md): the hose barbs, the hose slot and the side cable clamp are gone. Niels Bosmans chose this layout ("option 2") on 2026-11-06. The design is
  a first version for review, not yet built or tested.

Write this file in B2 English. Follow `.agents/rules/communication.md`.

## Context

The cooling channel in carriage-bottom is cut into the ceiling of the forcer pocket. The flat
mounting face of the forcer (MAXWELL MK21) closes it from below. Two things were missing:

- a seal, so that no water can reach the motor;
- a connection from the two channel ends to two hoses, which leave the carriage at the side
  together with the motor cable.

The space is small. Over the forcer, carriage-bottom has only 7.5 mm of aluminium
(z = 20 → 27.5 mm), and nothing may stand above its top face: the seal strip runs 1 mm above it.
A water-rated push-in fitting for 4 mm hose (Festo NPQH-D-M5-Q4-P10, 9 mm hex) is about 10 mm
across, so it does not fit there.

Three layouts were compared with sketches and 3D views:

1. Drilled passages in carriage-bottom and Festo fittings in the motor cable opening. Rejected:
   the side holes need a long, thin drill, and the heights fit with almost no margin.
2. A printed block in a shallow pocket, with standard O-rings. **Chosen.**
3. A long block with Festo fittings at the side edge and a recess in carriage-top. Rejected:
   it also changes carriage-top, and the fittings fit only just.

## Decision

- **Forcer seal:** one standard, moulded, endless O-ring, 90 × 2 NBR 70, in a groove with
  rounded corners in the ceiling of the forcer pocket. No printed seal and no glued cord. The
  groove centre line (288.5 mm) matches the O-ring centre line (289 mm).
- **No seal between the channel passes.** A leak there only moves water from the supply pass to
  the return pass. The pocket ceiling must be flat (0.02 mm or better).
- **Cooling block:** an SLA resin print. It lies in a 5 mm pocket over the channel ends. Its
  barbs point into the motor cable opening.
  - Two 5 × 1.5 NBR 70 face seals in its bottom, one around each port.
  - Two hose barbs are part of the print. The 4 × 2.5 PU hoses push over them. A socket with an
    O-ring was rejected: it needed a block head that hangs in the motor cable path.
  - Two countersunk M2.5 screws from below pull it down. They are tapped into the resin.
- **Cable clamp:** a printed part in two halves, just outside the side face. It closes the side
  exit around the hoses and both cables, and it holds the hoses on the barbs.
- **Order by size and material only** (inside diameter × cross-section, NBR 70). The dash
  numbers of the inch series differ between catalogues.

## Consequences

- The cooling channel is narrower (3 mm tool, 4.1 mm pitch, 8 passes, 31.7 mm wide) to make room
  for the groove inside the forcer screws. It has about 35 % less wetted area than before.
- The encoder slot is 1 mm shallower (5 mm), so it keeps 1 mm of wall over the groove. The read
  head cable is 3.7 mm thick, so it still fits.
- The hoses have their own slot (Pocket027) beside the motor cable. The motor cable bend moved
  5 mm towards the read head slot (radius 40 → 35 mm). The hoses cross over the motor cable in
  the cable opening, so the cable must stay low there.
- The block is a printed part with water inside. It must pass a leak test (2 bar, 1 hour) before
  the motor is powered.
- The barbs are thin (0.7 mm under the rings). A test print must show they survive pushing the
  hoses on and off.
