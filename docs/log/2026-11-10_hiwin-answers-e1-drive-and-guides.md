# 2026-11-10 — HIWIN answers on the E1 drive and the EGR15U / QEH15SA guides

**Role(s):** engineering, purchasing

## Goal

HIWIN answered our questions on the E1 drive, the ESC-SS-S02 encoder box, and the linear guides.
Record the answers and the open points.

## Work Done

### Short answer

- **HIWIN cannot sell the E2 drive in the EU.** The E1 drive ED1F-EN-0422-01-00 is the offer
  instead.
- **The 400 W drive gives 10 A for 1 s.** We need 5.9 A rms for 1 s. That passes, if the 10 A is a
  peak value and not an rms value. HIWIN did not say which.
- **The loop rates and the delay of the ESC box are still unknown.** HIWIN GmbH has no data and
  asks HIWIN in Taiwan.
- **Finding the commutation angle without Hall sensors is not confirmed for our encoder.** HIWIN
  sent pages 128 to 130 of the E1 manual. The table for "SW method 1" lists only three encoder
  signals: Tamagawa, digital TTL, and analog sin/cos with the ESC-AN box. It does not list serial
  BiSS-C with the ESC-SS box. The earlier
  [drive check](2026-11-05_hiwin-ed1-checked-against-the-requirements.md) marked this as "Yes".
  That cell needs a second look.
- **Guides in class H are in stock.** Delivery takes 5 to 10 working days. Class P takes about
  10 weeks. We chose class H.
- **A distributor makes the quote.** HIWIN GmbH forwarded our request to Vansichen BV. They send
  the quote for the drive and the guides.

### Timeline

| Date | Who | What |
| --- | --- | --- |
| 2026-11-04 | Niels Bosmans | Quote request to info@hiwin.nl: E2 drive ED2F-E0-003-1-C-00 and guides EGR15U418H and QEH15SAZAP+E2 |
| 2026-11-05 | HIWIN GmbH | No E2 in the EU. E1 is possible. Class H in stock, class P about 10 weeks |
| 2026-11-05 | Niels Bosmans | Chooses the E1 drive with the ESC-SS-S02 box, and class H. Asks 6 questions on the drive and 4 on the guides |
| 2026-11-10 | HIWIN GmbH | Answers the drive questions, with 3 pages of the E1 manual |
| 2026-11-10 | HIWIN GmbH | Answers the guide questions, with the assembly instructions. Forwards the quote request to Vansichen BV |

### Drive: the answers

| Question | Answer |
| --- | --- |
| Loop rates of the current, speed and position loops, with a linear motor and the ESC-SS-S02 | HIWIN GmbH has no information. They ask Taiwan |
| Does the ESC box delay the position signal? | HIWIN GmbH has no information. They ask Taiwan |
| Can the 400 W drive give 5.9 A rms for 1 s? | "The 400 W drive can give a peak current of 10 A for 1 s" |
| Does the PTC input of the ESC box read our motor sensor (3 PTC in series, SNM120)? | "The ESC has temperature monitoring with a PTC input." No switching point or resistance range given. Not confirmed |
| Can "SW method 1" find the commutation angle on a MAXWELL MK21 without Hall sensors? | "See the attachment." The attachment does not list BiSS-C. Not confirmed |
| Does the ESC-SS-S02 read the RSF AK MC 15 B (BiSS-C) without extra settings? | "The ESC-SS is suitable for the BiSS-C protocol." Nothing said about extra settings |
| Is the order code right for the EU? | Not answered. The distributor quotes |

### Guides: the answers

| Question | Answer |
| --- | --- |
| Order code of the set: 2 rails and 4 blocks | The quote gives the correct order codes |
| Is preload ZA in class H in stock? | Yes |
| Which grease, and is the E2 unit filled with Mobil SHC 636? | The blocks come preserved (no grease) or with HIWIN standard grease G05. The oil in the E2 unit is not named. Not answered |
| Can we take the blocks off the rail and put them back? | Yes. A mounting aid is part of the block and works as a dummy rail |
| Must each block go back on the same rail, in the same direction? | See the assembly instructions. They say the reference sides of the rail and the block must face the same direction |
| Do accuracy, preload and lubrication stay? | Yes, if the reference sides of the rail and the block face the same direction |
| Does the warranty stay if we take the blocks off ourselves? | Yes |

HIWIN sent a photo of a block on its mounting aid. We did not save it. It is in the email.

## Decisions Made

- Go on with the E1 drive ED1F-EN-0422-01-00 and the ESC-SS-S02 box, and with guides in class H.
- Wait for the quote from Vansichen BV. No reply to HIWIN is sent from this work.

## Open Questions

1. The loop rates of the current, speed and position loops of the E1 with the ESC-SS-S02. HIWIN
   asks Taiwan.
2. The delay that the ESC-SS-S02 adds to the position signal. HIWIN asks Taiwan.
3. Is the 10 A for 1 s an rms value or a peak value? We need 5.9 A rms.
4. Can the E1 find the commutation angle with a BiSS-C encoder and a third-party linear motor?
   Ask which method works with the ESC-SS box. Do not accept "see the attachment".
5. The switching point and the resistance range of the ESC PTC input, against the SNM120 values.
6. The oil in the E2 lubrication unit, and the order code of the set of 2 rails and 4 blocks.
7. Price and delivery time from Vansichen BV.

## Next Steps

- Send questions 3 to 5 to HIWIN GmbH. Niels Bosmans decides if and when.
- Update the HIWIN E1 row of the [servo drive selection page](../servo-drive-selection.md) when
  the answers come: the commutation cell and the peak current cell.
- The two documents HIWIN sent are in the parts library, on branch
  `claude/hiwin-answers-documents` of refaqt/stoq, not yet merged. They are the E1 manual pages
  128 to 130 and the linear guideway assembly instructions.

<details>
<summary>Sources</summary>

- Email thread "Offerteaanvraag – servodrive E2 Advanced en lineaire geleidingen EGR15U /
  QEH15SA", Niels Bosmans and Harjot Singh (HIWIN GmbH, application engineer), 2026-11-04 to
  2026-11-10. The thread is in Dutch. Answers are translated here.
- "SW Method 1.pdf": HIWIN E1 user manual ED1-01-5-EN-2610-MA, pages 128 to 130. Table 7.2 lists
  serial EnDat or BiSS-C with the ESC-SS box. Table 7.4 lists the encoder signals for SW method 1.
- "HIWIN-ASSEMBLY-INSTRUCTIONS-LINEAR-GUIDEWAYS (5).PDF": GW-06-2-EN-2610-MA, 76 pages. The
  reference side of the rail is marked with arrows (section 5.2.1).

</details>
