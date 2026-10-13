# 2026-10-13 — Load and life of the HIWIN QE15 guide blocks

**Role(s):** engineering, purchasing

## Goal

The compact stage is switching from HIWIN HGL15CA blocks on HGR15 rails to HIWIN
QEH15SAZAP+E2 blocks on matching rails. Check that the new blocks carry the load: the
milling forces and the pull of the linear motor magnet. Then estimate how many years they
last.

## Work Done

- **The new blocks carry the load with a large margin.** In the worst case, with all peak
  loads at once, one block carries about 530 N. The static load rating is 8,790 N. That is a
  safety factor of about 17. The catalogue asks for 3 to 5 when there is vibration.
- **The motor magnet sets the life.** The MK21 mover pulls toward the stator with 963 N, all
  the time. That is about 241 N on each of the four blocks, pressing down. The average load on
  one block is about 303 N.
- **At the planned use, the fatigue life is far longer than the life of the machine.** Niels
  gave the use: 3 m/min, 8 hours a day, 220 days a year. That is 317 km of travel a year.

  | Case | Load factor | Life in years |
  | --- | --- | --- |
  | Smooth running at this low speed | 1.2 | 265 – 695 |
  | Milling vibration counted | 2.0 | 57 – 150 |
  | Strokes under about 110 mm | 2.4 | 33 – 87 |
  | Short strokes and milling vibration together | 4.0 | about 7 at the worst |

  The load factor is the catalogue's allowance for vibration and speed. Each range covers the
  unknown preload of the blocks (see Open Questions).
- **The E2 oil unit is likely the first limit.** For QE15S the catalogue gives 20,000 km with
  one unit, about 63 years at our travel. That is twice the 10,000 km of the HG15 unit. The
  catalogue gives this only as a distance, not as a time.
- **The oil is SHC 636.** The catalogue sells it as "oil for filling long-term lubrication
  unit tank" (article 20-000350, 1 litre). This suggests the tank can be refilled.
- **The switch has costs:**
  - The new blocks are about 4 times less stiff: 115 N/µm per block, against 483 N/µm for
    the HG15C blocks with high preload (ZB).
  - At the same load, the new blocks last about 5 times less long than the old ones. The
    load ratings fall from 14,700 N to 8,560 N (dynamic) and from 23,470 N to 8,790 N
    (static).
- **The rails, the screws and the carriage must change:**
  - QE blocks run on EGR15 rails, which are 12.5 mm high instead of 15 mm. The block height
    stays 24 mm.
  - The standard EGR15R rail takes M3 screws, but the base is drilled for M4. The EGR15U
    rail takes M4 × 16 screws.
  - The QEH15SA block has 2 screw holes on top instead of 4, so the carriage hole pattern
    changes.
  - With one E2 unit, the block is 54.6 mm long instead of 75.4 mm.
- **QE blocks only come with the standard seal.** The stronger seals (ZZ, DD, KK) are not
  sold for QE. That puts more weight on the sealing strip.
- **Some coolant will likely pass the sealing strip.** It would get through as a fine mist
  and very fine chips, not as large chips. The coolant is SAMNOS AL, water based, applied as
  minimum quantity lubrication (a fine spray). The weak points:
  - The two ends of the carriage, where the rollers lift the strip and chips on the strip
    can ride in.
  - The strip edges, where a film of coolant can creep under.

  Water is a bigger risk than chips. It washes the oil off, and the standard rail is not
  stainless steel. This was judged from the design records. The CAD was not opened.

## Decisions Made

1. **Niels chose EGR15U rails, if the switch to QE goes ahead.** They take the M4 screws the
   base is already drilled for.
2. **The questions below wait until the design is worked out in more detail.** Ask HIWIN
   only then, so the load case in the request matches the real stage.

## Open Questions

Ask these once the design is more detailed.

**For our own design**

- How much of the work is short strokes, under about 110 mm? This is the only use that can
  bring the life down toward 10 years. The oil also reaches only a short part of the rail.
  HIWIN sell a grease for this case (G06).
- Does the carriage need a wiper or a brush at both ends, where the strip lifts?
- Does the base need a drain hole at its lowest point?
- Do the rails need a coating? The order code offers CTS, CZS and CCB.
- Is the stiffness of QE15S enough for chatter control? QEH15CA, the longer block, gives
  187 N/µm and a dynamic rating of 12,530 N.

**For HIWIN, about the preload**

