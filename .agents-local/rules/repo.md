# AQTUATOR: rules for this repository

AQTUATOR is a product line of linear stages. Each stage family is a module under `modules/`:
`flexure-ball-screw-servo-stage` (active chatter suppression, the first family) and
`compact-stage` (driven by a linear motor). A Mekanika Pro milling machine is the test bench. The
layout follows doqs.

## Where things go

| You are adding | It goes in |
| --- | --- |
| Code for the Controllino | `modules/flexure-ball-screw-servo-stage/firmware/<target>/` |
| Code for a PC | `modules/<family>/software/<project>/src/<package>/` (installable: `pip install -e …`) |
| A model of one stage family | `modules/<family>/simulation/cases/<slug>/` |
| A model not about one family | `simulation/cases/<slug>/` |
| A physical test campaign | `modules/<family>/measurement/cases/<slug>/` |

Stack: Python, Arduino C++, Octave, FreeCAD (`freecadcmd` for stress cases). Run commands from the
repository root. Python tests: set `PYTHONPATH` to the root, then
`python -m unittest discover -s tests -p "test*.py" -v`.

## Hard rules

- **The ODrive S1 is for testing only.** Do not suggest it, and do not choose any part because it
  works with the ODrive. Keep the existing ODrive code and logs.
  ([decision](../../docs/decisions/2026-10-02_odrive-is-for-testing-only.md))
- **No Israeli suppliers.** Do not suggest or shortlist their parts (for example Servotronix, Elmo,
  ACS, Agito Akribis, Dynamikwell).
  ([decision](../../docs/decisions/2026-10-06_kollmorgen-akd-and-copley-xenus-plus-as-candidates.md))
- **Pass or fail needs the maker's own data sheet.** This went wrong three times. Use the skill
  `source-documents`. If you cannot open the document, write "not confirmed".
- **Never commit measurement data.** Use the skill `measurement-data`.
- **When you add or connect a part, add the interface in the same change:** a versioned `port def`
  in `architecture/<module>.sysml`, and in `okh.toml` when it is on the outside of the module. Do
  not invent dimensions. Example: `modules/compact-stage/architecture/compact-stage.sysml`.
- **Never edit `.FCStd` files directly.** After a parameter change, run
  `exec(open("doqs/scripts/cad_sync_params.py").read())` and then `sync_active()` in the FreeCAD
  Python console.
- **People here use Windows and PowerShell.** In commands for them: no `&&`, no heredocs, no
  `cd /d`.
- Before a new solution for serial links, the ODrive, RP2040 PWM or ADC, or transfer estimates,
  use the skill `patterns`.

## Commits

`<type>(<scope>): <description>`. Extra types here: `cad`, `arch`, `okh`, `firmware`, `sim`,
`interface`, `model`, `build`. Slugs name the function, never a size or a material.
