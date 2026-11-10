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
- **The E1 manual lists our combination, but it does not name the method that finds the
  commutation angle.** HIWIN sent pages 128 to 130 of the E1 manual. Table 7.2 lists "linear
  motor" with a "serial EnDat or BiSS-C signal", and says the ESC-SS box is required. The manual
  says the electrical angle must be found before operation for these motors. So the combination
  of a linear motor, BiSS-C and the ESC-SS-S02 is a supported one. See
  [the check of 2026-11-10](#check-of-the-manual-pages-on-commutation) below. What the pages do
  not show is which method works for this combination, and with no Hall sensors.
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
| Can "SW method 1" find the commutation angle on a MAXWELL MK21 without Hall sensors? | "See the attachment." Table 7.2 lists a linear motor with BiSS-C and the ESC-SS. Table 7.4 for SW method 1 does not list serial signals. The method for our case is not named. Partly confirmed |
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

### Check of the manual pages on commutation

Niels Bosmans read the pages as showing that the ESC-SS box can find the commutation angle for a
linear motor with a BiSS-C absolute encoder. We checked each page of the file again, at a higher
resolution. The answer is: **yes for the combination, not yet for the method.**

| Page | What it says | What it proves |
| --- | --- | --- |
| 128 (section 7.4.2, Table 7.2) | For a linear motor, direct drive motor or torque motor, "detection for electrical angle must be completed before operation". The table lists "Linear motor and torque motor" with "Serial EnDat or BiSS-C signal", and "Required (ESC-SS)" | The drive supports a linear motor with a BiSS-C encoder, through the ESC-SS box |
| 128 (Table 7.2, other rows) | Rows with a digital or analog signal that also need Hall sensors say "+ digital Hall sensor signal" or "+ analog Hall sensor signal". The serial row has no Hall entry | Hall sensors are not listed for the serial row. The page does not say "no Hall sensors needed" |
| 129 (Table 7.3) | The test steps before first operation for a linear motor: wiring, encoder information, direction check, "Complete detection of electrical angle" | The angle detection is a required step. No method is named |
| 130 (section 7.5) | Three methods: SW method 1, STABS test/tune, and digital or analog Hall | The drive has more than one method. The page does not say which one fits our case |
| 130 (Table 7.4) | SW method 1 lists only Tamagawa, digital TTL, and analog sin/cos with the ESC-AN. No serial signal | SW method 1 is not listed for a serial encoder in this table |
| 130 (Fig. 7.2) | The Thunder screen for SW method 1 shows "Encoder type: Serial" and "Feedback detect ok" | An example. It does not say which motor or which serial protocol. It does not overrule Table 7.4 |

What this means:

- **Confirmed in writing:** the E1 drive with the ESC-SS-S02 supports a linear motor with a
  BiSS-C encoder. This also fits HIWIN's own words: "The ESC-SS is suitable for the BiSS-C
  protocol."
- **Not confirmed:** that the drive finds the angle on our motor without Hall sensors. Table 7.4
  leaves serial signals out of SW method 1. The pages do not say if STABS test/tune, or another
  method, covers this case.
- **Not confirmed:** that it works for a motor from another brand. The tables say "linear
  motor", not a brand. HIWIN did not say anything about MAXWELL.
- **The drive check of 2026-11-05 said "Yes" for this point.** That was too strong. The
  evidence is "the combination is listed". Mark that cell as "combination listed, method not
  confirmed" until HIWIN names the method.

## Decisions Made

- Go on with the E1 drive ED1F-EN-0422-01-00 and the ESC-SS-S02 box, and with guides in class H.
- Wait for the quote from Vansichen BV. No reply to HIWIN is sent from this work.

## Open Questions

1. The loop rates of the current, speed and position loops of the E1 with the ESC-SS-S02. HIWIN
   asks Taiwan.
2. The delay that the ESC-SS-S02 adds to the position signal. HIWIN asks Taiwan.
3. Is the 10 A for 1 s an rms value or a peak value? We need 5.9 A rms.
4. Which method finds the commutation angle with a BiSS-C encoder, the ESC-SS-S02 and a
   third-party ironless linear motor without Hall sensors? Is it SW method 1 or another one?
   Does it work for a non-HIWIN motor? Ask for the manual section.
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
  The file is in the parts library:
  [refaqt/stoq](https://github.com/refaqt/stoq/blob/29da3bd5f49a5330d4ab11046c8a8bbbedc8ac7c/modules/hiwin/docs/datasheets/hiwin-e1-manual-ED1-01-5-EN-2610-MA-pages-128-130.pdf).
- "HIWIN-ASSEMBLY-INSTRUCTIONS-LINEAR-GUIDEWAYS (5).PDF": GW-06-2-EN-2610-MA, 76 pages. The
  reference side of the rail is marked with arrows (section 5.2.1).

</details>
