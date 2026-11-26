# AQTUATOR: local agent files

What is true only for this repository. Everything shared lives in the kit at `.agents/`.

| File | What it holds |
| --- | --- |
| [`profile.toml`](profile.toml) | Name and profile, read by `.agents/scripts/sync_root.py` |
| [`rules/repo.md`](rules/repo.md) | Rules for this repository. Every session loads it, so keep it under 3 KB |
| [`skills/measurement-data/`](skills/measurement-data/SKILL.md) | The measurement archive |
| [`skills/patterns/`](skills/patterns/SKILL.md) | Coding patterns proven here |

`CLAUDE.md`, `AGENTS.md` and `.cursor/rules/refaqt-*.mdc` are generated from the kit. Do not edit
them. Run `python3 .agents/scripts/sync_root.py` after a change here.
