---
name: mistake-log
description: >-
  Logs incidents to docs/mistakes/, escalates repeated failures, and promotes
  prevention rules. Use at task start, after bugs, failed approaches, rejected
  output, or convention misunderstandings in this repository.
---

# Mistake log

## What counts as a mistake

- A bug introduced and fixed in the same session.
- A wrong approach taken and abandoned.
- A misunderstanding of project conventions that caused rework.
- A test failure from an incorrect assumption.
- Any output the user rejected or asked to redo.

## Before starting work

1. Read `docs/mistakes/` (and its `README.md` index).
2. State which prevention rules apply to the current task.

## After a mistake

1. Add `docs/mistakes/YYYY-MM-DD_topic.md` (per-entry files) and a row in `docs/mistakes/README.md`.
2. If the same mistake happens twice, add a bold warning on the relevant section and promote the prevention rule into standing guidance (`.agents/rules/` in the kit, or a scoped consumer adapter such as `.cursor/rules/`).
3. Treat every mistake as a process gap, not a one-off.

## Continuous improvement

- After a long session, review `docs/mistakes/` and `docs/patterns/SKILL.md` (if present) for rules or patterns to promote.
- Prefer making `docs/mistakes/` shorter over time by preventing repeat categories.

## Entry format

Use the consumer's mistake template when available (e.g. doqs `templates/mistake-entry.md`), or:

```markdown
# YYYY-MM-DD — Short title

## What happened

## Why it went wrong

## Prevention rule

## Related
```
