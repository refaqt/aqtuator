# 2026-09-16 — Checked every doqs template against this repository

**Role(s):** engineering, software

## What happened

The question was why `doqs/templates/cad/build_model.py` never appeared in this
repository. Nothing is broken: that file is not meant to be installed
automatically.

`doqs/scripts/install_root_tools.py` copies two groups of files, and
`build_model.py` is in neither:

- Root launchers: only `*.bat` and `*.sh` from `doqs/templates/<tool>/`, and
  never from `templates/setup-tooling/`. That gives us `syson.sh` and
  `syson.bat`.
- Agent configuration, copied once and never overwritten: `.mcp.json` and
  `.claude/settings.json`.

`templates/cad/build_model.py` is a **per-module seed**. A person copies it to
`modules/<module>/cad/build_model.py` and replaces its `build()` function with
real geometry, as described in `doqs/docs/agent-cad.md`. There is no single
correct place to put it, so no script puts it anywhere. This repository has no
CAD module yet — `modules/` is empty and `cad/` holds only a LICENSE and a
README — so there is nothing to seed.

Audit of every other template:

| Template | State here |
| --- | --- |
| `setup-tooling/setup-tooling.sh` / `.bat` | Identical to the template |
| `syson/syson.sh` / `.bat` | Identical to the template |
| `setup-tooling/gitattributes.snippet` | Covered by `*.sh text eol=lf` in `.gitattributes` |
| `setup-tooling/gitmodules.snippet` | `.gitmodules` matches it exactly |
| `agent-cad/claude-settings.json` | Deny rules present, next to the session hook |
| `agent-cad/mcp.json` | Written by the installer, kept local |
| `licensing/*` | `apply_licenses.py --check` reports ok |
| `data-index.csv` | All seven doqs columns present, plus our own |
| `cad/build_model.py` | Per-module seed; no CAD module exists yet |
| `measurement-case.md`, `measurement-summary.md`, `okh-module-with-parts.toml`, `variants/*` | Per-case and per-module seeds; used when we add one |

## Fixed

Documentation that still pointed at the old doqs layout. The FreeCAD skill and
the decision-record template moved to the agent kit, and the CAD tools moved
into `doqs/scripts/`:

- `cad/README.md` — FreeCAD skill link, `cad/sync_params.py` replaced by
  `doqs/scripts/cad_sync_params.py`, and a short section on seeding the first
  `build_model.py`.
- `.agents-local/rules/repo.md` — same two corrections, plus a row for
  `doqs/docs/agent-cad.md`.
- `docs/decisions/README.md` — template link now `.agents/templates/adr.md`.
- `docs/mistakes/README.md` — the entry format now lives in
  `.agents/skills/mistake-log/SKILL.md`; there is no `mistake-entry.md` any more.
- `docs/architecture.md` — two links pointed at a `dev-log/` folder that does
  not exist. The folder is `docs/log/`.
- `.cursor/rules/` — added the `freecad` and `doqs-naming` adapters from
  `.agents/templates/`. They were missing.
- `.gitignore` — added `.mcp.json`, so the file the installer writes stops
  showing up as an untracked change in every session.

Every markdown link in the repository now resolves, and
`python doqs/scripts/validate_all.py` passes.

## Decisions

No new decision record. The `.mcp.json` line is recorded in the consequences of
[2026-09-16_cloud-session-submodule-hook.md](../decisions/2026-09-16_cloud-session-submodule-hook.md),
which already said the file stays out of Git.

## Next Steps

Copy `doqs/templates/cad/build_model.py` into the first CAD module when the
actuator design starts, and run `python doqs/scripts/validate_cad.py` after it.
