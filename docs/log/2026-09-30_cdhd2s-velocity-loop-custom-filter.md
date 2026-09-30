# 2026-09-30 — Can the CDHD2S velocity loop run our own controller?

**Role(s):** engineering, hardware, purchasing

## Goal

The CDHD2S manual says the velocity loop, which runs at 8 kHz, has a "user-defined polynomial
filter". Can the drive run this controller in its velocity loop, in discrete-time form?

C(s) = K · (s + a) · (s + b) / ( s · (s² + c·s + d) )

The request wrote the last constant as `b`. The answer below uses `d`, so it covers both cases:
set d = b if that was meant.

If the drive can do this, and it also has EtherCAT, BiSS-C, 1 Vpp and runs the MAXWELL MK21, it
is a suitable drive.

## Work Done

### Short answer

- **Very likely yes, but not confirmed.** The velocity loop has a mode with free polynomials. It is
  called the "extended polynomial controller" (velocity controller mode 3). In that mode the drive
  also has two free second order output filters (a biquad each). Together they have more than
  enough order for our controller, which is third order.
- **The number format of these polynomials is not published.** The command manual lists the
  parameters, but it does not say which number is which coefficient, or how the numbers are
  scaled. We cannot load our own controller until Servotronix tells us, or until we measure it on
  a drive.
- **The free polynomials only exist in the command manual of the older CDHD2 (firmware 2.15).** The
  CDHD2S manual names the "advanced pole placement" controller and the "user-defined polynomial
  filter", but it has no details. There is no public command manual for the CDHD2S.
- **Using our own controller costs the 8 kHz position loop.** The free filters work only with the
  "linear" position controller, which runs at 4 kHz. The HD position controller at 8 kHz is a
  closed controller that we cannot change. The velocity loop itself still runs at 8 kHz.
- **With only the documented, simple settings, the controller cannot be built.** The simple PI
  velocity controller gives K · (s + a) / s exactly. But the filters that work with it (low-pass,
  double low-pass, notch) cannot make the extra zero at `b` together with a free pair of poles.
- **Every other requirement passes.** EtherCAT with CiA 402, BiSS-C, 1 Vpp, linear motors, and
  the MK21 currents all pass from the CDHD2S manual itself.

So the CDHD2S-003 is a suitable drive if Servotronix confirms two things: that the CDHD2S firmware
has velocity controller mode 3, and how its coefficients are written.

### What the drive offers in the velocity loop

| Setting | What it does | Free coefficients | Limit |
| --- | --- | --- | --- |
| Velocity controller mode 0 (PI) | K · (s + a) / s, set by two gains | No | Works with the fixed filters only |
| Output filter types 1, 2, 3, 7 | Low-pass, double low-pass, notch, notch with limited phase | No, only frequencies of 1 to 3500 Hz | Works in every linear mode |
| Velocity controller mode 3 (extended polynomial) | A general controller with three polynomials (R, D and H) | Yes: 10, 8 and 12 numbers | Format not published |
| Output filter type 6 (VF), second filter type 6 (VFEXT) | Two free second order filters in series after the controller | Yes: 7 numbers each | Only in mode 3. Format not published |
| Input filter (VFI) | A free filter on the velocity feedback | Yes: 7 numbers | Format not published |

The command manual has one example that hints at the format. A "do nothing" input filter reads
`1073741824 0 0 30 0 0 0`. 1073741824 is 2³⁰. So the numbers are most likely whole numbers,
scaled by a power of two, with the power (30) stored in the fourth place. That would give three
numerator coefficients, one scale and up to three denominator coefficients: a biquad. This is our
guess, not a published fact.

The drive has a command that converts a standard controller design into mode 3 numbers
(`VELDESIGN`). On a real drive, we can set a known PI controller, read the numbers it gives, and
work out the format ourselves. That is a fallback if Servotronix does not answer.

### The controller in discrete-time form

Split the controller into two parts, and convert each with the Tustin method at the velocity loop
period T = 125 µs. Write w = 2 / T = 16 000 s⁻¹.

**Part 1, the PI part:** K · (s + a) / s becomes

C₁(z) = g · (1 + p·z⁻¹) / (1 − z⁻¹), with g = K · (1 + a/w) and p = (a − w) / (a + w).

**Part 2, the second order part:** (s + b) / (s² + c·s + d) becomes a biquad. With
D₀ = w² + c·w + d:

| Coefficient | Value |
| --- | --- |
| b₀ | (w + b) / D₀ |
| b₁ | 2·b / D₀ |
| b₂ | (b − w) / D₀ |
| a₁ | 2·(d − w²) / D₀ |
| a₂ | (w² − c·w + d) / D₀ |

C₂(z) = (b₀ + b₁·z⁻¹ + b₂·z⁻²) / (1 + a₁·z⁻¹ + a₂·z⁻²)

The full controller is C(z) = C₁(z) · C₂(z). A numeric check against the direct Tustin conversion
of the whole controller agreed to 2 · 10⁻¹² (see the technical notes).

Two ways to put this into the drive, both in mode 3:

1. Put the PI part into the R, D and H polynomials, and part 2 into the output filter VF. This
   keeps the integrator inside the controller, where the drive can limit it.
2. Put the whole controller into the R, D and H polynomials, and leave VF and VFEXT free for a
   notch filter on a resonance.

If a corner frequency is above about 1 kHz, prewarp the Tustin method at that frequency. Below
1 kHz, the frequency error at 8 kHz is small.

### The other requirements, for the CDHD2S-003

