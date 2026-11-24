# 2026-11-24 — miControl servo drives checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

Check whether a servo drive from miControl fits the drive for the MAXWELL MK21 linear motor stage.
The requirements are in the [servo drive selection](../servo-drive-selection.md).

## Work Done

### Short answer

- **No miControl drive fits.** Every model has a power supply of 60 V DC at most. Our drive needs a
  DC bus of 320 V to 600 V (DRV-04). So all of them fail a hard requirement.
- miControl GmbH is a German company in Großbeeren. The supplier rule is not the problem.
- The drives are made for 24 V and 48 V machines with high current. They are now listed in the
  low voltage table of the drive overview.

### What was checked

The product list on the miControl website has two families: the older mcDSA and the newer mcDS.
One data sheet per group was read.

| Family | Model read | Supply | Current | Encoder input | EtherCAT | STO |
| --- | --- | --- | --- | --- | --- | --- |
| mcDSA-E2x XC | E27XC-EtherCAT | 9 to 60 V | 160 A peak, 54 A continuous at 24 V | 1 Vpp sin/cos, 13 bit per period | Yes, CiA 402 | Up to SIL 3 |
| mcDSA-E3x | E37-EtherCAT | 9 to 60 V | 80 A peak, 16 A continuous at 24 V or less | 1 Vpp sin/cos | Yes | Not in the data sheet |
| mcDSA-E4x | E47-EtherCAT | 9 to 60 V | 50 A peak, 8.5 A continuous at 48 V | 1 Vpp sin/cos | Yes | Not in the data sheet |
| mcDSA-E5x | E57-EtherCAT | 9 to 60 V | 50 A peak, 9 A continuous at 48 V | 1 Vpp sin/cos | Yes | Not in the data sheet |
| mcDSA-E6x | E65-Modul | 9 to 60 V | 15 A peak | Hall, incremental | CANopen only on this model | Not in the data sheet |
| mcDSA-B | B60 | 9 to 60 V | 15 A peak, 4.3 A continuous at 48 V | Hall only | No | No |
| mcDS | i5, h5, m5 (60 A) and i3 (25 A) | 10 to 60 V | 60 A or 25 A peak | SSI, BiSS-C | h5: yes | Not checked |

None of the data sheets gives a position loop rate (DRV-09) or a Bode plot tuning tool (DRV-10).
These were not followed up, because DRV-04 already fails.

## Decisions Made

- miControl drives are not candidates. They are listed with the other low voltage drives.

## Open Questions

None.

<details>
<summary>Sources</summary>

- [miControl servo controller list](https://www.micontrol.de/en/products/controller) and
  [mcDS list](https://www.micontrol.de/en/products/servocontroller). The site blocks simple
  downloads, so the pages were read in a browser.
- Data sheets:
  [mcDSA-E27XC-EtherCAT](https://www.micontrol.de/assets/datasheets/DataSheet_mcDSA-E27XC-EtherCAT-UL-STO_en.pdf),
  [mcDSA-E37-EtherCAT](https://www.micontrol.de/assets/datasheets/DataSheet_mcDSA-E37-EtherCAT-UL_en.pdf),
  [mcDSA-E47-EtherCAT](https://www.micontrol.de/assets/datasheets/DataSheet_mcDSA-E47-EtherCAT_en.pdf),
  [mcDSA-E57-EtherCAT](https://www.micontrol.de/assets/datasheets/DataSheet_mcDSA-E57-EtherCAT_en.pdf),
  [mcDSA-E65-Modul](https://www.micontrol.de/assets/datasheets/DataSheet_mcDSA-E65-Modul-UL_en.pdf),
  [mcDSA-B60](https://www.micontrol.de/assets/datasheets/DataSheet_mcDSA-B60_en.pdf),
  [mcDS-i5-60](https://www.micontrol.de/assets/datasheets/DataSheet_mcDS-i5-60cXX-E_en.pdf),
  [mcDS-h5-60-CT](https://www.micontrol.de/assets/datasheets/DataSheet_mcDS-h5-60cxx-E-CT_en.pdf),
  [mcDS-m5-60](https://www.micontrol.de/assets/datasheets/DataSheet_mcDS-m5-60cXX-E_en.pdf),
  [mcDS-i3-25](https://www.micontrol.de/assets/datasheets/DataSheet_mcDS-i3-25cXX_en.pdf)

</details>
