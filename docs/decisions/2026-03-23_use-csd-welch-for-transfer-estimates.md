# 2026-03-23 — Use CSD/Welch for transfer estimates

**Context:** The project needs a robust frequency-domain estimate of gain/phase between an excitation (torque/command) and a measured response (position or derived outputs).
**Decision:** Estimate transfer function using cross-spectral density and auto-spectral density:
- `H = Pxy / Pxx` where `Pxy` is from `scipy.signal.csd` and `Pxx` is from `scipy.signal.welch`.
**Alternatives considered:** FFT-based single-record transfer, pure FFT magnitude/phase at the excitation bin, or time-domain system identification.
**Consequences:** Consistent behavior across scripts; reduced sensitivity to noise vs naive single FFT, but still depends on windowing/segment length choices (`nperseg`).
