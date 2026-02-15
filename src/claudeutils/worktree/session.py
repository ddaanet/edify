"""Session.md parsing and editing utilities."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TaskBlock:
    """Task block from session.md."""

    name: str  # Task name extracted from markdown
    lines: list[str]  # All lines (task line + continuation lines)
    section: str  # Section name: "Pending Tasks" or "Worktree Tasks"


def extract_task_blocks(content: str, section: str | None = None) -> list[TaskBlock]:
    """Extract task blocks from session.md content.

    Args:
        content: Session.md file content
        section: Optional section name filter ("Pending Tasks", "Worktree Tasks")

    Returns:
        List of TaskBlock instances
    """
    lines = content.split("\n")
    blocks = []
    current_section = None
    task_pattern = re.compile(r"^- \[[ x>]\] \*\*(.+?)\*\*")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()
            i += 1
            continue

        # Match task lines
        match = task_pattern.match(line)
        if match:
            task_name = match.group(1)
            task_lines = [line]

            # Collect continuation lines (indented lines following the task)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # Stop at next task, next section, or blank line
                if (
                    task_pattern.match(next_line)
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


def move_task_to_worktree(session_path: Path, task_name: str, slug: str) -> None:
    """Move task from Pending Tasks to Worktree Tasks section.

    Args:
        session_path: Path to session.md file
        task_name: Task name to move
        slug: Worktree slug to append as marker

    Raises:
        ValueError: If task_name not found in Pending Tasks
    """
    content = session_path.read_text()
    lines = content.split("\n")

    # Find and extract task from Pending Tasks
    pending_blocks = extract_task_blocks(content, section="Pending Tasks")
    task_block = None
    for block in pending_blocks:
        if block.name == task_name:
            task_block = block
            break

    if task_block is None:
        msg = f"Task '{task_name}' not found in Pending Tasks"
        raise ValueError(msg)

    # Find the task block in the lines list to remove it
    task_start_idx = None
    task_end_idx = None
    for i, line in enumerate(lines):
        if line in task_block.lines:
            task_start_idx = i
            task_end_idx = i + len(task_block.lines)
            break

    # Add slug marker to first line
    first_line = task_block.lines[0]
    # Insert → `slug` after ** but before —
    modified_first_line = re.sub(r"(\*\*[^*]+\*\*)", f"\\1 → `{slug}`", first_line)
    modified_lines = [modified_first_line, *task_block.lines[1:]]

    # Remove task from Pending Tasks section
    del lines[task_start_idx:task_end_idx]

    # Find or create Worktree Tasks section
    worktree_bounds = find_section_bounds("\n".join(lines), "Worktree Tasks")
    if worktree_bounds is None:
        # Create Worktree Tasks section after Pending Tasks
        pending_bounds = find_section_bounds("\n".join(lines), "Pending Tasks")
        insert_idx = pending_bounds[1] if pending_bounds else len(lines)
        lines.insert(insert_idx, "")
        lines.insert(insert_idx + 1, "## Worktree Tasks")
        lines.insert(insert_idx + 2, "")
        insert_point = insert_idx + 3
    else:
        insert_point = worktree_bounds[1]

    # Insert task block at the end of Worktree Tasks section
    for line in modified_lines:
        lines.insert(insert_point, line)
        insert_point += 1

    session_path.write_text("\n".join(lines))
