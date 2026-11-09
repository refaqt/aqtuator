# 2026-11-09 — We do not continue with DGSMARTWIN for now

- **Date:** 2026-11-09
- **Status:** Accepted

## Context

DGSMARTWIN (Dongguan Smartwin) offered two parts for the compact stage: the AKS-4D52AECAB servo
drive and the SA32 absolute linear encoder with EnDat 2.2. We asked questions from 14 October to
9 November 2026. The answers and the prices are in the
[log entry of 2026-11-09](../log/2026-11-09_dgsmartwin-answers-and-stop.md).

## Decision

We stop with DGSMARTWIN for now, for the drive and for the encoder. Niels Bosmans gave four
reasons:

1. The drive documentation is not clear, and most of it is in Chinese.
2. We still have no loop rate for the control loops. The answer "minimum communication cycle:
   1 ms" is not a loop rate.
3. The SA32 encoder (CNY 5,500 for a head and a scale) is much more expensive than the RSF MC 15.
4. The encoder documentation is too limited: no manual, no installation manual, no CAD model.

## Consequences

- The AKS drive is out of the list of drive candidates. It stays "not confirmed" on DRV-09 and
  DRV-P3.
- The RSF MC 15 stays the encoder of the compact stage. The SA32 is not added to the stoq library.
- In maqers the DGSMARTWIN supplier stays a "candidate". Its two offers are "on hold".
- We may look at DGSMARTWIN again later. Before that, we need: written loop rates in Hz, the
  tuning documents in English, and the SA32 data sheet, manual and CAD model.
