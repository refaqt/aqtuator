# Flexure ball-screw servo stage

Linear stage with active chatter suppression. Flexure guidance, ball-screw transmission, servo
drive.

Chatter is self-excited vibration between tool and workpiece. It sets the maximum depth of cut a
milling machine can take. This stage measures that vibration and drives a short-stroke actuator
against it, so the machine can cut deeper.

The work so far is measurement and identification on the test machine, a Mekanika Pro mill:
frequency response at the tool and the spindle, and cutting stability limits, across three drive
configurations (stepper, servo with rotary encoder feedback, servo with linear encoder feedback).
Those numbers are what an actuator design can be held against.

## Layout

| Folder | What |
| --- | --- |
| [`measurement/`](measurement/) | Test campaigns and the manifest indexing 1.88 GB of data on Google Drive |
| [`firmware/`](firmware/) | Controllino MICRO (RP2040) targets |
| [`software/`](software/) | Host-side Python — identification stack, measurement tooling |

The chronological record of this work is in the repository root at
[`docs/log/`](../../docs/log/), and the technical overview is in
[`docs/architecture.md`](../../docs/architecture.md).

## Status

This is not yet a product family. It has no shared core module, no option modules and no
`catalog.toml`. Those arrive when the requirements and the architecture are settled. The commercial
name belongs in `catalog.toml` when there is one, never in a folder name.
