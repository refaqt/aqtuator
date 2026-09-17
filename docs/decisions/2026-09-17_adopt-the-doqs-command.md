# 2026-09-17 — One doqs command, and the hook stays committed

- **Date:** 2026-09-17
- **Status:** Accepted

## Context

doqs was hard to use. Nineteen files under `doqs/scripts/` could be run, and nothing
said which one or in what order. The install story was told six times in four
wordings, and there was no canonical command list.

doqs now has one command and one page. This repository adopts both.

## Decision

**CI runs `python doqs/doqs.py check`.** That is the seven gates this repository
already ran, plus three checks that committed generated files are current
(`resolve_params --table --check`, `resolve_instance --check`,
`apply_licenses --check`). We ran it here before switching: all ten pass, so the
move needs no `doqs generate` first.

`doqs.sh` and `doqs.bat` are installed in the repository root, next to `syson.sh`.
They are doqs's files: `doqs setup` overwrites them when the template changes, so
never edit them here.

**`.claude/hooks/session-start.sh` stays committed.** The installer now ships that
hook as a template and keeps our copy up to date — the first run changed one comment
line. It is tempting to then delete our copy and let the installer provide it. That
would be wrong, and it is worth writing down why:

> A fresh cloud clone has an empty `doqs/`. The hook is what fills it. The installer
> can only run **after** `doqs/` exists. If the hook file were not in git, a fresh
> clone would have `.claude/settings.json` pointing at a file that is not there, the
> hook would do nothing, and we would be back to the silent failure of
> [2026-09-16](2026-09-16_cloud-session-submodule-hook.md).

So the file is committed **and** installer-managed: git provides it to a fresh clone,
and `doqs setup` keeps it current afterwards.

**`graph/usage-graph.json` is gitignored for now.** This repository has no modules, so
the generated graph is a single node with empty lists. Track it once `modules/` has
entries, and gate it then with `resolve_graph.py --check`.

## Consequences

- `doqs.sh check` before every commit; `doqs.sh generate` after changing parameters,
  a BOM, or adding a content folder; `doqs.sh list` when you forget a command.
- CI is stricter than before, by three checks. Both were verified green here first.
- `python doqs/scripts/validate_all.py` still works and still runs only the seven
  gates, so an old habit or an old script does not break.
- Three doqs scripts were renamed. Only one mattered here: `graph/README.md` named
  `build_graph.py`, which is now `resolve_graph.py`. The old names still work until
  16 December 2026, printing the new name and exiting 2.
- Two scripts still run **inside** FreeCAD and have no subcommand:
  `cad_sync_params.py` and the `build_model.py` rebuild through `FreeCADCmd`.
  `doqs.sh list` names them, so nobody looks for a command that cannot exist.

## Related

- `doqs/docs/using-doqs.md` — what to run, what doqs installs, what each gate checks
- `doqs/docs/migration-2026-09.md` — what changed for a machine repository
- [2026-09-16_cloud-session-submodule-hook.md](2026-09-16_cloud-session-submodule-hook.md)
