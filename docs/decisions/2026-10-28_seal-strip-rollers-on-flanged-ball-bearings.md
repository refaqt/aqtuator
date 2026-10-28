# 2026-10-28 — The seal strip rollers turn on two flanged ball bearings

- **Date:** 2026-10-28
- **Status:** Accepted

## Context

The compact stage has eight seal strip rollers: four in carriage-bottom and four in carriage-top.
Each roller is 10 mm across and 20 mm long. It turns on a fixed axle of 2 mm, which a countersunk
screw clamps against the wall of the axle slot.

The first hand sketch of the roller had seven parts: the axle, two ball bearings, two washers, an
inner spacer tube and an outer sleeve. Niels Bosmans asked for a simpler roller made of standard
parts.

No bought part does the whole job. No bushing or ball bearing has a 2 mm hole and a 10 mm outside
diameter.

The simplest choice was a plastic ring that turns directly on the pin. MISUMI sells one: the resin
collar CLJJ2-10-20 in POM (polyacetal), 2 mm hole, 10 mm across, 20 mm long. POM has lower friction
than the MC nylon version of the same collar. Datasheets give 0.30 to 0.45 for POM-C and 0.40 to 0.60
for PA6, both against steel at 3 MPa.

The friction of a plastic roller is too high. At the default strip pull of 54 N, the seal strip page
gives 250 N on each outer roller position and 41 N on each inner one. Each position has two rollers,
one on each side of the slot. The drag at the strip is friction × roller force × 2 mm / 10 mm:

| At 54 N pull | Per roller | All 8 rollers, POM | All 8 rollers, nylon |
| --- | --- | --- | --- |
| Outer rollers (1 and 4) | 125 N | 30–45 N | 40–60 N |
| Inner rollers (2 and 3) | 20.5 N | 5–7 N | 7–10 N |
| **Total** | | **35–52 N** | **47–70 N** |

That is 4 to 6 times all the other friction on the carriage (8.5 to 9.1 N in the channel). With
ball bearings, the drag is about 0.2 N in total. Bearing makers give a friction value of about 0.0015
for deep groove ball bearings.

## Decision

Each roller is made of standard parts, with one simple machined part:

| Part | Qty per roller | What it is |
| --- | --- | --- |
| Axle | 1 | Hardened dowel pin, ISO 8734, 2 mm (m6) × 28 mm |
| Bearings | 2 | NSK F692ZZ flanged ball bearing, 2 × 6 × 3 mm, flange 7.5 × 0.8 mm, shields on both sides |
| Sleeve | 1 | Our part: precision tube 10 × 2 mm (6 mm hole), cut to 18.4 mm. Each end takes one bearing |
| Washers | 2 | ISO 7092 washer for M2, 2.2 × 4.5 × 0.3 mm, A2 stainless steel |

- Each bearing flange rests on an end of the sleeve. The flanges set where the bearings sit, so the
  inner spacer tube of the sketch is no longer needed.
- The washers sit between the inner ring of each bearing and the wall of the roller pocket. They keep
  the turning outer ring and its flange off the wall.
- The roller stays 10 mm across and 20 mm long. The roller pockets and axle slots do not change.
- The longest pin that fits the axle slot is 29 mm. The 28 mm pin keeps 0.5 mm at each end, and both
  axle screws still clamp it.
- The plastic collar is rejected because of its friction.

## Consequences

- The whole stage needs 16 bearings, 8 pins, 8 sleeves and 16 washers.
- The sleeve is the only part we make. Its hole needs a fit for the bearings: ream it to 6 mm, then
  glue or press the bearings in.
- The rollers have 0.4 mm of play along the axle (two gaps of 0.5 mm, minus two washers of 0.3 mm).
- A 2 mm pin is thin. With 125 N on an outer roller, carried by the two bearings near the pocket
  walls, it bends much less than it would under a plastic roller. Check the pin at the highest strip
  pull of the seal strip page.
- The bearings and the pin are not stainless steel. The rollers sit under the strip seal, but check
  them for rust when the stage runs with coolant.
- Check that the 4.5 mm washer touches only the inner ring of the bearing, not the shield.
- The seal strip page assumes that the rollers add no friction. With ball bearings, that stays true
  within about 0.2 N.
