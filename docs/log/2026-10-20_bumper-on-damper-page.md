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

## Update: the shape of the force curve

The user doubted the linear force curve. The question was: does the TA22-10 push with a nearly
constant 870 N from the first contact, and then jump to 90,000 N when it is fully pressed in?

The ACE datasheet (BIBUS, TUBUS TA, edition 21_22_0045) gives a different picture:

- **870 N to 90,000 N is the range of the whole TA family.** It runs from the smallest size,
  TA12-5, to the largest, TA116-48. It is not the force curve of one bumper.
- **The real curve is not linear and not constant.** ACE publishes one force–stroke graph, for the
  TA37-16. The force starts at zero, rises fast in the first millimetres, and then flattens out
  near the top. ACE says the TA types "take a lot of energy at the start of the stroke".
- The curve F = F_full·(1 − (1 − x/s)^1.8) fits the graph within a few percent. The work under it
  is 65 J, the catalog value of the TA37-16.

The page now has a choice of four curve shapes: the ACE TA curve (the new default), a constant
force, a linear spring, and a power law with a free p. The user asked for the constant force; it is
there as the ideal lower limit.

Results at 2 m/s (5 kg, 10 J, motor off), TA22-10 with a 10 mm stroke:

| Force curve | Compression | Peak force | Peak deceleration |
| --- | --- | --- | --- |
| ACE TA curve | 9.2 mm | 1.77 kN | 36.1 g |
| Constant force | 8.7 mm | 1.15 kN | 23.5 g |
| Linear spring | 9.3 mm | 2.14 kN | 43.7 g |

- **The peak force is about 17 % lower than the linear curve gave.** It is still about 50 %
  higher than a constant force.
- A constant force for the TA22-10 would be 1150 N (11.5 J over 10 mm), not 870 N. 870 N over
  10 mm holds only 8.7 J.
- The bounce back stays 1.26 m/s. It depends only on the energy and the absorbed part.
- At 3 m/s the bumper is still fully pressed in with every curve, and 11 J is left.

New open point:

- On the TA37-16 graph, the catalog energy of 65 J is reached at about 10.5 mm, not at the
  maximum stroke of 16 mm. If the TA22-10 behaves the same way, it reaches 11.5 J at about 6.5 mm.
  Then the peak force at 2 m/s is 2.72 kN (55.5 g) with the ACE curve. This is a guess from one
  size. Ask ACE for the TA22-10 curve before choosing the part.

