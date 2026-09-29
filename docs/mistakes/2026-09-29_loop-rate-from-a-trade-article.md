# 2026-09-29 — Took a drive loop rate from a trade article, not the manual

## What happened

Two drive searches listed the Kollmorgen AKD2G as a drive with an 8 kHz position loop. The first
one put it in second place and advised asking Kollmorgen for a quote. The number came from a trade
article about the launch of the two-axis model, and from a search result. The Kollmorgen web site
blocked downloads, so nobody opened the manual.

The AKD2G installation manual, in the 2018 beta edition and in the June 2023 edition, gives a
position loop update period of 250 µs. That is 4 kHz, so the drive fails the 8 kHz requirement.
The error came out when the user asked for single axis prices and the manual was read.

## Why it went wrong

A number that decides whether a part passes or fails was taken from a secondary source. The entry
marked it as "from a trade article", but it still counted the drive as a pass in the short answer
and in the table. The mark was in the sources block, where a reader does not look.

This is the same kind of error as
[the fatigue estimate without a data sheet](2026-09-22_fatigue-estimate-without-a-datasheet.md):
a number that decides the answer was used before the primary document was opened.

## Prevention rule

When a single number decides whether a part passes a hard requirement, read it in the maker's
own data sheet or manual before you call the part a pass. If the primary document cannot be
opened, list the part as "not confirmed" in the short answer and in the table, not only in the
sources. Try a public copy of the manual (for example on ManualsLib) before you give up.

## Related

- [Drives from non-Israeli suppliers with an open control loop](../log/2026-09-29_non-israeli-drives-with-open-control-loops.md)
- [HIWIN, Delta and Kollmorgen follow-up](../log/2026-09-29_hiwin-delta-kollmorgen-follow-up.md)
