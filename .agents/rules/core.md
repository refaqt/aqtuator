# Core

- Follow user, tool, system, and skill instructions completely; use real shell and tools; do not give up after one failure.
- At the start of each task, read `docs/mistakes/` and briefly state which prevention rules apply before editing.
- Before non-trivial work, read `docs/architecture.md`. Before new solutions, check `docs/patterns/SKILL.md` if it exists and use the `maintain-patterns` skill when maintaining patterns.
- If any required living-doc folder is missing (`docs/log/`, `docs/decisions/`, `docs/mistakes/`, `docs/architecture.md`), create it from `.agents/bootstrap/docs/` (or `templates/`) with a brief initial entry (empty is acceptable; missing is not).
- Maintain living documentation during work, not only at the end; follow the living-docs rule and the `mistake-log` / `log` skills when they apply.
- Read the existing codebase before writing; prefer editing existing files and patterns; when in doubt, do less and ask.
- Keep diffs focused: match local style, no drive-by refactors, and no unrelated markdown outside the `docs/` convention files.
