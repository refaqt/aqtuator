# 2026-09-29 — Encoder converters and drives that read SSI or BiSS-C

**Role(s):** engineering, hardware, purchasing

## Goal

Cheap drives often cannot read our 1 Vpp encoder, but they can read a digital encoder signal:
SSI or BiSS-C. So we checked four ways to connect the encoder to a cheaper drive:

1. A box that turns the 1 Vpp signal into SSI, and a drive that reads SSI.
2. A box that turns the 1 Vpp signal into BiSS-C, and a drive that reads BiSS-C.
3. An absolute encoder with BiSS-C, a box that turns BiSS-C into SSI, and a drive that reads SSI.
4. A drive that reads BiSS-C directly.

The drive must have EtherCAT and a position loop of 8 kHz or faster. Filters that we can set
ourselves are preferred. The drive and the converter together must cost less than 500 euro.

The earlier hard requirements still apply: the MAXWELL MK21 linear motor, a 230 VAC single phase
supply, at least 2.0 Arms continuous and 5.9 Arms peak, no Israeli suppliers, and no drive that
we build ourselves. The earlier searches are in
[Drives below 800 euro per axis](2026-09-29_drives-below-800-euro-per-axis.md) and
[HIWIN, Delta and Kollmorgen follow-up](2026-09-29_hiwin-delta-kollmorgen-follow-up.md).

## Work Done

### Short answer

- **The best find needs no converter.** A used KEBA ServoOne junior (the older name is LTi
  ServoOne junior) reads a 1 Vpp encoder directly. It has EtherCAT, a position and speed loop at
  8 kHz, and filters. Used units cost about 180 to 270 euro. This is the only drive in all the
  searches that meets every hard requirement in the maker's own documents and fits the budget.
  Two points are still open: the 8 kHz figure is in the brochure for the whole ServoOne family,
  and KEBA must approve encoders that it does not sell itself.
- **Options 1 and 2 are possible with one cheap board.** The iC-Haus iC-NQC chip turns 1 Vpp into
  SSI or into BiSS-C. It keeps a full position count, not only the angle inside one period. A
  ready evaluation board costs USD 87. The delay is almost zero, so it does not limit an 8 kHz
  loop.
- **But no cheap SSI or BiSS-C drive has a confirmed 8 kHz position loop.** The cheap Asian drives
  that read BiSS-C (Delta ASDA-A3, Inovance SV680N, HIWIN E2 and ED1) do not publish the rate.
  The drives that do publish it and pass (Parker PSD1, Metronix smartServo BL 4104-C) have no
  price we could find. So options 1, 2 and 4 are "not confirmed" today.
- **Option 3 is not worth it.** There is no ready box that turns BiSS-C into SSI. If we want an
  absolute encoder for an SSI drive, we can buy an encoder with SSI output instead, for example
  the RLS LA11. The encoder then adds to the cost, and the LA11 is less accurate (±40 µm per
  metre).

### The four options

| Option | Converter | Drive that fits best | Total cost | 8 kHz | Result |
| --- | --- | --- | --- | --- | --- |
| 1. 1 Vpp to SSI, SSI drive | iC-NQC board, USD 87 | KEBA ServoOne junior (reads SSI, but also 1 Vpp, so the box is not needed). Inovance SV680N (reads SSI) | 180 to 360 euro | ServoOne: yes (family brochure). Inovance: not published | Works, but the box adds nothing if we buy the ServoOne |
| 2. 1 Vpp to BiSS-C, BiSS-C drive | iC-NQC board, USD 87 | Delta ASD-A3-0421-E, used, about USD 225 with shipping | About 300 euro | Not published | Fits the budget. Loop rate not confirmed |
| 3. Absolute BiSS-C to SSI, SSI drive | No product found | Same as option 1 | Encoder extra | As option 1 | Not recommended. Buy an SSI encoder instead |
| 4. BiSS-C drive only | None, if the encoder is absolute BiSS-C. Otherwise the same box as option 2 | Delta A3-E, Inovance SV680N, Metronix BL 4104-C, Parker PSD1 | 200 to 300 euro for Delta; others not found | Parker and Metronix: yes. Delta and Inovance: not published | Only the drives without a price pass on paper |

