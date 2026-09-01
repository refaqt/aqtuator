# 2026-09-01 — Root launchers from setup-tooling

**Role(s):** engineering

## What happened

doqs treated `syson.bat` as copy-once, so `setup-tooling.bat` never created it.
Refreshed `setup-tooling.sh` / `.bat` here so they run
`python doqs/scripts/install_root_tools.py` after submodule update. That
installer copies `*.bat` / `*.sh` from `doqs/templates/<tool>/` (except
`setup-tooling/`) to this repo root.

## Decisions

Keep `setup-tooling.*` as a one-time bootstrap. After this refresh, new doqs
tools appear on the next helper run without another copy of the helper.

## Next Steps

The installer lives on the doqs branch `feat/root-launcher-install`. Until
that lands on doqs `main` and this submodule tracks it, run
`python doqs/scripts/install_root_tools.py` only after the submodule has the
script (or invoke it from a local doqs clone with `--root` pointing here).
