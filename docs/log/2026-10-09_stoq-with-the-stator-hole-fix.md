# 2026-10-09 — aqtuator uses the stoq version with the stator hole fix

**Role(s):** cad

## Goal

Move aqtuator to the newest stoq parts library. This was the first next step in
[the stators log](2026-10-07_stators-in-the-compact-stage-assembly.md).

## Work Done

- **aqtuator now uses the stoq version with the MK2 stator fix**
  ([refaqt/stoq#11](https://github.com/refaqt/stoq/pull/11), merged). The stoq parts table now says
  the stator holes are 60 mm apart, not 120 mm.
- **The stators show again when the FreeCAD window opens the assembly.** The stator files in stoq
  now have view data.
- **The stator shape and its mounting frame did not change.** The stators keep their place in the
  compact-stage assembly.

## Next Steps

1. Model the locating pin holes for the stators.
2. Choose the screws for the stators.

<details>
<summary>Technical notes</summary>

- stoq moved from `14fe9b1` to `a79713e`.
- `modules/stoq` had local changes to three part files: `HGL15CAZBC+E2.FCStd`,
  `HGR15R418H.FCStd` and `MK2-180.FCStd`. They held only FreeCAD save changes: time stamps, shown
  and hidden state, and view data. No shape changed. They are kept in a stash in `modules/stoq`
  ("FreeCAD save noise before stoq update 2026-10-09"), not deleted.
- `bash doqs.sh check` passes.
- Mistake rules checked: [reverted the tooling update](../mistakes/2026-09-22_reverted-the-tooling-update.md)
  (the tooling folders were left as they are), and the PowerShell rules (all shell work ran in
  bash).

</details>
