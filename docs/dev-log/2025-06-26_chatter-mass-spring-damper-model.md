# 2025-06-26 — Chatter mass-spring-damper model

- Chatter mass-spring-damper-model:

  - F - (k_s + c_s \* s) \* X = (m \* s^2 + c \* s + k) \* X

    - Check model of PhD Dries Hemschoote for feedback factor (if previous cut cuts less material, next cut experiences higher force?), cutting stiffness and cutting damping.

    - This seems to suggest that cutting stiffness and damping add up to the stiffness and damping of the system.

    - Higher feed speed means higher forces, but is this part of the cutting stiffness or damping?

- Acceleration feedback:

  - <!-- A diagram here was a Word drawing canvas and did not survive export to markdown; see docs/log.docx in the Drive archive. -->

  - Y \* m \* s² = D - k \* s² \* Y

    - Y (k \* s² + m \* s²) = D

    - Y/D = 1 / ((k + m) \* s²)

  - K adds a virtual mass to the system.

  - The higher the gain at any frequency, the higher the virtual mass at this frequency.
