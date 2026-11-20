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
- **Yes, a method works: "STABS test/tune".** The E1 drive finds the commutation angle for a
  linear motor with a BiSS-C encoder on the ESC-SS box, and it needs no Hall sensor. The full E1
  manual says so in section 7.5.2, Table 7.5.2.1. HIWIN GmbH sent only three pages of that manual.
  We read the full manual, which is public. See
  [the check of the full manual](#check-of-the-full-manual-on-commutation). The commutation
  question is closed. We ask HIWIN nothing more on it.
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
| Can "SW method 1" find the commutation angle on a MAXWELL MK21 without Hall sensors? | "See the attachment." The three pages do not settle it. The full manual does: SW method 1 is not for serial encoders, but "STABS test/tune" is. Answered by the full manual |
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
resolution. The answer from these three pages alone is: **yes for the combination, not yet for the
method.** The full manual, in the next section, names the method.

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
- **Not shown by these pages:** which method finds the angle. Table 7.4 leaves serial signals out
  of SW method 1. The pages do not say if STABS test/tune, or another method, covers this case.
- **Brand is not a limit.** The tables say "linear motor", not "HIWIN linear motor". Niels
  Bosmans reads this as: the combination works with a linear motor of any brand. We follow that
  reading. So the MAXWELL MK21 does not need a separate yes from HIWIN. HIWIN did not write this
  sentence itself, so it stays a reading of the table.
- **The drive check of 2026-11-05 named SW method 1 for this point.** That was the wrong method.
  The result "Pass" holds, because STABS test/tune works. See the next section.

### Check of the full manual on commutation

Niels Bosmans said the method does not matter. The question is whether a method works. The email
held only 3 of the manual's pages. The full "E1 Series Servo Drive User Manual" (MD09UE01-2607
V3.3, 663 pages) is a public download on the HIWIN Taiwan site. We downloaded it and read the
sections on electrical angle. We also read the Thunder software manual (MD12UE01-2605 V3.7,
435 pages), which describes the same screens.

**The answer is yes.** "STABS test/tune" finds the commutation angle for a linear motor with a
BiSS-C encoder on the ESC-SS box. It does not use Hall sensors.

| Where | What it says | What it proves |
| --- | --- | --- |
| E1 manual, section 7.5, page 7-7 | For a linear motor, the electrical angle must be found before closed loop control. The drive has three ways: "SW method 1, STABS test/tune, Digital Hall and Analog Hall" | A method must be run once. There are several |
| E1 manual, section 7.5.2, Table 7.5.2.1, page 7-9 | STABS test/tune applies to "Linear motor, direct drive motor or torque motor" with "Serial EnDat or BiSS-C signal", and "Required (ESC-SS)" | An exact match for our case: linear motor, BiSS-C, ESC-SS |
| E1 manual, section 7.5.2, page 7-9 | Steps: jog the motor and check the angle, select STABS test/tune and the range of pole pair pitch, click Start until "Tuned" is green, then click Start phase initialization until "Phase initialized" is green | A short procedure in Thunder. No Hall sensor in any step |
| E1 manual, sections 7.5.3 and 7.5.4 | Digital Hall and Analog Hall need a Hall signal in the table row | These two methods are not for us. The MK21 has no Hall sensors |
| E1 manual, section 7.5.1, Table 7.5.1.1, page 7-8 | SW method 1 lists Tamagawa, digital TTL, and analog sin/cos with the ESC-AN. No serial signal | SW method 1 is not the method for BiSS-C. This is why the three pages looked unclear |
| Thunder manual, section 4.6.4.2, page 4-103 | STABS is "a built-in phase initialization function of servo drive, which uses serial encoder to stably complete phase initialization" | The method is made for serial encoders |
| E1 manual, section 3.1.2, page 3-2 | "ESC-SS supports EnDat 2.1/2.2 or BiSS-C serial encoder" | The ESC-SS reads BiSS-C. HIWIN GmbH also wrote "The ESC-SS is suitable for the BiSS-C protocol" |

What this means for the drive requirement on the commutation angle: it is met, with STABS
test/tune. The brand of the motor is not a limit (see above).

