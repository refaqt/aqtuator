# 2026-10-22 — Kollmorgen AKD2G checked as a replacement for the AKD, for a price request to DynamicDrives

**Role(s):** engineering, purchasing

## Goal

The user wants to ask DynamicDrives (dynamicdrives.nl), a Kollmorgen distributor in the
Netherlands, for a price. The chosen drive, the Kollmorgen AKD-x00306 (first generation), is not
on their web site. Check whether the newer AKD2G meets the drive requirements, name the exact
AKD2G to ask for, and compare it with the AKD.

## Work Done

### Short answer

- **Ask for the AKD2G-SPE-6V03S-A1F3-0000-A.** It is the single axis, 3 A, 230 VAC model with
  EtherCAT, simple safe torque off (STO), the extra X23 encoder connector (option F3), and the
  mating connectors.
- **The F3 option is a must.** Without it the drive has only the X1 connector, which reads
  Kollmorgen's own two-wire motor feedback (SFD3 and HIPERFACE DSL). Only X23 reads a 1 Vpp
  sine and cosine encoder, EnDat 2.2 or BiSS-C.
- **On paper the AKD2G meets the hard requirements, like the AKD.** Current, bus voltage and the
  250 µs position loop are the same. Two points are not confirmed: the highest 1 Vpp signal
  frequency on X23, and the Bode plot tool (only the brochure says so).
- **The AKD2G is better in one way and worse in one way.** Better: it has four free second-order
  filters (DRV-P1), and it is a current product. Worse: it costs about CHF 1,050 per axis, which
  is about twice the budget of about 500 euro per axis.

### The AKD2G-SPE-6V03S-A1F3-0000-A against the requirements

| Req. | Needed | AKD2G-SPE-6V03S-A1F3 | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 3 A rms | Pass |
| DRV-02 | 5.9 A rms for 1 s | 9 A rms for 5 s | Pass |
| DRV-03 | Peak current limit and a motor thermal model | Current limits and a motor overload fold back | Pass |
| DRV-04 | DC bus 320 V to 600 V | 1 phase 100 to 240 VAC, rated bus 310 VDC | Pass, no margin at low mains voltage. Same as the AKD |
| DRV-05 | Linear motor, finds the commutation angle without Hall sensors | Linear motors allowed. "Wake and Shake" finds the angle for a sine encoder without Hall sensors | Pass |
| DRV-06 | Reads the motor thermal sensor | Thermal input on X23 pins 8 and 9 | Pass, if MAXWELL confirms the sensor type |
| DRV-07 | EtherCAT with CiA 402 | "E" in SPE: EtherCAT | Pass |
| DRV-08 | Reads the stage encoder directly | X23 reads sine encoders (1 Vpp), EnDat 2.2 and BiSS-C | Pass for EnDat 2.2 and BiSS-C. For 1 Vpp the highest signal frequency is not in the manual: **not confirmed** for 150 kHz |
| DRV-09 | Position loop 4 kHz or faster | 250 µs (4 kHz) | Pass |
| DRV-10 | Bode plots in the setup software | WorkBench, "advanced Bode Plot tool" | Pass, but only from the brochure |
| DRV-P1 | Free second-order filters | Four free biquad filters in the 16 kHz velocity loop | Pass |
| DRV-P2 | Block diagram of the loop | Not checked | Not checked |
| DRV-P3 | Position loop 8 kHz or faster | 250 µs | Fail |

### What each part of the order code means

| Part | Meaning | Why this one |
| --- | --- | --- |
| SP | Position indexer | The standard AKD2G model |
| E | EtherCAT | DRV-07 |
| 6V | 120 to 240 VAC, 1 or 3 phase | The 7V model (up to 480 VAC) has a 620 VDC bus. That breaks the 600 V limit of the MK21 |
| 03 | 3 A rms continuous, 9 A rms for 5 s | The smallest size. 06 and 12 are too large |
| S | Single axis | D is two axes in one box |
| A1 | Hardware revision A, safety option 1: STO by wired inputs | A2 (safety over EtherCAT) and A3 (more safety functions) are not needed |
| F3 | Extra X23 encoder connector | Needed for our encoder |
| 0000 | Standard boards, no coating | |
| -A | Mating connectors included | Ask DynamicDrives if their code includes this |

### AKD2G compared with the AKD chosen before

