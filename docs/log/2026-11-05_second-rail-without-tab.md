# 2026-11-05 — The second guide rail has no alignment tab now

**Role(s):** cad, architecture

## What happened

The base of the compact stage had three alignment tabs for the two guide rails. The reference
rail lies against two tabs. The second rail lay against one tab, near its left end.

The second rail is set parallel to the reference rail with the carriage, during assembly. So the
tab and the carriage both tried to set the position of the second rail at that end. The rail had
one constraint too many. Niels asked to remove that tab. It is now gone.

The reference rail keeps its two tabs. Nothing else in the base changed.

## Decisions

- **No tab at the second rail.** The carriage alone sets the position and the direction of the
  second rail ("alignment on the reference rail" in the HIWIN catalogue). The decision of
  2026-10-02 to keep one tab there is replaced.

## Next Steps

- None for the base. When the assembly instructions are written, they must say that the second
  rail has no stop: hold it near its line by hand until the carriage sets it.

<details>
<summary>Technical notes</summary>

- `Sketch001` of `base.FCStd`: the tab geometry (arc, three lines, arc) and the wall line after it
  are removed. The wall line at y = 17 mm now runs from x = 10 to x = 430 mm, tangent to the
  corner arcs at both ends. Its `Horizontal` constraint was removed, because the two end tangents
  already set its direction. The sketch is fully constrained, with one closed wire.
- Constraints `tab_inset`, `tab_length` and `second_rail_tab_depth` (with its expression) are
  gone. `tool_radius` (6 mm) moved from the old tab arc to the arc at the left end of that wall.
  All other corner arcs are `Equal` to it.
- Volume 1 388 037 → 1 387 301 mm³. Faces 231 → 225. The body is valid.
- External references of the later sketches (`Sketch002` to `Sketch007`) were measured before and
  after. They all point at the same edges. FreeCAD renamed `Pocket004` `Edge523` to `Edge514` in
  `Sketch007` by itself; it is the same wall edge (y = 193 mm, z = 39.35 mm).
- Probe check with a 418 × 15 × 2.5 mm rail footprint, moved 0.05 mm each way: the second rail
  meets no material on either side. The reference rail meets only its two tabs (5 mm³).
- The fingerprint was written in the FreeCAD window with `cad_fingerprint.write()` after the save.
  `doqs.sh check` passes the base and the assembly. `validate_names.py` fails, but it fails on
  `main` too: a Windows `charmap` encoding error in the script.
- Mistake rules checked: the FreeCAD work used `execute_code` on the main thread, not `doqs wrap`
  ([wrap crashed FreeCAD](../mistakes/2026-10-22_wrap-crashed-the-open-freecad.md)). Shell work ran
  in bash (the PowerShell rules).

</details>