Points to handle at the first power-up. They are not questions for HIWIN:

- **Our encoder is not on HIWIN's suggested list for BiSS-C.** Table 3.5.3.2 lists RSF MC15 under
  EnDat. Table 3.5.3.3, for BiSS-C, lists Renishaw, GIVI, FAGOR and YUHENG. Our RSF AK MC 15 B is
  the BiSS-C version of the MC 15. The list is a suggestion, not a limit. Check at the first
  test that the drive reads the position.
- **The manual is HIWIN's word, not our test.** Nobody has yet run STABS on the MK21. The first
  test on the machine is the real proof. Keep the carriage free to move, because the method moves
  the motor. Thunder asks for the pole pair pitch, which is "the minimum distance for the motor
  to move".

## Decisions Made

- Go on with the E1 drive ED1F-EN-0422-01-00 and the ESC-SS-S02 box, and with guides in class H.
- The commutation angle is settled: use STABS test/tune. Ask HIWIN nothing more about it.
- Wait for the quote from Vansichen BV. No reply to HIWIN is sent from this work.

## Open Questions

1. The loop rates of the current, speed and position loops of the E1 with the ESC-SS-S02. HIWIN
   asks Taiwan.
2. The delay that the ESC-SS-S02 adds to the position signal. HIWIN asks Taiwan.
3. Is the 10 A for 1 s an rms value or a peak value? We need 5.9 A rms.
4. The switching point and the resistance range of the ESC PTC input, against the SNM120 values.
5. The oil in the E2 lubrication unit, and the order code of the set of 2 rails and 4 blocks.
6. Price and delivery time from Vansichen BV.

## Next Steps

- Send open questions 3 and 4 to HIWIN GmbH. Question 3 asks if the 10 A is rms. Question 4 asks
  for the PTC switching point. Niels Bosmans decides if and when.
- Update the HIWIN E1 row of the [servo drive selection page](../servo-drive-selection.md): name
  STABS test/tune instead of SW method 1 in the commutation cell, and update the peak current
  cell when HIWIN answers.
- The three-page extract and the guideway assembly instructions are in the parts library
  (refaqt/stoq, merged). The full E1 manual is in the draft pull request
  [refaqt/stoq#31](https://github.com/refaqt/stoq/pull/31), not yet merged.

<details>
<summary>Sources</summary>

- Email thread "Offerteaanvraag – servodrive E2 Advanced en lineaire geleidingen EGR15U /
  QEH15SA", Niels Bosmans and Harjot Singh (HIWIN GmbH, application engineer), 2026-11-04 to
  2026-11-10. The thread is in Dutch. Answers are translated here.
- "SW Method 1.pdf": HIWIN E1 user manual ED1-01-5-EN-2610-MA, pages 128 to 130. Table 7.2 lists
  serial EnDat or BiSS-C with the ESC-SS box. Table 7.4 lists the encoder signals for SW method 1.
  The file is in the parts library:
  [refaqt/stoq](https://github.com/refaqt/stoq/blob/29da3bd5f49a5330d4ab11046c8a8bbbedc8ac7c/modules/hiwin/docs/datasheets/hiwin-e1-manual-ED1-01-5-EN-2610-MA-pages-128-130.pdf).
- HIWIN Mikrosystem "E1 Series Servo Drive User Manual", MD09UE01-2607 V3.3, 663 pages. Public
  download from <https://www.hiwinmikro.tw/Downloads/ManualOverview_EN.htm>, read on 2026-11-10.
  Sections 3.1.2, 3.5.3, 7.4.2 and 7.5. The page numbers in the table above are the printed page
  numbers.
- HIWIN Mikrosystem "E Series Servo Drive Thunder Software Operation Manual", MD12UE01-2605 V3.7,
  435 pages, from the same page. Section 4.6.4.
- "HIWIN-ASSEMBLY-INSTRUCTIONS-LINEAR-GUIDEWAYS (5).PDF": GW-06-2-EN-2610-MA, 76 pages. The
  reference side of the rail is marked with arrows (section 5.2.1).

</details>
