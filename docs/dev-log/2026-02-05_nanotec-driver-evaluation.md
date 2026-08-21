# 2026-02-05 — Nanotec driver evaluation

**Should we switch to Nanotec stepper motor driver?**

- Checked Nanotec C5-E and N5

- Have analog inputs, but can only be used at a rate of 1kHz in NanoJ programs.

- CANopen is also limited to 1kHz.

- Conclusion:

  - No, will not work. Stick to ODrive.

**Opamp unity gain amplifier for sensor outputs**

VOEDING:

Mean Well +12V --------+----\> LM324N Pin 4 (V+)

\|

\[100nF\] keramisch (DICHT bij chip!)

\|

Mean Well GND ---------+----\> LM324N Pin 11 (GND)

SIGNAAL:

Sensor Output (groen) -------\> LM324N Pin 3 (IN+)

LM324N Pin 2 (IN-) \<---------------+--- LM324N Pin 1 (OUT)

\|

+---\> Controllino & DataQ



- 100nF capacitor to prevent ripples of the source from entering opamp.
