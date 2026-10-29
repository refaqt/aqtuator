# 2026-10-28 — Seal strip rollers on flanged ball bearings, in the assembly

**Role(s):** engineering, cad, architecture, purchasing

## Goal

Niels Bosmans asked for a simpler seal strip roller made of standard parts. The first hand sketch
had seven parts. After the friction check, he chose flanged ball bearings. Then he asked to log the
decision, select the parts, add them to the parts library (stoq) and add the rollers to the
assembly.

## Short answer

- **Decision:** each roller is a 2 × 28 mm dowel pin, two NSK F692ZZ flanged ball bearings, a
  sleeve we make from 10 × 2 mm tube, and two M2 washers. See
  [the decision](../decisions/2026-10-28_seal-strip-rollers-on-flanged-ball-bearings.md).
- **A plastic roller was rejected.** A MISUMI POM collar on the pin would add 35 to 52 N of drag at
  the default strip pull. The ball bearings add about 0.2 N.
- **The three bought parts are in stoq**, on branch `claude/seal-strip-roller-parts`, not yet
  merged. Each has our own model, drawn from the published sizes.
- **All eight rollers are in the assembly**, four in each carriage half. Nothing overlaps.
- **The axle slots are 1 mm deeper (5.5 mm).** The rollers now stick out 0.5 mm from each carriage
  half, as the seal strip page assumes. The roller pockets did not change.
- All work is on branch `ccr-48c26499-qjdbrs`, not yet merged.

## Work Done

### Friction

| At 54 N pull | Per roller | 8 rollers, POM collar | 8 rollers, ball bearings |
| --- | --- | --- | --- |
| Outer rollers (1 and 4) | 125 N | 30–45 N | |
| Inner rollers (2 and 3) | 20.5 N | 5–7 N | |
| **Total** | | **35–52 N** | **about 0.2 N** |

The roller forces come from the seal strip page. Each roller position has two rollers. The drag is
friction × force × 2 mm / 10 mm. POM-C friction 0.30–0.45 and PA6 0.40–0.60 come from the MCAM
datasheets. The ball bearing value of 0.0015 is the usual value for deep groove ball bearings.

### Parts

| BOM | Part | Qty | Where |
| --- | --- | --- | --- |
| MEC-002 | NSK F692ZZ, 2 × 6 × 3 mm, flange 7.5 × 0.8 mm | 16 | `stoq:nsk/miniature-flanged-metric#F692ZZ` |
| MEC-003 | Dowel pin ISO 8734, 2 (m6) × 28 mm, type A | 8 | `stoq:iso/iso-8734#2X28-A` |
| MEC-004 | Washer ISO 7092, size 2, A2 | 16 | `stoq:iso/iso-7092#2-200HV-A2` |
| — | Roller sleeve, tube 10 × 2 mm cut to 18.4 mm | 8 | our part, `cad/parts/roller-sleeve/` |

- The 2 mm axle was already in the CAD: the axle slot edge sits 1 mm from the roller centre.
- The longest pin that fits the 37 mm slot is 29 mm. The 28 mm pin keeps 0.5 mm at each end. Both
  axle screws still press on it.
- The roller is 20 mm over the two bearing flanges. With the washers it is 20.6 mm, in a 21 mm
  pocket. That leaves 0.4 mm of play along the axle.

### CAD

- **Roller sleeve:** a new part with a build script. Its sizes come from the new parameter file of
  the module. It has three frames: one in the middle and one on each end face.
- **Roller assembly:** a new sub-assembly with the sleeve, two bearings, two washers and the pin,
  held by fixed joints. Its frame `IF_axle` sits on the pin axis.
- **Carriage halves:** the axle slots are 5.5 mm deep (were 4.5 mm). The depth is a new value
  `axle_slot_depth` in the `Params` sheet of carriage-bottom, with its reason. carriage-top reads it.
  Each half lost 433.8 mm³. The screw holes moved down with the slot floor.
- **Carriage halves:** four new frames in each, `IF_roller_a_start` and so on, on the axle centre.
  They follow the roller and slot sketches. The frames are saved hidden, as the others are.
- **Assembly:** eight links to the roller assembly, each with a fixed joint from its carriage frame
  to `IF_axle`. No other part moved.

### Checks

- No roller overlaps any part. Each pin touches its slot. A bottom roller keeps 1.5 mm to
  carriage-top. A top roller keeps 1.19 mm to carriage-bottom and 5.3 mm to the base.
- The thinnest wall at the axle screw holes is 0.8 mm, the same as before the deeper slot. In
  carriage-top, 5 mm of material stays above the screw holes (was 6 mm).
- The 28 mm pin still fits: the slot is as long as before.
- The roller places match the seal strip page: x = 155.60 and 267.60 mm in carriage-bottom, x =
  118.77 and 304.44 mm in carriage-top.
