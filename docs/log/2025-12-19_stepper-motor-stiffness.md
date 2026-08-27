# 2025-12-19 — Stepper motor stiffness

**Role(s):** engineering

- How to calculate the stiffness of stepper motors?

  - N = 200 poles (1.8° per pole)

  - T = 2.8 Nm holding torque

  - p = 10 mm pitch

  - Stiffness = slope of force vs displacement

  - k = N \* T \* (2pi / p)^2

    - N = 200

    - T = 2.8

    - P = 0.01m

    - K = 220 N/µm

- Stiffness of stepper motors is therefore much higher than we will ever achieve with a servo motor.

  - Consider closed loop stepper motor with linear encoder feedback for higher precision (but will the bandwidth and stiffness then drop?)

  - OR: calibrate and do op6en loop?
