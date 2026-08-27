# 2026-03-20 — Stepper eigenfrequency

**Role(s):** engineering

- Eigenfrequency of the stepper motor on the Mekanika Pro X-axis:

  - f = sqrt(150e6/8)/(2\*pi) = 689 Hz

  - This is probably the frequency spike we see in the FRF measurement.

- Consequence:

  - Stepper motors have little damping and will cause frequency spikes at high frequencies.

  - This makes **servo drives better for reducing chatter**.

  - AQTUATOR concept could even further reduce unwanted chatter peaks from not exciting the structure.
