# 2026-09-16 — Cloud agents can read the tooling submodules

**Role(s):** engineering, software

## What happened

A cloud session clones this repository without `--recurse-submodules`, so
`.agents/` and `doqs/` arrive as empty folders. Nothing warns about it. An agent
reads no rules, no skills, and no `doqs/docs/architecture.md`, and cannot run
`python doqs/scripts/validate_all.py`.

Work done:

- New `SessionStart` hook at `.claude/hooks/session-start.sh`, registered in
  `.claude/settings.json`. It runs the same two git calls as `setup-tooling.sh`,
  checks the marker files rather than the exit code, and always exits 0.
- `.cursor/environment.json` runs that same script, so Cursor cloud agents are
  covered by one implementation.
- `.claude/settings.json` also carries the agent-CAD deny rules. It had to:
  `install_root_tools.py` installs that file copy-once, so a settings file
  created for the hook alone would have blocked the guard for good.
- Refreshed `setup-tooling.sh`, `setup-tooling.bat`, `syson.sh` and `syson.bat`
  from `doqs/templates/`. The old `setup-tooling` ran a single
  `git submodule update --init --recursive --remote`, which moves **every**
  submodule to its remote — including the `modules/*` submodules that must stay
  SHA-pinned. The current template splits it into a pin pass and a
  tooling-only `--remote` pass.
- Bumped both pins: `doqs` `9279f99` → `65ef08c`, `.agents` `be32113` → `13c4cfc`.
  Both were two weeks old.

## Decisions

Recorded in
[2026-09-16_cloud-session-submodule-hook.md](../decisions/2026-09-16_cloud-session-submodule-hook.md).

The `doqs` bump matters beyond freshness. This repository does not set
`update = none` on `.agents`, so CI's `submodules: recursive` does check the kit
out, and the old `doqs` only had `is_under_doqs_submodule()`, which does not skip
it. The gates therefore walked a repository this one cannot fix. Commit `780d486`
replaces that check with `is_under_tooling_submodule()` over
`TOOLING_SUBMODULE_NAMES`.

We ran both versions against this repository with `.agents/` filled, and **both
pass today** — the kit currently holds no `okh.toml`, `catalog.toml` or `.sysml`
sample for a gate to trip over. So this is a latent failure, not a live one: the
bump removes it before the kit grows a sample file, which is what happened to
another machine repo in
[doqs mistakes, 2026-09-16](../../doqs/docs/mistakes/2026-09-16_validators-walked-agent-kit.md).

`.mcp.json` is left uncommitted on purpose. It registers the FreeCAD MCP server,
which a cloud container cannot run.

## Next Steps

Merge to `main`. Sessions started from `main` after that pick the hook up
automatically.
