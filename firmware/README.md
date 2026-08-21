# Firmware

Controllino MICRO (RP2040) targets, built with the Arduino IDE and the `controllino_rp2` core.

| Target | Role |
| --- | --- |
| [`torque-excitation`](torque-excitation/) | Plays a torque waveform as PWM into ODrive `GPIO1` while sampling analog channels on the same timer tick. The identification workhorse. |
| [`spindle-controller`](spindle-controller/) | Standalone 8 kHz closed-loop spindle controller: lead-lag, 2nd-order low-pass and two notches. |
| [`pwm-output-test`](pwm-output-test/) | PWM sine output test with the f_pwm / resolution / ripple trade-off documented in the sketch. |
| [`adc-test`](adc-test/) | 6-channel 8 kHz ADC test (RP2040 ADC + MCP3564RT). |

Host-side code that talks to these lives in [`software/`](../software/).

## Arduino layout

Arduino requires the sketch folder name to match the `.ino` filename, so these targets keep the
Arduino sketch layout rather than the `src/main.cpp` layout shown in the doqs firmware example.

## Pin mapping

Treat MICRO header `GPIO0`/`GPIO1` as Arduino pins `D0`/`D1` directly. Do not derive Arduino pin
indices from RP2040 package-pin numbers — see
[the decision record](../docs/decisions/2026-03-23_controllino-gpio-label-to-arduino-pin-mapping.md).
