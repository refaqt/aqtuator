# 2026-08-27 — Unify agent skills and rules

**Role(s):** engineering

## What happened

- Restructured agent guidance around a portable kit (refaqt-agents).
- Migrated `docs/dev-log/` → `docs/log/` with mandatory **Role(s)** (historical entries tagged
  `engineering`).
- Moved the thirteen coding patterns to `.agents-local/skills/patterns/SKILL.md`.
- Moved measurement archive skill to `.agents-local/skills/measurement-data/`.
- Replaced Cursor rules with thin adapters; removed `.cursorrules`, `docs/prompts-log/`, and
  duplicate `.cursor/skills` / `.claude/skills` bodies.
- Added ADR: `docs/decisions/2026-08-27_unify-agent-kit-via-refaqt-agents.md`.
- Published the kit to `refaqt/refaqt-agents` and mounted it as the `.agents/` git submodule.

## Next Steps

- [ ] Delete leftover remote probe branch `cursor/access-probe-bjlr` on refaqt-agents (optional cleanup)
