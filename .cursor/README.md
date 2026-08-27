# Portable agent kit (Cursor adapters)

Shared rules and skills live in [`.agents/`](../.agents/) (content from
[refaqt/refaqt-agents](https://github.com/refaqt/refaqt-agents)).

This `.cursor/` tree holds **thin adapters** so Cursor loads them:

| Path | Role |
| --- | --- |
| `.cursor/rules/*.mdc` | Pointers (and aqtuator-only `repo-profile`, `powershell`) |
| `.agents/rules/*.md` | Canonical portable rules |
| `.agents/skills/*/SKILL.md` | Canonical portable skills |
| `.agents-local/skills/` | Aqtuator-only skills (e.g. measurement-data) |

## After cloning

1. Ensure `.agents/` is present (submodule init once the kit is published as a submodule, or a
   vendored copy of refaqt-agents).
2. Prefer project rules over duplicate User Rules in Settings.
3. Confirm agents read `docs/mistakes/` and follow root `AGENTS.md`.
