# 2026-11-04 — The Akribis CASD drive looks like a Servotronix CDHD, and the two Akribis companies

**Role(s):** engineering, purchasing

## Goal

The user found the CASD series on the Akribis Systems web site. It looks the same as the
Servotronix drives. Find out which one is the original. Write down the official names of the
Akribis companies, so the logs and the drive list keep them apart.

## Work Done

### Short answer

- **Servotronix is almost certainly the original.** The CASD photo on the Akribis page shows the
  housing and connector layout of the Servotronix CDHD (connectors C1 to C4 and P1 to P5), with an
  Akribis label. Servotronix has sold the CDHD under its own name since at least 2012, and lists it at
  the EtherCAT Technology Group as "Servotronix Motion Control Ltd.". Akribis publishes no data
  sheet and no manual for the CASD. The page says: "For detailed specifications, please contact an
  Akribis sales engineer".
- **This is not confirmed in writing.** No document from Akribis or Servotronix says that the CASD
  is a CDHD. Only Akribis or Servotronix can confirm it.
- **The CASD stays out either way.** If it is a CDHD, it is a Servotronix design, and Servotronix is
  an Israeli company (rejected on 2026-10-06). This is the same pattern as Dynamikwell and the
  Googol GSHD, which also copy or license the CDHD.

### The companies and their official names

| Official name | Where | What it is | Source |
| --- | --- | --- | --- |
| Akribis Systems Pte Ltd | 56 Serangoon North Ave 4, Singapore | The parent company. It makes linear motors and stages, and sells drives: the Agito AGD and AGM drives, the CASD and SASD series, and Trust Automation drives | AGD155 manual page 2; Akribis web site |
| Agito Akribis Systems Ltd. | Kfar Saba, Israel | The research centre that designs the AGD and AGM drives. It "has full rights to distribute" them worldwide | AGD155 manual page 2; Agito catalogue, back cover |
| Servotronix Motion Control Ltd. (now STXI Motion) | Petah Tikva, Israel | Maker of the CDHD and CDHD2 drives. Midea Group (China) took control of it in 2017 | EtherCAT Technology Group product list; news reports |

The Akribis web site lists "Kfar Saba, Israel" as a site since 2018. The Agito drive manuals say
"designed by Agito Akribis Systems Ltd. in Israel. Sales of the products are licensed to Akribis
Systems Pte Ltd. under intercompany license agreement."

We found no link in ownership between Akribis and Servotronix.

### What changed in the drive list

The [servo drive selection page](../servo-drive-selection.md) had one row for "Agito Akribis,
Googol GSHD". It now has three rows: Agito Akribis Systems Ltd. (Israel), Akribis Systems Pte Ltd
(Singapore) with the CASD series, and Googol.

## Decisions Made

- The CASD series is left out, because it looks like a Servotronix design.

## Open Questions

- **Your decision:** does the rule "we do not buy from Israeli suppliers" also cover Akribis
  Systems Pte Ltd in Singapore? It is not Israeli, but it owns an Israeli research centre, and most
  of the drives it sells are designed in Israel. Today the rule names only "Agito Akribis".
- If needed: ask Akribis in writing who designs and makes the CASD.

## Next Steps

- Settle the open question above, and write the answer in the
  [decision record](../decisions/2026-10-06_kollmorgen-akd-and-copley-xenus-plus-as-candidates.md)
  or in a new one.

<details>
<summary>Sources</summary>

- Akribis CASD page, read on 2026-11-04: <https://www.akribis-sys.com/casd-series.html>. Features
  listed: AC/DC power supply; pulse, velocity or current mode; EtherCAT. Product photo:
  <https://akribis-sys.oss-cn-shanghai.aliyuncs.com/uploads/upload/images/20250902/457da3c0039ec7b0049a74e8eddbadc9.png>.
- Akribis user manual downloads (<https://www.akribis-sys.com/user-manuals.html>): only the AR4
  and AR6 series. No CASD manual.
- Akribis company page: <https://www.akribis-sys.com/discover-akribis.html>. Singapore address;
  "Kfar Saba, Israel" in the global footprint, 2018 in the timeline.
- AGD155 product manual Rev.3.4, page 2, "Products Rights":
  <https://agito-akribis.com/wp-content/uploads/2026/10/Agito-AGD155-Product-Manual-Rev.3.4.pdf>.
- Agito catalogue 26.5.2, back cover: "R&D Center, Agito Akribis Systems Ltd., P.O.Box 7172,
  Kfar-Saba 4464103, Israel":
  <https://agito-akribis.com/wp-content/uploads/2026/04/Agito-Motion-Controls-and-DrivesEN-26.5.2-1.pdf>.
- Servotronix CDHD at the EtherCAT Technology Group:
  <https://ethercat.org/en/products/E1753A559FBF4E2485C8C135BEEAC766.htm>.
- Servotronix CDHD in the trade press, 2012 (the year is in the address):
  <https://www.controldesign.com/vendors/products/2012/servotronix-cdhd-drive>. The exact launch
  date is not confirmed.
- Midea and Servotronix (2017): <https://en.globes.co.il/en/article-chinas-midea-buys-israeli-co-servotronix-1001176475>.

</details>
