# 2026-08-28 — Slim AGENTS.md to thin stub

**Role(s):** engineering

## What happened

- Completed the 2026-08-27 ADR follow-through: `AGENTS.md` is now a thin discovery stub per the
  refaqt-agents template.
- Moved repo-specific profile, folder map, conventions, and validation into
  `.agents-local/rules/repo.md`.
- Slimmed `.cursor/rules/core.mdc`, `living-docs.mdc`, and `repo-profile.mdc` to pointers only.
- Added an **Agents** section to `README.md` (humans) pointing at `AGENTS.md` and `.agents-local/`.
- Applied the same pattern to `refaqt/qarve`.

## Next Steps

- [ ] Pull updated refaqt-agents template if the kit adds `.agents-local/rules/` guidance
