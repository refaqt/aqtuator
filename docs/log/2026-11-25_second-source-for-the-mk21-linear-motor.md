# 2026-11-25 — Second source for the MK21 linear motor

**Role(s):** engineering, purchasing

## Goal

Find two more makers of a linear motor that fits in the space of the Maxwell MK21 and gives at
least the same continuous force. Peak force is less important. Israeli makers stay out, as in the
[drive search of 2026-09-29](2026-09-29_non-israeli-drives-with-open-control-loops.md).

The limits, from the MK21 data: moving part (forcer) at most 118 mm long and 86 mm wide, total
height of forcer plus magnet track at most 34 mm, and at least 181 N continuous force.

## Work Done

- **Only one other maker meets every limit: HIWIN (Taiwan), with the LMSA21.** Its published data
  is the same as the MK21 data: 181 N continuous, 512 N for 1 s, 2.0 A rms, 92.5 N per A rms,
  forcer 118 x 86 mm, 34 mm height, 30 mm pole pitch, 86 mm magnet track in 120, 180 and 300 mm
  lengths. The Maxwell MK2 range looks like a copy of the HIWIN LMSA range. HIWIN also sells the
  LMSA21L with the same force at 4.4 A rms.
- **No third maker fits.** Each other motor that was checked is too long, too high, or too weak.

  | Maker and motor | Forcer length x width | Height | Continuous force | Fails on |
  | --- | --- | --- | --- | --- |
  | HIWIN LMSA21 (Taiwan) | 118 x 86 mm | 34 mm | 181 N | Fits |
  | Chieftek LM-CB2-80 (Taiwan) | 130 x 80 mm | 45 mm | 201 N without heat sink, 301 N with heat sink | Length, height |
  | Chieftek LM-CA2-115 (Taiwan) | 97 mm x about 115 mm (coil width) | not read | 131 N without heat sink, 229 N with heat sink | Width |
  | Tecnotion TL6 / TLX6 (Netherlands) | 146 mm long | not read | 200 N / 236 N | Length |
  | Tecnotion TM6 (Netherlands) | 93 mm long | not read | 120 N | Force |
  | Siemens 1FN3050-1ND00 (Germany) | 162 x 67 mm | 59.4 mm | 151 N | Length, height, force |
  | Siemens 1FN3050-2WC00 (Germany) | 255 x 67 mm | 48.5 mm | 200 N | Length, height |
  | Mitsubishi LM-H3P3A-12P (Japan) | 128 mm long | not read | 120 N | Length, force |
  | Kollmorgen IC11-050 (USA) | 200 x 85 mm | about 58 mm | 263 N | Length, height |
  | Yaskawa SGLFW2-30A120A (Japan) | not read | not read | 90 N | Force |
  | Beckhoff AL2406 (Germany) | 143 x 51 mm | 40 mm | 120 N air cooled | Force; out of production |
  | Sodick small core motor (Japan) | 115 x 95 mm | 30 mm coil | 89 N, 132 N with heat sink | Width, force |
  | Hans Motor LSMFK (China) | 194 mm long or more | not read | 600 N or more | Length |

- **Makers rate continuous force in different ways.** Chieftek gives a value with and without a
  heat sink. Tecnotion and Siemens give a value at a set coil temperature, with the mounting face
  held at 20 °C. The test conditions behind the 181 N of the MK21 and the LMSA21 were not found.
  So a motor that is close on paper may be stronger or weaker in our stage.
- **Akribis (AKM and AJM series) was not checked,** because it has a research centre in Israel.

## Next Steps

- Ask HIWIN (HIWIN GmbH, who already answered on the E1 drive) for the LMSA21 drawing, price and
  delivery time. Check that the hole pattern and the magnet track match the MK21 and the MK2
  stators before calling it a drop-in second source.
- Ask Maxwell and HIWIN under which conditions the 181 N is given: coil temperature, heat sink
  size and ambient temperature.
- If a third source is needed, decide which limit may grow. With a 130 mm forcer, the Chieftek
  LM-CB2-80 gives about 200 N without a heat sink, but it is 11 mm higher.

<details>
<summary>Technical notes</summary>

- MK21 data: `modules/stoq/modules/maxwell/modules/mk2-mover/bom/parts.csv`. Height 34 mm =
  stator 9.6 mm + forcer 23.7 mm + 0.7 mm air gap.
- HIWIN LMSA data: HIWIN product table at motioncontrolsystems.hiwin.com (LMSA series) and the
  HIWIN LMSA data sheet copy at automation.lubielectronics.com. Read through web search results;
  the HIWIN host was not reachable from the session.
- Chieftek: `LM_en.pdf` (LM-05-R81-EN, 2024) from chieftek.com. Ratings at 25 °C to 110 °C.
- Tecnotion: main catalogue (2016) and TLX spec sheet v1.3. Coils at 100 °C, mount at 20 °C.
- Siemens: 1FN3 configuration manual 06/2023, tables for peak-load and continuous-load primaries.
- Mitsubishi: linear servo motor manual SH-030316ENG rev C.
- Kollmorgen, Yaskawa, Beckhoff, Sodick, Hans Motor: values from maker pages and distributor
  listings found by web search. Check them in the maker data sheet before use.
- Prodrive Chiron (Netherlands) could not be checked: the catalogue link returns 404.

</details>
