# 2026-01-08 — Controllino analog inputs

**Role(s):** engineering

- Testing analog inputs of Controllino

  - 8.64V battery voltage

  - Analog inputs AI0-AI5: ~4,200,000 raw bit value

  - Digital/Analog inputs DI0-DI3: ~4,000,000 raw bit value

- Testing ADC sampling rate of controllino

  - Analog inputs at 1.15 kHz cannot be sampled faster. They block the ISR loop.

  - Removed these ADCs from identification and control loop.

- Tested control loop at 8kHz. Worked.
