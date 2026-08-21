# 2026-01-12 — ODrive limitations

- Limitations of ODrive:

  - No feedforward from position setpoint to torque possible.

    - You can use POS_FILTER as the input_mode though: [<u>https://docs.odriverobotics.com/v/latest/fibre_types/com_odriverobotics_ODrive.html#ODrive.Controller.InputMode.POS_FILTER</u>](https://docs.odriverobotics.com/v/latest/fibre_types/com_odriverobotics_ODrive.html#ODrive.Controller.InputMode.POS_FILTER). Then at least the velocity is in feedforward.

  - Doing identification of servo drive through CAN not accurate

- Solution:

  - Read step/dir in Controllino and send feed-forward together with torque command from Controllino.

  - Tuning of servo position controller: manually.
