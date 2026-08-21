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
| [`docs/`](docs/) | Dev-log, decisions, mistakes |

Start with [`docs/architecture.md`](docs/architecture.md) for the technical overview, or
[`docs/dev-log/`](docs/dev-log/) for the chronological story — 71 entries from June 2025 onward.

## Clone

```bash
git clone --recurse-submodules https://github.com/nielsbosmans87/aqtuator.git
cd aqtuator
pip install -e software/identification -e software/measurement-tools
```

If you already cloned without submodules: `git submodule update --init --recursive`. Without
`doqs/`, the validators and templates are unavailable and the layout conventions cannot be inferred.

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

GPL-3.0. See [LICENSE](LICENSE).
