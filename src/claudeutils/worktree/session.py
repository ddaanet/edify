"""Session.md parsing and editing utilities."""

import re
from dataclasses import dataclass
from pathlib import Path

from claudeutils.worktree.git_ops import _git


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

    # Find and extract task from Pending Tasks (or check if already in Worktree Tasks)
    pending_blocks = extract_task_blocks(content, section="Pending Tasks")
    task_block = next((b for b in pending_blocks if b.name == task_name), None)

    if task_block is None:
        worktree_blocks = extract_task_blocks(content, section="Worktree Tasks")
        if any(b.name == task_name for b in worktree_blocks):
            return
        msg = f"Task '{task_name}' not found in Pending Tasks or Worktree Tasks"
        raise ValueError(msg)

    # Find the task block in the lines list to remove it
    task_start_idx = None
    task_end_idx = None
    for i, line in enumerate(lines):
        if line == task_block.lines[0]:
            task_start_idx = i
            task_end_idx = i + len(task_block.lines)
            break

    if task_start_idx is None:
        msg = f"Task '{task_name}' block found but could not locate in file content"
        raise ValueError(msg)

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
        lines.insert(insert_idx, "## Worktree Tasks")
        lines.insert(insert_idx + 1, "")
        insert_point = insert_idx + 2
    else:
        insert_point = worktree_bounds[1]

    # Insert task block at the end of Worktree Tasks section
    for line in modified_lines:
        lines.insert(insert_point, line)
        insert_point += 1
    # Add blank line after task block
    lines.insert(insert_point, "")

    session_path.write_text("\n".join(lines))


def _find_git_root(start_path: Path) -> Path:
    """Find git repo root by searching for .git directory."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    msg = f"No git repository found from {start_path}"
    raise ValueError(msg)


def _task_is_in_pending_section(
    task_name: str, worktree_branch: str, git_root: Path
) -> bool:
    """Check if task is in worktree branch's Pending Tasks section."""
    branch_content = _git(
        "-C",
        str(git_root),
        "show",
        f"{worktree_branch}:agents/session.md",
        check=False,
    )
    if not branch_content:
        return False

    branch_blocks = extract_task_blocks(branch_content, section="Pending Tasks")
    return any(block.name == task_name for block in branch_blocks)


def remove_worktree_task(session_path: Path, slug: str, worktree_branch: str) -> None:
    """Remove task from Worktree Tasks section based on branch completion state.

    Args:
        session_path: Path to session.md file
        slug: Worktree slug to find task by
        worktree_branch: Git branch name to check task completion state

    Reads the worktree branch's session.md via git show to determine if the task
    was completed (no longer in branch's Pending Tasks). If completed, removes the
    entry from Worktree Tasks. If still pending, keeps the entry.
    """
    content = session_path.read_text()

    # Find task in Worktree Tasks by slug marker
    worktree_blocks = extract_task_blocks(content, section="Worktree Tasks")
    task_block = None
    for block in worktree_blocks:
        if f"→ `{slug}`" in block.lines[0]:
            task_block = block
            break

    if task_block is None:
        return

    # Extract task name
    match = re.match(r"^- \[[ x>]\] \*\*(.+?)\*\*", task_block.lines[0])
    if not match:
        return
    task_name = match.group(1)

    # Check if task still pending in branch
    git_root = _find_git_root(session_path.parent)
    if _task_is_in_pending_section(task_name, worktree_branch, git_root):
        return

    # Task completed, remove from Worktree Tasks
    # Find task block starting line by matching first line
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line == task_block.lines[0]:
            task_end_idx = i + len(task_block.lines)
            del lines[i:task_end_idx]
            break

    session_path.write_text("\n".join(lines))


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
    blocks = extract_task_blocks(content, section="Pending Tasks")
    task_block = next((b for b in blocks if b.name == task_name), None)
    if not task_block:
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)
    task_lines_str = "\n".join(task_block.lines)
    plan_dir = (
        m.group(1) if (m := re.search(r"[Pp]lan:\s*(\S+)", task_lines_str)) else None
    )
    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n{task_lines_str}\n"
    )
    for section in ["Blockers / Gotchas", "Reference Files"]:
        if filtered := _filter_section(content, section, task_name, plan_dir):
            result += f"\n{filtered}"
    return result
