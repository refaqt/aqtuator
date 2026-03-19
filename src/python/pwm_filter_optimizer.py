"""
PWM Filter Optimizer
====================
Finds the optimal PWM bit depth for a Controllino Micro (125 MHz system clock)
driving a passive RC low-pass filter, by minimising total output noise.

System parameters
-----------------
- MCU clock       : 125 MHz
- PWM frequency   : f_pwm = 125e6 / 2^N  (N = PWM bits)
- Reference check : N=12 → f_pwm = 30.5 kHz  ✓
- Filter          : R = 330 Ω, C = 100 nF  (f_-3dB ≈ 4 kHz, 2-stage)
- Supply voltage  : Vcc = 3.3 V

Noise model
-----------
Two independent error sources are combined as total RMS noise:

  1. PWM ripple (dominant harmonic at f_pwm, 50 % worst-case duty cycle)
       1st-order : |H1| = 1 / sqrt(1 + (ω·RC)²)
       2nd-order : |H2| = 1 / sqrt((1 - (ω·RC)²)² + 9·(ω·RC)²)
       V_ripple_rms ≈ (2·Vcc / π) · |H(f_pwm)| / sqrt(2)   [sine approx.]

  2. Quantisation noise
       V_q_rms = (Vcc / 2^N) / sqrt(12)

  Total : V_total = sqrt(V_ripple_rms² + V_q_rms²)

Optimum = bit depth N that minimises V_total_rms.

ENOB (Effective Number Of Bits) = log2(Vcc / (V_total · sqrt(12)))
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── System constants ──────────────────────────────────────────────────────────
F_CLK   = 125e6          # Controllino Micro system clock [Hz]
VCC     = 3.3            # PWM high level [V]
R       = 330.0          # Filter resistor [Ω]  (nearest E24 to 319 Ω)
C       = 100e-9         # Filter capacitor [F]
RC      = R * C          # Time constant [s]

BIT_MIN = 4
BIT_MAX = 16

# ── Derived sweep arrays ───────────────────────────────────────────────────────
bits      = np.arange(BIT_MIN, BIT_MAX + 1)          # integer bit depths
f_pwm     = F_CLK / (2.0 ** bits)                    # PWM fundamental [Hz]
omega_pwm = 2 * np.pi * f_pwm                        # angular frequency

# ── Filter transfer-function magnitudes at f_pwm ─────────────────────────────
x = omega_pwm * RC   # normalised frequency (dimensionless)

H1 = 1.0 / np.sqrt(1.0 + x**2)                      # 1st-order (single stage)
H2 = 1.0 / np.sqrt((1.0 - x**2)**2 + 9.0 * x**2)   # 2nd-order (two cascaded stages, loaded)

# ── Noise contributions ────────────────────────────────────────────────────────
A_fund = (2.0 * VCC) / np.pi    # fundamental amplitude of a 50 % PWM [V_peak]

V_ripple1_rms = (A_fund * H1) / np.sqrt(2)   # 1st-order ripple RMS
V_ripple2_rms = (A_fund * H2) / np.sqrt(2)   # 2nd-order ripple RMS

V_q_rms = (VCC / (2.0 ** bits)) / np.sqrt(12)  # quantisation noise RMS

V_total1 = np.sqrt(V_ripple1_rms**2 + V_q_rms**2)
V_total2 = np.sqrt(V_ripple2_rms**2 + V_q_rms**2)

# ── Effective Number Of Bits ───────────────────────────────────────────────────
ENOB1 = np.log2(VCC / (V_total1 * np.sqrt(12)))
ENOB2 = np.log2(VCC / (V_total2 * np.sqrt(12)))

# ── Ripple peak-to-peak (for reference) ───────────────────────────────────────
V_ripple1_pkpk = 2 * A_fund * H1
V_ripple2_pkpk = 2 * A_fund * H2

# ── Find optima ───────────────────────────────────────────────────────────────
opt1_idx = np.argmin(V_total1)
opt2_idx = np.argmin(V_total2)

opt1_bits  = bits[opt1_idx]
opt2_bits  = bits[opt2_idx]
opt1_freq  = f_pwm[opt1_idx]
opt2_freq  = f_pwm[opt2_idx]
opt1_ENOB  = ENOB1[opt1_idx]
opt2_ENOB  = ENOB2[opt2_idx]
opt1_noise = V_total1[opt1_idx] * 1e3   # mV
opt2_noise = V_total2[opt2_idx] * 1e3

# ── Console report ────────────────────────────────────────────────────────────
SEP = "─" * 72

def freq_str(f):
    return f"{f/1e3:.2f} kHz" if f >= 1e3 else f"{f:.1f} Hz"

print(SEP)
print("  PWM FILTER OPTIMISATION — Controllino Micro @ 125 MHz")
print(SEP)
print(f"  Filter:  R = {R:.0f} Ω,  C = {C*1e9:.0f} nF")
print(f"  1st-order f_-3dB  ≈ {1/(2*np.pi*RC)/1e3:.2f} kHz")
print(f"  2nd-order f_-3dB  ≈ {0.8022/(2*np.pi*RC)/1e3:.2f} kHz")
print()
print(f"  {'Bits':>5}  {'f_PWM':>10}  {'Ripple1 pk-pk':>15}  {'Ripple2 pk-pk':>15}  "
      f"{'Q-noise':>10}  {'ENOB1':>6}  {'ENOB2':>6}")
print(f"  {'':>5}  {'':>10}  {'[mV]':>15}  {'[mV]':>15}  {'[mV]':>10}  {'[bits]':>6}  {'[bits]':>6}")
print("  " + "─"*70)
for i, b in enumerate(bits):
    marker1 = " ◄ OPT" if b == opt1_bits else ""
    marker2 = " ◄ OPT" if b == opt2_bits else ""
    print(f"  {b:>5}  {freq_str(f_pwm[i]):>10}  "
          f"{V_ripple1_pkpk[i]*1e3:>15.2f}  "
          f"{V_ripple2_pkpk[i]*1e3:>15.3f}  "
          f"{V_q_rms[i]*1e3:>10.3f}  "
          f"{ENOB1[i]:>6.2f}{marker1}  "
          f"{ENOB2[i]:>6.2f}{marker2}")

print()
print(SEP)
print("  OPTIMAL SETTINGS")
print(SEP)
print(f"  1st-order filter optimum:")
print(f"    PWM bits  = {opt1_bits} → f_PWM = {freq_str(opt1_freq)}")
print(f"    ENOB      = {opt1_ENOB:.2f} bits")
print(f"    Total RMS noise = {opt1_noise:.3f} mV")
print()
print(f"  2nd-order filter optimum:")
print(f"    PWM bits  = {opt2_bits} → f_PWM = {freq_str(opt2_freq)}")
print(f"    ENOB      = {opt2_ENOB:.2f} bits")
print(f"    Total RMS noise = {opt2_noise:.3f} mV")
print(SEP)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 10))
fig.suptitle("PWM Filter Optimisation — Controllino Micro (125 MHz)\n"
             f"R = {R:.0f} Ω, C = {C*1e9:.0f} nF  |  Vcc = {VCC} V  |  Worst-case 50 % duty cycle",
             fontsize=13, fontweight="bold")

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)

bit_ticks = bits

# ── Panel 1: Ripple pk-pk ─────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.semilogy(bits, V_ripple1_pkpk * 1e3, "o-", color="#e05c3a", lw=2, label="1st-order")
ax1.semilogy(bits, V_ripple2_pkpk * 1e3, "s-", color="#3a7ae0", lw=2, label="2nd-order")
ax1.set_xlabel("PWM Bits")
ax1.set_ylabel("Ripple pk-pk [mV]")
ax1.set_title("Output Ripple (pk-pk)")
ax1.set_xticks(bit_ticks)
ax1.grid(True, which="both", alpha=0.35)
ax1.legend()

# add secondary x-axis with f_pwm
ax1b = ax1.twiny()
ax1b.set_xlim(ax1.get_xlim())
ax1b.set_xticks(bit_ticks)
ax1b.set_xticklabels([f"{v/1e3:.0f}k" if v >= 1e3 else f"{v:.0f}"
                       for v in f_pwm], fontsize=7, rotation=45)
ax1b.set_xlabel("f_PWM [Hz]", fontsize=9)

# ── Panel 2: Quantisation noise ───────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.semilogy(bits, V_q_rms * 1e3, "D-", color="#20a080", lw=2, label="Q-noise RMS")
ax2.semilogy(bits, V_ripple1_pkpk * 1e3 / (2 * np.sqrt(2)), "--",
             color="#e05c3a", lw=1.5, alpha=0.7, label="Ripple RMS (1st)")
ax2.semilogy(bits, V_ripple2_pkpk * 1e3 / (2 * np.sqrt(2)), "--",
             color="#3a7ae0", lw=1.5, alpha=0.7, label="Ripple RMS (2nd)")
ax2.set_xlabel("PWM Bits")
ax2.set_ylabel("Noise RMS [mV]")
ax2.set_title("Noise Contributions (RMS)")
ax2.set_xticks(bit_ticks)
ax2.grid(True, which="both", alpha=0.35)
ax2.legend(fontsize=8)

ax2b = ax2.twiny()
ax2b.set_xlim(ax2.get_xlim())
ax2b.set_xticks(bit_ticks)
ax2b.set_xticklabels([f"{v/1e3:.0f}k" if v >= 1e3 else f"{v:.0f}"
                       for v in f_pwm], fontsize=7, rotation=45)
ax2b.set_xlabel("f_PWM [Hz]", fontsize=9)

# ── Panel 3: Total noise RMS ──────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
ax3.semilogy(bits, V_total1 * 1e3, "o-", color="#e05c3a", lw=2, label="1st-order total")
ax3.semilogy(bits, V_total2 * 1e3, "s-", color="#3a7ae0", lw=2, label="2nd-order total")

# Mark optima
ax3.axvline(opt1_bits, color="#e05c3a", lw=1.2, ls="--", alpha=0.7)
ax3.axvline(opt2_bits, color="#3a7ae0", lw=1.2, ls="--", alpha=0.7)
ax3.plot(opt1_bits, V_total1[opt1_idx] * 1e3, "*", color="#e05c3a",
         ms=14, zorder=5, label=f"1st opt: {opt1_bits} bits ({freq_str(opt1_freq)})")
ax3.plot(opt2_bits, V_total2[opt2_idx] * 1e3, "*", color="#3a7ae0",
         ms=14, zorder=5, label=f"2nd opt: {opt2_bits} bits ({freq_str(opt2_freq)})")

ax3.set_xlabel("PWM Bits")
ax3.set_ylabel("Total RMS noise [mV]")
ax3.set_title("Total Noise = √(Ripple² + Q-noise²)")
ax3.set_xticks(bit_ticks)
ax3.grid(True, which="both", alpha=0.35)
ax3.legend(fontsize=8)

ax3b = ax3.twiny()
ax3b.set_xlim(ax3.get_xlim())
ax3b.set_xticks(bit_ticks)
ax3b.set_xticklabels([f"{v/1e3:.0f}k" if v >= 1e3 else f"{v:.0f}"
                       for v in f_pwm], fontsize=7, rotation=45)
ax3b.set_xlabel("f_PWM [Hz]", fontsize=9)

# ── Panel 4: ENOB ─────────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
ax4.plot(bits, ENOB1, "o-", color="#e05c3a", lw=2, label="1st-order")
ax4.plot(bits, ENOB2, "s-", color="#3a7ae0", lw=2, label="2nd-order")
ax4.plot(bits, bits,  "k--", lw=1, alpha=0.4, label="Ideal (ENOB = bits)")

ax4.plot(opt1_bits, opt1_ENOB, "*", color="#e05c3a", ms=14, zorder=5,
         label=f"1st opt: {opt1_bits} bits → {opt1_ENOB:.1f} ENOB")
ax4.plot(opt2_bits, opt2_ENOB, "*", color="#3a7ae0", ms=14, zorder=5,
         label=f"2nd opt: {opt2_bits} bits → {opt2_ENOB:.1f} ENOB")

ax4.set_xlabel("PWM Bits")
ax4.set_ylabel("ENOB [bits]")
ax4.set_title("Effective Number of Bits (ENOB)")
ax4.set_xticks(bit_ticks)
ax4.grid(True, alpha=0.35)
ax4.legend(fontsize=8)

ax4b = ax4.twiny()
ax4b.set_xlim(ax4.get_xlim())
ax4b.set_xticks(bit_ticks)
ax4b.set_xticklabels([f"{v/1e3:.0f}k" if v >= 1e3 else f"{v:.0f}"
                       for v in f_pwm], fontsize=7, rotation=45)
ax4b.set_xlabel("f_PWM [Hz]", fontsize=9)

# plt.savefig("/mnt/user-data/outputs/pwm_filter_optimization.png", dpi=150, bbox_inches="tight")
# print("\n  Plot saved → pwm_filter_optimization.png")
plt.show()
