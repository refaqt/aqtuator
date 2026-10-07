# 2026-10-07 — The rail blocks are in the compact-stage assembly

**Role(s):** cad

## Goal

Put the blocks that run on the guide rails into the compact-stage assembly. This was the next step
in [the rails entry](2026-10-07_rails-in-the-compact-stage-assembly.md).

## Work Done

- **Niels placed four HIWIN HGL15 blocks in the assembly.** Each rail carries two blocks.
- **The stored measurements (fingerprints) of the assembly and the base are up to date again.**
  The assembly and the base were saved again in the FreeCAD window, so the old measurements did not
  match the files any more.

## Decisions Made

None.

## Next Steps

1. Check that the blocks sit at the right distance from each other and from the carriage plates.
2. Connect the carriage plates to the blocks.

<details>
<summary>Technical notes</summary>

- The new links are `HGL15CAZBC_E2` and `HGL15CAZBC_E001` to `HGL15CAZBC_E003`. Their placements
  are at z = 10 mm, on the rail centre lines y = 169 mm and y = 41 mm.
- Fingerprints were written with `freecadcmd` and `doqs/scripts/cad_fingerprint.py` `write()`,
  after `purgeTouched()`. The documents were closed without saving. The `.FCStd` hashes were the
  same before and after.
- `base.FCStd` grew from 127 KB to 1.8 MB, and the assembly from 24 KB to 224 KB, when saved from
  the window. The cause is not checked.
- `validate_all.py` passes. 29 warnings remain about typed-in sizes in the base. They were there
  before.
- `modules/stoq` shows a local change (a dirty marker). It is not part of this commit.

</details>
