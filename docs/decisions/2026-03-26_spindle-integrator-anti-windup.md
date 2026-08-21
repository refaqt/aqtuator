# 2026-03-26 — Spindle controller: pure discrete integrator with hold anti-windup

**Context:** The spindle vibration controller output is clamped to safe torque bounds before converting to ODrive GPIO1 voltage/PWM. Without anti-windup, an integrator can accumulate error while saturated, causing long recovery and overshoot once it desaturates.
**Decision:** Use a raw discrete integrator \(z/(z-1)\) with **pure-integrated output** (torque command is the integrator state). Integrate the post-filter signal (after lead-lag + LPF + notches). Apply **anti-windup by holding** the integrator state constant whenever the torque command is clamped.
**Alternatives considered:** PI-style summing (\(y + I\)); conditional integration only when the update would move back toward range; back-calculation anti-windup.
**Consequences:** Simple, deterministic behavior under saturation; however the effective integrator scaling depends on upstream signal units and sample rate, so it may need a gain \(K_i\) later for practical tuning.
