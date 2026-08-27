# refaqt-agents

Portable, tool-neutral rules and skills for AI agents working on Refaqt repositories.

Mount this repository as a git submodule at `.agents/` in each consumer repo (Cursor, Claude Code, and anything that reads `AGENTS.md`).

## Layout

| Path | Purpose |
| --- | --- |
| `rules/` | Standing guidance (markdown). Consumers load via thin adapters and root `AGENTS.md`. |
| `skills/` | Process skills (`SKILL.md`). |
| `templates/` | Starter `AGENTS.md` and living-doc stubs for new repos. |
| `bootstrap/docs/` | Same stubs, kept for kits that still reference `.cursor/bootstrap`. |

## Install into a consumer repo

```bash
# From the consumer repo root (after any existing .agents/ content is moved out)
git submodule add https://github.com/refaqt/refaqt-agents.git .agents
git submodule update --init --recursive
```

Then:

1. Copy or adapt [`templates/AGENTS.md`](templates/AGENTS.md) to the **repo root** as `AGENTS.md` (add a "This repository" section).
2. Keep root `CLAUDE.md` as a one-liner pointing at `AGENTS.md`.
3. Add thin Cursor adapters under `.cursor/rules/*.mdc` that point at `.agents/rules/*.md` (see consumer examples in aqtuator).
4. Put **repo-specific** skills under `.agents-local/skills/` (not inside the submodule).
5. Put **repo-specific** coding patterns in `.agents-local/skills/patterns/SKILL.md` and point agents at them from `AGENTS.md`.

Windows note: do not symlink root `AGENTS.md` into the submodule — use a thin stub file.

## Skills in this kit

| Skill | When |
| --- | --- |
| `log` | Add or edit `docs/log/` activity entries (any role) |
| `mistake-log` | Read/write `docs/mistakes/`; promote prevention rules |
| `maintain-patterns` | Update the consumer's `.agents-local/skills/patterns/SKILL.md` |

## License

GPL-3.0 (see [LICENSE](LICENSE)).
