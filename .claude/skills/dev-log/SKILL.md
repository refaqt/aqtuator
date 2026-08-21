---
name: dev-log
description: Add or edit an entry in the project development log (docs/dev-log/). Use whenever the user wants to record what they did today, log a result, note an idea, attach a photo of the machine or a measurement plot, or write up a meeting. Triggers on "log this", "add a log entry", "note that", "record today's work", or a photo sent with a description of work done.
---

# Adding a development log entry

The log is the chronological record of this project — 71 entries from June 2025 onward. It was
converted out of a Word document; **git is the source of truth now**, so entries are written here,
not in the Google Doc.

This skill exists because the most common way to add an entry is from a phone, where guessing the
convention wastes the user's time.

## File

```
docs/dev-log/YYYY-MM-DD_topic-slug.md
```

- `YYYY-MM-DD` — the date the work happened, not necessarily today. If the user says "yesterday" or
  "on Tuesday", resolve it.
- `topic-slug` — kebab-case, naming what the entry is *about*. Look at
  [`docs/dev-log/README.md`](../../../docs/dev-log/README.md) for the established style
  (`odrive-analog-torque-input`, `stability-testing-aluminium`, `thesis-meeting`).
- If a file for that date already exists and the new content belongs with it, **append to it** rather
  than creating a second file. Two entries for one date need distinct slugs.

## Content

Start with the H1, then write the entry. The doqs template is
[`doqs/templates/dev-log-entry.md`](../../../doqs/templates/dev-log-entry.md):

```markdown
# YYYY-MM-DD — Topic Title

## Goal

## Work Done

## Decisions Made

## Open Questions

- [ ]

## Next Steps

- [ ]
```

**Use the sections that carry content; drop the empty ones.** Historical entries are free-form prose
and bullet lists, and a short entry that is three bullets under `## Work Done` is perfectly normal.
Do not pad an entry to fill the template.

Write in the user's voice, keeping their numbers, units and terminology exactly. This is a lab
notebook — "spindle resonance at 700 Hz" is the content, and paraphrasing it into "a resonance was
observed" destroys the value.

## Photos and figures

Images go in `docs/dev-log/images/` named `YYYY-MM-DD-NN.ext`, numbered in the order they appear in
the entry, continuing from any images that date already has.

Reference them relatively so GitHub renders them:

```markdown
![](images/2026-08-21-01.png)
```

Add a line of context before or after each image saying what it shows — the converted historical
entries have no captions, and that is the one thing about them that is genuinely hard to read back.

## Related content

If the entry records a *choice* with lasting consequences, that belongs in
`docs/decisions/YYYY-MM-DD_topic.md` as well — link to it from the log entry.
If it records something that went wrong, add `docs/mistakes/YYYY-MM-DD_topic.md`.
If it discusses measurement data, cite the `relpath` from
[`measurement/data-index.csv`](../../../measurement/data-index.csv) so the run can be found later.

## Finish

1. Update the table in [`docs/dev-log/README.md`](../../../docs/dev-log/README.md) — add a row with
   the date, linked title, and image count. Keep it in date order.
2. Commit as `docs(dev-log): <short description>`.
3. Push to `main` unless the user asks for a PR. Log entries are additive and do not need review.

Confirm what you wrote and where, and give the user the path.
