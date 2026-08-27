# 2025-12-18 — Controllino CAN timing

**Role(s):** engineering

- Checking Controllino CAN communication

  - Check how long 1 CAN message takes

    - Torque command at 1 Mbps: approx 100 µs

  - Check how CAN messages are handled (one by one? 1 address, multiple messages?

    - Send and receive on the same wire, so they interfere with each other.

  - Can Controllino do FD-CAN, if needed?

    - No

  - Is analog voltage + CAN required? (CAN is required to get position setpoint)

    - Controllino cannot do analog voltage out.

  - We need to do CAN for the torque commands and UART to get position setpoints

    - Position setpoints should be filtered to avoid glitches. For instance oversample and do a prediction of the next positions by extrapolation. If a sample is too far off, it is replaced by the prediction

    - Prediction can also be used to provide higher rate acceleration setpoints to the acceleration controller.

  - How to mount Controllino?

    - Screws to DIN rail clamps

  - How to power Controllino?

    - Up to 36V power, 9-24V preferred
