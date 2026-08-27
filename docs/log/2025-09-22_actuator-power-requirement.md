# 2025-09-22 — Actuator power requirement

**Role(s):** engineering

- Power required

  - Assumption: the power required from the actuator equals the power introduced into the system by the cutting operation.

  - Parameters

    - F: cutting force

    - M: mass of axis

    - w: excitation frequency

    - A: excitation amplitude

  - [<u>https://chatgpt.com/share/68cf936f-a8ac-800f-b051-6097d2f25e1f</u>](https://chatgpt.com/share/68cf936f-a8ac-800f-b051-6097d2f25e1f)

  - P = F ¨\* v_M = M \* a_M \* v_M = M \* A \* w^2 \* cos(w\*t) \* A \* w \* sin(w\*t) = M \* A² \* w³ \* sin(2\*w\*t) / 2

  - A = F / (M \* w²)

  - P = F² / (2 \*M \* w)

  - Examples

    - F = 400N, w = 5000 rpm / 60 \* 2 \* pi \* 3 rad/s, M = 8 kg

      - P = 6.4W

- Is the frequency in the formula above equal to the spindle speed, as the chatter occurs at the machine’s resonant frequency?

  - The system is a mass-spring-(damper) system, with the spring including the cutting stiffness

  - When the power added from the cutting force variation exceeds the power that is dissipated by the damping, chatter occurs.

  - We can assume that the power added to the spring and mass is the worst case power we need to dissipate.

- Power from spring

  - P = k \* x \* v = k \* A² \* w \* sin(w \* t) \* cos(w\*t) = k \* A² \* w \* sin(2\*w\*t) / 2

  - A = F / k

  - P = F² \* w / (2\*k)

- Forget about the power from the process force. We only need to calculate what is the force and then calculate the power of the actuator by:

  - P = F \* v = m \* A² / 2 \* w³ \* sin(2\*w\*t)

  - v = A\*w\*sin(w\*t)

  - F = m\*A\*w²\*cos(w\*t) (provides amplitude A)
