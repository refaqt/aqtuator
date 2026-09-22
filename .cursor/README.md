# Portable agent kit (Cursor adapters)

Shared rules and skills live in [`.agents/`](../.agents/), a git submodule of
[refaqt/refaqt-agents](https://github.com/refaqt/refaqt-agents).

This `.cursor/` tree holds **thin adapters** so Cursor loads them:

| Path | Role |
| --- | --- |
| `.cursor/rules/*.mdc` | Pointers (and aqtuator-only `repo-profile`, `powershell`) |
| `.agents/rules/*.md` | Canonical portable rules |
| `.agents/skills/*/SKILL.md` | Canonical portable skills |
| `.agents-local/skills/` | Aqtuator-only skills (measurement-data, patterns) |

## After cloning

1. `bash setup-tooling.sh` from the repo root (fills `.agents/` and `doqs/` to latest `main`). Humans on Windows may double-click `setup-tooling.bat`. Agents must not run the `.bat`. Cursor cloud agents run the same work from [`.cursor/environment.json`](environment.json), and Claude Code runs it from the `SessionStart` hook in [`.claude/settings.json`](../.claude/settings.json); both point at [`.claude/hooks/session-start.sh`](../.claude/hooks/session-start.sh), which fills the same two folders. Both work only when the session opens **this repository** as its project folder. A session that opens a parent folder, or that attaches several repositories, reads neither file and fills neither folder. Then run the command yourself; [`CLAUDE.md`](../CLAUDE.md) holds the check that tells you.
2. Prefer project rules over duplicate User Rules in Settings.
3. Confirm agents read `docs/mistakes/` and follow root `AGENTS.md`.