| Req. | Needed | CDHD2S-003, from its own manual | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 3 A rms | Pass |
| DRV-02 | 5.9 A rms for 1 s | 9 A rms for 2 s | Pass |
| DRV-03 | Current limit and a motor thermal model | Motor peak and continuous current settings, and a "foldback" current limit that tracks the motor rms current | Pass |
| DRV-04 | Bus 160 V to 600 V | 120 or 240 VAC single phase, about 325 V bus at 230 VAC | Pass |
| DRV-05 | Linear synchronous motor, 30 mm period, finds the angle without Hall sensors | Linear motor type, motor pitch 0 to 100 000 mm, "Phase Find" routines that work without Hall sensors | Pass. Phase Find needs an axis without gravity load, which our horizontal stage is |
| DRV-06 | Reads the motor thermal sensor | PTC or NTC thermistor input, or an on/off thermostat, with a fault threshold | Pass, once MAXWELL confirms the sensor type |
| DRV-07 | EtherCAT with CiA 402 | EtherCAT models (EC, EB) with CANopen over EtherCAT and CiA 402 | Pass. Order an EtherCAT model |
| DRV-08 (1 Vpp) | 1 Vpp at 8.3 kHz | 1 Vpp sine and cosine, up to 300 kHz, interpolation up to 16 384 | Pass |
| DRV-08 (BiSS-C) | BiSS-C, full frame of the encoder | BiSS-C up to 26 bits, on the motor and on the second encoder input | Pass, if our BiSS-C encoder sends 26 bits or less |
| DRV-09 | Position loop 4 kHz or faster | 4 kHz linear position loop, 8 kHz HD controller | Pass |
| DRV-P1 | Free second order filters | Two free biquads plus a free polynomial controller, in mode 3 | Pass on paper, format not published |
| DRV-P2 | Published loop diagram | Diagrams for each velocity controller in the manual, but not for mode 3 | Partly |
| DRV-P3 | Position loop 8 kHz | Only with the HD controller, which cannot take our filter | Not with our own controller |

## Decisions Made

No purchase decision. The CDHD2S-003 with EtherCAT stays the best Servotronix choice. It now also
looks like the only drive found so far that may take a free controller in the velocity loop.

## Open Questions

Ask Servotronix:

1. Does the CDHD2S firmware have velocity controller mode 3 (extended polynomial controller), with
   the R, D, H polynomials and the VF and VFEXT filters?
2. What is the exact structure of mode 3, and the number format of VR, VD, VH, VF, VFEXT and VFI?
3. Can we write these values over EtherCAT while the drive is disabled? The CDHD2 manual gives
   EtherCAT addresses for them.
4. How does the integrator in mode 3 stop growing when the current is at its limit?
5. Is there a CDHD2S command manual (VarCom) we can have?

Also ask MAXWELL which thermal sensor the MK21 has, and check the frame length of the BiSS-C
encoder if we change to one.

## Next Steps

1. Send the questions above to Servotronix with the quote request for the CDHD2S-003 (EtherCAT).
2. When we have a drive, set a PI controller, read the numbers from `VELDESIGN`, and check the
   coefficient format against the formulas above.

<details>
<summary>Sources and technical notes</summary>

- CDHD2S user manual, version 1.12 (2023-11-01):
  <https://e-motors.tech/wp-content/uploads/2024/07/CDHD2S-Manual-V1.12-20231101-en.pdf>.
  Loop rates and the filter list on page 28 (velocity loop 125 µs, position loop 250 µs, HD
  125 µs; "user-defined polynomial filter"; "advanced pole placement"). Ratings on page 23.
  Feedback on page 32 (1 Vpp at 300 kHz, BiSS-C up to 26 bits, PTC or NTC input).
  EtherCAT models and CiA 402 on pages 11 to 12. Velocity loop diagrams on pages 188 to 191:
  they list only modes 0, 1, 2 and 7. Linear motor settings on page 119. Phase Find on pages 134
  to 135. Foldback current on page 151.
- CDHD2 and DDHD VarCom reference manual, firmware 2.15, revision 1.3:
  <https://stxim.com/wp-content/uploads/2024/01/CDHD2_DDHD_VarCom_fw2.15.x_Rev.1.3.pdf>.
  `FILTEXTMODE` page 145, `FILTHZ1` and `FILTHZ2` pages 146 to 147 (1 to 3500 Hz), `FILTMODE`
  page 148, `MPITCH` page 365, `PHASEFINDMODE` page 479, `VD` page 594, `VELCONTROLMODE` page 597,
  `VELDESIGN` page 599, `VF` page 604 ("Requires FILTMODE=6", "only in linear control mode and
  when VELCONTROLMODE=3"), `VFEXT` page 605, `VFI` page 606, `VH` page 608, `VR` page 612.
- CDHD2 user manual, firmware 2.38: no more detail on the polynomial controller.
- No CDHD2S VarCom manual was found online.
- Numeric check (scipy, T = 125 µs, K = 50, a = 2π·20, b = 2π·300, c = 2·0.3·2π·600,
  d = (2π·600)²): the product C₁·C₂ from the formulas above matched `scipy.signal.bilinear` of the
  full controller from 1 Hz to 4 kHz, largest relative error 1.8 · 10⁻¹². The discrete poles of the
  biquad sit at |z| = 0.874.
- Mistake rule applied: the loop-rate mistake of 2026-09-29. Every pass above comes from the
  maker's manual. Mode 3 and its filters come from the CDHD2 manual, not the CDHD2S manual, so
  they are marked "not confirmed" for the CDHD2S.

</details>
