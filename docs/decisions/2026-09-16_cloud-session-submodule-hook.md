# 2026-09-16 — A session hook checks out the tooling submodules

## Context

This repository mounts two tooling submodules: [doqs](https://github.com/refaqt/doqs)
at [`doqs/`](../../doqs/) and [refaqt-agents](https://github.com/refaqt/refaqt-agents)
at [`.agents/`](../../.agents/). Both gitlinks are committed, but a cloud session
clones the repository without `--recurse-submodules`, so both folders start empty:

```
$ git submodule status
-be3211364083577f243a366115033c38f43e0d39 .agents
-9279f99e64da8202711c802e2c3223c97ae47028 doqs
```

The leading `-` means "not checked out". An agent then cannot read
`.agents/rules/*.md` or `.agents/skills/*`, cannot read
`doqs/docs/architecture.md`, and cannot run `python doqs/scripts/validate_all.py`.

The failure is quiet, which is the worst part. The folders exist. They are simply
empty. An agent that does not look reads no rules and keeps working.
[`AGENTS.md`](../../AGENTS.md) tells agents to run `bash setup-tooling.sh` as the
first step, but an agent that never read the rules has no reason to.

doqs solved the same problem for itself in
[`doqs/docs/decisions/2026-09-16_agent-kit-session-hook.md`](../../doqs/docs/decisions/2026-09-16_agent-kit-session-hook.md).
This repository needs the same thing for two submodules rather than one.

## Decision

Add a `SessionStart` hook at the repository root.

1. [`.claude/settings.json`](../../.claude/settings.json) registers the hook.
2. [`.claude/hooks/session-start.sh`](../../.claude/hooks/session-start.sh) runs
   the same two git calls as [`setup-tooling.sh`](../../setup-tooling.sh).
3. [`.cursor/environment.json`](../../.cursor/environment.json) runs that same
   script, so Cursor cloud agents get the same result from one implementation.

The hook runs in every session, local and cloud. The problem is a clone without
submodules, and that can happen anywhere.

The hook is synchronous, not async. An agent reads `.agents/rules/core.md` as its
first step, so the files must be on disk before the turn starts. The download
takes a few seconds.

## Why two git calls, in this order

```bash
git submodule update --init --recursive        # every submodule at its recorded pin
git submodule update --remote -- doqs .agents  # tooling submodules track main
```

The first call must not use `--remote`: extracted machine modules under
`modules/` stay SHA-pinned, and `--remote` on a submodule without `branch` moves
it to the remote default branch instead.

The second call must not use `--recursive`: it would reach `doqs/.agents` and
move it off the pin doqs records.

## Why no `--checkout`

The doqs hook needs `--checkout` because doqs sets `update = none` on its own
nested `.agents`, and without the flag git prints `Skipping submodule`, exits 0,
and downloads nothing.

This repository sets `update = none` on neither tooling submodule, so the flag
changes nothing here. We tested whether it would mount the kit twice by reaching
`doqs/.agents` through `--recursive`, and it does not — git honours the nested
`update = none` while recursing, and the folder is never created:

```
$ git submodule update --init --recursive --checkout
Submodule path '.agents': checked out 'be32113...'
Submodule path 'doqs': checked out '9279f99...'
$ ls -A doqs/.agents
ls: cannot access 'doqs/.agents': No such file or directory
```

The flag is therefore left out, so the hook and `setup-tooling.sh` run the same
two commands. One behaviour, not two.

## Why the marker file and not the exit code

`git submodule update` can print `Skipping submodule`, exit 0, and leave a folder
empty. An exit code on its own proves nothing. The hook checks for
`.agents/rules/core.md` and `doqs/scripts/validate_all.py` and reports on those.

## No network

The hook must never stop a session. It uses `set -uo pipefail` without `-e`,
captures the output of git, and always exits 0. Without a network it prints what
git said, says the rules and validators are missing, and repeats the command to
run by hand. `GIT_TERMINAL_PROMPT=0` stops git from waiting for a password, and
`timeout` stops a dead network from holding the session open.

## Why the FreeCAD guard shares the settings file

`doqs/scripts/install_root_tools.py` installs `.claude/settings.json` from
`doqs/templates/agent-cad/claude-settings.json` **copy-once**: it skips a file
that already exists. Creating that file for the hook alone would permanently
block the agent-CAD deny rules from ever being installed, and `validate_cad.py`
fails CI on the commit that adds the first `.FCStd`. Both concerns therefore live
in one file: `hooks` for the session start, `permissions.deny` for the guard.

## Consequences

- A session starts with both submodules on disk, or with a clear message saying
  why not.
- `--remote` moves the `doqs` and `.agents` gitlinks to the latest `main`, so
  `git status` shows two modified submodules in most sessions. That is the
  behaviour `AGENTS.md` already describes: leave the moved gitlinks uncommitted
  unless you mean to set a new pin.
- `.mcp.json` is deliberately **not** committed. The next local
  `bash setup-tooling.sh` run writes it as an untracked file, because
  `install_root_tools.py` installs it copy-once. It registers the FreeCAD MCP
  server (`uvx freecad-mcp`), which a cloud container cannot run. Keep it locally
  if you use FreeCAD through an agent; delete it otherwise. Since 2026-09-16 the
  file is also listed in `.gitignore`, so it no longer shows up as an untracked
  change in every session.
- `bash setup-tooling.sh` stays the fuller step: it also runs
  `install_root_tools.py`, which the hook does not, so the hook never writes into
  the working tree beyond the two submodules.

## Update — 2026-09-22

This record assumed the hook always starts. It does not. Claude Code reads
`.claude/settings.json` from the session's own project folder only, so a session
that attaches several repositories opens the folder above them and never
registers the hook. It then prints nothing, and an empty `.agents/` looks exactly
like a working one. See
[The first step lives in CLAUDE.md](2026-09-22_first-step-lives-in-claude-md.md).
