# 2026-11-25 — A price request listed a motor current we do not need, so the supplier offered a larger drive

## What happened

On 23 October 2026 we asked DynamicDrives (Kollmorgen) for a price for the AKD-x00306 and the
AKD2G-6V03S. The email listed three motor currents: 2.0 A rms continuous, 5.9 A rms for 1 s, and
9.8 A rms for 0.5 s. On 30 October DynamicDrives answered that both drives are "too small",
because they give only 9 A peak, and offered the 6 A models. Our hard requirements are only
2.0 A rms and 5.9 A rms for 1 s (DRV-01, DRV-02). The 3 A drives meet both with a margin of 50 %.
The answer was not checked against the requirements for almost four weeks, and the quotation
expired in that time.

The same email described the 1 Vpp encoder. That was right on 23 October, but the encoder
changed to BiSS-C four days later, and nobody told DynamicDrives.

## Why it went wrong

We copied the motor data sheet into the request. The data sheet gives the motor limit (9.8 A for
0.5 s) next to the values we design for. The email did not say which values are requirements and
which are only motor limits. A supplier then sizes the drive for the largest number.

Currents also come in two forms: rms values (Kollmorgen) and peak values (Copley "Adc"). A
reader who mixes them up gets a wrong size in either direction.

## Prevention rule

- In a price request, write the hard requirements as requirements, with their short names
  (DRV-01, DRV-02), and in rms. Put motor limits in a separate line that says "motor limit, not
  needed from the drive". Say that we will lock the drive peak current.
- When a supplier says a drive is too small or too large, check the claim against
  `motor-drive.sysml` the same week, before the quotation expires.
- Before you compare drive currents, convert them all to rms.
- Before you send a request, check the encoder in it against the stage model, as the
  [mistake of 2026-11-04](2026-11-04_drive-check-used-the-old-encoder.md) says.

## Related

- [Log: Kollmorgen said our drives are too small](../log/2026-11-25_kollmorgen-too-small-answer-and-drive-comparison.md)
- [Servo drive selection](../servo-drive-selection.md)
