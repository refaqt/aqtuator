# 2026-08-27 — Unify agent kit via refaqt-agents

## Context

Agent guidance was split across `.cursor/` (rules + process skills), `.claude/skills/` (domain
skills), root `AGENTS.md` / `CLAUDE.md`, legacy `.cursorrules`, and an empty `docs/prompts-log/`.
A portable kit is needed for all Refaqt repos with Cursor and Claude Code.

## Decision

1. Canonical portable rules and skills live in [refaqt/refaqt-agents](https://github.com/refaqt/refaqt-agents),
   consumed here as a git submodule at [`.agents/`](../../.agents/).
2. Root `AGENTS.md` / `CLAUDE.md` stay thin per-repo stubs (tools discover them at the repo root;
   a submodule cannot own those paths).
3. Cursor `.cursor/rules/*.mdc` files are thin adapters pointing at `.agents/rules/*.md`, plus
   aqtuator-only `repo-profile` and `powershell`.
4. Repo-specific skills live in `.agents-local/skills/` (`measurement-data`, `patterns`).
5. One activity log at `docs/log/` (formerly `docs/dev-log/`); `docs/prompts-log/` is removed.

## Consequences

- Agents follow one discovery path via `AGENTS.md`.
- Updating shared process guidance is done in refaqt-agents and pulled into consumers.
- Aqtuator-specific measurement and patterns stay out of the portable kit.
