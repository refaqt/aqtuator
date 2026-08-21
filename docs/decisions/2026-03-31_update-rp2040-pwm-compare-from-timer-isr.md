# 2026-03-31 — Update RP2040 PWM compare from timer ISR

**Context:** The Controllino identification sketch logged the commanded CSV torque in the timer ISR, but deferred the actual PWM hardware write to `loop()`. That introduced timing skew and possible skipped intermediate duty values whenever the main loop lagged behind the sample timer.
**Decision:** Keep PWM configuration as a one-time `setup()` step, but move the real-time duty application into the timer ISR using the RP2040 low-level PWM API (`pwm_set_chan_level` / `pwm_set_gpio_level`) instead of calling high-level Arduino `analogWrite()` from the interrupt.
**Alternatives considered:** Keep the `loop()` handoff and relabel the input channel as the applied command; call `analogWrite()` directly from the ISR.
**Consequences:** The commanded CSV torque remains the transfer-function input while the physical PWM compare update occurs on the same sample tick as acquisition. Future firmware must avoid re-running `analogWriteFreq()`, `analogWriteRange()`, slice init, or `gpio_set_function()` from ISR context.
