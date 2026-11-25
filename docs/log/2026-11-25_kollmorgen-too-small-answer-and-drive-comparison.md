# 2026-11-25 — Kollmorgen said our drives are too small. That is not true. Drives still in the running, with prices

**Role(s):** engineering, purchasing

## Goal

Read the answer and the quotation from DynamicDrives (Kollmorgen distributor, 30 October 2026).
They wrote that the AKD-x00306 and the AKD2G-6V03S are "too small" and offered the 6 A models.
Check if that is right. Find where the mistake came from. Then list the drives that are still in
the running, with the requirements, the price with accessories, and the Bode plot tool.

## Work Done

### Short answer

- **The 3 A Kollmorgen drives are big enough.** Our hard requirement is 2.0 A rms continuous
  (DRV-01) and 5.9 A rms for 1 s (DRV-02). The AKD-x00306 and the AKD2G-6V03S give 3 A rms
  continuous and 9 A rms for 5 s. That is 50 % more than we need, on both values.
- **The mistake was in our own price request.** On 23 October we listed the motor data sheet
  values, including "9.8 A rms for 0.5 s (670 N)". We did not say that we do not need this value.
  DynamicDrives compared 9.8 A with the 9 A peak of the drive and wrote "too small, you need the
  6 A / 18 A model when you need more than 9 A peak". We do not need more than 9 A. The CE
  assessment even plans to lock the peak current at 5.9 A.
- **The Copley drive that Eltrex proposed is smaller than the Kollmorgen drive.** The Copley
  XEC-230-09 gives 2.12 A rms continuous and 6.4 A rms for 1 s. Copley writes its currents as
  peak values (3 A and 9 A "Adc"). Kollmorgen writes rms values. So "3 A / 9 A" means about
  40 % more current on the Kollmorgen drive than on the Copley drive.
- **The price request also described the old encoder.** It named a 1 Vpp encoder, or EnDat 2.2
  or BiSS-C as a second choice. Since 27 October the stage uses the RSF AK MC 15 B (BiSS-C,
  32 position bits, 2 status bits, 6-bit CRC, 0.1 µm step). DynamicDrives must check the drive
  against this encoder.
- **The quotation has expired.** Quotation 26MW1026 of 30 October was valid for 14 days, so up
  to 13 November. We need a new one.

### What DynamicDrives answered (30 October 2026)

| Our question | Their answer | What it means |
| --- | --- | --- |
| Do the drives meet the requirements? | "The drives are too small", because of more than 9 A peak | Not correct for our requirements. See above |
| Position loop rate, AKD and AKD2G | "In both cases the position loop is 4 kHz" | DRV-09 passes, now in writing. DRV-P3 (8 kHz) does not |
| 1 Vpp top frequency | 1 MHz without termination resistors, 250 kHz with them, for AKD X10 and AKD2G X23 | No longer important: the stage now uses BiSS-C |
| Bode plots in WorkBench | Frequency response measurement, Bode plots, simulation of the velocity and position loops, filter and resonance analysis | DRV-10 passes. They did not say clearly that the position loop itself can be measured |
| Thermal model for a third-party motor | Based on the motor settings and the thermal time constant. "Add extra monitoring in your application software" | Partly answered. No word on the peak time setting |
| Is the AKD-P00306-NBEC still made? | Order NDCC instead of NBEC. NDCC is the standard EtherCAT and CANopen version | The AKD is still offered |
| Encoder | With 1 Vpp: a "wake and shake" after every power-up. With EnDat 2.2 or BiSS-C: no wake and shake needed | Good for us: the RSF encoder is absolute BiSS-C |

### Quotation 26MW1026 (DynamicDrives, 30 October 2026, net, excluding VAT, about 6 weeks)

| Item | Price |
| --- | --- |
| AKD-P00306-NDCC-E000 (3 / 9 A rms, EtherCAT and CANopen) | € 961.88 |
| AKD-P00606-NDCC-E000 (6 / 18 A rms) | € 1,189.84 |
| AKD2G-SPE-6V03S-A1F3-0000-A (3 / 9 A rms, STO SIL 2 PL d, X23 feedback, connectors except X1 and X23) | € 1,219.86 |
| AKD2G-SPE-6V06S-A1F3-0000-A (6 / 18 A rms) | € 1,450.05 |

The 6 A models cost € 228 to € 230 more per axis. They also give a coarser current step for our
small motor. We do not need them.

