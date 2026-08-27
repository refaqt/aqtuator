# 2025-12-01 — High speed circular motion steppers

**Role(s):** engineering

- Testing high-speed circular motion with stepper motors

  - Circular motion with 0.02 amplitude, F2000

    - Following characteristics:

|                 |               |        |
|-----------------|--------------:|--------|
| Force           |           200 | N      |
| Mass            |             8 | kg     |
| Acceleration    |            50 | m/s²   |
| Spindle speed   |          5000 | rpm    |
| Number of teeth |             3 | \-     |
| Frequency       |           250 | Hz     |
| Frequency       |   1570.796327 | rad/s  |
| Amplitude       | 0.02026423673 | mm     |
| Velocity        |   31.83098862 | mm/s   |
| Feed            |   1909.859317 | mm/min |

- Acceleration in PlanetCNC settings: 25.000 mm/s²

  - Worked

    - Ball screw is vibrating

    - X-axis: no motion detected (didn’t check with accelerometers)

- Acceleration in PlanetCNC settings: 50.000 mm/s²

  - Didn’t work

    - Strange sound, no vibration detected

<!-- -->

- F2121, Amplitude 0.05 mm

|                 |           |          |
|-----------------|-----------|----------|
| **Parameter**   | **Value** | **unit** |
| acceleration    | 25        | m/s²     |
| **From radius** |           |          |
| radius          | 0.05      | mm       |
| frequency       | 112.54    | Hz       |
| speed           | 35.36     | mm/s     |
| feed            | 2121.32   | mm/min   |

- Worked, but horrible sound of the machine, like everything is rattling loose

<!-- -->

- 125Hz, F1145, A0.024

|              |               |        |
|--------------|--------------:|--------|
| acceleration |            15 | m/s²   |
| frequency    |        125.00 | Hz     |
| radius       | 0.02431708407 | mm     |
| speed        |         19.10 | mm/s   |
| feed         |       1145.92 | mm/min |

- Worked. Vibrations clearly felt in ball screw, gantry and spindle.

<!-- -->

- Arduino Giga HAL configuration doesn’t work.

- Investigated STM32-NUCLEO options: [<u>https://claude.ai/chat/126bf5ca-0dd9-4d3d-829c-73804c9c586d</u>](https://claude.ai/chat/126bf5ca-0dd9-4d3d-829c-73804c9c586d)

  - To be checked if this is feasible and still in stock

- Done FTO research on the accelerometer feedback.

  - At first sight, no problem with FTO

    - On espacenet: accelerometer chatter control machine tool

      - Only IDEKO patent, but withdrawn

    - accelerometer chatter feedback control drive

<span class="mark">Todo:</span>

- FTO research accelerometer feedback chatter control drives.

  - Check espacenet and google patents

  - Use Gemini

- FTO Research reaction mass:

  - I would like to have a Freedom-to-Operate research on a linear motion system or actuator. The actuator consists of a slide, a ball-screw, linear guides, a linear encoder, a rotative motor (stepper, DC or BLDC) and a base. The slide's motion is constraint by the guides. The slide is connected to the nut of the ball screw. The ball screw and motor are connected to the base via a spring mechanism. The spring mechanism acts such that the motor-ballscrew combination can apply a force on the slide through the nut, but the counter-force, that would normally go through the frame, is directed through the inertia of the motor-ballscrew combination. When the slide accelerates, the motor-ballscrew combination will accelerate in opposite direction, and the spring counteracts this force and leads the force through the frame. In this way, high-frequency accelerations are filtered from the base. The goal of the invention is to enable high accelerations while keeping the base from being excited. The advantage is also that relatively cheap stepper motors could be used for the motor to provide linear-motor-like performance with high forces. Please check for FTO in the EU and the US.

    - [<u>https://gemini.google.com/share/18757d08ddd3</u>](https://gemini.google.com/share/18757d08ddd3)
