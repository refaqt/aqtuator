# 2026-11-20 — Seal strip held by a printed end clamp on a ramp

**Role(s):** cad

## Goal

Niels Bosmans asked to replace the corner screws of the seal strip by a new concept. The strip
bends down over a ramp at each base end, and a 3D printed PLA clamp presses it there. The clamp
top stays below the top of the base, so the carriage has nothing in its way. The base, the strip
and the clamp had to fit together, with the right holes, and with every size that depends on
another one linked. The strip length and shape had to be computed again.

## Short answer

- **The three parts fit.** The strip lies on the ramp. The clamp keeps exactly 0.15 mm (one strip
  thickness) above the ramp and touches the strip with no overlap.
- **The clamp is 5.58 mm wide, not 7 mm.** In the first drawing the clamp underside was the ramp
  itself, with no room for the strip. With room for the strip, a 7 mm clamp would end in a
  0.06 mm edge. The edge facing the middle is now 0.4 mm thick (two printed layers).
- **The flat strip is 443.24 mm long** (was 441.95 mm). It is a plain rectangle, 185.6 mm wide,
  with four open slots and one preload hole at each end.
- **Nothing stands above the base top any more.** At both end stops, the carriage-top passes
  0.7 mm over the clamps and screw heads.
- **Solved later the same day:** the preload hole became an 8.5 mm slot, see
  [the preload slot log](2026-11-20_preload-slot-on-the-ramp.md).
- **Open point at the time: the preload screw could not pull the strip as drawn.** Under the screw, the strip
  slopes about 13.5°. The cone touches the inner edge of the strip hole first, at x = 8.4 mm, so
  tightening the screw would push the strip end inwards. Niels Bosmans will decide how to solve
  this. The strip hole and the screw stay as before for now.

## What changed

### Parameters

`cad/params/default.csv` has new rows for the base size, the ramp (`ramp_r` 15, `ramp_x` 10), the
clamp (`clamp_h`, `clamp_top_gap`, `clamp_end_gap`, `clamp_edge_t`, `clamp_screw_inset`,
`clamp_screw_y0`, `clamp_screw_hole_d`, `clamp_boss_d`, `clamp_boss_drop`, `clamp_notch_d`), the
room round the bosses (`boss_gap`, `boss_pocket_extra`), the tapped hole depth, the strip pocket
width, the preload screw position and the strip slide (`strip_boss_slide`). The corner slot rows
are gone. The base, the clamp and the strip read these rows into their own `Params` sheet.

### Base

- Length, width and height now come from the parameters.
- Ramp: one sketch on the XZ plane, both ends, radius and tangent point from the parameters, no
  references to edges. It cuts across the whole width.
- Strip pocket: a plain rectangle, 186 mm wide, over the whole length. No ears, no corner holes.
- Magnets: two slots with round ends for the long strips only. The end legs, the short magnet
  frames and the fill at the preload screws are gone.
- Twelve pockets of 8.4 mm for the clamp bosses, 5.1 mm deep from the base top, with an M3 tapped
  hole 8 mm deep under each. The walls to the damper pockets are at least 2.35 mm.
- Frames `IF_clamp_start` and `IF_clamp_end` for the clamps.

### Clamp (new part `cad/parts/sealing-strip-clamp/`)

- The profile is rebuilt: underside radius = ramp radius + strip thickness, on the ramp centre.
  Every size links to the parameters. The six bosses, the M3 countersunk holes and the 9 mm hole
  over the preload screw link to them too. Frame `IF_base`.
- Volume 2711 mm³, about 3.4 g of PLA.

### Strip

- The build script now draws the ramp ends, the slots round the bosses (open at the strip end,
  0.2 mm room, 0.5 mm extra room towards the middle) and the preload holes cut square to the
  strip.
- The shape over the rollers is the same strip model as before. Its input length is the distance
  between the two preload screws, 427 mm, and that did not change. So the model was not run
  again.

### Assembly

- Two clamps on the base frames, twelve ISO 10642 M3 × 10 screws on the clamp countersinks.
- The four corner screws and the eight short magnets are removed.
- The preload screws had lost their joint edge. They now rest where their cone first touches the
  strip (head top at z = 41.69 mm).

### Records

Bill of materials: corner screws and short magnets removed, M3 clamp screws added, notes updated.
Architecture: new interface `StripClampInterface_v1`, new part `SealingStripClamp`, the short
magnet ports removed. The clamp is in `okh.toml`. Decision record:
[the end clamp decision](../decisions/2026-11-20_strip-held-by-an-end-clamp.md).

## Checks

- Every new or changed sketch is fully constrained. None of the new sizes is a typed number.
- Base, clamp and strip are each one valid solid. The flat strip and the bent strip differ by
  0.2 % in volume, within the known volume error of curved faces in FreeCAD.
- In the assembly: no overlap between strip, base and clamps. The clamp is 0.15 mm above the
  base. Each M3 screw overlaps its tapped hole by 11.4 mm³ (its thread, about 5.3 mm engaged)
  and the clamp by 0.19 mm³ (the edge of the drawn head).
- At both end stops, with the dampers fully compressed: the damper body stays 0.29 mm below the
  clamp and 0.12 mm below the strip. The outer rollers reach x = 9.17 mm, just past the start of
  the ramp, where the strip is 0.02 mm lower.
- Link test: with a ramp radius of 16 mm and a screw inset of 4.5 mm, the clamp still keeps
  0.15 mm above the base, and the screws move with the bosses. Values set back.
- `doqs check`: all gates pass. The new screw joints use edges, like the other screw joints in
  this assembly, and give the same warning.

## Open questions

- **Preload:** tilt the M4 screw square to the ramp, or use a larger strip hole with a larger
  offset (about 6 mm and 0.8 mm, with only about ±0.07 mm of margin), or another way to set the
  pull.
- **Rollers cut into the strip:** the strip shape is drawn for the carriage centre at x = 220 mm,
  but the carriage in the assembly is not held there. Left for later on purpose.
- The scraper study and the end-stop crash study still name the corner screw heads. They need a
  new run without them.
- The strip bends to radius 15 mm on the ramp: about 0.5 % strain at its surface, close to the
  yield of 0.15 mm EN 1.4310. It may take a small permanent bend there. This is not checked.

<details>
<summary>Technical notes</summary>

- All FreeCAD work went through `execute_code` in the open window, never `doqs wrap`.
- The first run of the strip build ran in the clamp window, because that window was active. The
  clamp file on disk was saved before, so the window was closed without saving and opened again.
  The strip window then would not recompute, and a save did not write. It was closed, opened
  again, and the build ran cleanly.
- `cad/params.csv` is a stale generated file that the strip build also reads. It still has the
  old corner slot rows; the build ignores them.
- `doqs generate` again added copyright lines to the licence files in `modules/stoq`. That folder
  is its own repository and is not part of this change.
- The DIN 7984 corner screws of
  [the earlier log of today](2026-11-20_strip-corner-screws-din7984.md) are removed by this change.
- Mistake rules checked: FreeCAD (only `execute_code`), PowerShell (all shell work in bash),
  tooling (`.agents/` and `doqs/` left as they are), sharp corners (the magnet slots have round
  ends).

</details>
