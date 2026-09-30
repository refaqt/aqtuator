# 2026-09-30 — Delta ASDA-A3 is the fallback if the Servotronix drive does not work

- **Date:** 2026-09-30
- **Status:** Accepted

## Context

We plan to use a Servotronix CDHD2 drive for the linear motor stages. The
[Servotronix follow-up](../log/2026-09-29_servotronix-drives-with-a-faster-loop.md) found that the
CDHD2 is now a legacy product, so the model to buy is its successor, the CDHD2S-003. It reads the
1 Vpp encoder directly and has an 8 kHz position loop with its "HD" controller.

Some things can still go wrong with it. Servotronix may not quote or deliver it at a fair price.
Support for the legacy CDHD2 may end. The HD controller may not work together with the error table,
or may not behave well at our cutting force frequencies. We want a second drive ready, so that one
of these problems does not stop the project.

The [Delta ASDA-A3 check](../log/2026-09-30_delta-asda-a3-checked-against-the-requirements.md)
found one Delta drive that comes close to the requirements in
[`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml): the ASD-A3-0421-E. It
runs a linear motor from another maker, finds the commutation angle without Hall sensors, reads
a PTC or NTC motor sensor, and has EtherCAT with CiA 402. Delta is a large maker with a wide
dealer network, so the drive should be easy to buy.

## Decision

The **Delta ASD-A3-0421-E**, together with Delta's **ASD-IF-EN0A20** converter box for the 1 Vpp
encoder, is the fallback drive. We move to it only if the Servotronix drive does not work for one
of the reasons above.

The Delta drive is not confirmed yet. Two points must be settled before we buy it:

1. **Position loop rate (DRV-09).** Delta does not publish it. Delta must confirm in writing that
   it is 4 kHz or faster. If it is slower, the Delta drive is not a fallback.
2. **Converter box (DRV-08).** Today the requirement says the drive reads the encoder with no
   converter box in between. The Delta drive needs one. Before we buy, we either accept Delta's own
   box as an exception and change the requirement, or we drop the Delta drive.

## Consequences

- The Servotronix drive stays the plan. Nothing is bought from Delta now.
- When we ask Servotronix for a quote, we also ask a Delta distributor for the loop rate, the
  price of the drive and the box, and the delay the box adds. Then the fallback is ready if we
  need it.
- The Delta drive is likely weaker in the control loop. Its filters are notch filters only, with
  no free second order filter, and its loop rate may be only 4 kHz. So the stage may reach less
  chatter suppression with it than with the Servotronix drive.
- If we switch to the Delta drive, the thermal sensor of the MK21 must be a PTC or an NTC. MAXWELL
  has not confirmed the type yet.
