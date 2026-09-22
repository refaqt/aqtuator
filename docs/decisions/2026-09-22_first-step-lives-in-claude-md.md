# 2026-09-22 — The first step lives in CLAUDE.md

- **Date:** 2026-09-22
- **Status:** Accepted

## Context

[The 2026-09-16 record](2026-09-16_cloud-session-submodule-hook.md) added a `SessionStart`
hook so a cloud session would fill `.agents/` and `doqs/` before an agent read anything. It
assumed the hook always starts. It does not.

A cloud session on 2026-09-22 opened three repositories at once: aqtuator, doqs and
refaqt-agents, as sibling folders. Claude Code then opens the folder **above** them as the
session's project folder, and reads `.claude/settings.json` from that folder only. There is
no settings file there, so the `SessionStart` entry in this repository was never read, the
hook never started, and it printed nothing at all:

```
$ git submodule status
-58fd8512... .agents
-4decc8aa... doqs
-7043e422... modules/stoq
```

Every folder empty, network working, nothing on screen. The 2026-09-16 record named this
exact shape of failure — "the folders exist, they are simply empty" — and then relied on the
one mechanism that cannot run in it.

One thing did work. Claude Code reads `CLAUDE.md` from **every** repository a session
attaches. Both `aqtuator/CLAUDE.md` and `doqs/CLAUDE.md` reached that session's context.
Settings come from one folder; `CLAUDE.md` comes from all of them.

The 2026-09-16 record also foresaw the weakness of the other route: "`AGENTS.md` tells agents
to run `bash setup-tooling.sh` as the first step, but an agent that never read the rules has
no reason to." `CLAUDE.md` closes that gap, because an agent does not have to go looking for
it.

## Decision

1. `CLAUDE.md` grows from one line into the first step. It names the two marker files,
   `.agents/rules/core.md` and `doqs/scripts/validate_all.py`, and says to run
   `bash setup-tooling.sh` when either is missing. The file stays short: it enters the
   context of every session.
2. `AGENTS.md` leads with the same check, and says plainly when the hook runs and when it
   does not. "Usually fills those folders" is gone.
3. The hook finds the repository root from its own place on disk, so a wrong
   `$CLAUDE_PROJECT_DIR` cannot send it outside the repository. That change is owned by
   doqs; this repository receives it in `.claude/hooks/session-start.sh`.
4. **One repository per cloud session** is the layout to use for work on AQTUATOR. Attach
   only `refaqt/aqtuator`. `doqs/` and `.agents/` then arrive as submodules, at the paths
   this guide already names.

## Consequences

The failure is no longer silent. In a session where the hook cannot run, the first command an
agent runs is the check, and the check fails loudly.

Point 4 also fixes something the 2026-09-16 record never mentioned. The `permissions.deny`
entries for `mcp__freecad__execute_code_headless` and `mcp__freecad__reload_document` live in
the same `.claude/settings.json` that a multi-repository session never reads. In that layout
the FreeCAD guard is off. Only the one-repository layout switches it back on.

Work on doqs or refaqt-agents from a one-repository session still works. A submodule work
tree is a full repository, but `HEAD` is detached after `git submodule update`, so branch
first: `git -C doqs switch -c <branch> origin/main`, commit, then
`git -C doqs push -u origin <branch>`. This repository's own record of the tooling version
stays where it is, and `git status` no longer mentions it. See
[Hide the tooling gitlinks from `git status`](2026-09-22_hide-the-tooling-gitlinks.md).

The other layout stays possible. Keep several sources, and put `bash aqtuator/setup-tooling.sh`
in the cloud environment's own setup script. The cost is two checkouts of doqs and of the kit
in one session, and it is easy to read one copy and change the other. That is why it is not
the default.

## Related

- [A session hook checks out the tooling submodules](2026-09-16_cloud-session-submodule-hook.md)
- [The start-up hook never ran, and said nothing](../mistakes/2026-09-22_the-hook-never-ran-and-said-nothing.md)
- doqs: [The session hook finds its own repository](https://github.com/refaqt/doqs/blob/main/docs/decisions/2026-09-22_hook-finds-its-own-root.md)
