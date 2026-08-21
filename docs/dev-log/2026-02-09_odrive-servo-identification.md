# 2026-02-09 — ODrive servo identification

**Odrive servo identification**

- Only read buffer when buffer is empty and wait time is longer than ts/2. Then just take sample as packet and don't discard torque or position.
