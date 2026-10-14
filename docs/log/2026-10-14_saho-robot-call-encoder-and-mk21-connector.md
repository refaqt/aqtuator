# 2026-10-14 — Call with Saho Robot: Lamotion encoder parts and the MK21 connector

**Role(s):** purchasing, engineering

## What happened

Niels had a chat with Saho Robot. Saho Robot supplies the MAXWELL linear motors. Saho Robot also
supplies Lamotion encoders, through a partnership with Lamotion.

### Encoder parts asked for

Niels asked Saho Robot for these Lamotion parts:

| Part | What it is | Quantity |
| --- | --- | --- |
| AL26B100-05MUL | Reading head | 1 |
| ALZ00270G | Steel scale tape | 1 |
| ABS-ET-A/B | End clamp for the tape | 2 |
| ALZ-ASST-ABS | Tool to mount the scale tape | 1 |

### The MK21 motor connector

- **We can ask for any connector.** By default, the MK21 motors come with one large D-SUB
  connector. Saho Robot sent the wiring sheet for it:
  [MK21 motor wiring sheet, 2025-12-16](../documentation/maxwell-mk21-motor-wiring-2025-12-16.xls).
- **The motor phases and the temperature sensor share this one connector.** This is a single
  cable for both.
- **The motor connector has no Hall sensor.** The sheet lists only the 3 phases, earth and the
  temperature switch. The other 3 signal pins are empty. This answers the first open question in
  [the round connector note from yesterday](2026-10-13_mk21-motor-cable-connector.md).

What the wiring sheet says about the motor connector:

| Item | Value |
| --- | --- |
| Connector type | D-SUB 9W4M, male. This is a mixed D-SUB with 4 power contacts and 5 signal contacts. |
| Largest size | 52 × 54.5 × 16.7 mm |
| Cable diameter | 9.3 mm |
| Power pins A1, A2, A3, A4 | U, V, W, PE (earth) |
| Signal pins 1 and 2 | Temperature switch |
| Signal pins 3, 4 and 5 | Not used |
| Motor cable needed | 4 wires of 1 mm², with a shield |

The sheet also shows how to wire an encoder and the temperature sensor to a Servotronix drive.
We do not use Servotronix, because we do not buy from Israeli suppliers. That part of the sheet
does not apply to us.

## Decisions

No decision was made yet. The standard D-SUB connector is large. It is 52 mm wide, so it may not
fit the cable slot in the bottom carriage. A smaller round connector is still an option, because
Saho Robot can fit any connector we ask for.

## Open Questions

- The sheet gives a cable diameter of 9.3 mm. The MK2 data sheet gives 6.8 ± 1 mm. Which value is
  right for the MK21 cable? Is 9.3 mm perhaps the cable of the encoder or of an extension?
- The earlier encoder study found the Lamotion ABS head 16.5 mm wide and 18.4 mm high. That fails
  two of our size limits. Is the AL26B100-05MUL head the same size? Check its data sheet.
- What does the AL26B100-05MUL head send out (BiSS-C, Panasonic serial or other), and does our
  drive accept it?
- What will the four encoder parts cost, and when can they arrive?

## Next Steps

1. Wait for the Saho Robot quote on the four encoder parts.
2. Ask Saho Robot which cable diameter is right, and ask for a data sheet of the AL26B100-05MUL
   head.
3. Choose the motor connector: the standard D-SUB 9W4M, or a smaller round connector. Without a
   Hall sensor, an M15 connector (3 + PE + 5 signal) carries everything. See
   [the round connector note](2026-10-13_mk21-motor-cable-connector.md). Tell Saho Robot the
   choice before they make the motor.

<details>
<summary>Technical notes</summary>

- The wiring sheet has an English and a Chinese tab with the same content. The Chinese tab marks
  signal pins 3, 4 and 5 as "空" (empty).
- The encoder part of the sheet is for a "HOPO absolute grating encoder" on a D-SUB 9 female
  connector: SLO+/SLO- (pins 4, 8), MA+/MA- (pins 3, 7), 5 V (pin 5), 0 V (pin 9), shield on the
  shell. It maps to the SSI data and clock lines of a Servotronix MDR 26 connector. The motor
  temperature sensor goes to MDR 26 pins 11 and 25. The encoder cable must have 8 cores of
  0.2 mm², twisted in pairs, with a shield.
- The meaning of the code AL26B100-05MUL was not checked. It is not listed in
  [the linear encoder selection page](../linear-encoder-selection.md). The ALZ tape belongs with the
  Lamotion ABS head in that page.
- Mistake rule checked:
  [fatigue estimate without a datasheet](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md).
  All connector values come from the supplier's own sheet. No value was guessed.
- No CAD or parts list was changed.

</details>