### Converters

| Product | Output | Resolution | Delay | Position at power-up | Price |
| --- | --- | --- | --- | --- | --- |
| **iC-Haus iC-NQC**, evaluation board NQC6D | BiSS-C or SSI (Gray or binary), plus A/B/Z | 8192 steps per period, 24 bit period count | 250 ns | Starts at zero. The zero pulse can reset it | Board USD 87, chip about USD 9 |
| NiLAB NL-NQ6D (a DIN rail box with the iC-NQC) | BiSS-C or SSI | 8192 steps per period | Not published | Same | Not found |
| iC-Haus iC-TW29 | BiSS-C, no SSI | Up to 26 bit | 2.4 or 5.0 µs | Incremental | Not found |
| Heidenhain EIB 192 and EIB 392 | EnDat 2.2, Fanuc or Mitsubishi only. **No SSI or BiSS** | 16384 steps per period | ≤ 5 µs | After the reference mark | EIB 392 F: USD 795 |
| BiSS-C to SSI box | **No product found** | | | | |

Things to check before we use the iC-NQC:

- **Counter length.** Set the period counter to 24 bit. With 8 or 12 bit the position wraps every
  5 mm or 82 mm at a 20 µm period. The drive must read the full frame, about 37 bits of data.
  Many drives treat SSI as a rotary encoder with a limit of 25 to 32 bits. Check this in the
  drive manual.
- **SSI has no check sum.** One wrong bit gives a large position jump. BiSS-C has a check sum, so
  prefer BiSS-C where the drive allows it.
- **Commutation.** The converter gives no absolute position at power-up. The drive must find the
  motor phase itself at start-up, or we must use Hall sensors. The ServoOne can find the phase
  itself.
- **Signal levels.** The chip has logic level outputs. The drive needs RS422. The board is said to
  have RS422 connectors, but we did not see this in its manual.

### Drives

P = pass, F = fail, NC = not confirmed, NP = not published.

| Drive | Encoder input | Linear motor | Position loop | Filters | Price seen |
| --- | --- | --- | --- | --- | --- |
| **KEBA ServoOne junior SO22.006, EtherCAT version** | 1 Vpp with zero pulse, SSI, EnDat, HIPERFACE on port X7. BiSS-C only with an option card | P. Also finds the motor phase without an absolute encoder | P: 8 kHz (125 µs), current 16 kHz. From the ServoOne family brochure | Notch, low-pass (PT1, PT2), "higher-order filters" | About 180 to 270 euro used |
| Delta ASD-A3-0421-E | BiSS-C, EnDat 2.2 on CN2. No SSI | P | NP | 5 notches, low-pass | About USD 225 used |
| Inovance SV680N / SV680LN | BiSS-C, SSI, EnDat 2.2 on the second port | P (maker web page) | NP | One biquad in the sister model. NC for this model | NC |
| HIWIN ED1 or E2 Advanced | BiSS-C (ED1 only with the ESC box). No SSI | P | NP. EtherCAT cycle 250 µs at the shortest | 5 notches | NC, likely at or above budget |
| Metronix smartServo BL 4104-C | BiSS-C. SSI NC | P | About 125 µs (current loop time × 4) | 4 band-stop filters | Not found |
| Parker PSD1SW1300 | BiSS-C (limited availability). No SSI | NC | P: 125 µs (Parker catalog) | Notch, anti-resonance | Not found |
| Metronix ARS 2105 FS, used | BiSS NC | P | NC: 200 µs by default | Speed filter only | About 135 euro used |
| AMC DPEANIU-015S400 | 1 Vpp and BiSS-C | P | P: 100 µs | One biquad | USD 1,508 new. Over budget |
| Rexroth IndraDrive Cs HCS01 | SSI, BiSS-C, EnDat 2.2 | P | F or NC: 250 µs from a forum and an older manual | NC | Not searched |

Left out:

- **Position loop 250 µs (4 kHz) in the maker's documents:** Copley Xenus Plus, Kollmorgen AKD
  and AKD2G, Schneider Lexium 32. Kinco FD5P also fails with 4 kHz.
