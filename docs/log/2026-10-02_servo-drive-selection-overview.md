# 2026-10-02 — One overview of all servo drives we considered

**Role(s):** engineering, purchasing

## Goal

The drive search is spread over ten log entries and two decision records. Put every drive we looked
at into one table, next to the requirements, so a reader can see why each one was chosen or left out.

## Work Done

### Short answer

- **The overview page is [Servo drive selection](../servo-drive-selection.md).** It lists brand,
  model, a link to the data sheet, the specifications against DRV-01 to DRV-09, the price, and notes.
- **The chosen drive and the fallback have not changed.** Servotronix CDHD2S-0032AEC2 is chosen.
  Delta ASD-A3-0421-E with its converter box is the fallback.
- **Two gaps showed up while reading the logs.** No entry settles the bus voltage of the CDHD2S
  against DRV-04 (about 325 V at 230 VAC, or 311 V at 220 VAC, against a limit of 320 V). And the
  drives with a 4 kHz position loop were left out when the limit was 8 kHz. The limit is now 4 kHz,
  and nobody looked at them again.

## Decisions Made

None. The page only collects what the logs already say. No number was researched again.

## Open Questions

- Does the CDHD2S meet DRV-04 on the mains voltage we will use?
- Do the 4 kHz drives (Kollmorgen AKD, Copley Xenus Plus, Rexroth IndraDrive Cs, Schneider Lexium 32,
  Kinco FD5P) pass the other requirements?

## Next Steps

1. Keep the page up to date when a quote or an answer from a maker arrives.
2. Check the open questions above.

<details>
<summary>Technical notes</summary>

- Cells marked "Not in logs" were not checked in any entry. They are not failures.
- Datasheet links were copied from the Sources blocks of the entries. They were not opened again.
- Mistake rule applied: [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md).
  A number that decides pass or fail is marked NC unless the maker's own document gives it.

</details>
