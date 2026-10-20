# 2026-10-20 — The bottom carriage is 1 mm lower, because the MK21 cable is only 8.3 mm thick

**Role(s):** cad

## Goal

The cable of the MK21 forcer is 8.3 mm thick, not 10 mm as we thought. The cable needs less room,
so the bottom carriage can be lower.

## Work Done

- **Niels made the bottom carriage 1 mm lower in FreeCAD.** Its top is now at 27.5 mm, down from
  28.5 mm.
- **The stage is now 51.5 mm high, down from 52.5 mm.** The limit in the requirements is 60 mm.
- **The fingerprints of the bottom carriage and the assembly are up to date.**
- **Niels moved the forcer 2.5 mm along the travel axis** in the assembly (towards lower x).
- **The bottom carriage and its four blocks also moved 0.5 mm along the rails**, all together,
  towards higher x. This was not done on purpose. The parts did not change shape. Most likely,
  FreeCAD solved the assembly again and placed the free sliding group at a slightly different
  spot. So, compared with the carriage, the forcer moved 3 mm, not 2.5 mm.

## Open Questions

- **The top carriage has no geometry yet.** It now has 8.5 mm left under the 60 mm limit.
