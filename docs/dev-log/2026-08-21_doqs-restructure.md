# 2026-08-21 — doqs restructure

## Goal

Finish moving the repository onto the doqs layout, so that the specification lives in one place
(the `doqs` submodule) and this repo only holds project content that follows it.

## Work Done

- Merged `refactor/doqs-layout` (PR #5). The restructure is complete.
- `doqs` is in as a submodule at `doqs/`, pinned to `379c8e5` (`docs(architecture): add measurement/
  and software/ with external-data manifests`).
- Moved the code into the doqs module layout: `firmware/`, `software/`, `simulation/` at top level,
  alongside `architecture/`, `cad/`, `measurement/`, `modules/`, `bom/`, `builds/`, `manufacturing/`.
- Converted the Word project log to 71 markdown entries under `docs/dev-log/`. Git is the source of
  truth for the log now, not the Google Doc.
- Split the living docs and added agent entry points (`AGENTS.md`, `docs/onboarding.md`), and dropped
  the local copy of the measurement data.
- Indexed 1.88 GB of measurement data held on Google Drive into `measurement/data-index.csv`, then
  widened it to index the whole testing root rather than a single campaign.
- Pointed the Cursor agent rules at the new docs layout.

## Decisions Made

- Measurement data stays out of git and lives on Google Drive; the repo carries only the manifest.
  LFS is scoped to CAD.
- The doqs spec is consumed as a submodule at a pinned commit rather than vendored, so spec changes
  land as a deliberate pointer bump.

## Next Steps

- [ ] Keep `measurement/data-index.csv` rebuilt as new captures land.
