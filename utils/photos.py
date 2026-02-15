"""
local photo library helpers
"""

from pathlib import Path

from config import photos_dir

_SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def load_photos() -> list[str]:
    """
    Return a sorted list of absolute paths to all supported image files
    in the configured photos directory.

    Returns an empty list (rather than raising) if the directory does not
    exist or contains no matching files, so callers can degrade gracefully.
    """
    root = Path(photos_dir)

    if not root.is_dir():
        print(f"[photos] Warning: photos_dir does not exist: {root}")
        return []

    paths = sorted(
        str(p)
        for p in root.iterdir()
        if p.is_file() and p.suffix.lower() in _SUPPORTED_EXTENSIONS
    )

    if not paths:
        print(f"[photos] Warning: no supported images found in {root}")

    return paths