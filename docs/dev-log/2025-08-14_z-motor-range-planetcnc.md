# 2025-08-14 — Z motor range PlanetCNC

- Adjusted the Z-motor range and limits in PlanetCNC

  - [<u>Mekanika Pro S Upgraded - PlanetCNC settings</u>](https://docs.google.com/document/d/1UhyuXBgLY0LHlipag9wteZVD6MOwPljqlF_N65DBadU/edit?usp=sharing)

- Aligned X-axis with Z-axis (squareness)

  - 70 µm over 50 mm

  - Best I could do because the screw heads that attach the Z-axis plate to the guides of the X-axis are blocking any movement.

- Trammed the spindle to 5 µm over maximum radius capable with dial gauge.

- Checked lubrication. Still works.

<!-- -->

- Design data acquisition and motion system

  - G-code generation

  - Encoder readout

  - Acceleration measurement

  - Data acquisition

    - Accelerations

    - Encoder positions

    - Setpoint commands

- Current drivers in Mekanika Pro:

  - Stuck to bottom, probably using double side heat conductive tape.

  - 118 x 35 mm x 88 mm (including double sided heat-conductive tape)

- Idea

  - Replace stepper drivers with servo drives

    - ODrive seem suitable

  - Replace connectors (only 4 pins available)

    - Use “servo motor cables”

      - 3 twisted pairs for differential encoder signals

      - Power cables

  - Use the ODrive current/torque feedforward to feed the analog input

    - [<u>https://claude.ai/share/43ce9739-a7d3-4db8-9c4c-494f51f45e5f</u>](https://claude.ai/share/43ce9739-a7d3-4db8-9c4c-494f51f45e5f)

    - If needed, pre-filter the analog input in a separate controller or digital filter (check Notion), because the current controller needs to be optimized for the current control and sees a different system as the acceleration control system.
