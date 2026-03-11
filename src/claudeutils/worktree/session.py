"""Session.md parsing and editing utilities."""

import re
from dataclasses import dataclass
from pathlib import Path

from claudeutils.validation.task_parsing import TASK_PATTERN


@dataclass
class TaskBlock:
    """Task block from session.md."""

    name: str  # Task name extracted from markdown
    lines: list[str]  # All lines (task line + continuation lines)
    section: str  # Section name: "In-tree Tasks" or "Worktree Tasks"


def extract_task_blocks(content: str, section: str | None = None) -> list[TaskBlock]:
    """Extract task blocks from session.md content.

    Args:
        content: Session.md file content
        section: Optional section name filter ("In-tree Tasks", "Worktree Tasks")

    Returns:
        List of TaskBlock instances
    """
    lines = content.split("\n")
    blocks = []
    current_section = None
    i = 0
    while i < len(lines):
        line = lines[i]

        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()
            i += 1
            continue

        # Match task lines
        match = TASK_PATTERN.match(line)
        if match:
            task_name = match.group("name")
            task_lines = [line]

            # Collect continuation lines (indented lines following the task)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # Stop at next task, next section, or blank line
                if (
                    TASK_PATTERN.match(next_line)
                    or next_line.startswith("## ")
                    or not next_line.strip()
                ):
                    break
                # Stop at non-indented content line
                if next_line and next_line[0].isspace():
                    task_lines.append(next_line)
                    j += 1
                else:
                    break

            # Filter by section if requested
            if section is None or current_section == section:
                blocks.append(
                    TaskBlock(
                        name=task_name,
                        lines=task_lines,
                        section=current_section or "",
                    )
                )

            i = j
            continue

        i += 1

    return blocks


def extract_blockers(content: str) -> list[list[str]]:
    """Extract blocker items from Blockers / Gotchas section.

    Returns list of blocker groups. Each group is a list of strings: first
    element is the bullet line, remaining are continuation lines.
    """
    bounds = find_section_bounds(content, "Blockers / Gotchas")
    if bounds is None:
        return []

    lines = content.split("\n")
    section_lines = lines[bounds[0] + 1 : bounds[1]]
    blockers: list[list[str]] = []
    current: list[str] = []

    for line in section_lines:
        if line.startswith("- "):
            if current:
                blockers.append(current)
            current = [line]
        elif line.startswith("  ") and current:
            current.append(line)
        elif not line.strip():
            # Blank line ends current blocker if one is in progress
            if current:
                blockers.append(current)
                current = []
        elif current:
            current.append(line)

    if current:
        blockers.append(current)

    return blockers


def find_section_bounds(content: str, header: str) -> tuple[int, int] | None:
    """Find line bounds for a section header.

    Args:
        content: Session.md file content
        header: Section header name (without "## " prefix)

    Returns:
        (start_line, end_line) tuple or None if not found
        start_line: Index of "## header" line
        end_line: Index of line before next "## " or EOF
    """
    lines = content.split("\n")
    start_idx = None

    for i, line in enumerate(lines):
        if line == f"## {header}":
            start_idx = i
            break

    if start_idx is None:
        return None

    # Find end: next "## " header or EOF (default to len(lines) if no next section)
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break

    return (start_idx, end_idx)


def add_slug_marker(session_path: Path, task_name: str, slug: str) -> None:
    """Add slug marker inline to task in Worktree Tasks section.

    Args:
        session_path: Path to session.md file
        task_name: Task name to add marker to
        slug: Worktree slug to append as marker

    Raises:
        ValueError: If task_name not found in Worktree Tasks
    """
    content = session_path.read_text()

    # Find task in Worktree Tasks section
    worktree_blocks = extract_task_blocks(content, section="Worktree Tasks")
    task_block = next((b for b in worktree_blocks if b.name == task_name), None)

    if task_block is None:
        msg = f"Task '{task_name}' not found in Worktree Tasks"
        raise ValueError(msg)

    # Find task block within Worktree Tasks section only
    lines = content.split("\n")
    bounds = find_section_bounds(content, "Worktree Tasks")
    section_start, section_end = bounds or (0, len(lines))

    task_start_idx = None
    for i in range(section_start, section_end):
        if lines[i] == task_block.lines[0]:
            task_start_idx = i
            break

    if task_start_idx is None:
        msg = f"Task '{task_name}' block found but could not locate in file content"
        raise ValueError(msg)

    # Add slug marker to first line (after ** but before —)
    first_line = task_block.lines[0]
    modified_first_line = re.sub(r"(\*\*[^*]+\*\*)", f"\\1 → `{slug}`", first_line)
    lines[task_start_idx] = modified_first_line

    session_path.write_text("\n".join(lines))


