# 2026-10-20 — The damper page can now calculate a polyurethane bumper

**Role(s):** engineering, simulation

## Goal

A competitor uses short polyurethane bumpers as end stops, not oil dampers. A short bumper saves
travel. The user asked to add the bumper to the damper sizing page, with a clear way to choose
between a damper and a bumper.

## Work Done

- The page now starts with a choice: "Oil damper" or "Polyurethane bumper". Only the inputs for
  the chosen type show. The results, warnings and charts follow the choice.
- The bumper force depends on how far it is pressed in: F = F_full·(x/s)ᵖ. The inputs are the
  catalog values: stroke, energy per stroke, energy for emergency use, and the part of the energy
  that turns into heat. The shape p is the only estimate.
- Defaults come from the ACE product page for the TUBUS TA22-10: 10 mm, 11.5 J, 21.0 J emergency,
  58 to 73 % absorbed. This is a co-polyester elastomer, not polyurethane, but it is the closest
  short bumper with published energy values.
- New checks test the bumper against exact results for a linear spring and for p = 2, the energy
  balance, and a bumper that is fully pressed in.

Results at 2 m/s (5 kg, 10 J, motor off):

| End stop | Stroke | Peak force | Bounce back |
| --- | --- | --- | --- |
| TA22-10 bumper, linear curve | 9.3 mm of 10 mm | 2.14 kN, 43.7 g | 1.26 m/s |
| Oil damper, one fixed orifice | 15 mm | 3.99 kN, 81.5 g | none |
| Oil damper, even force | 15 mm | 0.67 kN, 13.6 g | none |

- **At 2 m/s a 10 mm bumper works.** It saves 5 mm per end against the 15 mm damper.
- **At 3 m/s (22.5 J) it does not.** The TA22-10 is fully pressed in and 11 J is left for
  metal-on-metal contact. A bumper only works if the drive limits the speed near the ends.

Open points:

- Ask ACE for the force–stroke curve of the chosen size, to replace the estimated shape p.
- Check the peak force against the static load rating of the QEH15SA blocks and the shock rating
  of the encoder read head.
- Friction is not counted in the bounce back.
