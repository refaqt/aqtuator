# 2026-09-30 — The compact stage has its parts, its assembly and its interfaces

**Role(s):** engineering, cad

## What happened

The user removed the old X axis models from `cad/`. They will not be used again. They stay in the
git history.

The compact stage now owns the linear motor stage. Its module holds three things:

- **The requirements.** The stage requirements (STG-01 to STG-14) and the servo drive
  requirements (DRV-01 to DRV-09) moved from the top level `architecture/` folder into
  [`modules/compact-stage/architecture/`](../../modules/compact-stage/architecture/). The stage
  requirements are now part of `compact-stage.sysml`, and the compact stage itself is their
  subject. `linear-stage.sysml` no longer exists. The drive requirements stay in
  `motor-drive.sysml`. No requirement value changed. The earlier log entry said no family owned
  these stages yet. That is no longer true.
- **Five parts we make, in CAD.** Base, carriage bottom, carriage top, sealing strip and sealing
  clamp. Each is its own FreeCAD file with one empty body. The assembly links all five by relative
  path, uses the sealing clamp twice (one at each end), and fixes the base in place. There is no
  geometry yet.
- **The interfaces.** The new file
  [`compact-stage.sysml`](../../modules/compact-stage/architecture/compact-stage.sysml) has a
  part for each of the five, and an interface for every pair of parts that touch. Two interfaces
  face the outside: the base on the machine, and the load on the carriage top. The module manifest
  lists those two as well.

| Interface | Joins |
| --- | --- |
| Base mount | base and the machine (outside) |
| Carriage mount | carriage top and the load (outside) |
| Carriage joint | carriage bottom and carriage top. The carriage bottom is screwed onto the guide blocks, not onto the base |
| Slot seal | sealing strip and base |
| Strip clamp | sealing clamp and sealing strip (twice) |
| Clamp mount | sealing clamp and base (twice) |

The two carriage halves screw onto each other (the carriage joint above). The sealing strip runs
through the carriage, over the carriage bottom and under the carriage top. The strip never touches
either carriage half, so there is no interface between the strip and the carriage. Rollers in the carriage touch the strip. They are bought parts, so their interface with
the strip comes when they enter the architecture.

## Decisions

- **An interface for every pair of parts that touch, from now on.** No rule asked for this
  before. The repository rules now say it: every new part or new connection gets its interface in
  the same change. The interfaces hold no dimensions until the CAD or a data sheet fixes them.
- **Bought parts wait.** The guide rails and blocks, the motor, the encoder, the rollers and the
  screws are not in the architecture yet. They go into the parts library first. The interfaces
  they bring (for example base to rail, block to carriage bottom, and roller to sealing strip)
  come with them.

## Open Questions

- The new SysML file was written by hand. No SysML parser has checked it yet.

## Next Steps

- Model the geometry of the five parts.
- Add the bought parts to the parts library, then to the architecture and the assembly.
- Open the two SysML files in SysON to check that they load without errors.
