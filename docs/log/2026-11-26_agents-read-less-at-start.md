# 2026-11-26 — Agents now read about a quarter of the text at the start of a task

**Role(s):** software

## What happened

Agents read about 82 KB of instructions before they did any work here. That is about 20,000 tokens
per session. Now they read about 20 KB. The rest loads only when a task needs it: the pull request
rules when an agent writes a pull request, the coding patterns when it writes code, and one mistake
note when its rule matches the task.

The entry files `CLAUDE.md` and `AGENTS.md` now come from the shared kit, so they look the same in
every Refaqt repository. The rules that are true only here are in `.agents-local/rules/repo.md`.

## Decisions

See [the decision record](../decisions/2026-11-26_shared-agent-files-come-from-the-kit.md).

## Next Steps

- Merge the kit change first, then the doqs change, then this one.
- Turn on the `refaqt` plugin for the organization in claude.ai, so every session gets the skills.
