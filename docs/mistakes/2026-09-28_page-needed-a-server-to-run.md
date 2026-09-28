# 2026-09-28 — The web page needed a server to run, and did not say so

**What happened:** The cutting force page, opened straight from disk in a local clone, said
"Calculating…" and never showed a result. The published page on GitHub Pages worked.

**Root cause:** The page loaded its model file `control_model.js` as a JavaScript module. Browsers
refuse to load a module for a page opened from disk (a `file://` address). The page script never
started, so the error handler that shows errors in the status line never ran either.

**Why it was missed:** The page was only tested through a local web server. The README said to
start one, but a page that looks like a single file is easy to double-click. On Windows, the
`python3` command in the README can also open the Microsoft Store instead of Python.

**Fix applied:** The model file is now a plain script that puts its functions on one object,
`ControlModel`. The page loads it with a plain script tag, which browsers allow from disk. The
check script reads the same object. The Pages workflow still adds the commit to the model address.

**Prevention rule:** A web page in this repository must work when it is opened straight from disk.
Load any second file with a plain script tag, not as a module, and test the page from disk before
you publish it.
