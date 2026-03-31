"""Validate task name uniqueness in session.md.

Checks:
- Task name format: - [ ] **Task Name** — description
- Uniqueness across session.md
- Disjointness with learning keys
- Git history search for new tasks only (using git log -S)
- Merge commit handling (compare against all parents, constraint C-1)
"""

import re
import subprocess
import sys
from pathlib import Path

from edify.validation.task_parsing import TASK_PATTERN

LEARNING_PATTERN = re.compile(r"^## (.+)$")
H1_PATTERN = re.compile(r"^# ")


def validate_task_name_format(name: str) -> list[str]:
    """Validate task name format.

    Args:
        name: Task name to validate.

    Returns:
        List of error strings. Empty list if valid.
    """
    errors = []

    # Check for empty or whitespace-only
    if not name.strip():
        errors.append("empty or whitespace-only")
        return errors

    # Check for forbidden characters
    if not re.fullmatch(r"[a-zA-Z0-9 .\-]+", name):
        # Find first forbidden character
        for char in name:
            if not re.match(r"[a-zA-Z0-9 .\-]", char):
                errors.append(f"contains forbidden character '{char}'")
                break

    # Check length
    if len(name) > 25:
        errors.append(f"exceeds 25 character limit ({len(name)} chars)")

    return errors


def extract_task_names(lines: list[str]) -> list[tuple[int, str]]:
    """Extract (line_number, task_name) pairs from task lines.

    Args:
        lines: List of file lines.

    Returns:
        List of (line_number, task_name) tuples.
    """
    tasks = []
    for i, line in enumerate(lines, 1):
        m = TASK_PATTERN.match(line.strip())
        if m:
            tasks.append((i, m.group("name")))
    return tasks


def extract_learning_keys(lines: list[str]) -> set[str]:
    """Extract learning keys from ## headers (exclude H1 document title).

    Args:
        lines: List of file lines.

    Returns:
        Set of learning key strings (lowercase).
    """
    keys = set()
    h1_seen = False
    for line in lines:
        stripped = line.strip()
        # Skip H1 lines (document title)
        if H1_PATTERN.match(stripped):
            h1_seen = True
            continue
        # Only process ## headers after we've seen H1
        if h1_seen:
            m = LEARNING_PATTERN.match(stripped)
            if m:
                keys.add(m.group(1).lower())
    return keys


