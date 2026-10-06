# 2026-10-06 — The linear encoder table has its own page

**Role(s):** engineering, purchasing

## Goal

The comparison table of linear encoders sat inside the log entry of 2 October. A log entry records
one day of work, so the table should not keep growing there. Move it to its own page, like the
servo drive overview.

## Work Done

- **The overview page is [Linear encoder selection](../linear-encoder-selection.md).** It holds the
  short answer, a copy of the requirements ENC-01 to ENC-11, the guide to reading the table, and the
  table itself.
- **The log entry of 2 October now links to the page.** It keeps its goal, decisions, open
  questions and list of sources.
- **No number changed.** The rows, the short list and the Heidenhain result are the same as before.
- **The page is a first version.** It is still work in progress.

## Decisions Made

None. The text only moved.

## Next Steps

1. Keep the page up to date when a data sheet or an answer from a maker arrives.
2. Decide whether the open questions and next steps of 2 October also belong on the page.

<details>
<summary>Technical notes</summary>

- Links inside the moved text now point from `docs/`, not from `docs/log/`.
- The requirements table on the page was copied from the log entry of 2 October on the encoder
  requirements. The SysML file stays the source.
- Mistake rule applied: [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md).
  No pass or fail was changed, and no number was read again.

</details>