def remove_slug_marker(session_path: Path, slug: str) -> None:
    """Remove slug marker inline from task in Worktree Tasks section.

    Args:
        session_path: Path to session.md file
        slug: Worktree slug to find and remove

    No-op if slug not found.
    """
    content = session_path.read_text()
    lines = content.split("\n")

    # Find line containing the slug marker within Worktree Tasks section only
    pattern = rf" → `{re.escape(slug)}`"
    bounds = find_section_bounds(content, "Worktree Tasks")
    section_start, section_end = bounds or (0, len(lines))
    modified = False

    for i in range(section_start, section_end):
        if re.search(pattern, lines[i]):
            lines[i] = re.sub(pattern, "", lines[i])
            modified = True
            break

    if modified:
        session_path.write_text("\n".join(lines))


def _extract_plan_from_block(block: TaskBlock) -> str | None:
    """Extract plan name from a task block.

    Checks continuation lines for 'Plan: <name>' first, falls back to extracting
    from backtick command paths.
    """
    block_text = "\n".join(block.lines)

    # Primary: "Plan: <name>" in continuation lines
    if m := re.search(r"[Pp]lan:\s*(\S+)", block_text):
        return m.group(1)

    # Fallback: plans/<name>/ in backtick command
    if m := re.search(r"plans/([^/\s`]+)/", block_text):
        return m.group(1)

    # Fallback: /orchestrate <name> in backtick command
    if m := re.search(r"/orchestrate\s+([^`|\s]+)", block_text):
        return m.group(1)

    return None


def extract_plan_order(content: str) -> dict[str, int]:
    """Extract plan ordering from session.md task order.

    Returns mapping of plan_name → position based on document order. Position is
    0-indexed sequential for tasks that reference plans.
    """
    blocks = extract_task_blocks(content)
    order: dict[str, int] = {}
    position = 0

    for block in blocks:
        plan_name = _extract_plan_from_block(block)
        if plan_name and plan_name not in order:
            order[plan_name] = position
            position += 1

    return order


def _filter_section(
    content: str, section_name: str, task_name: str, plan_dir: str | None
) -> str:
    """Filter section entries by task_name or plan_dir match."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    if not (match := re.search(pattern, content, re.DOTALL)):
        return ""

    def is_relevant(entry: str) -> bool:
        lo = entry.lower()
        return task_name.lower() in lo or bool(plan_dir and plan_dir.lower() in lo)

    lines = []
    include = False
    for line in match.group(1).split("\n"):
        if line.startswith("- "):
            include = is_relevant(line[2:].strip())
            if include:
                lines.append(line)
        elif include and line.strip():
            lines.append(line)
    return f"## {section_name}\n\n" + "\n".join(lines) + "\n" if lines else ""


def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Filter session.md to task_name with relevant context sections."""
    content = Path(session_md_path).read_text()
    blocks = extract_task_blocks(content, section="Worktree Tasks")
    task_block = next((b for b in blocks if b.name == task_name), None)
    if not task_block:
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)
    task_lines = list(task_block.lines)
    # Strip → `slug` marker from first line
    task_lines[0] = re.sub(r" → `[^`]+`", "", task_lines[0])
    task_lines_str = "\n".join(task_lines)
    plan_dir = (
        m.group(1) if (m := re.search(r"[Pp]lan:\s*(\S+)", task_lines_str)) else None
    )
    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## In-tree Tasks\n\n{task_lines_str}\n"
    )
    for section in ["Blockers / Gotchas", "Reference Files"]:
        if filtered := _filter_section(content, section, task_name, plan_dir):
            result += f"\n{filtered}"
    return result
