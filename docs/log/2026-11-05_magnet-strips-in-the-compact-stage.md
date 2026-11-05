# 2026-11-05 — The magnet strips are in the compact stage

**Role(s):** cad, architecture, purchasing

## What happened

The parts library (stoq) now has the magnet tape that holds the seal strip down: the roll
`3X0.5X500` and two cut pieces, `3X0.5X417.5` and `3X0.5X80`. We moved `modules/stoq` to that
version and put six pieces in the compact stage assembly:

| Piece | Part number | Where |
| --- | --- | --- |
| 2 long strips | `3X0.5X417.5` | One on each long side of the magnet ring |
| 4 short strips | `3X0.5X80` | Two in each end leg, between a corner and the split at the preload screw |

They lie on the floor of the ring pocket, adhesive face down. Their top is level with the floor of
the strip pocket, so the seal strip rests on them.

The bill of materials has two new rows, `MEC-007` (long) and `MEC-008` (short). The architecture
has a new interface for the ring pocket and a new part, `MagnetStrip`.

`.agents/` and `doqs/` were already on the newest version.

## Decisions

- **Each strip is placed with a Grounded joint**, like the seal strip and its screws. The base has
  no frames for the magnet ring, and adding six frames to the base only for this did not seem
  worth it. If the base moves, these placements must move too.
- **Order 3 rolls per base.** The BOM lists the cut pieces, because those are what the stage holds.
  The notes of `MEC-007` say how many rolls to buy.

## Next Steps

- Measure a real strip: the thickness with and without the adhesive layer, and the holding force on
  the 0.15 mm seal strip (see the stoq log of 2026-11-05).
- If the base gets frames for the magnet ring later, change the six Grounded joints to Fixed joints.

<details>
<summary>Technical notes</summary>

- stoq `45a67d1` → `70b619e`. Part files pulled with `git lfs pull`; each starts with `PK`.
- The base after `b4a342b` (no tab at the second rail) still has the ring of the stoq notes:
  `Sketch006` x 7 to 433, y 14 to 196, R4 corners; `MagnetRingSplitSketch` y 98.5 to 111.5 at the
  wall; ring floor z 39.35 (`Pocket004`, 0.65 mm from the top).
- Links to the `Part` App::Part of each stoq file. Placements (piece origin = a corner of the
  adhesive face):
  - `magnet_long_a` (11.25, 14, 39.35), `magnet_long_b` (11.25, 193, 39.35), no rotation.
  - `magnet_short_start_a` (10, 18.25, 39.35), `magnet_short_start_b` (10, 111.75, 39.35),
    `magnet_short_end_a` (433, 18.25, 39.35), `magnet_short_end_b` (433, 111.75, 39.35),
    rotated 90° about Z.
- Bounding boxes after the solve: long x 11.25 to 428.75; short y 18.25 to 98.25 and 111.75 to
  191.75; all z 39.35 to 39.85.
- Collision check: `common().Volume` of each strip with every other part: zero everywhere,
  also with the base and the seal strip.
- `Assembly.solve()` returned 0. No other part moved.
- Edits in the open FreeCAD 1.1 window through its RPC server, with `execute_code` (main thread).
  The fingerprint was written with `cad_fingerprint.write()` after the save: `saved: true`,
  40 objects. A first try gave 33 objects, because the base and the stoq files had been closed;
  they were opened again first.
- `bash doqs.sh generate` and `bash doqs.sh check` ran after the changes.

</details>
