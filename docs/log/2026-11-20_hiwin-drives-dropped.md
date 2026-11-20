# 2026-11-20 — HIWIN drives dropped: the speed loop is too slow

**Role(s):** engineering, purchasing

## Goal

HIWIN Taiwan answered the two open drive questions from 2026-11-10. Record the answers, and record
the decision that follows from them.

## Work Done

### Short answer

- **We drop every HIWIN drive.** Niels Bosmans decided that the speed loop of the E1 is too slow.
  The E1 ED1F-EN-0422-01-00 with the ESC-SS-S02 box is off the list. The E2 Advanced and the
  D2T-LM were already out. The HIWIN rows are removed from the
  [servo drive selection page](../servo-drive-selection.md).
- **Speed loop: 3.2 kHz. Current loop: 5 kHz.** HIWIN wrote "bandbreedte" (bandwidth) for both.
- **The ESC-SS-S02 box delays the position signal by 31.25 µs at most.** HIWIN calls this
  negligible in practice.
- **The HIWIN linear guides stay.** This decision is about the drive only.

### The answers

| Question (asked 2026-11-05) | Answer from HIWIN Taiwan, through Harjot Singh, HIWIN GmbH (2026-11-20) |
| --- | --- |
| Frequencies of the current, speed and position loops, with a linear motor and the ESC-SS-S02 | "The bandwidth of the speed loop is 3.2 kHz and the current loop is 5 kHz." No position loop value |
| Does the ESC box delay the position signal? How much? | "The maximum delay is 31.25 µs. It is negligible in practice." |

### Bandwidth is not the loop rate

The requirement DRV-09 asks for a position loop that runs at 4 kHz or faster: an update rate. HIWIN
gave bandwidths. A bandwidth says how fast the loop can follow a change. The update rate is
normally many times higher than the bandwidth. The E1 manual agrees that 5 kHz is a bandwidth:
"the current bandwidth is 5 KHz (maximum)" (section 10.5.1).

So these numbers do not prove that the position loop is slower than 4 kHz. They also do not prove
that it is faster. The position loop rate is still not published, so DRV-09 stays not confirmed
(NC). By our rule, not confirmed never counts as a pass. The drop does not depend on this reading:
it is the team's decision.

## Decisions Made

- Drop the HIWIN E1 drive and the ESC-SS-S02 box. No HIWIN drive is on the list.
- Keep the HIWIN guides EGR15U418H and QEH15SAZAH+E2 (class H).

## Open Questions

None for the drive. The open drive questions of 2026-11-10 (rms or peak current, PTC switching
point) are closed, because the drive is dropped.

## Next Steps

- Tell Vansichen BV that we need a quote for the guides only, without the drive. Niels Bosmans
  sends it. No email is sent from this work.
- The CE assessment page still lists the HIWIN E1. It is a dated assessment, so it is not changed
  here.

<details>
<summary>Sources</summary>

- Email from Harjot Singh (HIWIN GmbH, application engineer), 2026-11-20, in the thread
  "Offerteaanvraag – servodrive E2 Advanced en lineaire geleidingen EGR15U / QEH15SA". In Dutch,
  translated here. Earlier answers: [log of 2026-11-10](2026-11-10_hiwin-answers-e1-drive-and-guides.md).
- HIWIN Mikrosystem "E1 Series Servo Drive User Manual", MD09UE01-2607 V3.3, section 10.5.1, page
  10-17. The file is in the parts library, refaqt/stoq, `modules/hiwin/docs/datasheets/`.
- Rule on numbers that decide a pass:
  [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md).

</details>
