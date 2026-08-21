# 2025-11-04 — Servo motor setup

- Setup servo motor

  - Position measurement (RS485_encoder_group0 \> raw):

    - 1/(0.52716105-0.52709941) = 16223.232

      - Ok

  - Raw32 is the bit-value and is most accurate

- Spinout error

  - Velocity control, 0.5 Gain![](images/2025-11-04-01.png)

  - Velocity control, 0.8 gain

    - ![](images/2025-11-04-02.png)\
      ![](images/2025-11-04-03.png)

    - Increase limits to mechanical power spinout limit to -20:\
      ![](images/2025-11-04-04.png)

    - Increase limits to mechanical power spinout limit to -100:\
      ![](images/2025-11-04-05.png)
