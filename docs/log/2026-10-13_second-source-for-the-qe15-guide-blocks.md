# 2026-10-13 — Other makers for the QEH15SA block and EGR15U rail

**Role(s):** engineering, purchasing

## Goal

Find guide blocks and rails from other makers that can replace the HIWIN QEH15SA block on the
EGR15U rail without a new carriage or base. The hole patterns, the width and the height must match,
or differ by a few millimetres at most.

## Work Done

- **Five short size-15 blocks fit the same mounting pattern.** All have:
  - a block 24 mm high and 34 mm wide;
  - top holes for M4 screws, 26 mm apart across the block, in one row;
  - a rail 15 mm wide, with holes every 60 mm.

  | Maker and part | Block length | Gap under block | Rail height | Rail screws | Fit |
  | --- | --- | --- | --- | --- | --- |
  | HIWIN QEH15SA + EGR15U (reference) | 40.1 mm (54.6 mm with E2) | 4.0 mm | 12.5 mm | M4 (4.5 / 7.5 / 5.3) | — |
  | THK SSR15XV + SSR15 rail | 40.3 mm | not found | 12.5 mm | M4 (4.5 / 7.5 / 5.3), standard | Best match |
  | PMI MSB15TS + MSB15 rail | 40 mm | 4.5 mm | 12.5 mm | M4 (4.5 / 7.5 / 5.3), standard | Very good |
  | NSK NS15CL + NS15 rail | 40.4 mm | about 4.6 mm | 12.5 mm | M3 standard; M4 hole on request | Good |
  | TBI TRS15VS + TR15 rail | not clear | 3.2 mm | 13 mm | M4 (4.5 / 7.5 / 6) | Good, small differences |
  | HIWIN EGH15SA (same rail) | 40.1 mm | 4.5 mm | 12.5 mm | M4 (EGR15U rail) | Same pattern, weaker block |

  The rail screw column gives the hole sizes in mm: through hole / counterbore / counterbore depth.
  On every listed block, the distance from the rail side to the block side is 9.5 mm.
- **THK SSR15XV is the closest match.** M4 is THK's standard rail for size 15, with the same holes
  as the EGR15U. Distributors list 9.1 kN dynamic and 9.7 kN static load. That is a little above
  the QEH15SA (8,560 N and 8,790 N).
- **PMI MSB15TS is also a close match.** PMI's European shop sells it under the HIWIN number
  "EGH15SA…", so PMI itself treats it as a swap for the HIWIN short block. One distributor table
  gives a lower dynamic load: 6.7 kN.
- **NSK NS15CL fits only with the M4 rail option.** The standard NS15 rail takes M3 screws.
- **TBI TRS15VS has small differences.** The rail is 0.5 mm taller, the counterbore is 0.7 mm
  deeper, and the gap under the block is 3.2 mm instead of 4.0 mm. The carriage must still clear
  the base.
- **Bosch Rexroth size 15 is not a direct swap.** The block is 24 × 34 mm, but the rail has a
  different shape.
- **Some things differ on every other maker:**
  - The block length and the end parts. The HIWIN E2 oil unit makes the block 54.6 mm long. Other
    makers use their own oil units, wipers and grease nipple positions.
  - The hole position along the block. On the QEH15SA with E2, the hole row is 6.55 mm off the
    centre of the whole block. On another maker's block, the block ends sit in another place.
  - The quiet ball chain. THK SSR also has caged balls. The PMI, NSK and TBI blocks are probably
    plain ball blocks. This is not checked.
  - Stiffness and preload. Each maker has its own preload classes. The life and stiffness
    estimates in [the QE15 load entry](2026-10-13_qe15-guide-blocks-load-and-life.md) do not carry
    over.

## Open Questions

- How large is the gap under the THK SSR15XV block?
- Does the PMI MSB15TS short block have 2 top holes? One table is not clear.
- Does NSK keep the NS15 rail with M4 holes in stock?

## Next Steps

1. Download the THK SSR15XV and PMI MSB15TS CAD files. Lay them over the HIWIN parts in FreeCAD
   and compare the hole position along the block and the length over the seals.
2. When the preload questions go to HIWIN, send the same questions to THK. Then there is a real
   second source.
3. Ask a THK and a PMI distributor for the factory dimension tables before anyone drills a part.

<details>
<summary>Technical notes</summary>

- HIWIN figures: catalogue GW-13-1-EN-2606-K, table 3.45 (blocks) and table 3.48 (EGR_U rail), in
  `modules/stoq/modules/hiwin/docs/datasheets/`.
- TBI figures: the TBI TRS15 datasheet from Anaheim Automation.
- THK, PMI and NSK figures come from distributor listings and catalogue snippets, not from the full
  factory tables. The THK and PMI catalogues could not be opened directly. Treat the load ratings
  as unverified.
- THK SSR15XV and SSR15XW have the same cross-section. The rail height (12.5 mm), the rail holes
  and the 9.5 mm side distance were read from the SSR15XW listing.
- Sources:
  - [THK SSR-XV product page](https://www.thk.com/jp/en/products/lm_guide/caged_ball/ssr/xv)
  - [Coolen Bearings, THK SSR15XW1UU](https://www.coolenbearings.com/thk/linear-motion-guides/ssr15xw1uu)
  - [MISUMI, THK SSR15XV1UU(GK)](https://uk.misumi-ec.com/vona2/detail/221000461725/?HissuCode=SSR15XV1UU(GK))
  - [RS Components, THK SSR15XV1SS(GK)](https://se.rs-online.com/web/p/linear-guide-blocks/7300054)
  - [THK store, SR15 rail](https://store-na.thk.com/Product/sr15-340ly-rail)
  - [Aluflex, PMI MSB-S/TS table](https://www.aluflex.com/productcategory/msb-linear-guide-with-low-installation-height/)
  - [PMI AMT, MSB15TS listed as EGH15SAZAH](https://pmi-amt.eu/shop/egh15sazah-msb15tsssf0h-111847)
  - [PMI AMT, MSB15 rail](https://pmi-amt.eu/shop/msb15-mm-profile-rail-122294)
  - [NSK NH/NS series catalogue](https://www.nsk.com/content/dam/nsk/am/en_us/documents/precision-americas/Linear-Guides-NH-NS-Series.pdf)
  - [NSK interchangeable series reference guide](https://www.nskautomation.com/nsk-literature/linear-guides/NSK-Linear-Guides-Interchangable-Products-Reference-Guide.pdf)
  - [TBI TRS15 datasheet](https://anaheimautomation.com/media/anaheim/files/manuals/linearcomponents/L011020_-_TBI-TRS15_Linear_Guide.pdf)
  - [Bosch Rexroth size 15 block](https://www.sp-spareparts.de/en/p/r166619323-bosch-rexroth)
- Mistake rule checked: [fatigue estimate without a data sheet](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md).
  No life was estimated for the other blocks, because their factory data is not confirmed.

</details>
