# 2026-10-07 — The rails are in the compact-stage assembly

**Role(s):** cad

## Goal

Put the two HIWIN HGR15 linear guide rails into the compact-stage assembly, on the mounting frames
that the base got on 6 October.

## Work Done

- **Niels placed both rails in the assembly in the FreeCAD window.** Each rail is HGR15R418H, 418 mm
  long.
- **The rails sit where the base expects them.** Their centres are at y = 41 mm and y = 169 mm,
  the same as the two hole rows in the base. They stand on the pocket floor at z = 10 mm. They are
  centred along the 440 mm base, with 11 mm free at each end.
- **The stored measurements (fingerprints) of the assembly and the base are up to date again.**
  The shape of the base did not change. It was only saved again.

- **aqtuator now uses the newest stoq library.** The HIWIN HGL15 block has its own coordinate
  system (a rail frame) and the colours from the original STEP file. Running `setup-tooling` did not
  bring this in, because aqtuator records one fixed stoq commit. That is on purpose: a library change
  must not reach the machine unless someone records it. The record moved from `2fe6cb5` to
  `bf9eec5`.

## Decisions Made

None.

## Next Steps

1. Add the carriages (the blocks that run on the rails) to the assembly.
2. Commit the rail file in the stoq library if its change is wanted (see the technical notes).

<details>
<summary>Technical notes</summary>

- Fingerprints were written with `freecadcmd` and `doqs/scripts/cad_fingerprint.py` `write()` on the
  saved files. The documents were closed without saving. The `.FCStd` hashes were the same before
  and after.
- The models have no `build_model.py`, so a rebuild was not possible and not wanted: it would have
  lost the work done in the window.
- `validate_cad.py` passes for compact-stage. 29 warnings remain about sizes that are typed in and
  not linked to the Params sheet. They were there before.
- `modules/stoq/modules/hiwin/modules/hgr-rail/cad/parts/HGR15R418H.FCStd` also changed on disk,
  probably when the assembly was saved. It belongs to the stoq repository and is not in this commit.
  Later the same day, this local change was stashed in `modules/stoq` (with the deleted
  `HGL15CA2R760ZBC2-ZZ+E2.step`) before the move to `bf9eec5`. It is still in `git stash list`
  inside `modules/stoq`.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  (the tooling folders were left as they are).

</details>
