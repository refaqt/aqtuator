# The seal strip ends are held by a printed clamp on a ramp

- **Date:** 2026-11-20
- **Status:** Accepted

## Context

Four corner screws held the seal strip ears on the top of the base. Their heads stood above the
strip, in the path of the carriage. Every scraper design had to go round them, and the carriage-top
hit them before the end-stop dampers. Changing the screw type (ISO 7380-2, then DIN 7984) did not
solve this, because any head above the base top is in the way.

Niels Bosmans drew a new concept on 2026-11-20: the strip bends down at each base end, and a
printed clamp below the base top presses it there.

## Decision

- At each base end the base has a ramp of radius 15 mm across its whole width. It meets the
  strip pocket floor 10 mm from the base end, without a step in slope.
- The strip follows the ramp down and ends 1 mm from the base end.
- A clamp printed in PLA lies on it. Its underside has radius 15.15 mm on the same centre, so it
  presses the 0.15 mm strip on the ramp. Its top is 0.2 mm below the top of the base. The carriage
  passes over it.
- Six ISO 10642 M3 × 10 countersunk screws hold each clamp. Around each screw the clamp has an
  8 mm boss. The boss goes through a slot in the strip, open at the strip end, into an 8.4 mm
  pocket in the base, with an M3 tapped hole under it.
- The preload screw (ISO 10642 M4) still sets the pull before the clamp is tightened, and comes
  out through an 8.4 mm hole in the clamp. It moved from 6.5 to 4.75 mm from the base end.
- The corner screws, the strip ears, and the short magnet strips at the base ends are removed.
  The two long magnet strips stay.
- The clamp edge facing the middle is 0.4 mm thick (two printed layers). This makes the clamp
  5.58 mm wide instead of the 7 mm in the first drawing: at 7 mm the edge would be only 0.06 mm
  thick, once the clamp leaves room for the strip.

## Consequences

- Nothing stands above the base top any more. The scraper and the carriage-top no longer need to
  avoid screw heads at the ends.
- The flat strip as cut is 443.24 mm long (was 441.95 mm), because it now also covers the two
  ramps.
- On the ramp the strip slopes under the preload screw. So the screw moved out to 4.75 mm from
  the base end, the base hole has a 90° countersink that stops 0.5 mm before the cavity, and the
  strip hole is two joined circles. The cone touches only the outer side of the hole, with
  0.43 mm of screw travel, and the strip still closes the cavity. See
  [the sealed preload log](../log/2026-11-20_preload-on-the-ramp-sealed.md).
- The strip now spans the open damper pockets on the ramp, as it already did on the flat floor.
- All sizes come from `modules/compact-stage/cad/params/default.csv` and are linked in the base,
  the clamp and the strip.
- **Update 2026-11-24:** the preload screw moved in to 8.25 mm from the base end, on a 3.5 mm
  bulge of the end wall, and the strip hole is one round hole. The clamp keeps 3.85 mm of plastic
  at its outer edge next to the screw. See
  [the bulge log](../log/2026-11-24_preload-screw-on-the-bulge.md).
- Supersedes the corner screws of
  [the 2026-10-28 strip end decision](../log/2026-10-28_strip-end-clamp-and-preload.md).
