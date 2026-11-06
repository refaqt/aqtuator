# 2026-11-06 — Preload counterbore 6 mm wide

**Role(s):** cad

## Goal

Niels Bosmans asked for a wider counterbore under the seal strip preload screws: Ø6 mm instead of
Ø5 mm.

## Short answer

Done. `preload_counterbore_d` in the base `Params` is now 6 mm. The depth stays 2.48 mm.

## What changed

- `Params` B11 `preload_counterbore_d`: 5 mm → 6 mm. The note in C11 now says the size is wider
  than the strip hole (5 mm).
- The counterbore is still on the screw axis. The wall to the magnet pockets goes from about
  1.4 mm to about 0.9 mm.
- See [the first counterbore log](2026-10-30_preload-screw-counterbore.md) for the background.

## Checks

- The base recomputes with no errors. The solid is valid.
- The volume drops by 42 mm³. Two full rings of Ø6/Ø5 × 2.48 mm give 42.8 mm³, so the counterbore
  does not cut into the magnet pockets.
- The fingerprint was written from the saved file. `doqs check` passes (run with
  `PYTHONIOENCODING=utf-8`; without it, `validate_names.py` fails on the Windows console encoding,
  also on `main`).
