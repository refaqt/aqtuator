# 2026-09-30 — Try the Servotronix polynomial velocity controller

- **Date:** 2026-09-30
- **Status:** Accepted

## Context

We want to run our own controller in the velocity loop of the drive:
K · (s + a) · (s + b) / ( s · (s² + c·s + d) ). The drive must also meet the drive requirements in
[`architecture/motor-drive.sysml`](../../architecture/motor-drive.sysml): EtherCAT, BiSS-C,
1 Vpp, and the MAXWELL MK21 linear motor.

The [CDHD2S check](../log/2026-09-30_cdhd2s-velocity-loop-custom-filter.md) found that the
Servotronix drives have a velocity controller with free polynomials. Servotronix calls it the
"extended polynomial controller" (velocity controller mode 3). It also has two free second order
filters. Together they have enough order for our controller, and the velocity loop runs at 8 kHz.
Every other requirement passes for the CDHD2S-003.

Two things are not known:

- The number format of the polynomials is not published.
- Mode 3 is described only in the command manual of the older CDHD2 (firmware 2.15). The CDHD2S
  manual names it, but gives no details.

No other drive found so far lets us put a free controller inside the drive.

## Decision

We will try the Servotronix polynomial velocity controller (mode 3) for our own controller.

- We buy the CDHD2S-003 with EtherCAT, because the CDHD2 is marked "legacy". Before the order,
  Servotronix must confirm that the CDHD2S firmware has mode 3.
- If the CDHD2S does not have mode 3, we buy the legacy CDHD2-003 with EtherCAT instead. Its
  command manual describes mode 3.
- We write the controller in discrete-time form with the Tustin method at 125 µs, as in the
  CDHD2S check. It goes into the drive as a PI part in the controller polynomials and a second
  order part in the first output filter.
- If Servotronix does not give the number format, we find it on the drive: set a known PI
  controller, read the numbers the drive gives for it, and compare them with our formulas.

## Consequences

- With our own controller, the position loop runs at 4 kHz, not 8 kHz. The 8 kHz HD position
  controller is closed and cannot take our filter. This still meets the 4 kHz requirement.
- We depend on one maker and on parameters that the maker does not publish. A firmware update
  could change them. We keep the firmware version fixed once the controller works.
- If mode 3 does not work as we expect, we fall back to the simple PI controller with the fixed
  filters, or to a controller in the PC with the drive in current mode at 4 kHz.
- The first test on the drive must check the controller with a measured frequency response before
  it runs the stage at full gain.
