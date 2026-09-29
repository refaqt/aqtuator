# AQTUATOR repository profile

Agent-only. Humans: see `README.md` and `docs/onboarding.md`.

## What this repository is

AQTUATOR is a product line of linear stages. Each stage family is a module under `modules/`:
`flexure-ball-screw-servo-stage` (active chatter suppression, the family that started the project)
and `compact-stage` (compact
stage, name reserved only). A Mekanika Pro milling machine is the test bench. Layout follows
[doqs](https://github.com/refaqt/doqs) — read `doqs/docs/architecture.md` before adding folders. If
`doqs/` is empty: `bash setup-tooling.sh` from the repo root (agents, any OS). Humans on Windows may
double-click `setup-tooling.bat`.

## Where things go

| You are adding | It goes in |
| --- | --- |
| Code that runs on the Controllino | `modules/flexure-ball-screw-servo-stage/firmware/<target>/` |
| Code that runs on a PC | `modules/<family>/software/<project>/src/<package>/` |
| A model that predicts behaviour | `simulation/cases/<slug>/` |
| A new stage family | `modules/<family>/` — read `doqs/docs/variants.md` first |
| A physical test campaign | `modules/<family>/measurement/cases/<slug>/` |
| A day's work write-up | `docs/log/YYYY-MM-DD_topic.md` |
| Why a choice was made | `docs/decisions/YYYY-MM-DD_topic.md` |
| Something that went wrong | `docs/mistakes/YYYY-MM-DD_topic.md` |
| A reusable coding pattern | `.agents-local/skills/patterns/SKILL.md` |

## doqs references

| Read | When |
| --- | --- |
| `doqs/docs/using-doqs.md` | **Start here.** What to run, what doqs installs, what each gate checks |
| `doqs/docs/architecture.md` | New modules, versioning, interfaces, builds |
| `doqs/docs/naming.md` | Naming modules, parts, campaigns |
| `doqs/docs/agent-cad.md` | Any CAD work by an agent; seeding a module's `build_model.py` |
| `doqs/templates/` | Machine structure: CAD build script, measurement case, OKH, variants |
| `.agents/skills/freecad/SKILL.md` | FreeCAD debugging, assemblies, master sketches |
| `.agents/templates/adr.md` | Writing a decision record |

`docs/architecture.md` in this repo is a short overview — not a second copy of the spec.

## Stack and execution

- **Mixed stack:** Python (`modules/*/software/*`), Arduino/C++ (`modules/*/firmware/*`),
  Octave (`simulation/cases/*`), FreeCAD (`cad/`).
- Run commands from the repository root. The `software/*` folders are installable packages
  (`pip install -e modules/flexure-ball-screw-servo-stage/software/identification`); import them rather than manipulating
  `sys.path`.
- **Windows / PowerShell:** no `&&`, no bash heredocs, no `cd /d`. See `docs/mistakes/`.
- Before new solutions for serial / ODrive / RP2040 PWM/ADC / transfer estimation, read
  `.agents-local/skills/patterns/SKILL.md` and use the `maintain-patterns` skill.
- If living docs are missing, create them from `.agents/bootstrap/docs/`.

## GitHub Actions workflows

- **Use actions that run on Node 24.** GitHub has deprecated Node 20 for actions, and every run
  that still uses one shows a warning. Before you add or change a `uses:` line, find the newest
  major tag (`git ls-remote --tags https://github.com/actions/<name>.git`) and check `runs.using`
  in its `action.yml`. It must say `node24`, or `composite` with only Node 24 actions inside.
  Read the breaking changes of each major version you skip.
- In use now: `checkout@v7`, `setup-python@v7`, `setup-node@v7`, `configure-pages@v6`,
  `upload-pages-artifact@v5`, `deploy-pages@v5`.
- `setup-node@v5` and newer cache by default. Set `package-manager-cache: false` in a job that
  can deploy or holds secrets.
- After a workflow change, open the first run and read its annotations, not only its result. A
  green run can still carry a deprecation warning.
- `ubuntu-latest` moves to Ubuntu 26 from 2026-10-19. Our jobs only need Python and Node, so
  keep `ubuntu-latest`. If a job breaks after that date, check the runner image change first.

## Measurement data

**Never commit measurement data.** Use `.agents-local/skills/measurement-data/SKILL.md` for archive
queries and file access.

## Branching

Every task that changes the repo must start on a **new git branch** off `main`, unless the user explicitly says otherwise. Do not land task work as commits directly on `main`.

## Conventions

- **Commits:** `<type>(<scope>): <description>` — `feat`, `fix`, `docs`, `cad`, `arch`, `okh`,
  `firmware`, `sim`, `chore`, `refactor`, `interface`, `model`, `build`
- **Slugs:** kebab-case, name the function not the shape (`x-axis`, not `aluminium-plate`). Never
  encode dimensions or materials in folder names.
- **Never edit `.FCStd` files directly.** Use FreeCAD, and run
  `exec(open("doqs/scripts/cad_sync_params.py").read())` then `sync_active()` in its Python console
  after changing parameters. A module never keeps its own copy of a doqs tool.
  That script stays a manual step, and `doqs.sh` has no subcommand for it: it runs
  **inside** the FreeCAD interpreter, which `doqs.sh` cannot reach. `doqs.sh list`
  says so too.

## Numbers that decide a pass or a fail

**This mistake has happened three times.** Before you call a part a pass or a fail on a hard
requirement, read the deciding number in the maker's own data sheet or manual. A trade article, a
search result, a shop page or a textbook constant is not enough. If you cannot open the primary
document, write "not confirmed" in the short answer and in the table. See
[docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md](../../docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md).

## Validate

```bash
bash doqs.sh generate    # only after changing parameters, a BOM or a licence folder
bash doqs.sh check       # every gate, before every commit
```

`doqs.sh list` prints every command. `python doqs/doqs.py check` is the same thing
without the launcher, and is what CI runs.

`doqs check` runs the seven gates **plus** three checks that the committed generated
files are current. `python doqs/scripts/validate_all.py` still works and still runs
only the seven.
