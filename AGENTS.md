# Agent guide

Entry point for Cursor, Claude Code, and other agents working in this repository.

## Shared kit

This repo mounts [refaqt/refaqt-agents](https://github.com/refaqt/refaqt-agents) at [`.agents/`](.agents/).

1. Read [`.agents/rules/core.md`](.agents/rules/core.md) and [`.agents/rules/living-docs.md`](.agents/rules/living-docs.md).
2. Read [`docs/mistakes/`](docs/mistakes/) and state which prevention rules apply.
3. Read [`docs/architecture.md`](docs/architecture.md) before non-trivial work.
4. Before new coding solutions, check [`.agents-local/skills/patterns/SKILL.md`](.agents-local/skills/patterns/SKILL.md) if present.

If `.agents/` is empty: `git submodule update --init --recursive`.

## This repository

AQTUATOR — active chatter suppression on a Mekanika Pro milling machine. Repo profile, folder map,
and conventions: [`.agents-local/rules/repo.md`](.agents-local/rules/repo.md).

Repo-specific skills: [`.agents-local/skills/`](.agents-local/skills/).

## Skills

| Skill | Path |
| --- | --- |
| Activity log | [`.agents/skills/log/SKILL.md`](.agents/skills/log/SKILL.md) |
| Mistake log | [`.agents/skills/mistake-log/SKILL.md`](.agents/skills/mistake-log/SKILL.md) |
| Maintain patterns | [`.agents/skills/maintain-patterns/SKILL.md`](.agents/skills/maintain-patterns/SKILL.md) |
| Coding patterns | [`.agents-local/skills/patterns/SKILL.md`](.agents-local/skills/patterns/SKILL.md) |
| Measurement archive | [`.agents-local/skills/measurement-data/SKILL.md`](.agents-local/skills/measurement-data/SKILL.md) |
