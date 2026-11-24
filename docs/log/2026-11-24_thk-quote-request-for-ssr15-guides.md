# 2026-11-24 — Price request to THK for SSR15 guides

**Role(s):** engineering, purchasing

## Goal

Find the THK guide that can replace the HIWIN QEH15SAZAH+E2 block on the EGR15U418H rail without
a new carriage or base. Ask THK Belgium for a price in two accuracy classes.

## Work Done

- **The THK SSR15XV block on the SSR15 rail with M4 holes is the replacement.** It has the same
  mounting pattern as the HIWIN parts.

  | | HIWIN QEH15SA + EGR15U | THK SSR15XV + SSR15 rail (Y) |
  | --- | --- | --- |
  | Height, rail foot to block top | 24 mm | 24 mm |
  | Block width | 34 mm | 34 mm |
  | Block holes | 2 × M4, 26 mm apart | 2 × M4, 26 mm apart |
  | Rail side to block side | 9.5 mm | 9.5 mm |
  | Rail width, height, hole pitch | 15, 12.5, 60 mm | 15, 12.5, 60 mm |
  | Rail screw holes (through / counterbore / depth) | 4.5 / 7.5 / 5.3 mm | 4.5 / 7.5 / 5.3 mm |
  | Gap under the block | 4.0 mm | 4.5 mm |
  | Block length with long-term lubrication unit | 54.6 to 56.0 mm (E2 on one end) | 59.3 mm (QZSS) |
  | Load ratings, dynamic / static | 8.56 / 8.79 kN | 9.1 / 9.7 kN (downward load only) |
  | Highest preload for size 15 | ZA (medium) | C1 (light) |

- **The SSR15XV carries about half its downward rating upward and sideways.** THK Table 7 gives
  the factors for the SSR. The HIWIN QEH15SA has the same rating in all four directions.

  | Direction | Dynamic rating | Static rating |
  | --- | --- | --- |
  | Down (radial) | 9.1 kN | 9.7 kN |
  | Up (0.50 C, 0.50 C0) | 4.55 kN | 4.85 kN |
  | Sideways (0.53 C, 0.43 C0) | 4.82 kN | 4.17 kN |
  | HIWIN QEH15SA, all directions | 8.56 kN | 8.79 kN |

  Static moments for one block: 30.3 N·m pitch (MA), 18.9 N·m yaw (MB), 56.2 N·m roll (MC). For
  two blocks touching each other: 119 N·m pitch and 122 N·m yaw. The worst load on one block in
  our stage is about 530 N (log of 2026-10-13), so the weakest static rating (4.17 kN sideways)
  still gives a safety factor of about 8.
- **THK does not publish the stiffness of the SSR15XV.** The draft asks THK for the stiffness with
  preload C1 and for the C1 radial clearance. HIWIN gives about 115 N/µm for the QEH15SA.
- **THK has no lubrication unit that is sold for the whole life of the block.** The long-term unit
  is the QZ Lubricator. In a THK test with one greasing at the start, a block with grease and QZ
  ran 30,000 km at light load, 3,500 km at medium load and 962 km at heavy load. With grease only,
  it ran 465 km at heavy load. HIWIN gives up to 10,000 km for the E2 unit on size 15. The two
  tests are not the same, so the numbers do not compare directly.
- **The straightness per THK class, for a rail of 400 to 500 mm** (THK calls it "running
  parallelism"): Normal 9 µm, H 6 µm, P 4.5 µm, SP 2.5 µm, UP 1.5 µm. HIWIN class H allows 12 µm
  for the same length.
- **The SSR15XV has nine seal options. SS adds no length and is the closest to the HIWIN
  standard seal.** Block length L in mm, from THK pages A1-521, A1-532 and the QZ page:

  | Code | What it is | Without QZ | With QZ |
  | --- | --- | --- | --- |
  | UU | End seals | 40.3 | 59.3 |
  | SS | End seals and side seals | 40.3 | 59.3 |
  | ZZ | SS and a metal scraper | 44.9 | 62.7 |
  | DD | Double end seals and side seals | 47.3 | 65.1 |
  | KK | DD and a metal scraper | 50.7 | 68.5 |
  | SSHH | SS and a laminated contact scraper (LaCS) | 59.5 | 75.5 |
  | ZZHH | ZZ and LaCS | 60.7 | 76.7 |
  | DDHH | DD and LaCS | 65.3 | 81.3 |
  | KKHH | KK and LaCS | 66.5 | 82.5 |
  | GG / PP | Light-resistance contact seal (LiCS); PP adds side seals | 48.7 | not listed |

  Seal friction for one block, maximum, with lubricant: 2.0 N for the UU seals, 5.9 N extra for
  LaCS, and 1 N for LiCS.
- **We chose SS.** The blocks sit under the steel cover strip, so they see oil mist and very fine
  chips, not a flow of coolant. The side seals also close the underside of the block. Stronger
  seals add 4 to 23 mm of length and more friction, which is bad for a precise linear motor stage.
- **Niels Bosmans chose the Normal and H classes for the price request.**
- **A Gmail draft to info@thk.be asks for 2 rails and 4 blocks in each class.** It says that we
  look for a HIWIN replacement, gives our loads, and asks seven questions. The draft is not sent.

## Decisions Made

- Ask THK for a price in Normal and H. Ask for preload C1, the highest that THK offers on SSR15.

## Open Questions

- Can the QZ Lubricator go on one end of the block only? With QZ on both ends, the block is about
  3 to 5 mm longer than the HIWIN block with E2. The holes also sit at another place along the
  block.
- The SSR is a radial block. It carries less load upward and sideways than downward. The HIWIN QE
  block carries the same load in all four directions. Check the stage loads against THK Table 7.
- Light preload C1 is less stiff than HIWIN ZA.

## Next Steps

1. Niels Bosmans reviews and sends the draft.
2. When THK answers, compare price, delivery time and stiffness with the HIWIN offer from
   Vansichen BV.

<details>
<summary>Technical notes</summary>

- THK dimension table SSR-XV: <https://tech.thk.com/en/products/pdfs/en_a01_112.pdf>
- THK accuracy tables 15 and 16, pages A1-78 and A1-79:
  <https://tech.thk.com/en/products/pdf/en_a01_076.pdf>
- THK Table 7, load rating in each direction, page A1-61:
  <https://tech.thk.com/en/products/pdf/en_a01_060.pdf>
- THK QZ Lubricator lengths and life test: catalog pages en_a01_538, supplied by Niels Bosmans.
- HIWIN parts: `modules/stoq/modules/hiwin/modules/qeh-block/bom/parts.csv` and
  `modules/stoq/modules/hiwin/modules/egr-rail/bom/parts.csv`.
- Proposed THK codes: `SSR15XV2QZSSC1+418LY-II` and `SSR15XV2QZSSC1+418LYH-II`, 2 sets each.

</details>
