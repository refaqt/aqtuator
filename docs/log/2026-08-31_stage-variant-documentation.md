# 2026-08-31 — Linear-stage variant documentation

**Role(s):** engineering, cad

## Goal

Decide how to document and version many SKUs of the same linear stage (lengths, motors,
feedback) so shared geometry changes once, and a machine project can still vendor one
configuration.

## Work Done

- Read the doqs versioning model (parametric `[[model]]` vs structural composition vs
  Mode A/B extraction) against that catalogue problem.
- Wrote a proposed ADR:
  [`docs/decisions/2026-08-31_linear-stage-variant-structure.md`](../decisions/2026-08-31_linear-stage-variant-structure.md).

## Decisions

See the ADR (status **Proposed**). Short form: one family, length as `cad/params/` models,
motor/feedback as thin compositions, extract the family not each SKU, do not use FreeCAD
suppression as the configurator. Seven doqs spec gaps listed there (BOM/exports per model,
SKU catalogue, extraction examples).

The business pricing note
`aqtuator-business/docs/finance/2026-08-26_aqtuator-linear-stage-pricing` was not in this
workspace; the ADR uses the variation axes stated for this work rather than that sheet’s
exact SKU list.

## Next Steps

- [ ] Accept or amend the ADR.
- [ ] If accepted, open the listed doqs spec changes on `refaqt/doqs` (family extraction,
      per-model BOM and exports, catalogue / `[[sku]]`, `hasComponent` model pin).
- [ ] When CAD starts, create `modules/linear-stage/` and the first composition rather than
      a single parametric assembly with optional motors.
