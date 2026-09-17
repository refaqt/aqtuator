# 2026-09-17 — aqtuator moved to the one doqs command

**Role(s):** engineering, software

## What happened

The doqs clean-up is merged: five pull requests, from fixing wrong documentation to
one command, one page, and three renames. This repository now uses it.

- **CI runs `python doqs/doqs.py check`.** That is the seven gates we already ran,
  plus three checks that the committed generated files are current. We ran it here
  first: all ten pass, so no `doqs generate` was needed.
- **`doqs.sh` and `doqs.bat`** are in the repository root, installed by
  `doqs setup` next to `syson.sh`. They are doqs's files, not ours.
- **`.claude/hooks/session-start.sh`** gained one line from the template, the comment
  that now points at `doqs/docs/using-doqs.md`.
- `.agents-local/rules/repo.md` and `cad/README.md` use the new commands, and say
  which scripts stay manual because they run inside FreeCAD.
- `graph/README.md` named `build_graph.py`, renamed to `resolve_graph.py`.
- `.gitignore` lost `**/bom/bom_output.md`, left over from `process_bom.py` — a
  script that never existed in doqs, and which its documentation printed three times.
- The `doqs` pin moved from `65ef08c` to `ac186ae`.

## The plan said to delete the hook. That was wrong.

`doqs setup` now installs `.claude/hooks/session-start.sh` from a template and keeps
it current. The obvious next step is to delete our committed copy and let the
installer own it.

That would have reintroduced the exact bug the hook was written to fix. A fresh cloud
clone has an **empty** `doqs/`, and the hook is what fills it. The installer can only
run after `doqs/` exists. With no committed hook, a fresh clone would have
`.claude/settings.json` pointing at a missing file, the hook would do nothing, and an
agent would again read no rules and no specification, silently.

So the file is committed **and** installer-managed: git gives it to a fresh clone,
and `doqs setup` keeps it up to date afterwards. Written down in
[the decision record](../decisions/2026-09-17_adopt-the-doqs-command.md), because it
is exactly the kind of tidy-looking change someone will propose again.

## `graph/usage-graph.json` stays ignored

`doqs generate` writes it. We ran it to see what it holds today: one node, with empty
lists, because this repository has no modules. Committing that is noise. The
`.gitignore` entry says to track it once `modules/` has entries, and to gate it then
with `resolve_graph.py --check`.

## Checks

```
python doqs/doqs.py check      # ok, all gates passed (ten of them)
python doqs/doqs.py setup      # writes nothing new on a second run
bash .claude/hooks/session-start.sh
```

## Next Steps

qarve is the remaining consumer. It needs a desktop session with FreeCAD: its CAD
gate fails 45 times because 44 FreeCAD files have no fingerprint, and only FreeCAD
can write one. Its CI also calls `build_graph.py`, which needs the new name.