The quotation holds no accessories. The Kollmorgen catalogue (2021) says the AKD-x00306,
AKD-x00606, AKD2G-6V03S and AKD2G-6V06S have **no internal brake resistor**. So we need an
external one. The X23 plug of the AKD2G is not in the connector set.

### Drives still in the running

"In the running" means: not from an Israeli supplier, and no hard requirement fails in the
maker's documents. **NC** means not confirmed in writing. NC is never a pass.

| Requirement | Kollmorgen AKD-P00306-NDCC-E000 | Kollmorgen AKD2G-SPE-6V03S-A1F3-0000-A | Copley XEC-230-09 |
| --- | --- | --- | --- |
| DRV-01: 2.0 A rms continuous | Pass: 3 A rms | Pass: 3 A rms | Pass: 2.12 A rms (small margin) |
| DRV-02: 5.9 A rms for 1 s | Pass: 9 A rms for 5 s | Pass: 9 A rms for 5 s | Pass: 6.4 A rms for 1 s (small margin) |
| DRV-03: peak limit and motor thermal model | Pass, details NC | Pass, details NC | Pass: programmable continuous current, peak current and peak time |
| DRV-04: bus 320 V to 600 V | Pass, about 325 V on 230 VAC | Pass, rated 310 V | Pass, about 325 V on 230 VAC |
| DRV-05: linear motor, no Hall sensors | Pass | Pass | Pass |
| DRV-06: reads the 3 PTC motor sensor | Thermal input on X10. Trip level NC | Thermal input on X23. Trip level NC | Pass: input IN11 is made for PTC to BS 4999, the MK21 values |
| DRV-07: EtherCAT CiA 402 | Pass | Pass | Pass |
| DRV-08: reads the RSF BiSS-C encoder directly | BiSS-C in the catalogue. RSF encoder, 32 bits, CRC: NC | BiSS-C on X23. RSF encoder, 32 bits, CRC: NC | BiSS-C supported. Bits and clock: NC |
| DRV-09: position loop 4 kHz | Pass (in writing, 30 October) | Pass (in writing, 30 October) | Pass, 250 µs |
| DRV-10: Bode plots in the setup software | Pass: WorkBench | Pass: WorkBench | Pass for the velocity loop in CME. Position loop modes need firmware 4.92, the newest published XEC firmware is 4.60: NC |
| DRV-11: CE, Declaration of Conformity | Pass (C2 with a mains filter and motor cable under 10 m) | NC: only a 2018 beta manual seen | Pass: EC Declaration seen, EMC category C3 |
| DRV-12: certified STO, SIL 2 / PL d | SIL 2 / PL d, one input. Certificate NC | SIL 2 / PL d, two channels. Certificate NC | Pass: certified by UL |
| DRV-13: stops on following error, encoder fault, soft limits | Pass | NC | Following error and feedback loss pass. Soft limits NC |
| P1: free biquad filters | Not checked | Pass: four biquads | Pass: custom biquads in the velocity loop |
| P3: position loop 8 kHz | No | No | No |
| Brake resistor | None inside. External needed | None inside. External needed | Inside: 60 Ω, 20 W, 248 J |
| Drive price (excl. VAT) | € 961.88 (quote expired) | € 1,219.86 (quote expired) | About € 1,175, an indication for 1 to 2 pieces (Eltrex, 18 November) |
| Accessories not yet priced | Brake resistor, encoder plug or cable, mains filter for C2 | Brake resistor, X23 plug or cable, mains filter for C2 | Connector kit (CK), serial cable for CME (asked 23 November), mains filter for C2 |
| Setup software | WorkBench, no licence quoted | WorkBench, no licence quoted | CME, free download |
| Delivery | About 6 weeks | About 6 weeks | Not stated |

All three drives also need a 24 VDC control supply. None of them meets the budget of about
€ 500 per axis.

### Drives with an open problem, kept as a fallback

| Drive | Price | Problem |
| --- | --- | --- |
| HIWIN E1 ED1F-EN-0422-01-00 with ESC-SS-S02 encoder box | Asked from Vansichen on 24 November. No price yet | Reads BiSS-C only through the box, so DRV-08 fails as written. Position loop rate not given. Peak 10 A for 1 s. Bode plots in Thunder |
| Delta ASD-A3-0421-E with ASD-IF-EN0A20 box | Only used prices seen. Box price not found | Same box problem. Position loop rate not given. Best documented STO. Bode plots in ASDA-Soft |

### Out of the running

- **Copley XEL-230-18:** no certified STO (DRV-12).
- **Elmo Platinum PBAS-BS-10/230FEVQ** (about € 2,013, Eltrex), Servotronix and Agito Akribis:
  Israeli suppliers.
