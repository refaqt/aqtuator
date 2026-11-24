# 2026-11-24 — An old guide block was compared instead of the part in the design

## What happened

A search for a THK replacement started from the HIWIN HGL15CA block and the HGR15R rail. Those
parts are still marked active in the parts library, but the design moved to the QEH15SA block on
the EGR15U rail on 2026-10-13. The first answer to Niels Bosmans named the wrong THK block.

## Why it went wrong

The part number came from the first search hit in the parts library. Nobody checked which part
the current assembly uses, or read the newest log entries about the guides.

## Prevention rule

Before you compare or order a bought part, find the part that the current design uses. Read the
newest log entries for that part. A row marked active in the parts library is not proof that the
design still uses it.

## Related

- [Log 2026-10-13: other makers for the QEH15SA block](../log/2026-10-13_second-source-for-the-qe15-guide-blocks.md)
- [Log 2026-11-24: price request to THK](../log/2026-11-24_thk-quote-request-for-ssr15-guides.md)
