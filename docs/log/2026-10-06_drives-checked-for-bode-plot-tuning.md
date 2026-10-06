# 2026-10-06 — Servo drives checked for a Bode plot tuning tool

**Role(s):** engineering, purchasing

## Goal

Check the servo drive requirements for the MAXWELL MK21 linear motor stage. Lower the position loop
limit to 4 kHz if it is still higher. Add a new requirement: the drive software must have a tuning
tool that shows Bode plots of the transfer function. Then find out which drives meet all
requirements.

## Work Done

### Short answer

- **The position loop limit was already 4 kHz** (DRV-09, since 2026-09-29). Nothing changed there.
- **New hard requirement DRV-10.** The maker's setup software measures the axis on the real machine
  and shows a Bode plot (gain and phase against frequency) of the plant, the open loop or the
  closed loop. It is in
  [`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml).
- **Two drives now meet all ten hard requirements in the maker's own manuals:** the Kollmorgen AKD
  (first generation, model AKD-x00306 with EtherCAT) and the Copley Xenus Plus XEL-230-18. Both
  have a 4 kHz position loop. Both were left out earlier only because the limit was then 8 kHz.
  Neither price is confirmed.
- **The chosen drive, the Servotronix CDHD2S, does not meet DRV-10 as documented.** Its software
  shows a frequency response with gain only, no phase, and no Bode plot. Ask Servotronix whether a
  newer software version shows phase. Until then it is "not confirmed".
- **The fallback drive, the Delta ASDA-A3, meets DRV-10.** It still fails DRV-08 as written (it needs
  a converter box for 1 Vpp), and its position loop rate is still not confirmed.
- **Close candidates that meet DRV-10 but miss a check elsewhere:** Kollmorgen AKD2G (over
  budget), KEBA ServoOne junior (125 µs position loop, but the linear motor mode and the thermal
  input were never checked, and KEBA must approve the encoder), Triamec TSD350 (expensive).

### DRV-10 for each drive

Pass and Fail come from the maker's own document. NC means not confirmed.

| Drive | Software | DRV-10 | What it shows | Source |
| --- | --- | --- | --- | --- |
| Servotronix CDHD2S, CDHD2 | ServoStudio 2 | NC, leans to Fail | "Show Frequency Response" of the current command, gain only, linear scale, no phase. The drive can excite the axis with noise (command IDENT) | [ServoStudio 2 Reference Manual Rev 1.1](https://stxim.com/wp-content/uploads/2024/01/CDHD2_DDHD_ServoStudio2_fw2.15.x_Rev_1.1-1.pdf), p. 103, Figure 26-13. [VarCom Reference Rev 1.3](https://stxim.com/wp-content/uploads/2024/01/CDHD2_DDHD_VarCom_fw2.15.x_Rev.1.3.pdf), p. 228 |
| Delta ASDA-A3 | ASDA-Soft, System Analysis | Pass | Speed open loop as a Bode plot. A plant analysis type also exists | [ASDA-A3 User Manual 2025](https://www.damencnc.com/userdata/file/7617-5_Delta_ASDA_A3_Manual_English_2025.pdf), section 5.7.1.4, p. 5-49 |
| Kollmorgen AKD (first generation) | WorkBench, Performance Servo Tuner | Pass | Plant, closed loop and open loop. Noise, pseudo-random or sine excitation | [AKD User Guide Rev K](https://inmoco.co.uk/wp-content/uploads/2022/01/AKD-Servo-Drive-User-Guide.pdf), p. 189 to 204 |
| Kollmorgen AKD2G | WorkBench | Pass, weaker source | Same tool as the AKD. The AKD2G help pages blocked downloads | [AKD2G brochure](https://gmsi-co-jp.prm-ssl.jp/files/Kollmorgen_AKD2G_Servo_Amplifier_Brochure_EMEA1.pdf), p. 2: "Wizard-based tuning uses advanced Bode Plot tool" |
| Copley Xenus Plus XEL-230-18 | CME, Frequency Analysis | Pass | Sine sweep. Magnitude and phase of closed loop current and velocity, open loop velocity, the velocity plant, and open loop position | [CME User Guide Rev 02](https://actuation.curtisswright.com/sites/default/files/Resources/CW-CME-User-Guide.pdf), chapter 18, p. 172 to 178 |
| KEBA (LTi) ServoOne junior | DriveManager 5 | Pass | Gain and phase of the speed loop and the current loop, with a noise test signal | [ServoOne Device Help](https://www.etranstechnik.fr/mat/LTI_Servo_One/documentation/S-One/ServoOne_Device_help_PDF_format_EN.pdf), section 5.13, p. 106 to 107 |
| Triamec TSD350 | TAM System Explorer | Pass | Measured open loop with sine excitation, gain and phase | Triamec Servo Drive Setup Guide EP030 (triamec.com, Documents page), section 4.2, p. 33 to 40 |
| Elmo Gold Oboe | EASII | Pass, weaker source | Plant, open loop or closed loop. Multi-sine or sine sweep | [Elmo plant identification page](https://www.elmomc.com/capabilities/servo-technology/servo-tools/plant-identification-methods/). No full manual found |
| HIWIN E2 Advanced | Thunder, Frequency analyzer | Pass | Measured plant as a Bode plot. Loops worked out from it | [Thunder Software Operation Manual V3.5](https://www.hiwin.com/wp-content/uploads/E-Series-Servo-Drive-Thunder-Software-Operation-Manual-V3.5-EN.pdf), section 6.3, p. 6-10 |
| Bosch Rexroth ctrlX DRIVE | ctrlX DRIVE Engineering | Pass, weaker source | Frequency response analysis of plant and closed loops, gain in dB and phase | Rexroth application note on the [Rexroth community site](https://community.boschrexroth.com/ctrlx-automation-how-tos-qmglrz33/post/check-regulation-loop-settings-by-using-frequency-response-analysis-with-sb6ZU9dHthIRqYy) |
| Yaskawa Sigma-7 | SigmaWin+, Mechanical Analysis | Pass | Plant gain and phase graphs | [SigmaWin+ Operation Manual](https://www.e-mechatronics.com/download/tool/servo/sgmwinplsver7/en/SIETS80000134.html), section 6.5.7 |
| Beckhoff AX8000 | TwinCAT 3 Bode Plot TE1320 (separate licence) | Pass | Open loop, closed loop and plant | [TE132x manual](https://download.beckhoff.com/download/document/automation/twincat3/TE132x_TC3_BodePlot_EN.pdf), p. 8 and 25 |
| Inovance SV680N | InoDriverShop | Pass | Plant, speed open loop and speed closed loop, sweep excitation | [SV680N-INT User Guide B00](https://portal-file.inovance.com/owfile/ProdDoc/SC/PS00021314_PDF_EN/B00/SV680N-INT%20Series%20Servo%20Drive%20User%20Guide-EN-B00.PDF), p. 293 to 296 |
| Metronix smartServo BL 4104-C | Metronix ServoCommander | Fail | Oscilloscope only. Auto-tuning identifies the system but shows no plot | [BL 4000-C manual v2.0](https://www.metronix.de/fileadmin/user_upload/Dokumente/Downloads-EN/Manuals/BL_4000_C_M_D/P-HB_BL_4000-C_2p0_EN.pdf), p. 27 and 57 |
| Advanced Motion Controls DPEANIU-015S400 | DriveWare 7 | Fail | Waveform generator and oscilloscope only | [DriveWare User Guide](https://servo.a-m-c.com/hubfs/Software-Files/AMC_SW_Manual_DriveWare.pdf), p. 64 and 80 |
| Parker PSD1-S | PSD ServoManager | NC | The catalogue names only an oscilloscope and auto-tuning. The software help is behind a sign-up form | [PSD1 catalogue](https://www.dynamelec.com/wp-content/uploads/2024/01/PSD1_catalogue.pdf), p. 3 |
| Bosch Rexroth IndraDrive Cs | IndraWorks Ds | NC | Not found | — |
| Schneider Lexium 32 | SoMove | NC | The drive manual names auto-tuning only | — |
| Kinco FD5P | Kinco servo software | NC | The manual shows an oscilloscope only | — |

### The 4 kHz drives, checked again

These five drives were left out on 2026-09-29, when the position loop limit was 8 kHz. They were
checked against DRV-01 to DRV-10 in the makers' manuals.

| Drive | Result | Deciding points |
| --- | --- | --- |
| Kollmorgen AKD-x00306, EtherCAT | **Passes all ten** | 3 A rms continuous, 9 A rms for 5 s. Bus about 325 V on 230 VAC. Linear motors, finds the commutation without Hall sensors. Motor thermal input. EtherCAT with CiA 402. 1 Vpp sine and cosine up to 250 kHz with termination resistors. Position loop 250 µs. Bode plots in WorkBench |
| Copley Xenus Plus XEL-230-18 | **Passes all ten** | 4.24 A rms continuous, 12.7 A rms for 1 s. Bus about 325 V on 230 VAC. Linear motor set by the magnetic pole pair length, phasing without Hall sensors. Motor thermal input. EtherCAT with CiA 402. 1 Vpp sine and cosine up to 230 kHz. Position loop 4 kHz. Bode plots in CME |
| Bosch Rexroth IndraDrive Cs, HCS01 230 V model | Not confirmed | The position loop is 250 µs only in "Advanced" performance, otherwise 500 µs. The peak current time, the thermal model, CiA 402 over EtherCAT and DRV-10 are not confirmed |
| Schneider Lexium 32M with encoder module | Fails DRV-08 | The 1 Vpp input reads at most 100 kHz. The stage needs 150 kHz |
| Kinco FD5P | Fails DRV-08 | Its encoder port reads serial encoders only, no sine and cosine |

I read the deciding numbers for the AKD and the Xenus Plus again myself in the downloaded manuals:
the AKD position controller at 250 µs and its 1 Vpp input, the Xenus Plus position loop at 4 kHz and
its 230 kHz input, and the magnitude and phase plot in CME.

### The KEBA position loop

The ServoOne Device Help gives the position controller at 125 µs (8 kHz). This confirms DRV-09 and
DRV-P3 for the ServoOne family. Before, the overview page said "not confirmed" for the junior.

## Decisions Made

- DRV-10 is a hard requirement, as asked. A frequency response that only feeds an automatic tuning
  step, or a plain oscilloscope, does not pass.
- The choice of the CDHD2S is not changed here. That is for the team to decide after Servotronix
  answers.

## Open Questions

- Does a newer ServoStudio 2 version show the phase, and a real Bode plot? Ask Servotronix.
- What do the Kollmorgen AKD-x00306 and the Copley XEL-230-18 cost new, and are they still made?
  Both are older product lines. The overview page gives USD 250 to 400 used for the AKD.
- The 1 Vpp input of the AKD reaches 250 kHz only when the encoder needs termination resistors.
  Check this against the encoder we choose.

## Next Steps

- Ask Kollmorgen and Copley (Curtiss-Wright) for a price and the delivery state.
- Ask Servotronix about phase in the ServoStudio 2 frequency response.
- Check the KEBA ServoOne junior against DRV-05 and DRV-06.
