"""Resolve the measurement data root.

Raw data lives on a Google Drive shared drive, not in Git. Nothing should
hardcode the absolute path: the drive letter differs per machine, the mount can
move, and the backend may change. Everything resolves through here instead.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "AQTUATOR_DATA_ROOT"

# Google Drive for Desktop mount on the project owner's machine.
DEFAULT = Path(r"H:/Shared drives/3 - Projects/2025-03 AQTUATOR/Development/7. Testing")


def data_root(required: bool = True) -> Path:
    """Return the measurement data root.

    Set AQTUATOR_DATA_ROOT to override the default mount. Pass required=False to
    get the path back without checking that it exists, which is what manifest
    tooling wants when it only needs to resolve relative paths.
    """
    root = Path(os.environ.get(ENV_VAR, DEFAULT))
    if required and not root.is_dir():
        raise FileNotFoundError(
            f"Measurement data root not found: {root}\n"
            f"Mount the shared drive via Google Drive for Desktop, or set {ENV_VAR} "
            f"to a local copy. See measurement/README.md."
        )
    return root


def resolve(relpath: str, required: bool = True) -> Path:
    """Resolve a manifest relpath against the data root."""
    return data_root(required) / relpath
