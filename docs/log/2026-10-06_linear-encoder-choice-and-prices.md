# 2026-10-06 — Best linear encoder on paper, and what the short list costs

**Role(s):** engineering, purchasing

## Goal

Pick the most suitable encoder from the short list on the
[Linear encoder selection](../linear-encoder-selection.md) page. Find the prices, and name the
cheapest one, so the design can go on with one encoder.

## Work Done

- **The Renishaw TONiC T1030 head with an RTLC20-S steel tape is the best fit on paper.** It has
  the most margin on the requirements we can check:
  - Periodic error ±0.03 µm, against a limit of ±0.3 µm. RSF MS 15 MK has ±0.065 µm. Numerik Jena
    LIKgo has ±0.085 µm.
  - Accuracy about ±1.1 µm over 200 mm (our own conversion of ±5 µm/m), against a limit of ±5 µm.
  - Top speed 10 m/s. Head 13.5 × 10 × 35 mm. Tape 0.4 × 8 mm.
  - Renishaw is the only short-list maker outside the Heidenhain group. RSF, Numerik Jena and AMO
    all belong to Heidenhain, so they are not independent second sources for each other.
- **The TONiC row was not read again in the Renishaw data sheet.** It comes from an earlier search.
  A number that decides pass or fail must come from the maker's own document, so this check is
  still needed.
- **We cannot name the cheapest encoder yet.** Only RSF and Renishaw prices are public, and neither
  is for the exact part we need. The prices below are list or asking prices, seen on 6 October 2026.
  They are not quotes.

| Encoder | Head | Scale | Notes |
| --- | --- | --- | --- |
| RSF MS 15 MK | USD 406 (US reseller) | USD 221 (620 mm, ±5 µm/m grade, US reseller) | The head on sale is the TTL ×10 version, which fails the output requirement. The 1 Vpp head has no public price. |
| Renishaw TONiC T1030-15A | EUR 404 (earlier search), GBP 290 (Renishaw UK shop), USD 689 (US reseller, 3 to 5 weeks) | Price on request | Also needs the Ti interface, EUR 52.90 (earlier search). One used 1.1 m tape was offered for USD 400. |
| Numerik Jena LIKgo, LAKgo, LAK | Not public | Not public | The reseller asks you to call for a price. Numerik Jena sells LIKgo as a low-cost encoder. |
| AMO LMK 1005 | Not public | Not public | Only used heads of other LMK models are on offer. Needs an external electronics box. |
| Lamotion COIN 1 Vpp | Not public | Not public | The scale width is still unknown (ENC-10 is open). |

- **The price mix is not a fair comparison.** The prices are in three currencies. Only the RSF
  figure covers a head and a scale, and it is for the wrong output. Our stage needs only about
  300 mm of tape, so the real scale cost is lower than for the long tapes above.

## Decisions Made

No purchase decision. The TONiC is the preferred encoder on technical grounds. The final choice
waits for quotes.

## Open Questions

- What do the TONiC head, about 300 mm of RTLC20-S tape and the Ti interface cost together, new?
- What does the RSF MS 15 MK with 1 Vpp output cost? And the MS 14 MK? Its ±15 µm/m grade still
  gives ±3 µm over 200 mm, which passes.
- What does the Numerik Jena LIKgo with 1 Vpp output and about 300 mm of tape cost?

## Next Steps

1. Ask Renishaw, RSF and Numerik Jena for a quote for 1 and for 10 units of the parts above.
2. Read the TONiC data sheet again and check every number in its row on the selection page.
3. If the TONiC quote is close to the cheapest one, choose the TONiC for its margin. If it costs a
   lot more, the LIKgo or the RSF MS 15 MK are the second choice.

<details>
<summary>Technical notes and sources</summary>

- Mistake rule applied: [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md).
  No pass or fail on the selection page was changed. Prices come from shops and resellers, not
  from the makers, and are marked as such.
- The RSF reseller parts are ID 1120198-04 (head, "AK MS 15 TTLx10 HH M 1") and ID 1090262-75
  (MS 15 MK scale, 620 mm, ±5 µm/m). A second listing of the same TTL head, ID 1187349-01, shows
  USD 598.
- The Renishaw UK shop page returned "403 Forbidden" to our reader. The GBP 290 figure comes from
  the search result text only.
- Sources:
  - [Renishaw T1030-15A, Renishaw UK shop](https://store.renishaw.com/en-GB/product/T1030-15A)
  - [Renishaw T1030-15A, e-motionsupply](https://www.e-motionsupply.com/Renishaw_TONiC_readheads_T1030_15A_p/t1030-15a.htm)
  - [RTLC20-S scale, Renishaw shop (price on request)](https://www.renishaw.com/shop/Product.aspx?Product=A-9715-0200)
  - [Used RTLC20-S tape, 1100 mm, eBay](https://www.ebay.com/itm/143880677680)
  - [RSF MS 15 head 1120198-04, e-motionsupply](https://www.e-motionsupply.com/Encoder_Incremental_system_Reader_head_p/1120198-04.htm)
  - [RSF MS 15 head 1187349-01, e-motionsupply](https://www.e-motionsupply.com/RSF_Elektronik_Exposed_Linear_Encoder_MS_15_p/1187349-01.htm)
  - [RSF MS 15 MK scale 1090262-75, e-motionsupply](https://www.e-motionsupply.com/Encoder_Incremental_system_Linear_scale_p/1090262-75.htm)
  - [Numerik Jena LAK, e-motionsupply (call for price)](https://www.e-motionsupply.com/product_p/lak.htm)
  - [LIKgo low-cost announcement](https://www.globenewswire.com/news-release/2019/05/22/1840781/0/en/NUMERIK-JENA-s-New-Low-Cost-LIKgo-Linear-Encoder-for-Semiconductor-Industry.html)
  - [AMO LMK used listing, eBay](https://www.ebay.com/itm/276526211739)

</details>
