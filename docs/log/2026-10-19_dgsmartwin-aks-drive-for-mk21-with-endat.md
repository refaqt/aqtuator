# 2026-10-19 — DGSMARTWIN AKS drive checked for the MK21 with an EnDat 2.2 encoder

**Role(s):** engineering, purchasing

## Goal

The user supplied the DGSMARTWIN "Servo Driver and Encoder" catalog (2026 edition). Pick the AKS
drive for the MAXWELL MK21 linear motor with an EnDat 2.2 absolute linear encoder. Check whether
the control loop rate is fast enough.

## Work Done

### Short answer

- **Drive: AKS-4D52AECAB.** This is the AKS-4D5 (4.5 A rms continuous, 16 A rms for 2 s), for
  220 VAC, with EtherCAT (EC) and the "AB" function board.
- **The "AB" board is a must.** The catalog table of encoder types says EnDat 2.2 works only on
  the "-AB" version. The "-DB" version does not read it.
- **The loop rate is not confirmed.** The catalog gives only the PWM frequency (10 kHz). It gives
  no current, velocity or position loop rate. Under DRV-09 the drive is "not confirmed" until
  DGSMARTWIN sends the number in writing.
- **Matching parts in the same catalog:** encoder read head SA32EH05A-MC (EnDat 2.2, 0.05 µm) or
  SA32EY05A-MC (0.1 µm), scale SA32-L…-MC, and adapter cable E-FN09-26-L□-TC1 (D-sub 9 to the
  26-pin encoder port of the drive).

### Why the AKS-4D5 and the 220 VAC version

| Req. | Needed | AKS-4D52AECAB | Result |
| --- | --- | --- | --- |
| DRV-01 | 2.0 A rms continuous | 4.5 A rms | Pass |
| DRV-02 | 5.9 A rms for 1 s | 16 A rms for 2 s | Pass. Set the current limit to 5.9 A rms |
| DRV-03 | Peak current limit and motor thermal model | Motor I²t alarm (alarm 120) with current fold back | Pass on paper. Limit setting not shown in the catalog |
| DRV-04 | DC bus 160 V to 600 V | 220 VAC gives about 310 V. Overvoltage trip 420 V | Pass |
| DRV-05 | Linear motor, finds the commutation angle | Built for AKS linear motors. Automatic direction search (alarms 200, 201) | Pass on paper. Pole pitch setting not shown |
| DRV-06 | Reads the motor thermal sensor | PTC or NTC, own fault threshold | Pass, if the MK21 sensor is PTC or NTC |
| DRV-07 | EtherCAT with CiA 402 | EtherCAT. CiA 402 not named | Not confirmed |
| DRV-08 | Reads the stage encoder | EnDat 2.2 on the "-AB" version | Pass |
| DRV-09 | Position loop 4 kHz or faster | Not published | **Not confirmed** |
| DRV-P1 | Own filters | Not published | Not confirmed |
| DRV-P2 | Loop block diagram | Not published | Fail |
| DRV-P3 | Position loop 8 kHz or faster | Not published | Not confirmed |

The AKS-4D5 is the smallest size. Its peak current is 2.7 times the MK21 peak. The current
measurement is therefore coarser than with a better matched drive. This is acceptable, but it is
one more reason to set the limits with care.

Do not use the 380 VAC sizes (AKS-012 and up). Their brake resistor switches on at 720 V to 800 V,
and they trip on overvoltage only at 780 V. Both are above the 600 V limit of the MK21. They are
also far too large: 12 A rms and more.

### What the catalog says about timing

- PWM frequency: 10 kHz for every size.
- Alarm 216 names a "general configuration" with an EtherCAT interpolation period of 500 µs
  (2 kHz). This is the cycle of the master, not the loop inside the drive. It does not decide
  DRV-09. But it means that 500 µs is the usual setting, so ask whether a shorter cycle works.
- A PWM of 10 kHz usually means a current loop of 10 kHz or 20 kHz. That is a guess. It says
  nothing about the position loop.

### Follow-up: is the AKS a rebranded drive?

The user could not find the AKS drives on the DGSMARTWIN web site, and asked whether they are a
rebranded drive from another maker.

