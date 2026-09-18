# 2026-09-18 — AQTUATOR becomes a product line of linear stages

**Role(s):** engineering

## Goal

Turn the repository from a single chatter-suppression investigation into the root of a product line
of linear stages, and decide how a stage family is stored before any family is designed.

## Work Done

- Answered the open question first, in
  [Stage families are modules of AQTUATOR](../decisions/2026-09-18_stage-families-as-modules.md):
  each family is a plain folder under `modules/`, and it becomes its own repository only when
  something concrete asks for it.
- Created two family modules: `modules/flexure-ball-screw-servo-stage/` for the chatter-suppression
  stage, and `modules/compact-stage/` for the compact stage. The second one is a reserved module and
  nothing more.
- Moved `firmware/`, `measurement/` and `software/` from the repository root into
  `modules/flexure-ball-screw-servo-stage/`, with `git mv`, so the history follows the files.
- Wrote the three licence stubs inside the module by hand. The licence tool only covers the
  first-level folders of a repository root, so without them the firmware, the software and the
  measurement records would have inherited the hardware licence from `modules/LICENSE`.
- Updated every path that pointed at the three moved folders: the README, the architecture overview,
  the onboarding guide, the licence overview, the continuous-integration workflow, the Git metadata,
  the agent rules and skill, and the default index path inside the measurement tools.
- Corrected the GitHub organisation in the project manifest and the clone instructions. It said
  `nielsbosmans87`; the remote is `refaqt`.

## Decisions Made

- A Git submodule is a separate repository, so "a submodule now, a repository later" is one step,
  not two. Families stay plain folders until an outside consumer, a separate release rhythm,
  different access rules, or repository size asks otherwise.
- Measurement, firmware and software belong to the family they serve, not to the product-line root.
- Family folders are named after what the stage is, not after what it is called on a price list.
  The commercial names stay out of the tree until a family has a `catalog.toml` to hold them.

## Next Steps

- [ ] Write the requirements for linear stages in `architecture/`, then decide which properties are
      parameters of a shared core and which are separate option modules.
- [ ] Raise two points against doqs: `firmware/` and `software/` are listed as root-only but are
      needed at module depth, and the naming check reports every standard content folder under
      `modules/` as an orphan.
- [ ] Decide whether `simulation/` also belongs inside the flexure ball-screw servo stage. Both of
      its cases are chatter-suppression work, but it was left at the root in this change.

<details>
<summary>Checks</summary>

`python doqs/doqs.py check` — all ten gates pass. Twenty naming warnings, all of the form
"directory under modules/ has no okh.toml (orphan?)", explained in the decision record.

`python doqs/scripts/validate_links.py --markdown` — every SysML import, OKH path and relative
markdown link resolves. This was clean before the move and is clean after it.

</details>