- **No SSI or BiSS-C input:** Yaskawa Sigma-7 (its own serial protocol; it reads 1 Vpp only
  through the JZDP converter), Panasonic A6BL, Mitsubishi MR-J5, Sanyo Denki R 3E.
- **No third-party linear motor in the manual:** Inovance SV660N, HCFA X3E, and a long list of
  other Chinese drives.
- **Voltage too low:** Ingenia, Technosoft, Synapticon, Nanotec.
- **Wrong protocol:** Beckhoff AX5000 uses the Sercos profile over EtherCAT (SoE), not CiA402.

### Delta ASDA-A3 warning

The Delta A3 manual (January 2024 issue) says that BiSS-C and EnDat may not work on A3 drives made
in week 23 of 2022 or later, because of a chip shortage. Buy an older unit, or ask the seller or
Delta to confirm that BiSS-C works on that unit.

### KEBA ServoOne junior: what to check before buying

- **The bus.** Many used units have Sercos III (type code ending in 0082). We need EtherCAT, with a
  3 in the option position of the type code (for example SO22.006.0030).
- **The current.** The SO22.003 gives 3.0 A continuous and 6.0 A peak for 10 s. That is just
  above our 5.9 A. The SO22.006 gives 5.9 A continuous and 11.8 A peak, so it has margin.
- **Encoder approval.** The manual says that KEBA must approve an encoder that it does not sell.
  Ask KEBA whether a third-party 1 Vpp linear encoder is fine.
- **The loop rate.** The 8 kHz comes from the ServoOne family brochure. Ask KEBA to confirm it for
  the junior.
- **Support.** The earlier search found that the product may no longer be sold. Check that the
  setup software (DriveManager 5) and the EtherCAT description file are still available.

## Decisions Made

No purchase decision. The suggested order:

1. Ask KEBA the three questions above: the loop rate of the junior, approval of a third-party
   1 Vpp encoder, and whether the software and support are still available.
2. If KEBA answers yes, buy one used SO22.006 with EtherCAT and test it on one stage. No
   converter is needed.
3. As the fallback, ask Delta and Inovance for the position loop period. If one of them reaches
   8 kHz, the iC-NQC board plus that drive stays below 500 euro.

## Open Questions

- Does the ServoOne junior run its position loop at 125 µs, like the rest of the family?
- Does KEBA allow a third-party 1 Vpp linear encoder on port X7?
- What is the position loop period of the Delta ASDA-A3 and the Inovance SV680N?
- What do the Parker PSD1SW1300 and the Metronix BL 4104-C cost?
- Does the iC-NQC board give RS422 outputs, and at what cable length does SSI still work?

## Next Steps

1. Send the questions to KEBA, Delta and Inovance.
2. Look for a used ServoOne junior with EtherCAT, not Sercos.

<details>
<summary>Sources and remarks</summary>

Prices were seen on 29 September 2026. eBay prices come from search result text, because eBay
blocked page reads. They are asking prices.

Checked in this session in the maker's own documents:

- ServoOne junior operation manual, 02/2022, table 4.10 (encoder types on X7, KEBA approval
  note): <https://www.parkem.ch/fileadmin/user_upload/Website/6_Produkte/Servodrives/KEBA%20ServoOne/TEXT&CAD&CERT&MANU/Manual_KEBA_ServoONEjunior_en.pdf>
- LTi ServoOne family brochure, p. 16 (16 kHz current, 8 kHz speed and position, commutation
  finding for linear motors): <https://www.controlinmotion.com/bm~doc/lt_servoone-ds.pdf>

Converters and encoders:

- iC-NQC data sheet (distributor copy): <https://img.ozdisan.com/ETicaret_Dosya/507359_163230.pdf>
- iC-NQC evaluation board price: <https://us-shop.ichaus.com/ProductDetails.asp?ProductCode=iC-NQC+EVAL+NQC6D>
- iC-TW29 fact sheet: <https://www.ichaus.de/wp-content/uploads/TW29_factsheet_rev4.pdf>
- NiLAB NL-NQ6D: <https://en.nilab.at/products/nl-nq6d-sin-cos-interpolator/>
- Heidenhain EIB 192: <https://www.heidenhain.us/wp-content/uploads/2022/07/PI_EIB192_ID1106705_en.pdf>
- Heidenhain EIB 392: <https://www.heidenhain.us/wp-content/uploads/2022/07/PI_EIB392_ID545817_en.pdf>
- EIB 392 price: <https://www.e-motionsupply.com/product_p/eib-392.htm>
- RLS LA11 data sheet: <https://www.rls.si/eng/fileuploader/download/download/?d=0&id=126&title=Data+sheet%3A+LA11+absolute+magnetic+encoder+system+%28LA11D01%29>
- Renishaw RESOLUTE BiSS readhead, USD 982 (BiSS only, no SSI): <https://www.e-motionsupply.com/RESOLUTE_readhead_BiSS_Model_RL32BAT050B30A_p/rl32bat050b30a.htm>

Drives:

- ServoOne junior price, out of stock: <https://www.ntc-tech.com/products/lti-drives-so22-003-0030-0000-1-servo-one-junior-controller>
- ServoOne junior on eBay.de: <https://www.ebay.de/p/912765978>
- Delta A3 manual, January 2024: <https://deltaacdrives.com/Delta-ASDA-A3-Servo-Drive-User-Manual.pdf>
- Delta A3-E used price: <https://www.ebay.com/itm/145926524218>
- Inovance SV680: <https://www.inovance.com/global/content/details_815_557127.html>
- Inovance SV660N manual: <https://www.inovance.eu/fileadmin/downloads/Servo_drives_and_motors/SV660N_Advanced_User_Guide.pdf>
- HIWIN ED1 manual: <https://www.hiwin.de/medias/sys_master/hiwinDocumentMedia/hiwinDocumentMedia/h60/h54/14712629493790/ED1-01-4-EN-2403-MA.pdf?attachment=true>
- HIWIN E-series EtherCAT manual (250 µs cycle): <https://www.hiwin.de/medias/sys_master/hiwinDocumentMedia/hiwinDocumentMedia/h8b/h41/14712455004190/E-SERIES-SERVO-DRIVE-ETHERCAT-COE-COMMUNICATIONS-COMMAND-MANUAL-V1.3-EN-.pdf?attachment=true>
- Metronix BL 4000-C manual: <https://www.metronix.de/metronixweb/fileadmin/user_upload/Dokumente/Downloads/Handbuecher/P-HB_BL_4000-C_1P1_EN.pdf>
- Metronix ARS 2100 FS manual: <https://www.metronix.de/fileadmin/user_upload/Dokumente/Downloads-EN/Manuals/Servo%20Drive%20ARS%202000%20FS/P-HB_ARS2100_FS_5p0_EN.pdf>
- Used ARS 2105: <https://www.lagerwerk.com/en/electrics-mechanics/automation-devices/others/17066/metronix-ars-2105-servo-positioning-controller-w/o-ext.-fan>
- Parker PSD catalog: <https://dpbrowntech.com/files/Parker/Drives/PSD.pdf>
- AMC DPEANIU-015S400: <https://servo.a-m-c.com/hubfs/Datasheets/Servo-Drives/DigiFlex-Performance/AMC_Datasheet_DPEANIU-015S400.pdf>
- Copley Xenus Plus: <https://datasheet.datasheetarchive.com/originals/crawler/copleycontrols.com/cca4087b61878b31d8b405e0457256be.pdf>
- Kinco FD5P manual: <https://aiq-robotics.com/wp-content/uploads/2024/01/Kinco-FD5P-series-AC-servo-system-manual-EN-23125.pdf>
- Rexroth forum post on loop times: <https://community.boschrexroth.com/ctrlx-drive-5thklqt9/post/axis-control-parameter-indradrive-GHtiXeA83gRrHGP>

The drive and converter facts other than the ServoOne were read by research helpers from the
documents above. The Heidenhain, Renishaw shop, SIKO and Parker distributor pages blocked
downloads.

</details>
