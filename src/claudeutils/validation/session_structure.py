"""Validate session.md structural conventions.

Checks:
- Worktree Tasks entries have → slug format
- No task appears in both In-tree Tasks and Worktree Tasks
- Reference Files entries point to existing versioned files
"""

import re
from pathlib import Path

TASK_PATTERN = re.compile(r"^- \[[ x>!✗–]\] \*\*(.+?)\*\*")  # noqa: RUF001
TERMINAL_STATUS_PATTERN = re.compile(r"^- \[[!✗–]\] ")  # noqa: RUF001
SECTION_PATTERN = re.compile(r"^## (.+)$")
REF_FILE_PATTERN = re.compile(r"^- `([^`]+)`")


def parse_sections(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    """Parse session.md into named sections.

    Args:
        lines: File content as list of lines.

    Returns:
        Dict mapping section name to list of (line_number, line_text) pairs.
    """
    sections: dict[str, list[tuple[int, str]]] = {}
    current_section = ""
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m = SECTION_PATTERN.match(stripped)
        if m:
            current_section = m.group(1)
            sections.setdefault(current_section, [])
            continue
        if current_section:
            sections.setdefault(current_section, []).append((i, stripped))
    return sections


def extract_section_tasks(
    section_lines: list[tuple[int, str]],
) -> list[tuple[int, str]]:
    """Extract task names from section lines.

    Args:
        section_lines: List of (line_number, line_text) pairs from a section.

    Returns:
        List of (line_number, task_name) pairs.
    """
    tasks = []
    for lineno, line in section_lines:
        m = TASK_PATTERN.match(line)
        if m:
            tasks.append((lineno, m.group(1)))
    return tasks


def check_worktree_format(
    section_lines: list[tuple[int, str]],
) -> list[str]:
    """Verify Worktree Tasks entries have → slug format.

    Args:
        section_lines: Lines from Worktree Tasks section.

    Returns:
        List of error strings.
    """
    errors = []
    for lineno, line in section_lines:
        task_m = TASK_PATTERN.match(line)
        if task_m and "\u2192" not in line and not TERMINAL_STATUS_PATTERN.match(line):
            errors.append(
                f"  line {lineno}: worktree task missing \u2192 slug: "
                f"**{task_m.group(1)}**"
            )
    return errors


def check_cross_section_uniqueness(
    pending_tasks: list[tuple[int, str]],
    worktree_tasks: list[tuple[int, str]],
) -> list[str]:
    """Check no task appears in both In-tree and Worktree sections.

    Args:
        pending_tasks: Tasks from In-tree Tasks section.
        worktree_tasks: Tasks from Worktree Tasks section.

    Returns:
        List of error strings.
    """
    errors = []
    pending_names = {name.lower(): (lineno, name) for lineno, name in pending_tasks}
    for lineno, name in worktree_tasks:
        key = name.lower()
        if key in pending_names:
            p_lineno, _ = pending_names[key]
            errors.append(
                f"  line {lineno}: task in both In-tree (line {p_lineno}) "
                f"and Worktree: **{name}**"
            )
    return errors


def check_reference_files(
    section_lines: list[tuple[int, str]], root: Path
) -> list[str]:
    """Verify Reference Files entries point to existing files.

    Args:
        section_lines: Lines from Reference Files section.
        root: Project root directory.

    Returns:
        List of error strings.
    """
    errors = []
    for lineno, line in section_lines:
        m = REF_FILE_PATTERN.match(line)
        if m:
            ref_path = m.group(1)
            if not (root / ref_path).exists():
                errors.append(f"  line {lineno}: reference file not found: {ref_path}")
    return errors


def validate(session_path: str, root: Path) -> list[str]:
    """Validate session.md structure.

    Args:
        session_path: Path to session file (relative to root).
        root: Project root directory.

    Returns:
        List of error strings. Empty if no errors.
    """
    full_path = root / session_path
    if not full_path.exists():
        return []

    with full_path.open() as f:
        lines = f.readlines()

    sections = parse_sections(lines)
    errors = []

    # Worktree task format
    if "Worktree Tasks" in sections:
        errors.extend(check_worktree_format(sections["Worktree Tasks"]))

    # Cross-section uniqueness
    pending = extract_section_tasks(sections.get("In-tree Tasks", []))
    worktree = extract_section_tasks(sections.get("Worktree Tasks", []))
    errors.extend(check_cross_section_uniqueness(pending, worktree))

    # Reference Files existence
    if "Reference Files" in sections:
        errors.extend(check_reference_files(sections["Reference Files"], root))

    return errors
