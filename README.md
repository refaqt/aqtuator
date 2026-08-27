# AQTUATOR

Active chatter suppression for a Mekanika Pro milling machine.

Chatter — self-excited vibration between tool and workpiece — sets the maximum depth of cut a machine
can take. This project characterises where that limit sits on a real machine, and develops an
actuator to raise it.

The work so far has been measurement: frequency response functions at the tool and spindle, and
cutting stability limits, across three drive configurations (stepper, servo with rotary encoder
feedback, servo with linear encoder feedback). Those measurements are what an actuator design can be
held against.

## Layout

This repository follows [doqs](https://github.com/refaqt/doqs), included as a submodule at
[`doqs/`](doqs/). Every folder is a module with the same internal structure.

| Folder | What |
| --- | --- |
| [`cad/`](cad/) | FreeCAD models |
| [`architecture/`](architecture/) | SysML requirements and block definitions |
| [`simulation/`](simulation/) | Design-time models — structural dynamics, PWM/RC trade-off |
| [`measurement/`](measurement/) | Test campaigns and the manifest indexing 1.88 GB of data on Google Drive |
| [`firmware/`](firmware/) | Controllino MICRO (RP2040) targets |
| [`software/`](software/) | Host-side Python — identification stack, measurement tooling |
| [`docs/`](docs/) | Activity log, decisions, mistakes, patterns |

Start with [`docs/architecture.md`](docs/architecture.md) for the technical overview, or
[`docs/log/`](docs/log/) for the chronological story — 71 entries from June 2025 onward.

## Clone

```bash
git clone --recurse-submodules https://github.com/nielsbosmans87/aqtuator.git
cd aqtuator
pip install -e software/identification -e software/measurement-tools
```

If you already cloned without submodules: `git submodule update --init --recursive`. Without
`doqs/` and `.agents/`, layout validators and shared agent rules/skills are unavailable.

## Measurement data

Raw data is **not in this repository**. 1 659 files and 1.88 GB live on the `3 - Projects` Google
Drive shared drive; [`measurement/data-index.csv`](measurement/data-index.csv) describes every one of
them with a checksum and parsed metadata, so the archive can be queried without downloading it.

See [`measurement/README.md`](measurement/README.md) for access and the reasoning.

## Hardware

- Mekanika Pro milling machine with PlanetCNC control
- ODrive S1 servo drive, linear and rotary encoder feedback
- Controllino MICRO (RP2040) for torque excitation and acquisition
- DATAQ WinDaq HiRes DAQ, 8 channels, accelerometers and impact hammer

## Licence

This repository uses different licences for different kinds of content:

- **Hardware** (`cad/`, `architecture/`, `manufacturing/`, `bom/`, `builds/`, `modules/`) —
  [CERN-OHL-S v2.0](LICENSES/CERN-OHL-S-2.0.txt)
- **Firmware & software** (`firmware/`, `software/`, `simulation/`) —
  [GPL-3.0](LICENSES/GPL-3.0.txt)
- **Media & documentation** (`docs/`, `measurement/`) —
  [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt)

The REFAQT name and logo, and the AQTUATOR name and logo, are trademarks and
are not covered by the above — see [TRADEMARKS.md](TRADEMARKS.md).

See [LICENSE](LICENSE) for the full overview and directory mapping.
