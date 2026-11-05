# 2026-11-04 — A drive check used the old encoder, because the drive requirements were not updated

## What happened

On 2026-11-04 the Agito Akribis AGD155-EC was checked against the drive requirements, and a price
request email was drafted. Both said the stage encoder gives 1 Vpp sine and cosine signals up to
150 kHz. That is wrong. Since 2026-10-27 the compact stage uses the RSF AK MC 15 B read head, with a
BiSS C output. The user noticed it, and the log entry and the email were corrected the same day.

## Why it went wrong

When the encoder changed on 2026-10-27, three places were updated: the CAD, the stage architecture
(`compact-stage.sysml`) and the bill of materials. Two places were not:

- the stage description in the drive requirements (`currentStage` in `motor-drive.sysml`), which
  still said 1 Vpp and a 20 µm pitch, and
- the requirements table on the drive selection page, which copies that file.

The drive requirements file calls itself the source, so the check trusted it. It did not compare it
with the read head in the stage architecture or the bill of materials. The requirements file and
the stage model each describe the encoder on their own, so nothing warns when they disagree.

## Prevention rule

- When you change a bought part of a stage, search the whole repository for the old part and its
  key values (for example `1 Vpp`, `20 µm`, `150 kHz`), and update every requirement that uses
  them in the same change.
- Before you check a drive against the drive requirements, compare `currentStage` in
  `motor-drive.sysml` with the `ReadHead` in `compact-stage.sysml` and with the bill of materials.
  If they disagree, fix the requirements first, then check the drive.

## Related

- [Agito Akribis AGD155-EC check and price request](../log/2026-11-04_agito-akribis-agd155-ec-price-request.md)
- [The RSF MC 15 encoder replaces the LAMOTION encoder](../log/2026-10-27_rsf-encoder-in-the-compact-stage.md)
- [Servo drive selection](../servo-drive-selection.md): most rows were checked against the old
  1 Vpp encoder and must be checked again for BiSS C.