- **The AKS catalog pages are copied from the Servotronix CDHD user manual.** The table shapes
  and many numbers are the same. Examples: "Line fuses (FRN-R, LPN, or equivalent)", "1500 VAC
  (2121 VDC)", a fan at "quarter power", "VLOW" and "VMAX" for the brake resistor, and the full
  motor feedback table (5 VDC (7 VDC*), 250 mA, AWG 28 for 3 m, 4 MHz, 8 kHz excitation, 6 to
  22 Vpp, 55 mA rms, 65 536 interpolation, 16 384 effective).
- **The 120/240 VAC sizes are the CDHD sizes:** 4D5, 006, 008, 010 and 013, with the same
  continuous currents. The order code has the same shape: AKS-4D52AEC… and CDHD-4D52AEC2.
- **The AKS-006 numbers match the CDHD-006 exactly:** 18 A rms for 2 s (25.45 A peak), input
  current 10 / 5.8 A rms, 0.7 and 1.5 kVA. The AKS-4D5 page lists 6.36 A peak continuous. The CDHD
  manual lists 6.63 A. This looks like a typing error made while copying.
- **But the drive is not the same unit.** The AKS has another connector layout (STO on an RJ45
  socket, an Ethernet service port, a 36-pin I/O plug and a 26-pin feedback plug). The CDHD has
  USB, RS232 and other plugs. The AKS lists a 10 kHz PWM, the CDHD 16 kHz. The AKS-4D5 peak current
  is 16 A rms, the CDHD-4D5 18 A rms. The AKS alarm list and parameter names (for example
  p11280) do not follow the CDHD style. The AKS also adds EnDat 2.2 and BiSS-C, a 270 kHz sine
  input (CDHD: 100 kHz), and 380 VAC sizes 040 and 050, which the CDHD does not have.

So the most likely story is: DGSMARTWIN used the CDHD manual as a template, and maybe the CDHD
power stage as a base, but the drive has its own front, firmware, or both. We cannot prove which.

**What this means for the loop rate.** The CDHD manual gives a current loop of 32 kHz, a velocity
loop of 8 kHz and a position loop of 4 kHz. If the AKS keeps the CDHD control core, it meets DRV-09
only just, and fails DRV-P3. We cannot use the CDHD numbers for the AKS. The AKS stays "not
confirmed" until DGSMARTWIN answers in writing.

## Decisions Made

No purchase decision. The AKS-4D52AECAB goes on the short list as "not confirmed" for DRV-07 and
DRV-09.

## Open Questions

- What are the current, velocity and position loop rates of the AKS-4D5? Ask DGSMARTWIN for the
  manual or a written answer.
- Does the EtherCAT interface follow CiA 402, and what is the shortest cycle time?
- Which EnDat 2.2 clock rate does the drive use?
- Is the AKS built on the Servotronix CDHD, under a licence or as an OEM product? If yes, which
  firmware does it run, and are the CDHD loop rates valid?
- The drive requirement model knows only 1 Vpp and BiSS-C encoders. If the stage moves to EnDat 2.2,
  add EnDat 2.2 to the model.

## Next Steps

- Send the questions above to DGSMARTWIN (win@dgsmartwin.com).
- Only after a written loop rate of 4 kHz or more, count the drive as a pass.

<details>
<summary>Sources</summary>

- DGSMARTWIN "Servo Driver and Encoder" 2026 product catalog, supplied by the user: order code
  (page 04), encoder support table (page 05), AKS-4D5 data (pages 08 and 09), 380 VAC sizes
  (pages 12 to 21), alarms 120, 200, 201 and 216 (pages 22 to 25), SA32 encoder (pages 32 and 33),
  cable E-FN09-26-L□-TC1 (page 42).
- Servotronix CDHD User Manual, firmware 1.41.x, Rev 8.6: Table 3-2 (CDHD-4D5 and CDHD-006),
  Table 3-11 (motor feedback), loop update rates in the specifications chapter.
  <https://www.stxim.com/wp-content/uploads/2024/01/CDHD_User_Manual_fw1.41.x_Rev_8.6-i.pdf>
- CDHD size table (Chinese distributor): <http://www.stx-hq.com/index.php?id=43>
- DGSMARTWIN is an EtherCAT Technology Group member:
  <https://ethercat.org/en/members/members_A48E51551D8F4A14B4A7A7A98090CB84.htm>
- MK21 values and requirements:
  [`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml).

</details>
