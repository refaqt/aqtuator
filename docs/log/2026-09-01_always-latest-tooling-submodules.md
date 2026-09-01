# 2026-09-01 — Always-latest tooling submodules

**Role(s):** engineering

## What happened

Copied root helpers `setup-tooling.sh` / `setup-tooling.bat` from doqs templates. Set `branch = main` on `doqs` and `.agents`. Prepended **First step (required)** to `AGENTS.md`: agents run `bash setup-tooling.sh`; humans on Windows may double-click the `.bat`. Updated README, onboarding, `repo.md`, and `.cursor/README.md` so they no longer tell people to `git submodule update --init --recursive` for tooling. CI still uses `submodules: recursive` (recorded pin).

## Decisions

Do not commit dirty submodule gitlinks after `--remote` unless freezing a pin.
