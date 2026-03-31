"""Validate session.md structural conventions.

Checks:
- No task appears in both In-tree Tasks and Worktree Tasks
- Reference Files entries point to existing versioned files
- Command fields in task lines don't contain known anti-patterns
- Worktree markers correspond to actual git worktrees
"""

import re
from pathlib import Path

from edify.validation.session_commands import (
    check_command_presence,
    check_command_semantics,
    check_skill_allowlist,
)
from edify.validation.session_paths import check_task_paths
from edify.validation.session_worktrees import check_worktree_markers
from edify.validation.task_parsing import (
    TASK_PATTERN,
    VALID_CHECKBOXES,
    VALID_MODELS,
    parse_task_line,
)

SECTION_PATTERN = re.compile(r"^## (.+)$")
REF_FILE_PATTERN = re.compile(r"^- `([^`]+)`")

SECTION_ORDER = [
    "Completed This Session",
    "In-tree Tasks",
    "Pending Tasks",
    "Worktree Tasks",
    "Blockers / Gotchas",
    "Reference Files",
    "Next Steps",
]
ALLOWED_SECTIONS = set(SECTION_ORDER)


def check_status_line(lines: list[str]) -> list[str]:
    """Validate H1 header and status line format.

    Expected format:
    - Line 1: H1 header matching '# Session Handoff: YYYY-MM-DD'
    - Line 2: Blank line
    - Line 3: Bold status line '**Status:** <non-empty text>'

    Args:
        lines: File content as list of lines.

    Returns:
        List of error strings.
    """
    errors = []

    if len(lines) < 1:
        errors.append("  line 1: file too short, missing H1 header")
        return errors

    h1_pattern = re.compile(r"^# Session Handoff: \d{4}-\d{2}-\d{2}$")
    h1_line = lines[0].rstrip()

    if not h1_pattern.match(h1_line):
        if not h1_line.startswith("# Session Handoff:"):
            errors.append(
                "  line 1: H1 header must match '# Session Handoff: YYYY-MM-DD'"
            )
        else:
            errors.append("  line 1: H1 header date must be in YYYY-MM-DD format")

    if len(lines) < 2:
        errors.append("  line 2: expected blank line between H1 and status")
        return errors

    blank_line = lines[1].strip()
    if blank_line:
        errors.append("  line 2: expected blank line between H1 and status")

    if len(lines) < 3:
        errors.append("  line 3: expected status line with format '**Status:** <text>'")
        return errors

    status_line = lines[2].rstrip()
    status_pattern = re.compile(r"^\*\*Status:\*\*\s*(.*)$")
    status_match = status_pattern.match(status_line)

    if not status_match:
        if "Status:" in status_line and not status_line.startswith("**Status:**"):
            errors.append(
                "  line 3: status line must use bold formatting: **Status:** <text>"
            )
        else:
            errors.append(
                "  line 3: expected status line with format '**Status:** <text>'"
            )
    else:
        status_text = status_match.group(1).strip()
        if not status_text:
            errors.append("  line 3: status text cannot be empty")

    return errors


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
            tasks.append((lineno, m.group("name")))
    return tasks


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


def check_section_schema(lines: list[str]) -> list[str]:
    """Validate that session.md contains only allowed sections in correct order.

    Args:
        lines: File content as list of lines.

    Returns:
        List of error strings.
    """
    errors = []
    seen_sections = []
    seen_names = set()

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip()
        m = SECTION_PATTERN.match(stripped)
        if not m:
            continue

        section_name = m.group(1)

        if section_name not in ALLOWED_SECTIONS:
            errors.append(f"  line {i}: unrecognized section: {section_name}")
            continue

        if section_name in seen_names:
            errors.append(f"  line {i}: duplicate section: {section_name}")
            continue

        seen_names.add(section_name)
        seen_sections.append((i, section_name))

    for i, (lineno, name) in enumerate(seen_sections):
        if i == 0:
            continue

        prev_name = seen_sections[i - 1][1]
        prev_order = SECTION_ORDER.index(prev_name)
        curr_order = SECTION_ORDER.index(name)

        if curr_order < prev_order:
            errors.append(
                f"  line {lineno}: section out of order: {name} "
                f"should appear before {prev_name}"
            )

    return errors


