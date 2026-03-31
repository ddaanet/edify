"""Validate backtick-wrapped paths in session.md task metadata.

Extracts paths from backtick content in task lines:
- Standalone paths: `plans/foo/design.md`
- Skill command arguments: `/design plans/foo/requirements.md`
- Inline metadata: `Plan: plans/foo/`

Rejects:
- Paths that don't exist on disk (warning)
- Paths under tmp/ (error)
- Paths containing plans/claude (sandbox temp pattern, error)
- Absolute paths outside project tree (error)
"""

import re
from pathlib import Path

from edify.validation.task_parsing import parse_task_line

# Known project directory prefixes that indicate a path
_PATH_PREFIXES = (
    "plans/",
    "src/",
    "agents/",
    "plugin/",
    "tests/",
    ".claude/",
)

# Skill commands that take a path argument
_SKILL_COMMAND_PATTERN = re.compile(
    r"^/(design|runbook|orchestrate|inline|deliverable-review|requirements"
    r"|review|brief)\s+(.+)"
)

# Extract all backtick-wrapped content
_BACKTICK_CONTENT = re.compile(r"`([^`]+)`")


def extract_paths_from_line(line: str) -> list[str]:
    """Extract filesystem paths from backtick content in a task line.

    Identifies paths via:
    - Known directory prefixes (plans/, src/, agents/, etc.)
    - Skill command arguments (/design plans/x, /runbook plans/x)
    - Content containing / that looks path-like

    Skips:
    - CLI tool names (_worktree, _recall, etc.)
    - Flags (--force, --fix)
    - Code references (no / in content)
    - Glob patterns containing *

    Returns:
        List of path strings found in backtick content.
    """
    paths = []

    for match in _BACKTICK_CONTENT.finditer(line):
        content = match.group(1).strip()

        # Skill command with path argument
        skill_match = _SKILL_COMMAND_PATTERN.match(content)
        if skill_match:
            path_arg = skill_match.group(2).strip()
            # Strip trailing tokens (e.g., "execute" in "/inline plans/x execute")
            parts = path_arg.split()
            if parts:
                candidate = parts[0]
                if "/" in candidate:
                    paths.append(candidate)
            continue

        # Skip non-path content
        if "/" not in content:
            continue
        if content.startswith("--"):
            continue
        if content.startswith("_"):
            continue
        if "*" in content:
            continue

        # Skip bare skill commands (/when, /how, /recall, /design, etc.)
        if re.match(r"^/[a-z][-a-z]*$", content):
            continue

        # Standalone path
        paths.append(content)

    return paths


def check_task_paths(
    lines: list[str],
    root: Path,
) -> list[str]:
    """Validate paths found in backtick content of task lines.

    Args:
        lines: File content as list of lines.
        root: Project root directory.

    Returns:
        List of error strings.
    """
    errors = []

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        task = parse_task_line(stripped, lineno=lineno)
        if not task:
            continue

        paths = extract_paths_from_line(stripped)
        for path_str in paths:
            # Reject tmp/ paths
            _tmp_segment = "/tmp/"  # noqa: S108
            if path_str.startswith("tmp/") or _tmp_segment in path_str:
                errors.append(
                    f"  line {lineno}: tmp/ path in task metadata: {path_str}"
                )
                continue

            # Reject plans/claude (sandbox temp directory pattern)
            if "plans/claude" in path_str:
                errors.append(
                    f"  line {lineno}: plans/claude reference in task metadata: "
                    f"{path_str}"
                )
                continue

            # Reject absolute paths (out-of-tree)
            if path_str.startswith("/"):
                errors.append(
                    f"  line {lineno}: absolute path in task metadata: {path_str}"
                )
                continue

            # Check existence (warning-level, but reported as error for now
            # since NFR-1 warnings are handled at validate() level)
            if not (root / path_str).exists():
                errors.append(
                    f"  line {lineno}: path not found in task metadata: {path_str}"
                )

    return errors
