# 2026-09-18 — Stage families are modules of AQTUATOR, not separate repositories

- **Date:** 2026-09-18
- **Status:** Accepted

## Context

AQTUATOR started as one investigation: suppress chatter on a Mekanika Pro milling machine. It is now
the root of a product line of linear stages. The mill is the test bench, not the product.

That raised a question we had to answer before drawing anything. A product family is a line of
stages with similar properties — compact, heavy duty, high force, ultra precision. Should each
family be its own Git repository from the start?

One level down, the answer was already written. doqs says a length is a parameter of one shared
core, a different drive or sensor is an option module combined by a thin composition module, and
one repository per sold item (SKU) is an anti-pattern. See
[`doqs/docs/variants.md`](../../doqs/docs/variants.md). What doqs does not answer is the level above
that: several families in one project.

The measurement campaigns, the excitation firmware and the host identification software were sitting
at the repository root. They are not shared across the product line. They belong to the
chatter-suppression stage and to nothing else.

## Decision

**1. Each stage family is a plain folder under `modules/`.**

`modules/flexure-ball-screw-servo-stage/` is the chatter-suppression stage. `modules/compact-stage/` is the compact stage, name
reserved only. A Git submodule *is* a separate repository, so "a submodule now, a repository later"
is not two steps. It is one step, and we are not taking it yet.

**2. A family moves out only when something concrete asks for it.**

Any one of these is enough: an outside project wants that family alone; the family needs its own
release numbers and rhythm; it needs different access rules or a different licence; or the
repository has grown too heavy to clone, which supplier CAD per stocked length will eventually do.
Until then, the families share interfaces, supplier tables, purchased-part geometry, electronics,
firmware and control software, and one commit should reach all of them.

The move stays cheap by design. Inside a family, modules reference each other with paths relative to
the family root, so the family travels as one unit, keeps its history through
`git subtree split`, and changes no path on the way out.

**3. Measurement, firmware and software belong to the family they serve.**

`firmware/`, `measurement/` and `software/` moved from the repository root into
`modules/flexure-ball-screw-servo-stage/`. If that family ever leaves, its evidence and its code
leave with it. Leaving them at the root would have made the chatter work look like product-line
infrastructure, which it is not.

**4. Family folders are named after what the stage is, not what it is called.**

`flexure-ball-screw-servo-stage` and `compact-stage`. doqs asks a module folder to name the
function and keeps commercial names in `catalog.toml`, so that a price list can be rewritten
without renaming a folder, a repository and every path that points into it. We follow that rule.

The first name also states the architecture: flexure guidance, ball-screw transmission, servo
drive. That is deliberate. Families are separated by architecture, not by marketing, so the name
says which architecture this one is. A stepper version of the same stage would be a different
family, or an option module inside this one — and in either case the name stays honest.

## Consequences

**Good.** One commit reaches every family while the shared parts are still moving. Nothing about the
chatter work is stranded at the root. Adding a third family costs one folder.

**We deviate from the doqs specification in one place.** doqs lists `firmware/` and `software/` as
root-only folders. We now have them at module depth. This is where they have to be if a family is
ever extracted, because an extracted module repository is allowed both — so the specification is
behind, not the layout.

**Licence stubs are hand-written inside the module.** The licence tool only writes stubs for the
first-level folders of a repository root. An embedded module's folders inherit the hardware licence
from `modules/LICENSE`, which is wrong for code and wrong for measurement records. We wrote the
three stubs by hand. When a family is extracted, the tool takes over automatically.

**The naming check now prints twenty warnings.** It treats every directory under `modules/` as a
possible module and only excuses `cad/`, `bom/` and `architecture/`. Every other standard content
folder at module depth is reported as an orphan, including `measurement/`, which is fully allowed by
the specification. All gates still pass. This is a doqs bug to raise, not a problem with this
repository.

**No catalogue yet.** Neither family has `catalog.toml`, a core module or compositions. A catalogue
with no products would be a claim we cannot back. It arrives with the requirements and the
architecture, and it is where the commercial names FLEQXURE and COMPAQT will live.

<details>
<summary>Notes for reviewers</summary>

- Family root discovery is `catalog.toml` at any depth (`doqs/scripts/naming_rules.py:84`), and
  `validate_variants.py:247` collects them with `rglob`, so several families in one repository is a
  supported configuration.
- The orphan warning comes from `check_module_directories` in `doqs/scripts/validate_names.py`. Its
  skip list is `adapters`, `modules`, and any path containing `cad`, `bom` or `architecture`. Adding
  `docs`, `firmware`, `software`, `measurement`, `simulation` and `manufacturing` would clear it.
- Licence stub markers are checked, not compared byte for byte
  (`_write_if_needed` in `doqs/scripts/license_rules.py:375`), so the hand-written stubs are stable
  and `apply_licenses.py --check` passes.
- The earlier proposal for the level below this one is
  [refaqt/aqtuator#15](https://github.com/refaqt/aqtuator/pull/15). It was closed unmerged on
  2026-09-16 because its content moved into doqs as
  [ADR-003](../../doqs/docs/decisions/2026-09-15_product-family-variants.md).
- The root `okh.toml` and the clone URL still said `nielsbosmans87`. The remote is `refaqt`. Both
  were corrected in this change.

</details>
