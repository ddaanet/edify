"""Path encoding utilities for Claude history directories."""

from pathlib import Path


def encode_project_path(project_dir: str) -> str:
    """Convert absolute path to Claude history encoding format."""
    if not Path(project_dir).is_absolute():
        msg = "project_dir must be an absolute path"
        raise ValueError(msg)
    # Handle root path specially
    if project_dir == "/":
        return "-"
    return project_dir.rstrip("/").replace("/", "-")


def get_project_history_dir(project_dir: str) -> Path:
    """Return Path to ~/.claude/projects/[ENCODED-PATH]/."""
    return Path.home() / ".claude" / "projects" / encode_project_path(project_dir)