def check_task_section_lines(lines: list[str]) -> list[str]:
    """Validate all lines in task sections parse as valid tasks.

    Task sections: In-tree Tasks, Worktree Tasks, Pending Tasks (legacy).

    For each non-blank, non-indented, non-HTML-comment line in these sections:
    1. Must parse via parse_task_line() → error if not
    2. Checkbox must be in VALID_CHECKBOXES → error if not
    3. Model metadata must be in VALID_MODELS or absent → error if invalid

    Args:
        lines: Raw file content lines (preserves indentation).

    Returns:
        List of error strings.
    """
    errors = []
    task_sections = {"In-tree Tasks", "Worktree Tasks", "Pending Tasks"}
    current_section = ""

    for lineno, raw_line in enumerate(lines, 1):
        stripped = raw_line.rstrip()
        m = SECTION_PATTERN.match(stripped)
        if m:
            current_section = m.group(1)
            continue

        if current_section not in task_sections:
            continue

        if not stripped:
            continue

        if stripped.startswith("  "):
            continue

        if stripped.startswith("<!--"):
            continue

        if stripped.startswith("#"):
            continue

        parsed = parse_task_line(stripped, lineno)
        if parsed is None:
            errors.append(
                f"  line {lineno}: invalid task line format in "
                f"{current_section}: {stripped}"
            )
            continue

        if parsed.checkbox not in VALID_CHECKBOXES:
            errors.append(
                f"  line {lineno}: invalid checkbox '{parsed.checkbox}' in "
                f"{current_section}: {stripped}"
            )

        _check_invalid_model_in_line(lineno, stripped, current_section, errors)

    return errors


def _check_invalid_model_in_line(
    lineno: int, line: str, section_name: str, errors: list[str]
) -> None:
    """Check if line contains invalid model tier in pipe-separated metadata."""
    if "—" not in line:
        return

    parts = line.split("—", 1)
    if len(parts) < 2:
        return

    metadata = parts[1]
    segments = [s.strip() for s in metadata.split("|")]

    for seg in segments[1:]:
        seg_lower = seg.lower().strip()
        if not seg_lower:
            continue

        # Multi-word segments are free-text description, not metadata
        if " " in seg_lower:
            continue

        if seg_lower == "restart":
            continue

        if re.match(r"^\d+(\.\d+)?$", seg_lower):
            continue

        if seg_lower not in VALID_MODELS:
            errors.append(
                f"  line {lineno}: invalid model '{seg}' in {section_name}: {line}"
            )


def validate(
    session_path: str,
    root: Path,
    worktree_slugs: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate session.md structure.

    Args:
        session_path: Path to session file (relative to root).
        root: Project root directory.
        worktree_slugs: Optional set of worktree slugs (for testing).
                       If None, queries git worktree list.

    Returns:
        Tuple of (errors, warnings). Errors fail the check; warnings
        are informational (orphaned worktrees).
    """
    full_path = root / session_path
    if not full_path.exists():
        return [], []

    with full_path.open() as f:
        lines = f.readlines()

    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_status_line(lines))
    errors.extend(check_section_schema(lines))

    stripped_lines = [line.rstrip() for line in lines]
    errors.extend(check_command_presence(stripped_lines))
    errors.extend(check_skill_allowlist(stripped_lines))
    errors.extend(check_command_semantics(stripped_lines))

    errors.extend(check_task_section_lines(lines))

    sections = parse_sections(lines)

    # Cross-section uniqueness
    pending = extract_section_tasks(sections.get("In-tree Tasks", []))
    worktree = extract_section_tasks(sections.get("Worktree Tasks", []))
    errors.extend(check_cross_section_uniqueness(pending, worktree))

    # Reference Files existence
    if "Reference Files" in sections:
        errors.extend(check_reference_files(sections["Reference Files"], root))

    # Backtick path validation in task metadata
    errors.extend(check_task_paths(stripped_lines, root))

    # Worktree marker validation
    marker_errors, marker_warnings = check_worktree_markers(
        stripped_lines, worktree_slugs=worktree_slugs
    )
    errors.extend(marker_errors)
    warnings.extend(marker_warnings)

    return errors, warnings
