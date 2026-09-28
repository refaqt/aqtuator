# 2026-09-28 — The web page ran against an old, cached model file

**What happened:** After the update that added the controller force and power, the published
cutting force page said "Calculating…" and never showed a result. The files on GitHub Pages were
correct. Locally the page worked.

**Root cause:** The page is two files: `index.html` and the model file `control_model.js`. GitHub
Pages lets the browser keep each file for 10 minutes. The browser fetched the new `index.html`
but used the old `control_model.js` from its cache. The new page calls `steadyState`, which the
old model does not have. That error stopped the update, and nothing caught it, so the status line
kept its first text, "Calculating…".

**Why it was missed:** The page was only tested from a fresh local copy, where both files are
always new. The page also had no place to show an error.

**Fix applied:**

- The Pages workflow adds the commit to the model file address (`control_model.js?v=<commit>`),
  for both web pages. A new page now always fetches its own model file.
- The page catches any error during the update and shows it in the status line.

**Prevention rule:** A web page that loads a second file must load it under an address that
changes with each release. Any error during a calculation must show on the page, never only in
the browser console.
