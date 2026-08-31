# 2026-08-31 — Linear-stage variants: family repo, params for length, composition for options

- **Date:** 2026-08-31
- **Status:** Proposed

## Context

The same linear stage will ship in many configurations: standard lengths, different motors
(stepper, rotary servo, possibly linear motor), and different feedback (none, rotary encoder,
linear encoder). A later machine project should be able to take one configuration and drop it
into a larger assembly as a Git submodule.

Two naive layouts fail that combination of needs:

1. **One Git repo or long-lived branch per SKU.** A shared change (mounting-hole pattern, rail
   size, carriage envelope) must be copied or cherry-picked across every SKU. That does not
   scale, and it fights the doqs rule that versions are tags on one history, not forks.
2. **One parent repo per SKU, with the shared core as a child submodule.** Propagation is
   better than (1), but every shared fix still means: commit the core, then bump the pointer
   in every parent. That is the submodule tax multiplied by the catalogue.

The remaining idea is a **single parametric FreeCAD model** whose spreadsheet turns parts on
and off and sets length. That matches how length *should* work. It is a poor product
configurator for motors and encoders.

doqs already splits this problem in
[`doqs/docs/architecture.md`](../../doqs/docs/architecture.md) (*Versioning Across
Dimensions*):

| Kind of difference | Mechanism |
| --- | --- |
| Numbers only (300 mm vs 500 mm travel) | Parametric `[[model]]` + `cad/params/<model>.csv` on shared `.FCStd` files |
| Architecture (belt vs ballscrew, motor family, feedback family) | Thin **composition** modules that share a core and pick different nested modules |
| Time / install base | Git tags + `release/vN.x`, not a branch per SKU |
| A real machine instance | `builds/<id>/build.toml` pinning module version **and** `model` |

The stage family is the first time this repo will use that machinery in anger. The spec is
mostly right. A few holes appear once a commercial catalogue (many lengths × a few option
packages) is the thing being published, not a one-off machine axis.

The SKU list and costing live in the business log
`aqtuator-business/docs/finance/2026-08-26_aqtuator-linear-stage-pricing` (not in this
workspace). Engineering structure here must still join to those commercial names later.

## Decision

Treat the stages as **one product family**, not as N products and not as one mega-assembly
with visibility flags.

### 1. Split variation the way doqs already does

**Length (and other scalars)** is a parametric model of the *shared core*. Rail cut length,
ballscrew or belt length, extrusion length, encoder-scale length, and any offsets that
follow travel live in `cad/params/default.csv` plus sparse overrides (`300mm.csv`,
`500mm.csv`, …). Geometry files are shared. A mounting-hole change is one CAD edit and
applies to every length.

**Motor family and feedback family** are structural options: nested modules plus a few thin
composition modules. They are not spreadsheet rows. Each composition is a real (but thin)
doqs module — its own `okh.toml`, assembly `.FCStd` that `App::Link`s the core plus one
drive plus one feedback, its own purchased-parts BOM, and the interfaces that SKU actually
offers.

Do not flatten the cartesian product into model slugs such as `800mm-servo-linear`. That
mixes two axes of variation and explodes the `[[model]]` list. Length stays a model of the
core; drive and feedback stay compositions. Three compositions × a handful of length CSVs
is the catalogue, not 24 named CAD files.

Suggested tree while the family still lives in this repository (names are functional slugs,
not commercial SKUs):

```
modules/
  linear-stage/                 # shared core: rails, carriage, ends, envelope, mount ports
    cad/params/
      default.csv
      300mm.csv
      500mm.csv
    modules/
      drive-stepper/
      drive-servo/
      feedback-none/
      feedback-rotary/
      feedback-linear/
  linear-stage-stepper/         # thin composition: core + drive-stepper + feedback-none
  linear-stage-servo-rotary/    # core + drive-servo + feedback-rotary
  linear-stage-servo-linear/    # core + drive-servo + feedback-linear
```

Keep compositions few. Before adding a fourth, ask whether the difference is a parameter
(doqs: “Structural models are expensive”). A cover strip, a hole pattern that every
carriage can tolerate, or a fastener length that follows travel is a parameter, not a
composition.

### 2. Extract the family, not the SKU

doqs Mode A (embedded folders) is how the family is *developed*. Mode B (extracted Git
submodule) is how a *machine* consumes it — but the extracted unit is the **family
repository**, not `linear-stage-servo-linear` as its own GitHub repo.

A downstream project:

1. Adds the family as one submodule (path stable, so FreeCAD relative links keep working).
2. Links only the composition assembly it uses.
3. Pins that composition and a parametric model in `builds/<id>/build.toml`:

```toml
[[module]]
path    = "modules/linear-stage-servo-linear"
version = "v1.0.0"
model   = "500mm"
```

Unused compositions are inert files in the clone. That is cheaper than N submodule
pointers. Sparse checkout / skipping unused LFS objects can come later if the CAD tree
gets heavy; it is an optimisation, not the layout.

Do **not** create one parent repo per SKU with `linear-stage` as a child submodule.
Compositions are folders in the family repo so a shared-core commit is visible to every
SKU without pointer-bumping.

Stay embedded under `modules/` in aqtuator until a second machine (or a published
catalogue) actually consumes the family. Then subtree-split the family as a whole.
Aqtuator itself is the chatter-suppression project; it should consume the family the same
way Qarve would, not become the catalogue’s Git history.

