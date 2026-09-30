# Compact stage

Compact linear stage, driven by an iron core linear motor.

## Parts

The stage is one assembly of five parts that we make. The sealing clamp is used twice, once at
each end of the base.

| Part | What it does | CAD |
| --- | --- | --- |
| Base | The fixed body. It mounts on the machine. | [`cad/parts/base/`](cad/parts/base/) |
| Carriage bottom | The moving part inside the base. | [`cad/parts/carriage-bottom/`](cad/parts/carriage-bottom/) |
| Carriage top | The moving part above the base. The load mounts on it. | [`cad/parts/carriage-top/`](cad/parts/carriage-top/) |
| Sealing strip | Closes the slot in the top of the base. | [`cad/parts/sealing-strip/`](cad/parts/sealing-strip/) |
| Sealing clamp | Holds one end of the sealing strip on the base. | [`cad/parts/sealing-clamp/`](cad/parts/sealing-clamp/) |

The assembly is [`cad/assemblies/compact-stage/`](cad/assemblies/compact-stage/). It links each
part by a relative path, and fixes the base in place. The parts have no geometry yet.

Bought parts (guide rails and blocks, the motor, the encoder, screws) are not in this list. They
belong in the parts library in [`modules/stoq/`](../stoq/). They enter the architecture and the
assembly later.

## Architecture

| File | What it holds |
| --- | --- |
| [`architecture/compact-stage.sysml`](architecture/compact-stage.sysml) | The stage requirements (`STG-01` to `STG-14`: size, accuracy, speed, force, load and the screw hole grid), the parts of the stage, and an interface for every pair of parts that touch. |
| [`architecture/motor-drive.sysml`](architecture/motor-drive.sysml) | Requirements for the servo drive of the MAXWELL MK21 linear motor (`DRV-01` to `DRV-09`, and `DRV-P1` to `DRV-P3`). |

Every pair of parts that touch has an interface: a `port def` in `compact-stage.sysml`, a port on
each part, and a connection in the assembly. The two interfaces of the whole stage (the base on
the machine, and the load on the carriage) are also listed in [`okh.toml`](okh.toml).

## Next

1. Model the geometry of each part. Add a dimension to its interface when the CAD fixes it.
2. Add the bought parts to the parts library, then to the architecture and the assembly, each
   with its interfaces.
3. Decide what is a number and what is a structure. A travel length is a parameter of one shared
   core. A different drive or a different feedback sensor is a separate option module combined by a
   thin composition module. The rules are in
   [`doqs/docs/variants.md`](../../doqs/docs/variants.md).
4. Add `catalog.toml` once there are real compositions to sell. The commercial name goes there, not
   in a folder name.
