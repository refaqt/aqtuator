# torque-excitation

Controllino MICRO (RP2040) firmware that plays a torque waveform as PWM into ODrive `GPIO1` while
sampling analog channels on the same timer tick, for system identification of the machine.

Full specification: [`docs/specification.md`](docs/specification.md).

## How it works

A host uploads a multisine waveform over serial. A repeating RP2040 timer ISR drives **both** the PWM
compare update and the ADC sample on one tick, so command generation and acquisition stay
synchronous. The PWM output passes through an RC network and reaches the ODrive as an analog torque
setpoint.

```
host (software/identification) --serial--> torque-excitation --PWM+RC--> ODrive GPIO1 (analog in)
                               <--DATA---
```

## Serial protocol

| Command | Response |
| --- | --- |
| `UPLOAD_CSV,<num_lines>` | `READY`, then `ACK: CSV loaded` or `NACK: CSV load failed` |
| `START_OUTPUT,<duration>` | `ACK: Output started`; serial is blocked during output; `ACK: Output complete` on finish |
| `START_IDENTIFICATION,<acq_duration>,<acq_start_delay>` | `ACK: Identification started`; playback begins at once, acquisition after the delay; `ACK: Acquisition complete` on finish |
| `GET_DATA` | `DATA:<sample_count>,<sample_period>,2`, then one line per sample of `torque_command,x_spindle`, terminated by `DATA_END` |
| `GET_STATUS` | Runtime PWM debug state: mode, slice/channel, GPIO function, requested/written duty, `CC A`/`CC B` compare registers, `TOP`, `CSR`, write counters |

Serial is deliberately blocked during real-time output — see
[the decision record](../../docs/decisions/2026-03-23_blocking-serial-during-real-time-operation.md).

## Safety invariants

**PWM must idle at 0 Nm, not 0 % duty.** ODrive `GPIO1` has a pull-up, so 0 % duty does not yield 0 V
after the RC network and maps to a non-zero, negative torque. See
[the decision record](../../docs/decisions/2026-03-30_hold-0-nm-at-idle-and-gate-odrive-analog-endpoint.md).

**`gpio1_mode` must stay `ANALOG_IN`** whenever the analog torque path is expected to work. This is a
monitored runtime invariant on the host side, not merely a setup step —
[decision record](../../docs/decisions/2026-03-31_treat-odrive-gpio1-mode-as-a-runtime-invariant.md).

**Debug in two stages.** Stage A: Controllino plus RC output only, using `GET_STATUS` and a direct
voltage measurement. Stage B: only once the RC output is proven correct, connect the ODrive. The
2026-03-31 investigation concluded the PWM path was working all along and the fault lay in the
host-side ODrive lifecycle being insufficiently observable.

## Pin mapping

For `controllino_rp2` sketches, treat MICRO header `GPIO0`/`GPIO1` as Arduino pins `D0`/`D1`
directly. **Do not** derive Arduino pin indices from the RP2040 package-pin numbers in the chip
pinout drawing. Sources of truth: the Controllino MICRO datasheet and block diagram in
[`docs/documentation/`](../../docs/documentation/), and `controllino_rp2`'s `pins_arduino.h`
(`D0 = 0u`, `D1 = 1u`). See
[the decision record](../../docs/decisions/2026-03-23_controllino-gpio-label-to-arduino-pin-mapping.md).

## Build

Arduino IDE with the `controllino_rp2` core. The sketch folder name must match the `.ino` name, so
this target keeps the Arduino layout rather than the `src/main.cpp` layout in the doqs firmware
example.

`PWM_RUNTIME_MODE` is a compile-time switch between mixed Arduino setup with low-level ISR updates,
fully low-level PWM setup, and `analogWrite()` inside the ISR as a fallback experiment.
