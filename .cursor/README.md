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

1. `bash setup-tooling.sh` from the repo root (fills `.agents/` and `doqs/` to latest `main`). Humans on Windows may double-click `setup-tooling.bat`. Agents must not run the `.bat`.
2. Prefer project rules over duplicate User Rules in Settings.
3. Confirm agents read `docs/mistakes/` and follow root `AGENTS.md`.