def get_session_from_commit(commit_ref: str, session_path: Path) -> list[str]:
    """Get session.md content from a specific commit.

    Args:
        commit_ref: Git commit reference (e.g., "HEAD", "MERGE_HEAD").
        session_path: Path to session file in git.

    Returns:
        List of file lines from commit. Empty list if file not found in commit.
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_ref}:{session_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []


def get_merge_parents() -> tuple[str, str] | None:
    """Get parent commits for current merge. Returns (parent1, parent2) or None.

    Returns:
        Tuple of (HEAD, MERGE_HEAD) if in a merge, None otherwise.

    Raises:
        subprocess.CalledProcessError: If git commands fail unexpectedly.
    """
    try:
        # Check if we're in a merge
        result = subprocess.run(
            ["git", "rev-parse", "MERGE_HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None  # Not in a merge

        merge_head = result.stdout.strip()

        # Get HEAD
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        head = result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    else:
        return (head, merge_head)


def get_staged_session(session_path: Path) -> list[str]:
    """Get staged session.md content.

    Args:
        session_path: Path to session file.

    Returns:
        List of staged file lines. Empty list if not staged.
    """
    try:
        result = subprocess.run(
            ["git", "show", f":{session_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []


def get_new_tasks(session_path: Path) -> list[str]:
    """Get task names that are new (not present in any parent).

    For regular commits: compares against HEAD.
    For merge commits: compares against both parents.

    A task is "new" only if present in current session.md but not present in
    either parent (C-1).

    Args:
        session_path: Path to session file.

    Returns:
        List of new task names.

    Raises:
        SystemExit: On octopus merge detection.
    """
    try:
        parents = get_merge_parents()

        # Get current (staged) task list
        current_lines = get_staged_session(session_path)
        current_tasks = {name for _, name in extract_task_names(current_lines)}

        if parents is None:
            # Regular commit - compare against HEAD
            parent_lines = get_session_from_commit("HEAD", session_path)
            parent_tasks = {name for _, name in extract_task_names(parent_lines)}
            new_tasks = current_tasks - parent_tasks
            return list(new_tasks)

        # Merge commit - check both parents (C-1 constraint)
        parent1, parent2 = parents

        # Check if we have more than 2 parents (octopus merge)
        result = subprocess.run(
            ["git", "rev-list", "--parents", "--max-count=1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        parent_count = len(result.stdout.strip().split()) - 1
        if parent_count > 2:
            print(
                f"Error: Octopus merge detected ({parent_count} parents). "
                "Task validation logic needs augmentation for n-way merges.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Get task lists from both parents
        p1_lines = get_session_from_commit(parent1, session_path)
        p1_tasks = {name for _, name in extract_task_names(p1_lines)}

        p2_lines = get_session_from_commit(parent2, session_path)
        p2_tasks = {name for _, name in extract_task_names(p2_lines)}

        # Combine parent task lists (C-1: task is new only if absent from ALL parents)
        all_parent_tasks = p1_tasks | p2_tasks

        # A task is "new" if present in current but not in either parent
        new_tasks = current_tasks - all_parent_tasks

        return list(new_tasks)

    except subprocess.CalledProcessError:
        # Not in a git repo or no staged changes
        return []


def check_history(task_name: str) -> bool:
    """Check if task name exists in git history using git log -S.

    Case-insensitive search using --regexp-ignore-case.

    Args:
        task_name: Task name to search for.

    Returns:
        True if task name found in history, False otherwise.
    """
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "-S",
                task_name,
                "--regexp-ignore-case",
                "--format=%H",
                "--",
                "agents/session.md",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def validate(session_path: str, learnings_path: str, root: Path) -> list[str]:
    """Validate task names. Returns list of error strings.

    Args:
        session_path: Path to session file (relative to root).
        learnings_path: Path to learnings file (relative to root).
        root: Project root directory.

    Returns:
        List of error messages. Empty list if no errors found.
    """
    full_session_path = root / session_path
    full_learnings_path = root / learnings_path

    errors: list[str] = []

    # Read session.md
    try:
        with full_session_path.open() as f:
            session_lines = f.readlines()
    except FileNotFoundError:
        return []

    # Read learnings.md
    try:
        with full_learnings_path.open() as f:
            learning_lines = f.readlines()
    except FileNotFoundError:
        learning_lines = []

    # Extract task names and learning keys
    tasks = extract_task_names(session_lines)
    learning_keys = extract_learning_keys(learning_lines)

    # Check format of each task name
    for lineno, task_name in tasks:
        errors.extend(
            f"  line {lineno}: Task '{task_name}': {msg}"
            for msg in validate_task_name_format(task_name)
        )

    # Check uniqueness within session.md
    seen: dict[str, int] = {}
    for lineno, task_name in tasks:
        key = task_name.lower()
        if key in seen:
            errors.append(
                f"  line {lineno}: duplicate task name (first at line {seen[key]}): "
                f"**{task_name}**"
            )
        else:
            seen[key] = lineno

    # Check disjointness with learning keys
    for lineno, task_name in tasks:
        key = task_name.lower()
        if key in learning_keys:
            errors.append(
                f"  line {lineno}: task name conflicts with learning key: "
                f"**{task_name}**"
            )

    # Check git history for new tasks only
    new_tasks = get_new_tasks(full_session_path)
    errors.extend(
        f"  new task name exists in git history: **{task_name}**"
        for task_name in new_tasks
        if check_history(task_name)
    )

    return errors