| Item | AKD-P00306-NBEC (chosen before) | AKD2G-SPE-6V03S-A1F3-0000-A |
| --- | --- | --- |
| Current | 3 / 9 A rms for 5 s | 3 / 9 A rms for 5 s |
| Supply and bus | 120 to 240 VAC, about 325 V | 100 to 240 VAC, rated 310 V |
| Position loop | 250 µs (4 kHz) | 250 µs (4 kHz) |
| Velocity loop | 62.5 µs (16 kHz) | 62.5 µs (16 kHz) |
| Free filters (DRV-P1) | Not checked | Four free biquads |
| Encoder connector | X10, built in | X23, only with option F3. Same pin layout as the AKD X10 |
| 1 Vpp highest frequency | 250 kHz, with termination resistors | Not in the manual |
| Second axis | One drive per axis | A two-axis model exists (6V03D-A1F3) |
| Product state | Older line. Not on the DynamicDrives web site | Current line. Oxni gives about 4 weeks delivery |
| Price | USD 250 to 400 used. New price not found | CHF 1,050.47 excl. VAT (Oxni, 22 October 2026). Two-axis model CHF 1,740.19 |

Kollmorgen's migration notes say that WorkBench files of the AKD do not carry over to the AKD2G.
For us this does not matter, because we have no AKD setup yet.

## Decisions Made

No purchase decision. The AKD2G-SPE-6V03S-A1F3-0000-A is the Kollmorgen drive to ask
DynamicDrives for. The AKD stays on the question list, in case DynamicDrives can still supply it
new at a lower price.

## Open Questions

Ask DynamicDrives:

1. The price and delivery time of the AKD2G-SPE-6V03S-A1F3-0000-A, for 1 and for 2 drives.
2. The price of the two-axis AKD2G-SPE-6V03D-A1F3-0000-A, as an option for two stages.
3. Can they still supply the AKD-P00306-NBEC new, and at what price?
4. What is the highest sine and cosine (1 Vpp) signal frequency on X23? We need 150 kHz.
5. Does WorkBench for the AKD2G measure and show Bode plots (gain and phase) of the speed loop?
6. Which cables and connectors come with the "-A" code, and what does WorkBench cost?

## Next Steps

- Send the questions above to DynamicDrives.
- After the answer, update the [servo drive selection page](../servo-drive-selection.md) and
  decide between the AKD2G, the AKD and the Copley Xenus Plus.

<details>
<summary>Sources</summary>

- Kollmorgen AKD2G-S installation manual, Safety 1, beta edition December 2018, public copy:
  <https://servostar.ru/_uploads/offers/2c62531152/_pdf/AKD2G%20Installation%20Manual%20with%20FS1%20EN%20REV%20BETA.pdf>.
  Order code and options: page 31. Loop rates: pages 32 and 34. Supply and bus: page 35.
  Output current: page 36. Feedback types per connector and X23 pin layout. Kollmorgen's own
  PDF downloads were blocked. The June 2023 edition gives the same 250 µs (see the
  [follow-up log of 29 September](2026-09-29_hiwin-delta-kollmorgen-follow-up.md)).
- Kollmorgen AKD2G help, "Wake and Shake Overview":
  <https://webhelp.kollmorgen.com/akd2g/english/content/AKD2G_User_Manual/Wake%20and%20Shake%20Overview.htm>.
- Kollmorgen help, feedback devices on FB3 (EnDat 2.2, BiSS Mode C, sine encoder):
  <https://webhelp.kollmorgen.com/kas3.02/Content/AKD2G%20User%20Manual/Feedback_Devices.htm>.
- Kollmorgen AKD to AKD2G migration FAQ:
  <https://www.kollmorgen.com/en-us/developer-network/akd-akd2g-migration-faq>.
- Oxni prices and order codes, seen on 22 October 2026:
  <https://shop.oxni.ch/en/store/drives/servo-drives/akd2g>.
- DynamicDrives home page, seen on 22 October 2026: names Kollmorgen as a partner and shows AKM
  motors, no AKD or AKD2G: <https://www.dynamicdrives.nl>.
- Biquad filters and the Bode plot brochure: earlier logs
  [2026-09-29](2026-09-29_hiwin-delta-kollmorgen-follow-up.md) and
  [2026-10-06](2026-10-06_drives-checked-for-bode-plot-tuning.md).

</details>
