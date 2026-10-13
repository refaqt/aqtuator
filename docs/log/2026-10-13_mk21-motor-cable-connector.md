# 2026-10-13 — Round connector for the MK21 motor cable

**Role(s):** engineering, purchasing

## Goal

Find the smallest round connector that fits the cable of the MAXWELL MK21 linear motor. Assume
the cable carries the 3 phases, a Hall sensor and a temperature sensor.

## Work Done

### Short answer

- **The smallest single connector that carries everything is an M17 hybrid connector.** M17 means
  a 17 mm thread. The part is the Phoenix Contact M17 PRO HYBRID, 630 V version. It has 3 power
  contacts, 1 earth contact (PE) and 4 + 4 signal contacts.
- **Its cable clamp is too large for the motor cable.** It takes 8.5 to 12.3 mm. The MK21 cable
  is 6.8 ± 1 mm. The cable needs to be made thicker at the clamp, for example with heat-shrink
  tube, or joined to a thicker cable first.
- **Two smaller connectors may be the better choice.** The MK21 data sheet lists no Hall sensor.
  If the Hall sensor has its own cable, an M15 connector fits the motor cable directly. A small
  M8 or M12 signal connector can take the Hall sensor.

### The motor cable

All values are from the
[MAXWELL MK2 data sheet](../../modules/stoq/modules/maxwell/docs/datasheets/maxwell-mk2-iron-core-linear-motor.pdf),
pages 010 and 011.

- One round cable, Ø6.8 ± 1 mm, so 5.8 to 7.8 mm.
- Smallest bend radius: 69 mm.
- Temperature sensor: "3 PTC SNM120 in series". This is a heat switch that needs 2 wires.
- Highest operating voltage: 600 V DC. Current: 2.0 A continuous, 5.9 A peak, 9.8 A for 0.5 s.

### Contacts needed

| Function | Wires |
| --- | --- |
| Phases U, V, W | 3 |
| Earth (PE) | 1 |
| Digital Hall sensor: +5 V, 0 V, A, B, C | 5 |
| Temperature sensor (PTC) | 2 |
| **Total** | **4 power, 7 signal** |

The power contacts must be rated for at least 600 V.

### Connectors checked

| Connector | Layout | Power voltage | Cable range | Result |
| --- | --- | --- | --- | --- |
| TE Intercontec M12, 8 pin | 3+PE+4 | 630 V | 8.0–9.9 mm | Too few signal contacts |
| TE Intercontec M12, 10 pin | 3+PE+6 | 300 V | 8.0–9.9 mm | Power rating too low. A drive on 230 V mains has about 325 V DC inside. |
| TE Intercontec M15 (ytec and itec) | 3+PE+5 | 630 V | 6.5–8.5 mm | Too few signal contacts. Fits the cable well. |
| TE Intercontec M17 | 3+PE+5 | 630 V | 6.0–9.5 mm | Too few signal contacts |
| Phoenix Contact M17 PRO HYBRID | 3+PE+4+4 | 630 V | 8.5–12.3 mm | Fits. The motor cable is too thin for the clamp. |

The TE values come from the TE Intercontec quick reference guide. The Phoenix Contact website
blocked automatic access (error 403). The Phoenix values come from search results that quote
their pages. Check the exact part number and pin layout on the Phoenix Contact product page
before you order.

## Open Questions

- Does the MK21 have a Hall sensor? If it does, is it in the motor cable or in its own cable?
- Does the drive accept the PTC and the Hall sensor on the same signal cable?
- The PTC wires sit inside the motor coil, which runs at up to 600 V. Can they share wires or 0 V
  with the Hall sensor? Ask the drive maker or Maxwell before you do this.

## Next Steps

1. Ask Maxwell how the Hall sensor is wired.
2. If the Hall sensor has its own cable, use an M15 connector (3+PE+5) for the phases and the
   PTC, and a small M8 or M12 connector for the Hall sensor.
3. If one connector is needed, use the Phoenix Contact M17 PRO HYBRID. Plan how to make the motor
   cable thicker at the clamp.
4. Use the 69 mm bend radius and the connector size when you draw the cable slot in the bottom
   carriage. See
   [the cable path idea](2026-10-12_motor-cable-path-in-the-bottom-carriage.md).

<details>
<summary>Technical notes</summary>

- TE Intercontec part series: 912 (M12), 915 (M15, ytec and itec), 917 (M17), 617 (M17 signal).
  Ratings and cable codes from the
  [TTI / TE Intercontec quick reference guide](https://www.ttieurope.com/content/dam/tti-europe/resources/Literature/SupplierGuides/Quick-Reference-Guide.pdf).
  - M12, 8 pin: 8 A (3+PE) / 1 A (4x), 630 V / 48 V. 10 pin: 300 V power, 32 V (4x), 50 V (2x).
    Cable code 08: 8.0–8.9 mm, 09: 8.7–9.9 mm.
  - M15, 9 pin (3+PE+5): 14 A / 3.6 A, 630 V / 63 V. Cable code 31: 4.5–6.5 mm, 32: 6.5–8.5 mm.
  - M17, 9 pin (3+PE+5): 14 A, 630 V power, 63 V signal. Cable code 87: 3.5–6.0 mm,
    85: 6.0–9.5 mm.
- [TE Intercontec M12 motor connector](https://www.te.com/en/products/connectors/intersection/intercontec-m12-motor-connector.html).
- [Phoenix Contact M17 PRO hybrid connectors](https://www.phoenixcontact.com/en-gb/m17-pro-hybrid-connectors):
  630 V version, 4+4+3+PE, 14 to 16 A, power wire 0.06 to 1.5 mm².
- [Phoenix Contact M17-7EPSA8A8004S, item 1550175](https://www.phoenixcontact.com/en-lt/products/cable-connector-m17-7epsa8a8004s-1550175):
  cable 8.5–12.3 mm. Its pin layout was not confirmed.
- [Phoenix Contact M17 to M58 overview 2024](https://www.mouser.com/pdfDocs/52004434_EN_M17-M58_LoRes.pdf).
- binder M12 hybrid was ruled out: 63 V power rating.
- No CAD or parts list was changed.
- Mistake rules checked: the PowerShell rules (all shell work ran in bash), and
  [fatigue estimate without a datasheet](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md)
  (all motor values come from the data sheet).

</details>
