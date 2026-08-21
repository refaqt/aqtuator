# 2026-01-28 — Controllino MCP analog scaling

**Controllino Micro MCP Analog input scaling**

- Experiment

  - 2X gain, USB power, measured accelerometer voltage

    - 1467844/2^24\*28

      - ans = 2.4497 V

  - Changed gain to 8X, measured accelerometer voltage:

    - 12V power supply

      - 5783676/2^24\*28\*2/8

        - 2.4131 V

      - 5786676/2^24\*28\*2/8

        - 2.4144 V

    - USB power supply

      - 5795444/2^24\*28\*2/8

        - 2.4180 V

- Conclusion

  - There is a deviation of 0.04 because of the scaling, and a deviation of 0.1V with respect to the value measured by the dataQ device.

**Controllino Micro ADI Analog Input scaling**

- **Experiments**

  - 2X gain, DI0, 2.5V voltage from accelerometer:

    - Readout value: 1486848

    - 28V range:

      - 1486848 / 2^24 \* 28 = 2.481V

    - 25.8V range

      - 1486848 / 2^24 \* 25.8 = 2.286V

  - 8X gain doesn’t change the value. **The gain doesn’t affect the ADI analog inputs.**

**Voltage drop when connecting to both DataQ DI-2108 and Controllino Micro (with 12V power supply)**

- Separate measurements:

  - DI-2108: 2.50 V

  - Controllino: 1486848

    - 1486848/2^24\*28 = 2.4814 V

- Both connected to signal:

  - DI-2108: 2.21 V

  - Controllino:

- Both connected to signal, but DataQ unplugged:

  - Controllino: 1482752/2^24\*28 = 2.475

- Measure current:

  - 284 µA when both DataQ and Controllino are connected

  - 283 µA when only Controllino is connected

  - 0.8 µA when only DataQ is connected