- The carriage halves are each one valid solid. Apart from the deeper slots, the solids did not change.
- `bash doqs.sh check` passes in this repository and in stoq.

### Architecture

- New interfaces: roller mount (axle in the carriage slot), roller axis, bearing seat and washer
  face. Eight `SealRoller` parts in the stage, each made of a sleeve, two bearings, two washers and
  a pin.

## Decisions Made

- Niels Bosmans chose the flanged ball bearings over the plastic roller, to keep the friction low.
- Niels Bosmans approved NSK as the bearing brand, the A2 stainless washers and the 28 mm pin.
- Niels Bosmans chose to make the axle slots 1 mm deeper, so the rollers stick out 0.5 mm.

## Open Questions

- **The pin and the bearings are not stainless steel.** Check them for rust in coolant. ISO 8734
  type C1 is a stainless pin.
- **Does the 4.5 mm washer touch only the inner ring?** NSK gives no shoulder sizes for the F692ZZ.
- **The sleeve needs a fit for the bearings.** Ream the tube to 6 mm, then glue or press. The tube
  stock has no BOM row yet.
- The own models in stoq are not compared with a brand file or a real part yet.

## Next Steps

1. Merge the stoq branch first, then this branch. This branch points the stoq submodule at the
   stoq branch commit.
2. Open the assembly in the FreeCAD window and look at the rollers.
3. Add a BOM row for the tube stock of the sleeves.

<details>
<summary>Technical notes</summary>

- FreeCAD 1.1.3 from conda-forge, in the container. The files were last saved with 1.1.4. The
  edited files were saved by the FreeCAD GUI with an offscreen display, so `GuiDocument.xml` stays in
  each file. A headless save would drop it, and the FreeCAD window would open everything hidden.
- The container's locale is ASCII. FreeCAD then fails silently on the non-ASCII dash in the
  build-script template. All runs use `LANG=C.UTF-8 PYTHONUTF8=1`.
- Fixed joints line up the two frames with the same direction. When a joint allows two turns, the
  solver keeps the turn the part already has. The first roller build flipped one bearing and both
  washers. Each part now starts at its joint position before the joints are made.
- `validate_cad.py` resolves only the first name of a joint sub-path in the linked file. A joint to
  `pin.Frame.XY_Plane001.` inside the roller link was reported as ending on a link. So the roller
  assembly has its own frame, `IF_axle`, at its origin, on the pin axis.
- carriage-bottom frames: x `Sketch034.Constraints.roller_x` (or `w_carrier` minus it), y
  `Sketch034.Constraints.roller_y` (or `l_carrier` minus it), z `Sketch015.Placement.Base.z +
  Sketch015.Geometry[1].Radius * 1 mm` (slot floor plus pin radius, 24 mm). Turned 90° about Y.
- carriage-top frames: x `±Sketch001.Geometry[0].EndPoint.x * 1 mm`, y
  `±Sketch005.Constraints.roller_offset`, z `Pocket004.Length -
  carriage_bottom#Sketch015.Geometry[1].Radius * 1 mm` (3.5 mm). Turned −90° about X. Side a is
  y < 0 and start is x > 0, so the names match carriage-bottom.
- Roller assembly: sleeve grounded; `IF_seat` of each bearing on `IF_end_a` / `IF_end_b`;
  `IF_face` of each washer on `IF_flange_face`; pin `IF_centre` on sleeve `IF_centre`.
- `roller-sleeve/build_model.py` writes the module parameters into the `Params` sheet, because the
  scaffold sheet starts empty. A headless build leaves the document marked as changed, so each file
  was opened again, recomputed and saved with `cad_build.save()` before the fingerprint.
- New module parameter file `cad/params/default.csv`; `cad/params-table.csv` is generated from it.
- Fingerprints: carriage-bottom and carriage-top changed only their checksums, the audited count,
  and one bounding box value of 0.0006 mm (27.5006 → 27.5). In the assembly fingerprint, the damper
  bounding boxes changed by under 1 mm with the same centre of mass. This is a difference between
  FreeCAD 1.1.3 and 1.1.4. The added volume, 9 571 mm³, is eight rollers.
- Deeper slot: carriage-bottom `Params.axle_slot_depth` = 5.5 mm drives `Pocket005.Length`;
  carriage-top `Pocket004.Length` already reads `carriage_bottom#Pocket005.Length`. `Sketch015` sits
  on the slot floor, so it moved to z = 22 mm and the frames to z = 23 mm (bottom) and 4.5 mm (top).
  The rollers were started on the new frames and the assembly was solved again. No other part moved.
- Mistake rules checked: the fatigue mistake (no value without a source), the tooling update rule
  (submodules not put back), the wrap mistake (no FreeCAD window was open), the PowerShell rules
  (bash only).

</details>
