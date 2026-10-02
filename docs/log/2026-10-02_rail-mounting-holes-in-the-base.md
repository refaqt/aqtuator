# 2026-10-02 — The base has mounting holes and alignment tabs for the guide rails

**Role(s):** cad, architecture

## What happened

The base of the compact stage now has threaded holes for the two guide rails, and short tabs that
align them. The base is now 440 mm long instead of 420 mm, and the floor for the rails is 420 mm
long. The HIWIN rail from the parts library is 418 mm long, so it fits with 1 mm free at each end.

One rail is the reference rail. It lies against two tabs, one near each end. The tabs set both its
position and its direction. The second rail lies against one tab, near its left end. Its direction
is set during assembly. The carriage goes on both rails and moves from end to end while the screws
of the second rail are tightened one after the other. The HIWIN catalogue describes this method as
"alignment on the reference rail".

The tabs stand out from the side walls of the base, and each rail touches them with its outer side.
Each tab is 20 mm long and starts 19 mm in from the end of the rail, so no tab touches a rail end.
The rounded corners at the foot of each tab stay 4.5 mm away from the rail.

The two low ribs between the rail floors and the motor floor are gone. All three floors were at the
same depth, and the ribs no longer guided anything, because the motors are aligned with pins. With
the ribs, the rounded corner at each end of the lower rib would have touched the rail ends, or the
rib would have been only 1 mm thick. Now the inner side of each rail touches nothing.

The guide rails and their interface to the base are now in the stage architecture.

## Decisions

- **Reference rail on two tabs, second rail on one tab.** Two tabs fix the reference rail fully.
  One tab fixes only one end of the second rail, so the carriage can set the second rail parallel
  to the first. A full reference face would fight the carriage.
- **Tabs on the outer side, at the side walls.** The rounded corners that the cutter leaves sit at
  the wall, away from the rail, and the tabs stay clear of the rail ends.
- **No ribs between the rail floors and the motor floor.** This removes every corner near the
  inner side of the rails. The motor floor did not move.
- **Threaded holes go through the 10 mm floor, and the rails use M4 x 16 screws.** HIWIN lists
  M4 x 20 for this rail, but that screw would come out of the bottom face by 0.3 mm. An M4 x 16
  screw stays inside and engages 6.3 mm of thread.

## Open Questions

- Is 6.3 mm of thread enough in the base material? This depends on the material, which is not
  chosen yet.
- The stage length requirement allows (travel + 340 mm − 2 × height). The longer base uses more of
  that allowance. Check it again when the travel and the height are known.

## Next Steps

- Model the pin holes for the linear motors.
- Add the guide blocks to the architecture, with their interface to carriage-bottom.

<details>
<summary>Technical notes</summary>

- Rail data from the HIWIN catalogue `GW-13-1-EN-2606-K`, table 3.9 (HGR15R: WR 15, HR 15,
  D 7.5, h 5.3, d 4.5, P 60, end distance 6 to 53 mm) and table 3.18 (HG15 shoulder height 3.0 mm
  for the rail, H1 4.3 mm). The catalogue is in `modules/stoq/modules/hiwin/docs/datasheets/`.
- `BlockSketch` constraint `Length`: 420 → 440 mm. The pockets follow, because they keep 10 mm
  from each end.
- `Sketch001` is now one closed outline: the main pocket outline with three tabs, fully
  constrained. Named constraints: `tool_radius` 6, `tab_inset` 20 (from the pocket end to the tab),
  `tab_length` 20, `second_rail_tab_depth` 10.5, and the same values for the two reference tabs
  (`ref_tab_left_*`, `ref_tab_right_*`). Tab faces at y = 33.5 and y = 176.5. Tabs at x = 30 to 50
  and x = 390 to 410.
- `Sketch002` and `Pocket002` (the motor floor) are removed. `Pocket001` now cuts that area too.
- The old `Sketch001` used open outlines that relied on six of its external edges being
  "defining" geometry, a FreeCAD 1.1 option. A new closed outline then overlapped them, and the
  pocket failed with "Wire is not closed". The external edges were added again as construction
  references with `addExternal(obj, sub, False, False)`.
- A corner arc that meets a wall line at its lowest or highest point is tangent to that line. A
  plain `Coincident` there leaves the solver unsure. `Tangent` endpoint-to-endpoint fixes it.
- `RailHoleSketch` on `XY_Plane` with a 10 mm offset, and `RailHoles` (PartDesign Hole,
  `M4x0.7`, through all, cosmetic thread). Named constraints: `first_hole_x` 40, `hole_pitch` 60,
  `reference_rail_y` 169, `second_rail_y` 41. Hole centres at x = 40 to 400.
- Fit check on a 418 × 15 × 3 mm rail footprint, centred: no overlap with the base. A probe moved
  0.05 mm outwards meets material only at the tabs. A probe moved 0.05 mm inwards meets nothing.
- `delGeometries()` with a list removed more constraints than expected. Deleting one element at a
  time with `delGeometry()` works. Line-to-line `Distance` to external geometry gave solver code −5
  (malformed). `DistanceY` between two points works.
- FreeCAD hung on `doc.save()` through the bridge and then crashed, so the first build was lost
  and was built again from the same steps. After the restart, `doc.save()` failed with "file is
  marked as read-only", although the file was writable. FreeCAD itself held a lock on the file.
  The fix was `saveCopy()` to a new file, closing FreeCAD completely, and moving the copy into
  place. After a clean restart, `doc.save()` worked again.
- `base.FCStd` is about 0.9 MB instead of 70 kB, also after a normal save. The cause is not
  checked.

</details>
