# 2025-10-16 — Spindle speed verification

- Found out that spindle was operating at 367Hz When getting command of 24000 rpm. Check with sound signal that it was also actually rotating at 367 Hz, so definitely offset.

  - In the control box, the PWM output of the PlanetCNC controller is converted to a 0-10V signal.

  - Adjusted the potentiometer on this component to make sure that 24000 rpm equals 400Hz.
