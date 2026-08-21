---
name: project-skills-md
description: >-
  Applies and maintains project-specific reusable patterns in .claude/skills/project-patterns/SKILL.md.
  Use before starting implementation, after a novel codebase-specific fix, when
  the user mentions skills.md, project skills, reusable patterns, or deprecating
  a documented pattern.
---

# Project skills (`.claude/skills/project-patterns/SKILL.md`)

## Before starting work

1. Read `.claude/skills/project-patterns/SKILL.md` if it exists.
2. If an entry matches the task, follow that pattern instead of inventing a new approach.
3. If nothing applies, proceed with normal implementation.

## After a novel, codebase-specific fix

When you solve something specific to this repository in a way worth repeating:

1. Add or update an entry in `.claude/skills/project-patterns/SKILL.md` using the format below.
2. Do not add generic programming knowledge; only patterns tied to this project.
3. If the pattern should become standing agent guidance, add or update a scoped project rule instead of duplicating long prose in multiple places.

## When updating or deprecating

- Change or remove the entry in `.claude/skills/project-patterns/SKILL.md` in the same change as the code, or immediately after.
- If deprecated, mark clearly or remove after migration, per team preference.

## Entry format

Each skill is one `##` heading plus four labeled lines:

    ## [Skill name]
    **When to use:** [One sentence]
    **Pattern:**
    ```[language]
    // minimal example
    ```
    **Gotchas:** [Any known edge cases or pitfalls]
    **Last used:** [Date or task reference]

## Quality bar

- **Name:** Short, unique, searchable.
- **When to use:** One sentence so the agent can match tasks quickly.
- **Pattern:** Smallest example that still shows the project-specific hook.
- **Gotchas:** Real pitfalls for this repo.
- **Last used:** ISO date or issue/PR reference.

## Additional reference

For the live registry, open [.claude/skills/project-patterns/SKILL.md](../../../.claude/skills/project-patterns/SKILL.md).