- **Kollmorgen 6 A models:** they work, but they cost more and we do not need them.
- The other drives on the [servo drive selection page](../servo-drive-selection.md): they fail a
  hard requirement, or the price is far too high.

## Decisions Made

No purchase decision. The Kollmorgen AKD-x00306 and AKD2G-6V03S stay in the running. We do not
accept the 6 A models.

## Open Questions

Questions for DynamicDrives:

1. Please send a new quotation for the AKD-P00306-NDCC-E000 and the AKD2G-SPE-6V03S-A1F3-0000-A.
   Our requirement is 2.0 A rms continuous and 5.9 A rms for 1 s. The 9.8 A rms for 0.5 s is
   only the motor limit. We will lock the drive peak current at or below 5.9 A. Please confirm
   that the 3 A drives are then large enough.
2. The encoder is now the RSF AK MC 15 B: absolute, BiSS-C unidirectional, 32 position bits,
   2 status bits, 6-bit CRC, 0.1 µm step, clock up to 10 MHz, supply 3.6 V to 14 V. Do the AKD
   (X10) and the AKD2G (X23) read this encoder, including the CRC? Is BiSS-C on the AKD only for
   Renishaw encoders? What BiSS clock do they use?
3. Can WorkBench measure the open loop of the **position** loop, or only of the velocity loop?
   Can we export the data (gain and phase) as a file? Is WorkBench free?
4. Motor thermal sensor: three PTC in series, which must not trip below 1,650 Ω and must trip
   above 3,990 Ω. Can X10 (AKD) and X23 (AKD2G) read this, and can we set the trip level?
5. Thermal model: can we set the continuous current, the peak current and the peak time (5.9 A
   rms for 1 s) for a third-party linear motor?
6. Please quote the accessories: a brake resistor for each drive (the 3 A models have none
   inside), the encoder plug or a ready cable for X10 and X23, and the mains filter for EMC
   category C2.
7. Please send the EU Declaration of Conformity and the STO certificate (testing body, SIL, PL)
   for both drives. For the AKD2G we only have the beta installation manual of 2018.
8. Does the AKD2G stop the motor at software position limits (DRV-13)?
9. What is the price for 2 pieces?

## Next Steps

- Send the questions above to DynamicDrives.
- Wait for the Copley answers through Eltrex (firmware for the position loop Bode plot, BiSS-C
  bits, connector kit price).
- Wait for the HIWIN E1 price from Vansichen.
- Then update the [servo drive selection page](../servo-drive-selection.md) and choose.
- See the [mistake note](../mistakes/2026-11-25_price-request-listed-a-current-we-do-not-need.md).

<details>
<summary>Sources</summary>

- Email from Marc Weezenaar, DynamicDrives, 30 October 2026, answers written into our email of
  23 October, with quotation 26MW1026 (file `RF-1026-eof.pdf`, also on the shared Google Drive).
- Email from Han Weijenborg, Eltrex Motion, 18 November 2026, with the comparison
  `Refaqt - Aqtuator - 18-11-2026.pdf`: XEC-230-09 about € 1,175 and Elmo PBAS-BS-10/230FEVQ about
  € 2,013, for 1 to 2 pieces.
- Our email to Eltrex of 23 November 2026, which asks for the connector kit and serial cable.
- HIWIN and Vansichen emails, 4 to 24 November 2026. No price yet.
- Kollmorgen catalogue KM_CA_000246 Rev G (June 2021),
  [`docs/documentation/AMC-KM_CA_000246_RevG_EN-mobile.pdf`](../documentation/AMC-KM_CA_000246_RevG_EN-mobile.pdf):
  AKD2G model table (3 / 9 A rms, no internal regen for 6V03S and 6V06S) and AKD general
  specifications (AKD-x00306 3 / 9 A rms, internal regen 0 W).
- Copley XEC datasheet 16-01435 Rev 04, in the parts library under `modules/copley/`: peak 9 Adc
  (6.4 A rms) for 1 s, continuous 3 Adc (2.12 A rms), I2T programmable, IN11 for PTC.
- Requirements: `modules/compact-stage/architecture/motor-drive.sysml` (DRV-01, DRV-02, DRV-03).
- Safety checks: [CE assessment](../compact-stage-ce-assessment.md#the-drives-on-your-list).
- Copley Bode and firmware: [log of 2026-11-23](2026-11-23_copley-cme-loops-filters-and-bode.md).

</details>
