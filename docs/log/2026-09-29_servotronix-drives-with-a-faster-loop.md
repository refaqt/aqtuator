# 2026-09-29 — Servotronix drives with a faster position loop

**Role(s):** engineering, hardware, purchasing

## Goal

The [drive survey](2026-09-25_linear-stage-drive-and-motion-controller-survey.md) chose the
Servotronix CDHD2-003 as the second choice, with a position loop of 4 kHz. Does Servotronix sell a
drive that can do everything the CDHD2-003 does, with a position loop of at least 10 kHz? If not,
at least 8 kHz?

## Work Done

### Short answer

- **No Servotronix drive has a position loop of 10 kHz or more.** No data sheet we found gives a
  position loop faster than 8 kHz.
- **The CDHD2-003 already has an 8 kHz position loop.** The drive has two position controllers
  that you can choose between. The simple one (PID with feedforward) runs at 4 kHz. The other one,
  which Servotronix calls the "HD" controller, runs at 8 kHz. The manual calls the HD controller
  "the recommended controller". The survey only saw the 4 kHz number.
- **The CDHD2 is now marked "legacy" on the Servotronix website.** Its successor is the CDHD2S.
  The CDHD2S-003 has the same ratings, the same 1 Vpp encoder input, the same error table and the
  same loop rates. It is the safer model to buy.
- **The newer Servotronix drives do not fit.** The CD3E has a true 8 kHz position loop, but it
  cannot read a 1 Vpp encoder. The other new drives run on 60 VDC or less, or cannot read a 1 Vpp
  encoder.

### What the HD controller is

The HD controller is a position controller that Servotronix does not publish in detail
(a proprietary, nonlinear controller). It skips the separate velocity loop. It reads the position
and sends a current command directly, every 125 µs. It has its own filters: a second order
low-pass and two notch filters. It also has an adjustable feedforward at the end of each move to
shorten the settling time. The drive accepts position commands for it over EtherCAT.

Two limits:

- **It is not a PID loop you can design freely.** Its gains are set by the drive's automatic
  tuning, and then adjusted by hand. If you need a controller you design yourself inside the
  drive, the HD controller does not help.
- **The EtherCAT cycle is still at least 250 µs.** So a controller that runs in the PC, with the
  drive in torque mode, is still limited to 4 kHz. The 8 kHz only helps when the drive closes the
  position loop itself.

### Servotronix drives checked

| Drive | Supply | Current, continuous / peak | 1 Vpp input | Current / velocity / position loop | Result |
| --- | --- | --- | --- | --- | --- |
| CDHD2-003 (legacy) | 1 phase, 120 to 240 VAC | 3 / 9 Arms for 2 s | Yes, up to ×16 384 | 32 / 8 / 4 kHz. HD position controller 8 kHz | The present choice. Meets 8 kHz with the HD controller |
| CDHD2S-003 | 1 phase, 120 to 240 VAC | 3 / 9 Arms for 2 s | Yes, up to ×16 384 | 32 / 8 / 4 kHz. HD position controller 8 kHz | **Best Servotronix choice.** Same as the CDHD2, and not legacy |
| CDHD2-LV | 20 to 90 VDC | Up to 15 Arms | Yes | Same as the CDHD2 | Bus voltage too low for peak force at full speed |
| CD3E-003 | 1 phase, 220 VAC | 3 / 9 Arms for 2 s | **No.** Digital A/B only. BiSS-C "in development" | 16 / 8 / 8 kHz | Rejected. Also no dual loop and no error table |
| LDHD3-006 (new in 2026) | 1 phase, 200 to 240 VAC | 6 / 18 Arms | **No.** A/B, BiSS-C, Tamagawa | Not published | Rejected |
| LVD2 | 24 to 48 VDC | Not checked | Yes | 16 / 8 kHz. Position loop not published | Bus voltage too low |
| ZED 15 to 65 | 18 to 60 VDC | Up to 45 Arms | **No** | Not published | Rejected |
| Rayon 70, Rayon 300 | 12 to 48 VDC | 55 Arms and more | Yes | Not published | Bus voltage too low |

The CD3E, LDHD3 and LVD2 come from the Chinese Servotronix company (Gaochuang). The other drives
come from STXI Motion, the Israeli company. Both sell under the Servotronix name.

The "3 to 5 kHz" on the Servotronix pages is the bandwidth of the current loop. It is not a loop
rate.

### Compared with the first choice

The Elmo Gold Oboe 6/230, the first choice in the survey, has a position loop of 10 kHz. So the
Elmo is still the only drive in the survey that meets 10 kHz with 230 VAC and a 1 Vpp input. For
8 kHz, the Servotronix CDHD2S-003 with the HD controller is a real second choice.

## Decisions Made

No purchase decision. If Servotronix is chosen, buy the CDHD2S-003, not the legacy CDHD2-003, and
plan to use the HD position controller.

## Open Questions

- Does the error table work together with the HD controller? The manual does not say.
- How does the HD controller behave at our cutting force frequencies? This needs a test on the
  stage.
- Does the CDHD2S accept an EtherCAT cycle shorter than 250 µs with newer firmware?
- How long will Servotronix still sell and support the CDHD2?

## Next Steps

1. When asking Servotronix for a quote, ask for the CDHD2S-003 and ask the open questions above.

<details>
<summary>Sources</summary>

- CDHD2 user manual, firmware 2.38, revision 2.6. Loop rates on page 43, the HD controller on
  pages 212 and 218:
  <https://stxim.com/wp-content/uploads/2024/01/CDHD2_User_Manual_fw2.38.x_Rev_2.6-i.pdf>
- CDHD2S user manual, version 1.12 (2023-11-01). Loop rates on page 28, ratings on page 23,
  1 Vpp input on page 32, error correction in chapter 6.17:
  <https://e-motors.tech/wp-content/uploads/2024/07/CDHD2S-Manual-V1.12-20231101-en.pdf>
- CDHD2S flyer: <https://stxim.com/wp-content/uploads/2025/07/CDHD2S_EC_241220-EN-1.pdf>
- STXI Motion product list, with the CDHD2 marked legacy: <https://stxim.com/products/>
- CDHD2-LV page: <https://stxim.com/product/cdhd2-lv-low-voltage-high-performance-servo-drives/>
- CD3E quick start guide, version 0.86 (2025-03-04), in Chinese. Loop rates and ratings on pages
  12 and 13, encoder types on page 16:
  <https://28526507.s21i.faiusr.com/61/1/ABUIABA9GAAgjqvIwgYo-oP2iQY.pdf>
- LDHD3 flyer, 2026-08-20: <https://www.servotronix.cn/en/download/1136>
- LVD2 flyer, 2026-06-26: <https://www.servotronix.cn/en/download/1132>
- ZED 65 data sheet, revision 1.15:
  <https://stxim.com/wp-content/uploads/2026/07/Datasheet-ZED-65-Rev.1.15.pdf>
- ZED flyer: <https://stxim.com/wp-content/uploads/2026/03/ZED_EN_2026_v1_web.pdf>
- Rayon flyer:
  <https://stxim.com/wp-content/uploads/2024/01/Rayon-Harsh-Environment_Flyer_EN_2021_V1.pdf>

A web search summary said the CD3E position loop is 2 kHz. The guide itself says 8 kHz. The table
uses the guide.

</details>
