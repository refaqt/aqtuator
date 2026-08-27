---
name: log
description: >-
  Add or edit an entry in the unified activity log (docs/log/). Use whenever the
  user wants to record work — engineering, hardware, software, outreach, research,
  a call or meeting, or a business decision. Triggers on "log this", "add a log
  entry", "note that", "record today's work", or a photo sent with a description
  of work done.
---

# Adding an activity log entry

`docs/log/` is the chronological record of work on the project across **all** roles.
One flat directory — no per-role subfolder. Every entry is labeled with the role(s)
it belongs to under the heading.

## File

```
docs/log/YYYY-MM-DD_topic-slug.md
```

- `YYYY-MM-DD` — the date the work happened, not necessarily today. Resolve relative dates ("yesterday", "on Tuesday").
- `topic-slug` — kebab-case, naming what the entry is *about*. Follow style in `docs/log/README.md`.
- If an entry for that date already exists and the new content belongs with it, **append to it** rather than creating a second file. Two entries for one date need distinct slugs.

## Content

```markdown
# YYYY-MM-DD — Topic Title

**Role(s):** engineering

## What happened

## Decisions

## Open Questions

## Next Steps
```

**Role(s)** is mandatory. Use one or more of:

- Engineering: `engineering`, `hardware`, `software`, `firmware`, `cad`, `simulation`, `measurement`
- Business: `business-dev`, `marketing`, `sales`, `finance`, `purchasing`

List every role the work touches. Prefer the sections that carry content; drop empty ones.
Write in the user's voice; keep numbers, units, and terminology exact.

For engineering lab-notebook style, these alternate section names are fine when they fit better:
`## Goal`, `## Work Done`, `## Decisions Made`, `## Open Questions`, `## Next Steps`.

## Photos and figures

Images go in `docs/log/images/` named `YYYY-MM-DD-NN.ext`, numbered in order of appearance.
Reference them relatively (`![](images/2026-08-21-01.png)`) and add a short caption line.

## Related content

- Lasting technical choices → also `docs/decisions/YYYY-MM-DD_topic.md` (link from the log entry).
- Failures / prevention → also `docs/mistakes/YYYY-MM-DD_topic.md`.
- Repo-specific deliverables (datasets, pitch drafts, etc.) live outside `docs/log/`; link them from the entry.

## Finish

1. Update the table in `docs/log/README.md` (date, linked topic, role(s), image count if used). Keep date order.
2. Commit as `docs(log): <short description>`.
3. Push per the repo's normal branch/PR flow.

Confirm what you wrote and where, and give the user the path.
