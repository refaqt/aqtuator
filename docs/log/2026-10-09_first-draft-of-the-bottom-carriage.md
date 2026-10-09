# 2026-10-09 — First draft of the bottom carriage

**Role(s):** cad

## Goal

Draw a first version of the bottom carriage of the compact stage. The bottom carriage is the plate
that sits on the four rail blocks and carries the top carriage.

## Work Done

- **Niels drew a first draft of the bottom carriage.** It is a plate of 190 × 170 × 15 mm. It has
  holes for the rail blocks and holes for the top carriage.
- **The start and the end of the plate are sloped.** Niels chose this to make the plate stiffer.
- **The plate has tabs on its sides, also for stiffness.** The tabs do not work yet. Their screws
  go in from below, and nobody can reach that side once the carriage sits on the rails.
- **The carriage is in the assembly, but it is not fixed to anything yet.** It sits at the origin
  of the assembly. Two rail blocks on one rail were moved along their rail. The other parts did not
  move.
- **The fingerprints of the carriage, the base and the assembly are up to date.** The project
  checks pass.

## Open Questions

- How should the side tabs be screwed, so that the screws can be reached from above or from the
  side? Some options: screw in from the top through the tab, screw in sideways, or put the thread
  in the tab and the screw head on the other part. Niels decides.

## Next Steps

1. Change the side tabs so their screws can be reached.
2. Add mounting frames to the carriage and fix it to the four rail blocks in the assembly.
3. Choose the material, and check the mass and the stiffness of the plate.

<details>
<summary>Technical notes</summary>

- Carriage features: `Pad` (15 mm, `Sketch`), `Pad001` (2 mm, `Sketch006`, the side tabs),
  `Pocket` (`Sketch005`, through all), `Pocket001` (`Sketch003`, through all, reversed, the sloped
  ends), `Hole` (4.5 mm, `Sketch001`), `Hole001` (3.4 mm, `Sketch007`), `Hole002` (3.3 mm,
  `Sketch008`, 30 mm pitch, the top interface).
- Volume of the finished body: 375 797 mm³. In aluminium (2.7 g/cm³) that is about 1.0 kg. The
  material is not chosen yet.
- Assembly: link `carriage-bottom` at placement (0, 0, 0), no joint. `HGL15CAZBC+E2` and
  `HGL15CAZBC+E001` moved along their sliders: x from 62.6 to 14.1 mm and from 168.3 to 121.0 mm
  (bounding box minimum).
- The base `.FCStd` changed on disk but its geometry did not. Only the file hash in its fingerprint
  changed.
- Fingerprints were written with `freecadcmd` 1.1.4 and `cad_fingerprint.write()` after
  `purgeTouched()`. The documents were closed without saving, and the `.FCStd` hashes stayed the
  same. The FreeCAD window was not running, so there was no unsaved work.
- `bash doqs.sh check`: all gates passed. 24 typed-in sizes in the carriage are not yet linked to a
  parameter.
- `modules/stoq` still has local changes to two HIWIN part files. They were there before this work
  and are not part of this commit.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md) (the tooling
  folders were left as they are).

</details>
