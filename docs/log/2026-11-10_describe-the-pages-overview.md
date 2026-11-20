# 2026-11-10 — Short descriptions on the web pages overview

**Role(s):** engineering

## Goal

Niels asked to show the crash simulation results page on the overview page at
https://refaqt.github.io/aqtuator/. He also asked for a short text that explains what the pages are about.

## Work Done

- The crash results page was already linked from the overview page in the publish workflow. It stays there.
- Added one intro sentence that says what the pages are.
- Added one short line under each of the four page links. The line says what that page shows.

## Decisions Made

- None.

## Open Questions

- None.

## Next Steps

1. After the pull request is merged, open the overview page and check the text.

<details>
<summary>Technical notes</summary>

- Changed file: `.github/workflows/pages.yml`, in the `index.html` heredoc of the "Collect the site" step.
- The workflow runs only on pushes to `main` or by hand, so the live page does not change until the merge.

</details>
