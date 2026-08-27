# Agent guide

Entry point for Cursor, Claude Code, and other agents working in this repository.

## Shared kit

This repo vendors [refaqt/refaqt-agents](https://github.com/refaqt/refaqt-agents) at [`.agents/`](.agents/)
(portable rules and skills). Prefer that tree over duplicated guidance elsewhere.

1. Read [`.agents/rules/core.md`](.agents/rules/core.md) and
   [`.agents/rules/living-docs.md`](.agents/rules/living-docs.md).
2. Read [`docs/mistakes/`](docs/mistakes/). Four of the six logged incidents are the same class of
   error: **using bash syntax in PowerShell**. This is a Windows machine — no `&&`, no bash
   heredocs, no `cd /d`. Use `;` and `if ($?) { }`.
3. Read [`docs/architecture.md`](docs/architecture.md) before non-trivial work.
4. Before writing new code for serial protocols, ODrive control, RP2040 PWM/ADC, or
   transfer-function estimation, check [`docs/patterns/SKILL.md`](docs/patterns/SKILL.md).

If `.agents/` is empty or incomplete, restore it from the refaqt-agents kit (submodule init once
published, or copy from that repository).

## Layout (doqs)

This repo follows [doqs](https://github.com/refaqt/doqs), a submodule at [`doqs/`](doqs/).
**Do not guess the layout from memory** — read the spec. If `doqs/` is empty, run
`git submodule update --init --recursive` first.

| Read | When |
| --- | --- |
| `doqs/docs/architecture.md` | New modules, versioning, interfaces, builds |
| `doqs/docs/architecture.md` (Measurement) | Test campaigns, or data held outside Git |
| `doqs/docs/architecture.md` (Software) | Host-side apps and analysis libraries |
| `doqs/docs/architecture.md` (Simulation) | Design-time analysis cases |
| `doqs/docs/naming.md` | Naming modules, parts, campaigns, repos |
| `doqs/skills/freecad/SKILL.md` | FreeCAD debugging, assemblies, master sketches |
| `doqs/templates/` | Creating log, ADR, mistake or OKH entries |

`docs/architecture.md` in this repo is a short overview and pointer, not a second copy of the spec.

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
| A reusable coding pattern | `docs/patterns/SKILL.md` |

## Measurement data

**Never commit measurement data.** `data/`, `*.WDH` and `*.WDQ` are gitignored, and Git LFS here is
scoped to CAD binaries only.

1 659 files, 1.88 GB, on a Google Drive shared drive. To answer a question about what was measured,
read [`measurement/data-index.csv`](measurement/data-index.csv) — it has one row per file with
campaign, path, tier, size, sha256, and parsed metadata (axis, position, material, spindle speed,
feed, depths of cut, tool, sample rate). Most questions are answerable from that CSV alone, with no
download.

To read an actual file, resolve its path through `$AQTUATOR_DATA_ROOT`:

```python
from measurement_tools.data_root import resolve
path = resolve(row["relpath"])
```

See [`.agents-local/skills/measurement-data/SKILL.md`](.agents-local/skills/measurement-data/SKILL.md).

## Skills

| Skill | Path |
| --- | --- |
| Activity log | [`.agents/skills/log/SKILL.md`](.agents/skills/log/SKILL.md) |
| Mistake log | [`.agents/skills/mistake-log/SKILL.md`](.agents/skills/mistake-log/SKILL.md) |
| Maintain patterns | [`.agents/skills/maintain-patterns/SKILL.md`](.agents/skills/maintain-patterns/SKILL.md) |
| Measurement archive | [`.agents-local/skills/measurement-data/SKILL.md`](.agents-local/skills/measurement-data/SKILL.md) |

## Conventions

- **Commits:** `<type>(<scope>): <description>` — `feat`, `fix`, `docs`, `cad`, `arch`, `okh`,
  `firmware`, `sim`, `chore`, `refactor`, `interface`, `model`, `build`
- **Slugs:** kebab-case, name the function not the shape (`x-axis`, not `aluminium-plate`).
  Never encode dimensions or materials in a folder name — those are data.
- **Python:** run entry points from the repo root. `software/*` are installable packages; import
  them properly rather than manipulating `sys.path`.
- **Never edit `.FCStd` files directly.** Use FreeCAD, and run `cad/sync_params.py` inside it after
  changing parameters.

## Validate

```bash
python doqs/scripts/validate_all.py
```