The preload is the force the blocks are built with, so they have no play. For QE15S it is
larger than the magnet load on one block, so it controls the life.

1. What is the exact preload of QEH15SA with ZA, in newtons? The catalogue only gives 3 to
   5 % of the dynamic rating: 257 to 428 N.
2. Does this preload hold when blocks and EGR15U rails are ordered separately and mixed, not
   as matched sets? How much can it vary?
3. How does HIWIN count the preload in a life calculation? Please run your calculation with
   our load case:
   - four blocks;
   - 963 N steady magnet pull, pressing down;
   - 500 N peak drive force and 500 N sideways load;
   - 3 m/min, 317 km a year.
4. Is the light preload (Z0) better for us? The magnet already presses the blocks down. With
   Z0 the life is about 3 to 4 times longer, but the stiffness per block falls from 115 to
   96 N/µm. What are the stiffness figures up, down and sideways under the magnet load?
5. How much friction do four blocks give with the magnet load and the E2 units?

**For HIWIN, about the oil and the E2 unit**

1. Does the E2 unit on QE15S come filled with SHC 636 from the factory? Is it Mobil SHC 636?
   That is our guess, not a catalogue fact.
2. Can the tank be refilled? How, with how much oil, and through which opening?
3. How long does the oil last in years, not in kilometres? How long may the machine stand
   still?
4. Under which speed, stroke and load is the 20,000 km valid? Does the unit oil the whole
   rail at 3 m/min and with short strokes?
5. Do the blocks also need grease at assembly? If yes, which grease mixes safely with SHC
   636? (Still open from [the lubrication entry](2026-10-12_lubrication-of-the-guide-blocks.md).)
6. What happens when water-based coolant reaches the oil or the felt of the unit?
7. Where does the grease nipple go when an E2 unit is fitted, and on which end does the unit
   go?

## Next Steps

1. Work out the carriage and the base in more detail for the QE blocks and EGR15U rails: the
   rail height, the 2-hole block pattern and the shorter blocks.
2. Then send the questions above to a HIWIN application engineer.
3. Update the parts library with the QE block and the EGR15U rail when the switch is final.

<details>
<summary>Technical notes</summary>

- Source: HIWIN catalogue GW-13-1-EN-2606-K, in
  `modules/stoq/modules/hiwin/docs/datasheets/`:
  - life formula F 2.4 and load factor table 2.2;
  - block loads, tables 2.3 and 2.4;
  - QE order code, page 71 (footnote 4: no ZZ, DD or KK seals for QE);
  - preload table 3.42, load ratings table 3.43, stiffness table 3.44;
  - block sizes table 3.45, rails EGR15R and EGR15U, E2 unit table 3.52;
  - oil table 4.4.
- MK21 attraction 963 N: `modules/stoq/modules/maxwell/modules/mk2-mover/bom/parts.csv`.
- Load case, confirmed by Niels:
  - rails 128 mm apart, blocks about 107 mm apart (from the CAD of 2026-10-09);
  - 5 kg moving mass;
  - STG-11 500 N peak drive force with a 30 mm lever;
  - STG-13 500 N sideways load with a 40 mm lever;
  - cutting force 50 N mean, 50 N swing, 60 mm lever (defaults of the cutting force case).
- Sine-varying parts were averaged with Pm = 0.65 × Pmax (table 2.5).
- Equivalent load per block: radial plus sideways, about 303 N.
- Preload effect: Peff = (1 + F / (2.8 × Fpr))^1.5 × Fpr. This is Bosch Rexroth's method,
  because HIWIN publishes none. It gives 435 N at 3 % preload and 600 N at 5 % preload.
- Life L = (Cdyn / (fw × P))³ × 50 km, with Cdyn = 8,560 N.
  - fw 2.4 is 1.2 doubled for short strokes, as the catalogue asks for strokes under two
    block lengths.
  - The worst case is fw 4.0 at 5 % preload: about 2,300 km.
- Old block for comparison: HGL15CA, Cdyn 14,700 N, C0 23,470 N. HG15C stiffness with ZB
  preload is 483 N/µm. "ZBC" in the old part number was read as ZB preload and class C.
- Coolant facts: [strip seal decision](../decisions/2026-09-22_strip-seal-material-and-roller-size.md).
- Mistake rule checked: [fatigue estimate without a data sheet](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md).
  - Every rating comes from the catalogue.
  - The load case was stated and confirmed before the life was given.
  - The preload method and the oil brand are marked as estimates.

</details>