### 3. Do not use FreeCAD suppression as the product configurator

Spreadsheet-driven **dimensions** are first-class and already specified (CSV →
`resolve_params.py` → `sync_params.py` → Spreadsheet aliases → sketch expressions). Use
that for length.

Spreadsheet-driven **presence of a motor or encoder** is not a doqs mechanism, and it is a
weak FreeCAD one:

- PartDesign `Suppressed` can be bound to a spreadsheet only via a hidden expression
  (right-click the property — there is no `f(x)` control). See
  [forum t=93265](https://forum.freecad.org/viewtopic.php?t=93265).
- Suppressing geometry that other features (fillets, binders, assembly joints) depend on
  breaks the model. See [forum t=105096](https://forum.freecad.org/viewtopic.php?t=105096).
- `Visibility` is a view property, not “omit from BOM / STEP / CAM”.
- doqs BOMs, OKH `[[part]]` rows, SysML ports, and manufacturing files are text. A hidden
  Suppress flag in an LFS `.FCStd` is invisible to git diff, validators, and agents.
- A stepper SKU and a servo+linear-encoder SKU **provide different interfaces**. That
  belongs in `[[provides-interface]]` on the composition, not in a boolean named
  `has_linear_encoder`.

Allowed exception: optional features on **one manufactured part** (an extra hole pattern
the stepper carriage can keep). Prefer over-holing a shared carriage over a second
carriage module, unless the holes hurt stiffness, sealing, or machining setup. If the
part is truly different, it lives in the feedback (or drive) module.

FreeCAD configuration tables / `LinkCopyOnChange` are a way to instantiate the *same*
part at different dimensions — the parametric-model case — not a substitute for
composition.

### 4. Join commercial SKUs with a catalogue file, not with folder names

Pricing and order codes stay in the business repo. Engineering gets a text catalogue that
those sheets can join on: commercial name → composition path + parametric model. Draft
shape (filename and exact schema are a doqs change, below):

```toml
[[sku]]
name          = "ALS-S-300"          # commercial / pricing key
composition   = "modules/linear-stage-stepper"
model         = "300mm"

[[sku]]
name          = "ALS-SL-500"
composition   = "modules/linear-stage-servo-linear"
model         = "500mm"
```

Module folders keep functional slugs (`linear-stage-servo-linear`). They never contain
`500mm` or material names ([naming.md](../../doqs/docs/naming.md)).

### 5. What to change in doqs (proposals, not done here)

The family/composition/params split above can be used today. These spec gaps will hurt
once more than one length is exported or purchased:

1. **Extraction examples imply SKU repos.** Mode B and the `x-axis-belt` example read as
   “extract the composition.” State that the default extractable unit is the **family**;
   extract a composition only when it has its own maintainers, licence, or release
   cadence.
2. **BOM is not model-aware.** One `bom/bom.csv` cannot describe a 300 mm rail and a
   500 mm rail, or different cut lengths of the same profile. Add sparse BOM overlays
   (`bom/<model>.csv`) or a `models` column, analogous to `cad/params/`. Structural BOM
   differences (which motor is fitted) stay in the composition’s own BOM — that part
   already works.
3. **Exports are not model-aware.** `cad/exports/x-axis.step` is one file. Lengths need
   `cad/exports/<model>/` (or an equivalent naming rule). Naming.md forbids dimensions
   in *module folder* names; export artefacts of a declared model slug should be
   allowed.
4. **No SKU catalogue.** `[[model]]` plus compositions do not name what sales and
   pricing call a product. A `catalog.toml` (or OKH `[[sku]]`) mapping commercial id →
   composition + model is the join key to the business repo.
5. **`[[hasComponent]]` cannot select a model.** `build.toml` already has `model`.
   Consuming a family repo from another machine needs the same pin on the component
   declaration (path of the composition inside the family + `model`).
6. **`500mm-hd` as a model slug mixes axes.** Keep it as a last-resort example. Prefer
   orthogonal params × compositions so the catalogue does not become a cartesian
   `[[model]]` list.
7. **Anti-pattern.** Document that FreeCAD `Visibility` / `Suppressed` expressions are
   not the product-variant mechanism.

Do not add a general `[[option]]` configurator language yet. Three compositions and a
handful of length files are inside what the spec already calls “few.” A spreadsheet
configurator for 3 × 2 × 4 SKUs would cost more than the compositions.

## Consequences

- A mounting-point change is one commit in the core module; every composition and length
  picks it up because they Link the same files.
- A machine repo vendors **one** submodule (the family) and pins one composition +
  length in its lockfile — the checkout story without N Git repositories.
- Motor and encoder swaps stay reviewable in git: new or changed files under
  `drive-*` / `feedback-*` / the thin composition, not a boolean in an LFS document.
- Pricing sheets join on catalogue SKU names; they do not dictate folder names.
- doqs needs the seven spec deltas above before a published catalogue (per-model BOM
  and exports especially). Until then, compositions carry structural BOM lines, and
  parametric cut lengths are noted in `spec` / `notes` on the core BOM by hand if
  needed.
- This ADR does not create the module tree or CAD. It constrains the first
  `modules/linear-stage/` work.
