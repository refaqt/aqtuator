# Python

- Run package entry points from the repository root so config paths and imports resolve.
- Prefer installable packages (`pip install -e …`) over manipulating `sys.path`.
- Prefer the project's existing test runner; when none is documented, `python -m unittest discover` from the repo root is a reasonable default.
