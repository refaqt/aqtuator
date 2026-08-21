# 2026-03-23 — Blocking serial during real-time operation

**Context:** During waveform playback and acquisition, the microcontroller must maintain tight timing. Any extra serial parsing can introduce jitter and risk buffer overruns.
**Decision:** Block serial reads while acquisition/output is active (and send completion acknowledgements only once the real-time window ends).
**Alternatives considered:** Keeping serial parsing active during acquisition (risking timing jitter and data corruption), or streaming during acquisition (more complex framing/backpressure).
**Consequences:** Host-side code must treat acquisition/output as a non-interactive critical section; Python waits for `ACK: ... complete` before issuing `GET_DATA`.
