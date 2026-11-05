# 2026-11-05 — The magnet strips are in the compact stage

**Role(s):** cad, architecture, purchasing

## What happened

The magnet strips that hold the seal strip down are now in the compact stage assembly. There are
ten of them, all from the parts library (stoq):

| Pieces | Part number | Where |
| --- | --- | --- |
| 2 long strips | `3X0.5X417.5` | One on each long side of the magnet ring |
| 8 short strips | `3X0.5X21.5` | Four in each end leg, one on each piece of solid floor |

They lie on the floor of the ring pocket, adhesive face down. Their top is level with the floor of
the strip pocket, so the seal strip rests on them.

The first version had one 80 mm strip on each side of the split in each end leg. Niels saw that
these lay over the damper slots in the end walls, where the strip has no floor under it. The floor
of each end leg has four solid pieces, between a cavity at each corner, the two damper slots and
the split at the preload screw. One 21.5 mm strip now sits on each piece. The new length was added
to stoq ([refaqt/stoq PR #26](https://github.com/refaqt/stoq/pull/26)); the 80 mm piece is `eol`
there.

Niels also asked that no part needs to be moved by hand when the base changes:

- **Magnet strips:** the base has ten new frames, `IF_magnet_*`, one for each strip. Each strip is
  held by a Fixed joint between its frame `IF_end` and its base frame.
- **Strip screws:** the two preload screws and the four corner screws are no longer grounded. Each
  has a Fixed joint between a round edge of the screw and the round edge of its hole in the base.
  Screws have no frames, so the joint uses the features.

The bill of materials has two new rows, `MEC-007` (long) and `MEC-008` (short, 8 per base). Order
3 rolls per base. The architecture has a new interface for the ring pocket, ten ports on the base
and a new part, `MagnetStrip`.

## Decisions

- **One length for all short strips, 21.5 mm.** The two outer floor pieces of each end leg are
  23.5 mm long, the two middle ones 22 mm. Niels chose one part number over two lengths.
- **Short strips centred on their floor piece.** 0.25 mm room at each end in the middle, 1 mm at
  the outer pieces.
- **The seal strip stays grounded.** Only the magnets and the screws were asked for.

## Next Steps

- Measure a real strip: the thickness with and without the adhesive layer, and the holding force on
  the 0.15 mm seal strip (see the stoq log of 2026-11-05).
- The seal strip itself is still grounded. It could get a joint to the base in the same way.

<details>
<summary>Technical notes</summary>

- stoq `45a67d1` → `dc5e65b` (the merge of PR #26). Part files pulled with `git lfs pull`.
- Floor of the ring end legs (x 7 to 10 and 430 to 433), measured with a 0.2 mm box under the
  floor, z 39.1 to 39.3: holes at y 18 to 29, 52.5 to 76.5, 102.55 to 107.45 (counterbore, under
  the split), 133.5 to 157.5 and 181 to 192. The long sides have no holes.
- Base `Params`, new cells: `magnet_long_l` 417.5, `magnet_short_l` 21.5, `magnet_y_1a` 40.75,
  `magnet_y_2a` 87.5, `magnet_y_2b` 122.5, `magnet_y_1b` 169.25 (centres of the floor pieces).
- Base frames, `FlatFace` on `XY_Plane001` like the other frames, offsets by expression:
  - `IF_magnet_long_a/b`: x `(BlockSketch.Length − magnet_long_l) / 2` = 11.25; y 14 and 193 from
    `BlockSketch.Width`, `Sketch.pocket_w` and `MagnetRingSplitSketch.ring_w`; no rotation.
  - `IF_magnet_start_*` at x 10 (`ring_outer_x + ring_w`), `IF_magnet_end_*` at x 433
    (`ring_outer_x_end`), y = centre − `magnet_short_l` / 2 (30, 76.75, 111.75, 158.5), 90°
    about Z.
  - All at z `Block.Length − Pocket004.Length` = 39.35.
  - Body unchanged: 1 387 301 mm³, 225 faces.
- Assembly: joints `Fixed_magnet_*` (base `IF_magnet_*` XY plane ↔ strip `IF_end` XY plane).
  The first solve put the short strips on their frame origin but did not turn them. Set close to
  the right turn, the solve held them; a strip pushed 5 mm and 30° off went back.
- Screw joints `Fixed_*_screw_*`: preload screw head top edge ↔ base counterbore top edge
  (z 39.85), `Offset1` z 2.48 mm. Corner screw collar underside (z 40.0) ↔ base tapped hole top
  edge (z 39.85), `Offset1` z −0.15 mm and 180° (the hole edge points down). Every screw kept its
  place; a screw pushed off went back.
- Follow test: `magnet_y_1a` set to 45 mm in the base → strip `start_a1` moved 4.25 mm; set back to
  40.75 mm.
- Collision check: the strips touch no part. The screws overlap the base only in the tapped
  holes (thread 4 mm in a 3.3 mm hole), as before.
- Edits in the open FreeCAD 1.1 window through its RPC server, with `execute_code` (main thread).
  Fingerprints written after the save: base 29 objects, assembly 44 objects, both `saved: true`.
- `bash doqs.sh generate` and `bash doqs.sh check` ran after the changes.

</details>
