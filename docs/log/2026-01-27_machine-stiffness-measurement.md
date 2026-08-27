# 2026-01-27 — Machine stiffness measurement

**Role(s):** engineering

**Measure stiffness of machine**

- Dial gauge in spindle, measuring to worktable

- Pull on spindle nut with force gauge.

- 100 N

- 140 µm

**Controllino MICRO input scaling**

- Accelerometer measured with

  - DataQ system: 2.5021 V

  - Controllino (unplugged from DataQ):

    - USB powered:

      - 1467500 / 2^24 \* 28V = 2.4492 V

    - 12V Meanwell power source:

      - <span class="mark">1464924</span> → 2.4449 V

- TODO:

  - Change the gain to improve accuracy:

    - [<u>https://claude.ai/chat/39030f5d-6e06-48a7-a1a9-9772e6389d7d</u>](https://claude.ai/chat/39030f5d-6e06-48a7-a1a9-9772e6389d7d)

  - Look up ADC accuracy

  - Check DI analog inputs as well.
