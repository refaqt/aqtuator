# 2026-10-06 — Kollmorgen AKD and Copley Xenus Plus are the drive candidates. Servotronix is out

- **Date:** 2026-10-06
- **Status:** Accepted
- **Replaces:** [Try the Servotronix polynomial velocity controller](2026-09-30_try-the-servotronix-polynomial-velocity-controller.md)

## Context

On 2026-10-06 the drive requirements got a new hard requirement, DRV-10: the drive software must
measure the axis and show Bode plots. All candidate drives were checked again in the makers' own
manuals. See the [log entry](../log/2026-10-06_drives-checked-for-bode-plot-tuning.md).

Two drives meet all ten hard requirements in
[`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml):

- the **Kollmorgen AKD-x00306**, first generation, EtherCAT version, and
- the **Copley Xenus Plus XEL-230-18**, EtherCAT version.

Both have a 4 kHz position loop, read the 1 Vpp encoder directly, run a linear motor without Hall
sensors, and show Bode plots in their setup software.

The chosen drive until now was the Servotronix CDHD2S. Servotronix (STXI Motion) is an Israeli
company. The drive searches of 2026-09-29 already left out Israeli suppliers, but the CDHD2S was
chosen without applying that rule. The CDHD2S also does not meet DRV-10 as documented: its software
shows a frequency response with gain only, no phase.

## Decision

- **The Kollmorgen AKD-x00306 and the Copley Xenus Plus XEL-230-18 are the most suitable
  candidates.** We ask both makers for a price and the delivery state, and choose between them
  after that.
- **The Servotronix drives are rejected, because Servotronix is an Israeli company.** This covers
  the CDHD2S, the CDHD2 and every other Servotronix drive.
- **We do not buy from Israeli suppliers.** This rule now applies to every drive search. Elmo, ACS,
  Agito Akribis and Dynamikwell stay out for the same reason.
- **The Delta ASD-A3-0421-E with the ASD-IF-EN0A20 converter box stays the fallback.** See
  [the fallback decision](2026-09-30_delta-asda-a3-as-fallback-drive.md). It still needs a converter
  box for the 1 Vpp encoder, and its position loop rate is still not confirmed.

## Consequences

- The plan to run our own controller in the Servotronix velocity loop (mode 3) stops. Neither
  candidate offers a free polynomial controller inside the drive. The Kollmorgen AKD2G has four free
  second order filters, but it is not a candidate. The filters of the AKD and the Xenus Plus are not
  yet checked against DRV-P1.
- Both candidates have a 4 kHz position loop. This meets DRV-09, but not the 8 kHz preference
  DRV-P3.
- Both are older product lines. Their new price and whether they are still made are not confirmed.
- Ask the makers before the order:
  - Kollmorgen: the price of an AKD-P00306 with EtherCAT, and whether it is still made.
  - Kollmorgen: the 1 Vpp input reaches 250 kHz only for encoders that need termination resistors.
    Check this against the chosen encoder.
  - Copley (Curtiss-Wright): the price of an XEL-230-18 with EtherCAT, and whether it is still made.
- Old logs and decisions that name Servotronix stay as they are. They record what was true at the
  time.
