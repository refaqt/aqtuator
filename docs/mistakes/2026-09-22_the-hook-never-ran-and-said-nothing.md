# 2026-09-22 — The start-up hook never ran, and said nothing

**What happened:** A cloud session opened aqtuator, doqs and refaqt-agents together.
`.agents/`, `doqs/` and `modules/stoq/` were all empty for the whole session. Nothing on
screen said so. The `SessionStart` hook that exists to fill them printed no line at all,
and an agent reading `AGENTS.md` would have followed links into folders with no files in
them.

**Root cause:** Claude Code reads `.claude/settings.json` from the session's own project
folder only. A session that attaches several repositories opens the folder **above** them,
which in this case was `/home/user`. There is no settings file there, so this repository's
`SessionStart` entry was never read and the hook was never started. The network was fine:
`git ls-remote` reached all three remotes. Nothing was broken. Nothing ran.

The hook had a second fault underneath. Its first line was
`root="${CLAUDE_PROJECT_DIR:-...}"`, and in that layout the variable holds the parent
folder, which is not a git repository. Even a hook that did start would have failed on
every git call, without naming the folder it had used.

**Why it was missed:** silence looked the same as success. A hook that works prints one
line; a hook that never runs prints nothing. Nobody checks for a line that is not there.
[The 2026-09-16 decision record](../decisions/2026-09-16_cloud-session-submodule-hook.md)
warned that "the folders exist, they are simply empty", and then trusted the one mechanism
that cannot run in this layout.

**Fix applied:**

- `CLAUDE.md` now opens with the check, because Claude Code reads that file from every
  repository a session attaches, while it reads settings from one folder only.
- `AGENTS.md` leads with the same check and says when the hook does and does not run.
- The hook finds the repository root from its own place on disk (owned by doqs; this
  repository receives the file).
- One repository per cloud session is now the stated layout. See
  [the decision record](../decisions/2026-09-22_first-step-lives-in-claude-md.md).

**Prevention rule:** Never treat a start-up hook as proof. Check the marker files
yourself, before anything else:

```bash
ls .agents/rules/core.md doqs/scripts/validate_all.py
```

A hook that does not run prints nothing, which looks exactly like a hook that has nothing
to report. The same rule holds for any tool that is supposed to run for you: prove the
result, do not read the absence of a message as good news.

**Affected files:** [`CLAUDE.md`](../../CLAUDE.md), [`AGENTS.md`](../../AGENTS.md),
[`.claude/hooks/session-start.sh`](../../.claude/hooks/session-start.sh),
[`.cursor/README.md`](../../.cursor/README.md),
[`docs/decisions/2026-09-22_first-step-lives-in-claude-md.md`](../decisions/2026-09-22_first-step-lives-in-claude-md.md)
