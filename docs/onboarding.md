# Onboarding

Getting from a fresh clone to a running identification measurement.

## 1. Clone

```bash
git clone --recurse-submodules https://github.com/refaqt/aqtuator.git
cd aqtuator
```

Already cloned without submodules, or `doqs/` is empty? From the repo root, agents run
`bash setup-tooling.sh`. Humans on Windows may double-click `setup-tooling.bat`. Without `doqs/` the
layout conventions and validators are unavailable.

## 2. Python

```bash
pip install -e modules/flexure-ball-screw-servo-stage/software/identification
pip install -e modules/flexure-ball-screw-servo-stage/software/measurement-tools
```

Python 3.10+. Installs `pyserial`, `odrive`, `numpy`, `scipy`, `pandas`, `matplotlib`, `PyQt5`.

## 3. Measurement data (optional)

Only needed if you are analysing recorded captures. The archive lives on the `3 - Projects` Google
Drive shared drive; install Google Drive for Desktop, or set `AQTUATOR_DATA_ROOT` to a local copy.
Check what you have:

```bash
python -m measurement_tools.verify_index --quick
```

See [`modules/flexure-ball-screw-servo-stage/measurement/README.md`](../modules/flexure-ball-screw-servo-stage/measurement/README.md).

## 4. Hardware

For **Workflow A** (torque playback and acquisition):

- Controllino MICRO flashed with
  [`firmware/torque-excitation`](../modules/flexure-ball-screw-servo-stage/firmware/torque-excitation/)
  in the stage module
- ODrive S1 with `GPIO1` mapped to torque input — the Python side configures and verifies this
- Wiring: Controllino `D0` PWM output → RC filter → ODrive `GPIO1`, with a common ground

For **Workflow B** (servo identification sweep): ODrive on USB only. No Controllino, no CAN.

> **Idle at 0 Nm, not 0 % duty.** ODrive `GPIO1` has a pull-up, so 0 % duty does not give 0 V after
> the RC network and maps to a negative torque. The firmware handles this; do not defeat it.

## 5. Flash the firmware

Arduino IDE with the `controllino_rp2` board support installed. The targets live in
[`modules/flexure-ball-screw-servo-stage/firmware/`](../modules/flexure-ball-screw-servo-stage/firmware/).
Open the target's `.ino` and upload:

| Target | Purpose |
| --- | --- |
| [`firmware/torque-excitation`](../modules/flexure-ball-screw-servo-stage/firmware/torque-excitation/) | Torque playback + multi-channel acquisition |
| [`firmware/spindle-controller`](../modules/flexure-ball-screw-servo-stage/firmware/spindle-controller/) | Standalone 8 kHz spindle controller (`GPIO1`/`D1` must be HIGH to run) |
| [`firmware/pwm-output-test`](../modules/flexure-ball-screw-servo-stage/firmware/pwm-output-test/) | Validate the RC output stage without an ODrive |

Serial is `115200`. The serial port is currently hardcoded — update `CONTROLLINO_PORT` in
`modules/flexure-ball-screw-servo-stage/software/identification/src/aqtuator_id/sequential_run.py`.

## 6. Run

### Workflow A — torque playback and acquisition

```bash
aqtuator-sequential
```

Connects over serial, prompts for the ODrive control mode (`p` position, default, or `t` torque),
uploads a multisine waveform, runs `START_IDENTIFICATION`, waits for `ACK: Acquisition complete`,
then retrieves samples with `GET_DATA` and plots time series plus a Bode-style estimate.

### Workflow B — servo identification sweep

```bash
aqtuator-servo-id
```

Needs ODrive firmware **0.6.12+** and the `odrive` package **0.6.11.post0+**. Sweeps `fmin`→`fmax`
in steps of `df`, recording `torque_setpoint` and `pos_estimate` by on-device high-rate capture at
the control-loop rate. Prompts before starting; type `q` to stop early.

Keep `duration` ≤ 1 s — with two captured variables the on-device buffer spans at most 1024 ms.

### Generate a waveform

```bash
aqtuator-multisine
```

`MAX_CSV_SAMPLES = 2000` must stay in sync with the firmware buffer.

## Debugging

When PWM output looks wrong, validate in two stages — do not skip to stage B:

- **Stage A:** Controllino plus RC output only. Use `GET_STATUS` and measure the voltage directly.
- **Stage B:** only once stage A is proven, connect the ODrive.

The 2026-03-31 investigation found the PWM path had been working all along; the fault was in the
host-side ODrive lifecycle being insufficiently observable. If a run misbehaves, compare the printed
`gpio1_mode`, endpoint, min/max, control mode and input mode against a working manual GUI session
before changing firmware.

## Working on Windows

This is a Windows machine and the shell is PowerShell. Four of the eight entries in
[`docs/mistakes/`](mistakes/) are bash syntax used in PowerShell — no `&&`, no bash heredocs, no
`cd /d`.

## FreeCAD for agents (optional)

Only needed if you want an agent to help you build a CAD model. An agent then works inside the
FreeCAD window you have open, on the same model you are looking at. It can measure and change the
geometry. It can never save the file — that stays your keystroke. The reasoning is in
[`doqs/docs/agent-cad.md`](../doqs/docs/agent-cad.md).

**Install the add-on once.** FreeCAD needs a small add-on, which is not in the FreeCAD add-on list,
so you copy it in by hand. Close FreeCAD first, then in PowerShell:

```powershell
git clone https://github.com/neka-nat/freecad-mcp.git
Copy-Item -Recurse freecad-mcp\addon\FreeCADMCP "$env:APPDATA\FreeCAD\v1-1\Mod\"
```

FreeCAD 1.1 for Windows keeps a folder per version. `%APPDATA%\FreeCAD\v1-1\Mod` is the right
one; `%APPDATA%\FreeCAD\Mod`, which several guides still name, is not read at all. Check the
version folder against your own FreeCAD if you run something other than 1.1.

**Install the bridge program once.**

```powershell
uv tool install --system-certs freecad-mcp
```

`--system-certs` is needed on this network. Without it every download fails with a certificate
error — see [`docs/mistakes/2026-09-17_uv-download-certificate.md`](mistakes/2026-09-17_uv-download-certificate.md).

**Switch it on when you want help.** Start FreeCAD, open the workbench list in the top toolbar and
choose **MCP Addon**. In the **FreeCAD MCP** toolbar that appears, click **Start RPC Server**. Do
this before you start the agent session, because the connection is made once, at the start.

The add-on can run any command inside FreeCAD, so leave it off when you are not using it, and leave
**Remote Connections** off. It listens on this computer only, on port 9875.

## Agent guidance

Root [`AGENTS.md`](../AGENTS.md) is the entry point for Cursor and Claude Code. Shared rules and
skills live in [`.agents/`](../.agents/). Repo-specific skills are under
[`.agents-local/skills/`](../.agents-local/skills/). Coding patterns:
[`.agents-local/skills/patterns/SKILL.md`](../.agents-local/skills/patterns/SKILL.md).

