# Agent guide

Entry point for Cursor, Claude Code, and other agents working in this repository.

## First step (required)

Check the tooling folders before anything else. Run this from the repository root:

```bash
ls .agents/rules/core.md doqs/scripts/validate_all.py
```

- **Both files are there.** The folders are filled. Go on to [Shared kit](#shared-kit).
- **Either file is missing.** Run `bash setup-tooling.sh` from the repository root, then check again. That also installs the root launchers (`doqs.sh`, `syson.sh`).
- **People on Windows** may double-click `setup-tooling.bat` (`pause` is OK there only). Agents must not run the `.bat`.

A `SessionStart` hook at [`.claude/hooks/session-start.sh`](.claude/hooks/session-start.sh) does the
same submodule work at the start of a session, and prints one line when it worked. Do not trust it
blindly. It runs only when the session opens **this folder** as its project folder. Claude Code reads
[`.claude/settings.json`](.claude/settings.json) from that folder only, so a session that opens a
parent folder, or that attaches several repositories at once, never reads the file, never starts the
hook, and prints nothing at all. Silence and success look the same. The check above is the only step
that works in every session. See
[the decision record](docs/decisions/2026-09-22_first-step-lives-in-claude-md.md).

Run the setup file anyway when you need the launchers it installs, or when the hook said it could not
reach the network. Both leave the submodule gitlinks modified on purpose — leave them uncommitted
unless you mean to set a new pin. Installing the kit in a new repo:
[`.agents/INSTALL.md`](.agents/INSTALL.md).

## Shared kit

This repo mounts [refaqt/refaqt-agents](https://github.com/refaqt/refaqt-agents) at [`.agents/`](.agents/).

1. Read [`.agents/rules/core.md`](.agents/rules/core.md) and [`.agents/rules/living-docs.md`](.agents/rules/living-docs.md).
2. Read [`docs/mistakes/`](docs/mistakes/) and state which prevention rules apply.
3. Read [`docs/architecture.md`](docs/architecture.md) before non-trivial work.
4. Before new coding solutions, check [`.agents-local/skills/patterns/SKILL.md`](.agents-local/skills/patterns/SKILL.md) if present.

## This repository

AQTUATOR — active chatter suppression on a Mekanika Pro milling machine. Repo profile, folder map,
and conventions: [`.agents-local/rules/repo.md`](.agents-local/rules/repo.md).

Repo-specific skills: [`.agents-local/skills/`](.agents-local/skills/).

## Skills

| Skill | Path |
| --- | --- |
| Activity log | [`.agents/skills/log/SKILL.md`](.agents/skills/log/SKILL.md) |
| Mistake log | [`.agents/skills/mistake-log/SKILL.md`](.agents/skills/mistake-log/SKILL.md) |
| Maintain patterns | [`.agents/skills/maintain-patterns/SKILL.md`](.agents/skills/maintain-patterns/SKILL.md) |
| Coding patterns | [`.agents-local/skills/patterns/SKILL.md`](.agents-local/skills/patterns/SKILL.md) |
| Measurement archive | [`.agents-local/skills/measurement-data/SKILL.md`](.agents-local/skills/measurement-data/SKILL.md) |
