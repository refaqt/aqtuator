# 2026-10-19 — The encoder protocol follows the drive. BiSS-C is not required

- **Date:** 2026-10-19
- **Status:** Accepted

## Context

The encoder requirements of the compact stage allowed only two outputs: 1 Vpp sine and cosine, or
BiSS-C. So every absolute encoder with EnDat 2.2 failed, for example the Heidenhain LIC parts. But
many drives read EnDat 2.2, and some read other serial protocols too. The DGSMARTWIN AKS drive, for
example, reads EnDat 2.2. The old rule rejected good encoders for no real reason.

## Decision

For an absolute encoder, we do not limit ourselves to BiSS-C.

- EnDat 2.2 is allowed.
- Any other serial protocol is also allowed, if the drive reads it.
- The only rule for the encoder output is this: the chosen servo drive for the linear motor reads it
  directly, with no converter box, and reads the full position word.

The rule is in requirement ENC-04 in
[`modules/compact-stage/architecture/linear-encoder.sysml`](../../modules/compact-stage/architecture/linear-encoder.sysml),
and in the encoder input requirement DRV-08 in
[`modules/compact-stage/architecture/motor-drive.sysml`](../../modules/compact-stage/architecture/motor-drive.sysml).

## Consequences

- The choice of encoder and the choice of drive depend on each other. Until the drive is chosen,
  check each encoder against every drive that is still a candidate.
- Encoders that failed ENC-04 only because of EnDat 2.2 or another serial protocol must be judged
  again. This covers the Heidenhain LIC rows in the
  [encoder selection page](../linear-encoder-selection.md).
- Old logs stay as they are. They record the rule that was true at the time.
