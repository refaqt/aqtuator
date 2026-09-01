# AQTUATOR repository profile

Agent-only. Humans: see `README.md` and `docs/onboarding.md`.

## What this repository is

AQTUATOR investigates active chatter suppression on a Mekanika Pro milling machine. Layout follows
[doqs](https://github.com/refaqt/doqs) — read `doqs/docs/architecture.md` before adding folders. If
`doqs/` is empty: `bash setup-tooling.sh` from the repo root (agents, any OS). Humans on Windows may
double-click `setup-tooling.bat`.

## Where things go

| You are adding | It goes in |
| --- | --- |
| Code that runs on the Controllino | `firmware/<target>/` |
| Code that runs on a PC | `software/<project>/src/<package>/` |
| A model that predicts behaviour | `simulation/cases/<slug>/` |
| A physical test campaign | `measurement/cases/<slug>/` |
| A day's work write-up | `docs/log/YYYY-MM-DD_topic.md` |
| Why a choice was made | `docs/decisions/YYYY-MM-DD_topic.md` |
| Something that went wrong | `docs/mistakes/YYYY-MM-DD_topic.md` |
| A reusable coding pattern | `.agents-local/skills/patterns/SKILL.md` |

## doqs references

| Read | When |
| --- | --- |
| `doqs/docs/architecture.md` | New modules, versioning, interfaces, builds |
| `doqs/docs/naming.md` | Naming modules, parts, campaigns |
| `doqs/skills/freecad/SKILL.md` | FreeCAD debugging, assemblies, master sketches |
| `doqs/templates/` | Creating log, ADR, mistake entries |

`docs/architecture.md` in this repo is a short overview — not a second copy of the spec.

## Stack and execution

- **Mixed stack:** Python (`software/*`), Arduino/C++ (`firmware/*`), Octave (`simulation/cases/*`),
  FreeCAD (`cad/`).
- Run commands from the repository root. `software/*` are installable packages
  (`pip install -e software/identification`); import them rather than manipulating `sys.path`.
- **Windows / PowerShell:** no `&&`, no bash heredocs, no `cd /d`. See `docs/mistakes/`.
- Before new solutions for serial / ODrive / RP2040 PWM/ADC / transfer estimation, read
  `.agents-local/skills/patterns/SKILL.md` and use the `maintain-patterns` skill.
- If living docs are missing, create them from `.agents/bootstrap/docs/`.

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
- **Never edit `.FCStd` files directly.** Use FreeCAD, and run `cad/sync_params.py` inside it after
  changing parameters.

## Validate

```bash
python doqs/scripts/validate_all.py
```
