# 2026-11-05 — Price request to HIWIN for the E1 drive and class H guides

**Role(s):** engineering, purchasing

## What happened

HIWIN GmbH answered our first price request. They cannot deliver the E2 drive in the EU. They
offer the E1 drive instead. For the guides, class H is their standard and comes from stock in 5 to
10 working days. Class P takes about 10 weeks. If we order rail and blocks as a set, HIWIN can
deliver them already greased.

We drafted a reply. It asks for a price for the E1 drive
**ED1F-EN-0422-01-00** with the **ESC-SS-S02** encoder box, and it chooses class H guides instead
of class P. The reply also asks whether we may take the blocks off the rail and put them back
ourselves, when they come as a greased set. The full text is in the closed block at the end.

### Class H accuracy, size 15, from the HIWIN EG catalogue

| Item | Class H | Class P, for comparison |
| --- | --- | --- |
| Tolerance of the height H | ± 30 µm | 0 / −30 µm (interchangeable parts: ± 15 µm) |
| Tolerance of the width N | ± 30 µm | 0 / −30 µm (interchangeable parts: ± 15 µm) |
| Height difference between blocks on one axis | 10 µm | 6 µm |
| Width difference between blocks on one axis | 10 µm | 6 µm |
| Running parallelism, rail 300 to 500 mm (our rail is 418 mm) | 12 µm | 6 µm |

Running parallelism is how straight a block runs along the rail, measured against the rail's
reference faces. With preload ZA on size 15, the two mounting surfaces must be parallel within
18 µm. Their height difference must be at most 85 µm per 500 mm between the rails.

### The risk for the stage

The stage requirement STG-05 asks for a straight motion within ± 2 µm over the full travel. On a
418 mm rail, the catalogue allows 12 µm in class H and 6 µm in class P. Even class UP (ultra
precision) allows 2 µm. The real carriage error is often smaller, because two rails and four blocks
average part of it. But no class promises ± 2 µm on paper. So the choice between H and P mainly
changes the delivery time. It does not decide whether STG-05 is met.

## Decisions

- Class H guides instead of class P, from stock. The block code becomes QEH15SAZAH+E2. We made
  this code ourselves by changing P to H. HIWIN must confirm it.
- The E1 drive to ask a price for is the ED1F-EN-0422-01-00 with the ESC-SS-S02. See the
  [ED1 check](2026-11-05_hiwin-ed1-checked-against-the-requirements.md).

## Open Questions

- Can STG-05 (± 2 µm straightness and flatness) be met with class H guides plus measurement and
  compensation?
- What is the order code for one set of 2 rails and 4 blocks?
- Can we take the blocks off the rail and put them back? Do we need a dummy rail for that? Do
  accuracy, preload, grease and warranty stay the same?
- Which grease does HIWIN use, and which oil is in the E2 unit?

## Next Steps

- Send the reply to HIWIN GmbH.
- Record the answers in a new log entry, and update the
  [servo drive selection page](../servo-drive-selection.md) when the loop rates are known.

<details>
<summary>Sources and the email text</summary>

Sources:

- HIWIN EG Series catalogue G99TE24-2410 (2025), distributor copy:
  <https://s3.amazonaws.com/www.motionusa.com/hiwin/2025/EG%20Series_2025.pdf>. Table 2-2-3
  (non-interchangeable, EG15/20), table 2-2-5 (interchangeable), table 2-2-7 (running parallelism)
  on pages 48 and 49. Tables 2-2-18 and 2-2-19 (mounting surfaces) on page 55.
- The QE block runs on the EGR rail. A HIWIN tolerance document lists QE in the same running
  parallelism table. The separate QE catalogue was not opened.
- STG-05 in `modules/compact-stage/architecture/compact-stage.sysml`.
- Thermal sensor values from [the MK21 thermal sensor entry](2026-11-05_mk21-thermal-sensor-known.md).

Email text, in Dutch, as drafted:

> Beste Harjot,
>
> Bedankt voor uw snelle antwoord.
>
> **Drive**
>
> Een E1-drive kan voor ons werken. Wij denken aan de **ED1F-EN-0422-01-00** (400 W, EtherCAT,
> 230 VAC, voor lineaire motoren, met gecertificeerde STO). De drive leest onze BiSS-C-encoder niet
> rechtstreeks. Daarom hebben we ook de encoderbox **ESC-SS-S02** nodig (artikel 80050247 in uw
> catalogus ED1-03-0-EN-2410-K).
>
> Graag een offerte voor 1 en voor 2 sets, met levertijd. Eén set bestaat uit:
> - ED1F-EN-0422-01-00
> - ESC-SS-S02
> - de kabels tussen drive en ESC, en tussen ESC en encoder
> - de connectorset
>
> Klopt deze bestelcode voor levering in de EU? Zo niet, welke code raadt u aan?
>
> Onze vragen over de drive:
> 1. Wat zijn de frequenties van de stroom-, snelheids- en positieregellus, met een lineaire motor
>    en de ESC-SS-S02?
> 2. Geeft de ESC-box vertraging op het positiesignaal? Zo ja, hoeveel?
> 3. Kan de 400 W-drive 5,9 A rms gedurende 1 s leveren? Zo niet, graag ook een prijs voor de
>    ED1F-EN-1022-01-00.
> 4. De motor heeft 3 PTC-thermistoren in serie (SNM120). Bij 25 °C is de weerstand maximaal
>    300 Ω. 5 °C onder het schakelpunt is die maximaal 1 650 Ω. 5 °C boven het schakelpunt is die
>    minimaal 3 990 Ω. De sensor mag nooit meer dan 30 V zien. Leest de PTC-ingang van de ESC-box
>    deze sensor correct?
> 5. Kan "SW method 1" de commutatiehoek vinden bij een ijzerloze lineaire motor van een ander merk
>    (MAXWELL MK21, poolsteek 30 mm), zonder Hall-sensoren?
> 6. Leest de ESC-SS-S02 de RSF AK MC 15 B (BiSS-C, 32 bit positie, 2 bit status, 6 bit CRC)
>    zonder extra instellingen?
>
> **Lineaire geleidingen**
>
> Wij kiezen voor klasse H in plaats van P, uit voorraad. Graag een prijs voor 1 en voor 2 stages,
> als set gesmeerd geleverd:
> - rail EGR15U418H: 2 of 4 stuks
> - blok QEH15SAZAH+E2 (voorspanning ZA, klasse H, met E2-smeerunit): 4 of 8 stuks
>
> Onze vragen:
> 1. Welke bestelcode heeft de set van 2 rails met 4 blokken per stage?
> 2. Is voorspanning ZA in klasse H ook uit voorraad leverbaar?
> 3. Welk vet gebruikt u bij het smeren? Met welke olie is de E2-unit gevuld? Is dat Mobil SHC 636?
> 4. Bij de montage van de stage moeten we de blokken misschien van de rail halen en later
>    terugplaatsen. Kan dat bij een set, of bij blokken die gesmeerd geleverd worden?
>    - Hebben we daarvoor een montagerail (dummy rail) nodig, zodat de kogels niet uit het blok
>      vallen? Kan HIWIN die leveren?
>    - Moet elk blok terug op dezelfde rail en in dezelfde richting? Hoe zijn de blokken en rails
>      gemerkt?
>    - Blijven de nauwkeurigheid, de voorspanning en de smering dan behouden?
>    - Blijft de garantie geldig als wij de blokken zelf verwijderen en terugplaatsen?
>
> Alvast bedankt.
>
> Met vriendelijke groeten,
> Niels Bosmans

</details>
