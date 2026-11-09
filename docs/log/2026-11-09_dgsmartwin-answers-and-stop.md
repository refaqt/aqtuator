# 2026-11-09 — DGSMARTWIN answers on the AKS drive and the SA32 encoder. We stop with them for now

**Role(s):** engineering, purchasing

## Goal

DGSMARTWIN answered our questions on the AKS-4D52AECAB drive and the SA32 absolute encoder. Record
the answers and the prices. Niels Bosmans decided not to continue with DGSMARTWIN for now.

## Work Done

### Short answer

- **We do not continue with DGSMARTWIN now.** This covers both the AKS drive and the SA32 encoder.
  We may look at them again later. See the
  [decision record](../decisions/2026-11-09_no-dgsmartwin-for-now.md).
- **The four reasons**, from Niels Bosmans:
  1. The drive documentation is not clear, and most of it is in Chinese.
  2. We still have no loop rate for the current, speed and position loops.
  3. The absolute encoder is much more expensive than the RSF MC 15 encoder.
  4. The encoder documentation is too limited. There is no manual and no CAD model.
- **The AKS drive stays "not confirmed" on DRV-09 and DRV-P3.** DGSMARTWIN gave a "minimum
  communication cycle" of 1 ms. That is not a loop rate.

### How the questions went

| Date | Who | What |
| --- | --- | --- |
| 2026-10-14 | Niels Bosmans | Web form: asks for an English catalog and manuals, with interest in the SA32 |
| 2026-10-15 | DGSMARTWIN | Sends the "Drive&Encoder" catalog |
| 2026-10-19 | Niels Bosmans | Asks for the drive manual and loop rates, and ten questions on the SA32 |
| 2026-10-21 | DGSMARTWIN | Sends the AKS drive manual and the first answers |
| 2026-10-22 | Niels Bosmans | Asks again for the loop rates, the position loop tuning, the software language, and prices |
| 2026-10-30 | Niels Bosmans | Reminder |
| 2026-10-31 | DGSMARTWIN | "Our technical team is too busy." Will reply later |
| 2026-10-31 | Niels Bosmans | Asks for a price for one unit of each |
| 2026-11-09 | DGSMARTWIN | Answers, prices, and two extra drive documents in Chinese |

### AKS-4D52AECAB drive: the answers

| Question | Answer |
| --- | --- |
| Current, speed and position loop rates, in Hz or ms | 21 Oct: the three loops "are tuned according to actual operating conditions". 9 Nov: "Minimum communication cycle: 1 ms" |
| Position loop tuning | Two extra PDF files, both in Chinese: a gain and smoothing tutorial for the AKS and EKS drives, and a quick setup and alarm guide |
| Is the software in Chinese only? | The software supports English |
| Price for 1 unit | CNY 3,600, FOB Shenzhen |

**What the 1 ms means.** It is the time between two messages on the bus, not how often the drive
runs its loops. It also does not match the manual: page 44 allows an EtherCAT cycle from 0.125 ms
to 16 ms. So the answer gives no loop rate. Under our rule we need a written loop rate (see the
mistake entry [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md)).
DRV-09 (4 kHz) and DRV-P3 (8 kHz) stay "not confirmed".

The other open points of the
[manual check](2026-10-22_aks-drive-manual-checked-against-the-requirements.md) got no answer: the
frequency sweep, the I²t fold back for a third-party motor, the MK21 thermal sensor, and the tested
encoders.

### SA32 encoder: the answers

The questions were for the read head SA32EY05A-MC (EnDat 2.2, 0.1 µm step). The
[earlier log](2026-10-19_dgsmartwin-sa32-endat-encoder-order.md) had the SA32EH05A-MC (0.05 µm
step) as first choice. Both pass ENC-01.

| Question | Answer |
| --- | --- |
| Scale length for 220 mm of travel | SA32-L250-MC (250 mm) |
| Scale material and how it is fixed | A steel tape, glued to the base. A bracket is needed to hold the read head |
| Homing | Not needed for the absolute head. The incremental head needs homing at each start |
| Scale applicator and end clamps | "We provide" a Renishaw-type applicator and end clamps. No product numbers given |
| "±2.5 µm/m after 25° position compensation" | 25 °C is normal room temperature. The compensation is done after a laser interferometer calibration. Not said where the correction is stored |
| Top speed at 0.05 µm and 0.1 µm | 10 m/s for both |
| Product manual, installation manual, 3D CAD model | Not sent. No answer on the manual or the CAD model |
| Installation video | Too large for email. They ask for WhatsApp, WeChat or DingTalk |
| Price for one set | CNY 5,500, FOB Shenzhen, for 1 read head SA32EY05A-MC and 1 scale SA32-L250-MC. Applicator and end clamps not in the price |

What changes in the encoder check: ENC-03 now passes on a written answer (10 m/s at 0.1 µm). ENC-02,
ENC-05, ENC-06, ENC-09 and ENC-10 stay "not confirmed", because we have no data sheet.

### Prices next to each other

| Item | Price, FOB Shenzhen | Not in the price |
| --- | --- | --- |
| AKS-4D52AECAB drive, 1 unit | CNY 3,600 | Shipping, import duty, VAT, cables, connector set |
| SA32EY05A-MC head + SA32-L250-MC scale, 1 set | CNY 5,500 | Shipping, import duty, VAT, applicator, end clamps, extension cable |

The prices are also in maqers, on the DGSMARTWIN supplier (offers on hold). There is no written
RSF price in our repositories. "Much more expensive than the RSF MC 15" is the judgement of Niels
Bosmans.

## Decisions Made

- Stop with DGSMARTWIN for now, for the drive and for the encoder. See the
  [decision record](../decisions/2026-11-09_no-dgsmartwin-for-now.md).
- The RSF MC 15 stays the encoder of the compact stage.
- No reply to DGSMARTWIN is sent from this work. The user decides if and how to tell them.

## Open Questions

Not answered by DGSMARTWIN. Ask these first if we look at them again:

1. The current, speed and position loop rates of the AKS-4D52AECAB, in Hz.
2. An English version of the position loop tuning documents.
3. The SA32 product manual, installation manual, and 3D CAD model.
4. Product numbers and prices of the scale applicator and the end clamps.
5. Where the SA32 accuracy correction is stored: in the head, or in the drive.

## Next Steps

- None for DGSMARTWIN now.
- The drive choice goes on with the other candidates on the
  [servo drive selection page](../servo-drive-selection.md).

<details>
<summary>Sources</summary>

- Email thread "Quotation for AKS-4D52AECAB & SA32 encoder", DGSMARTWIN sales
  (qy@dgsmartwin.com, copy to win@dgsmartwin.com), 2026-10-21 to 2026-11-09.
- Earlier thread "官网询盘留言" (web form inquiry), 2026-10-14 to 2026-10-19, with the
  "Drive&Encoder" catalog.
- Attachments of 2026-11-09, not added to the repository: "AKS&EKS操作教程-增益平滑调整2.0白（刚性）260328.pdf"
  (gain and smoothing tutorial) and "快速调试手册及警报处理.pdf" (quick setup and alarms).
- AKS manual: [`docs/documentation/AKS Drive Manual.pdf`](../documentation/AKS%20Drive%20Manual.pdf),
  page 44 for the EtherCAT cycle.

</details>
