# pwm-rc-filter

Numerical trade-off between PWM resolution and RC low-pass corner frequency for the torque-command
path: `firmware/torque-excitation` emits PWM, an RC network smooths it, and the result drives ODrive
`GPIO1` as an analog torque setpoint.

Higher PWM resolution costs carrier frequency, which raises ripple; a lower RC corner suppresses
ripple but limits command bandwidth. The script sweeps both and reports the resulting ENOB.

**Tool:** Python (numpy, scipy, matplotlib).

```bash
python pwm_filter_optimizer.py
```

No hardware required. The hardware measurements this informs are in the dev-log entry
[2026-03-25 — ODrive analog torque input](../../../docs/log/2026-03-25_odrive-analog-torque-input.md).
