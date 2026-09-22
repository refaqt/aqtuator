# 2026-09-22 — The first step always runs now

**Role(s):** engineering, software

## What happened

A cloud session opened this repository together with doqs and refaqt-agents. The tooling
folders stayed empty for the whole session, and nothing said so. The `SessionStart` hook
that fills them never started.

The cause is a rule that is easy to miss: Claude Code reads `.claude/settings.json` from
the session's own project folder only. A session with several repositories opens the folder
above them, so this repository's hook entry was never read. The network was fine. Nothing
was broken; nothing ran. `git submodule status` showed a leading `-` on all three
submodules.

Under that sat a second fault. The hook's first line trusted `$CLAUDE_PROJECT_DIR`, which
in that layout holds the parent folder. Even a hook that started would have moved to a
folder that is not a repository and failed on every git call, without saying which folder
it used.

## What changed

- `CLAUDE.md` grew from one line into the first step: look for `.agents/rules/core.md` and
  `doqs/scripts/validate_all.py`, and run `bash setup-tooling.sh` when either is missing.
  Claude Code reads `CLAUDE.md` from **every** repository a session attaches, so this step
  works where the hook cannot.
- `AGENTS.md` leads with the same check and says plainly when the hook runs and when it
  does not.
- `.claude/hooks/session-start.sh` now finds the repository root from its own place on
  disk, checks it is a git work tree, and names it in every message. The file comes from
  doqs and was taken byte for byte from its template, as the installer would write it.
- `.cursor/README.md` no longer says cloud agents need no setup step.
- New decision record and a mistake entry.

## What did not change

`setup-tooling.sh` and `setup-tooling.bat` are untouched. They already find their own
folder, so they work from any working directory. They were never the fault: nothing called
them.

## What this means for the next session

Open one repository per cloud session. That way the hook runs, and the FreeCAD guard in
`.claude/settings.json` is switched on as well; in a session with several repositories that
file is never read, so the guard is off. Work on doqs or the agent kit still happens from
the submodule folders: branch first, because `HEAD` is detached after a submodule update.

## Related

- [The first step lives in CLAUDE.md](../decisions/2026-09-22_first-step-lives-in-claude-md.md)
- [The start-up hook never ran, and said nothing](../mistakes/2026-09-22_the-hook-never-ran-and-said-nothing.md)
