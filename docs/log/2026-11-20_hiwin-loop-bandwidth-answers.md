# 2026-11-20 — HIWIN answers on the E1 loop bandwidth and the encoder box delay

**Role(s):** engineering, purchasing

## Goal

HIWIN Taiwan answered the two open drive questions from 2026-11-10. Record the answers.

## Work Done

### Short answer

- **Speed loop bandwidth: 3.2 kHz. Current loop bandwidth: 5 kHz.** HIWIN wrote "bandbreedte"
  (bandwidth) for both. These are not loop rates.
- **The position loop rate is still unknown.** HIWIN did not give it. DRV-09 (a position loop at
  4 kHz or faster) stays not confirmed for the E1.
- **The ESC-SS-S02 box delays the position signal by 31.25 µs at most.** HIWIN calls this
  negligible in practice.
- **The HIWIN drives stay on the list.** The E1 with the ESC-SS-S02 box is still a candidate.

### The answers

| Question (asked 2026-11-05) | Answer from HIWIN Taiwan, through Harjot Singh, HIWIN GmbH (2026-11-20) |
| --- | --- |
| Frequencies of the current, speed and position loops, with a linear motor and the ESC-SS-S02 | "The bandwidth of the speed loop is 3.2 kHz and the current loop is 5 kHz." No position loop value |
| Does the ESC box delay the position signal? How much? | "The maximum delay is 31.25 µs. It is negligible in practice." |

### Bandwidth is not the loop rate

DRV-09 asks for a position loop that is updated 4 000 times per second or more: an update rate. A
bandwidth says how fast the loop can follow a change. The update rate is normally many times
higher than the bandwidth. So a speed loop bandwidth of 3.2 kHz is a high value. It does not mean
the loop is slow. The E1 manual uses the word in the same way: "the current bandwidth is 5 KHz
(maximum)" (section 10.5.1).

At first the team read 3.2 kHz as a loop rate and dropped the HIWIN drives. That was corrected the
same day. The drives stay on the list.

## Decisions Made

- Keep the HIWIN E1 drive with the ESC-SS-S02 box on the drive list.

## Open Questions

1. The update rate of the E1 position loop, in µs or kHz. HIWIN has not given it yet.
2. Is the 10 A for 1 s an rms value or a peak value? We need 5.9 A rms. (Open since 2026-11-10.)
3. The switching point and the resistance range of the ESC PTC input, against the SNM120 values.
   (Open since 2026-11-10.)
4. Price and delivery time from Vansichen BV.

## Next Steps

- Ask HIWIN for the update rate of the position loop, together with open questions 2 and 3.
  Niels Bosmans decides if and when. No email is sent from this work.

<details>
<summary>Sources</summary>

- Email from Harjot Singh (HIWIN GmbH, application engineer), 2026-11-20, in the thread
  "Offerteaanvraag – servodrive E2 Advanced en lineaire geleidingen EGR15U / QEH15SA". In Dutch,
  translated here. Earlier answers: [log of 2026-11-10](2026-11-10_hiwin-answers-e1-drive-and-guides.md).
- HIWIN Mikrosystem "E1 Series Servo Drive User Manual", MD09UE01-2607 V3.3, section 10.5.1, page
  10-17. The file is in the parts library, refaqt/stoq, `modules/hiwin/docs/datasheets/`.

</details>
