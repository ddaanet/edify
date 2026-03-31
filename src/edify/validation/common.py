"""Shared validation utilities."""

from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Find project root by walking up from start directory.

    Searches for CLAUDE.md marker file to identify project root.

    Args:
        start: Starting directory to search from. Defaults to current working directory.

    Returns:
        Path to project root directory containing CLAUDE.md.

    Raises:
        FileNotFoundError: If CLAUDE.md is not found in any parent directory.
    """
    if start is None:
        start = Path.cwd()

    current = start.resolve()
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent

    msg = "Could not find project root (CLAUDE.md marker not found)"
    raise FileNotFoundError(msg)
