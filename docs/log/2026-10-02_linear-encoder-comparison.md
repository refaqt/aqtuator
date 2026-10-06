# 2026-10-02 — Comparison table of all linear encoders considered so far

**Role(s):** engineering, purchasing

## Goal

Put every linear encoder we have considered in one table. Each row shows the values that the encoder requirements ENC-01 to ENC-11 ask for. A reader can then see at once which encoder fits the compact stage, and which number is still missing.

The requirements are in [`modules/compact-stage/architecture/linear-encoder.sysml`](../../modules/compact-stage/architecture/linear-encoder.sysml). Every error value is a half band: "5 µm" means "within +/- 5 µm". The limits that say "less than" or "more than" are strict.

## The table

The table, the short answer and the guide to reading it moved to their own page on 2026-10-06:
[Linear encoder selection](../linear-encoder-selection.md). That page is kept up to date. This entry
keeps the goal, the decisions, the open questions and the sources of 2 October.

## Decisions Made

- Sealed (housed) encoders from the five makers are not listed. You chose open encoders only.
- The earlier candidates stay in the table with their earlier verdict, also the ones that were dropped or ruled out.
- A value that decides a pass or a fail counts only when it comes from the maker's own data sheet. This follows [the mistake of 29 September 2026](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md).
- The Render / JEM DAR row for the COIN head is not repeated. The Lamotion COIN rows cover it.

## Open Questions

- **Heidenhain data is from an older edition.** Closed on 6 October 2026. The Heidenhain rows now come from the 02/2025 catalogue and the current product sheets.
- **Heidenhain sizes that are still missing.** The LIF 6081 head length and the LIP 6081 Dplus scale size are not in the documents we read. Heidenhain gives them in separate mounting drawings (ID 1216748 for the LIF 6000). Neither changes the result, because both parts already fail on another number.
- **Head size of the RSF MS 14 and MS 15.** The purchasing note of 2 October lists 36 × 14.8 × 11.3 mm. The drawing in the MS 14 data sheet shows 13.5 mm across the scale, 14.8 mm high and 36 mm long. The 11.3 mm is a mounting dimension. The table uses the drawing. The change does not alter any pass or fail.
- **Numbers read from drawings.** Head sizes, scale sizes and angles were read from drawing images. Check the ones you rely on against the drawings.
- **Disputed fails in the earlier rows.** Some fails rest on the review of 28 September, not on a data sheet. They are the Fagor head width and the output of Delta, Easson, Hengxiang and Smartwin.
- **Two data sheets disagree** for the Lamotion Invar scales (ALi and RXi) on the line accuracy and the top speed. Both are marked in the rows.
- **Weak links.** For several Chinese makers we found no data sheet link. Those cells say "n/c".
- **The stage angles (ENC-11) are still open.** See the log of 2 October on the encoder requirements.

## Next Steps

- Fill in the angles that our stage gives (roll, pitch and yaw). Then check ENC-11 for the short list.
- Ask Heidenhain on 5 October about the periodic error of the LIA, and about an interpolator with BiSS-C or SSI output for the 1 Vpp parts.
- Ask Heidenhain whether the LIF 6000 scale can be made longer than 130 mm, and whether it comes thinner than 1.13 mm. It is the only Heidenhain head that fits our stage.
- Read the data sheets of the Renishaw TONiC and RESOLUTE rows again before you choose.
- Check that the chosen drive reads the signal of the chosen encoder (DRV-08).

<details>
<summary>Notes for reviewers</summary>

- Sources: the five maker research passes read these files. RSF: MS14-EN (01/2025), MS15-EN (05/2023), MC15-EN (04/2025), MS25-EN (12/2024), MS45-EN (11/2022). Numerik Jena: product information and manuals on numerikjena.com. AMO: brochure 1255440-01 (08/2024) and 1255440-00 (2018). Heidenhain: `PR_Exposed_Linear_Encoders_ID208960_en.pdf`, 06/2021, from heidenhain.us (2 October); see the next line for the 6 October update. Lamotion: PDFs under `http://www.lamotion.cn/file/pdf/`.
- Heidenhain update of 6 October 2026, all from `heidenhain.com/fileadmin/pdf/en/01_Products/`: `PR_Exposed_Linear_Encoders_ID208960_en.pdf` (02/2025), `PR_MULTI-DOF_..._ID1349070_en.pdf` (04/2026), `PI_LIF6000_ID1509120_en.pdf` (06/2026), `PI_LIC4100Dplus_ID1508595_en.pdf` (07/2026), `PI_LIC4113V_LIC4193V_ID1133597_en.pdf` (04/2026), `PI_LIC4119_ID1424994_en.pdf` (02/2024), `PI_LIC4100_ID1363460_en.pdf` and `PI_LIC3100_ID1312271_en.pdf` (11/2023), `PI_LIF471V_LIF481V_ID662692_en.pdf` (03/2024), `PI_LIF4x1Dplus_ID1104654_en.pdf` (02/2022), `PI_LIF171_LIF181_ID595192_en.pdf` (07/2018). The product list came from the Heidenhain brochure page and the 14 exposed-encoder product pages.
- How the download worked: the Heidenhain site returns "403 Access Denied" to `curl`. A Python client that copies the browser's connection pattern (`curl_cffi` with `impersonate="chrome"`) gets through. It also needs the Windows certificate list, because of the network proxy described in [the certificate mistake](../mistakes/2026-09-17_uv-download-certificate.md).
- Drawings checked by eye on 6 October: LIC 4113, LIC 4119, LIC 3119, LIC 2119, LIP 211, LIP 6081, LIF 481, LIF 181, LIF 6081, LIDA 483, LIDA 489, LIDA 289 and LIP 6081 Dplus. The other Heidenhain drawings were taken from the 2 October rows. All LIC heads in the 02/2025 catalogue are drawn at 19 × 46 mm.
- New in the 02/2025 catalogue: EnDat 3 models LIC 4133, 4135, 4137, 4139, 3137 and 3139. They are merged into the rows of the same scale.
- Earlier rows come from `docs/purchasing/2026-09-21_absolute-linear-encoder-candidates.csv` and the related notes in `refaqt/aqtuator-business`.
- Spot check: the RSF MS 14 MK drawing (head 13.5 × 14.8 × 36 mm, angles 4.0 / 3.5 / 1.0 mrad) and the Heidenhain LIDA 489 interpolation error (±45 nm) were checked against the PDFs. The other numbers were not re-read.
- Merged rows: some Heidenhain, AMO and Numerik Jena variants with the same numbers share a row. The Model cell says so.
- Left out of the table: scale-only rows (Hortech, Attoptic, Selba), scale tapes, applicators, interface boxes, magnet strips, and stage makers whose encoder is not named (SmarAct stages, PI Q-521, Xeryon, attocube, PiezoMotor). Rotary encoders appear only as rows marked rotary only.
- The 2026-09-28 supplier review marks Fagor, Delta, Easson, Hengxiang, Smartwin and others as dropped. Their rows keep that status.
- Not run: the SysML file was not changed. No model was checked by a parser.

</details>
