"""Tests for remove_worktree_task function."""

import subprocess
from pathlib import Path

from claudeutils.worktree.session import remove_worktree_task


def test_remove_worktree_task_reads_branch_state(tmp_path: Path) -> None:
    """Remove_worktree_task reads branch state via git show."""
    # Set up main repo with Worktree Tasks entry
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)

    # Create initial commit with session.md containing Worktree Tasks
    agents_dir = repo / "agents"
    agents_dir.mkdir()
    main_session = """# Session

## Pending Tasks

- [ ] **Other Task** — `/design` | sonnet

## Worktree Tasks

- [ ] **Task A** → `task-a` — `/design` | sonnet
"""
    session_path = agents_dir / "session.md"
    session_path.write_text(main_session)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "main"],
        check=True,
        capture_output=True,
    )

    # Create branch where Task A is NOT in Pending Tasks (completed)
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "-b", "task-a"],
        check=True,
        capture_output=True,
    )
    branch_session = """# Session

## Pending Tasks

- [ ] **Other Task** — `/design` | sonnet
"""
    session_path.write_text(branch_session)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "branch"],
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "main"],
        check=True,
        capture_output=True,
    )

    # Call remove_worktree_task - it should read the branch state
    # The test verifies the function can be called and reads branch state
    # (actual removal logic tested in cycles 2.6 and 2.7)
    # For now, just verify it doesn't crash
    remove_worktree_task(session_path, "task-a", "task-a")


def test_remove_worktree_task_completed(tmp_path: Path) -> None:
    """Remove worktree task when task completed in branch."""
    # Set up main repo with Worktree Tasks entry
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)

    # Create initial commit with session.md containing Worktree Tasks
    agents_dir = repo / "agents"
    agents_dir.mkdir()
    main_session = """# Session

## Pending Tasks

- [ ] **Other Task** — `/design` | sonnet

## Worktree Tasks

- [ ] **Task A** → `task-a` — `/design` | sonnet
  - Plan: task-a
"""
    session_path = agents_dir / "session.md"
    session_path.write_text(main_session)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "main"],
        check=True,
        capture_output=True,
    )

    # Create branch where Task A is NOT in Pending Tasks (completed)
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "-b", "task-a"],
        check=True,
        capture_output=True,
    )
    branch_session = """# Session

## Pending Tasks

- [ ] **Other Task** — `/design` | sonnet
"""
    session_path.write_text(branch_session)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "branch"],
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "main"],
        check=True,
        capture_output=True,
    )

    # Call remove_worktree_task - should remove the entry
    remove_worktree_task(session_path, "task-a", "task-a")

    # Verify Task A removed from Worktree Tasks
    result = session_path.read_text()
    assert "## Worktree Tasks" not in result or "**Task A**" not in result
    # Other Task should still be in Pending Tasks
    assert "- [ ] **Other Task** — `/design` | sonnet" in result


def test_remove_worktree_task_still_pending(tmp_path: Path) -> None:
    """Keep worktree task when task still pending in branch."""
    # Set up main repo with Worktree Tasks entry
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)

    # Create initial commit with session.md containing Worktree Tasks
    agents_dir = repo / "agents"
    agents_dir.mkdir()
    main_session = """# Session

## Pending Tasks

- [ ] **Other Task** — `/design` | sonnet

## Worktree Tasks

- [ ] **Task A** → `task-a` — `/design` | sonnet
  - Plan: task-a
"""
    session_path = agents_dir / "session.md"
    session_path.write_text(main_session)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "main"],
        check=True,
        capture_output=True,
    )

    # Create branch where Task A IS still in Pending Tasks (not completed)
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "-b", "task-a"],
        check=True,
        capture_output=True,
    )
    branch_session = """# Session

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet
  - Plan: task-a
- [ ] **Other Task** — `/design` | sonnet
"""
    session_path.write_text(branch_session)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "branch"],
        check=True,
        capture_output=True,
    )

    # Switch back to main
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "main"],
        check=True,
        capture_output=True,
    )

    # Call remove_worktree_task - should NOT remove the entry
    remove_worktree_task(session_path, "task-a", "task-a")

    # Verify Task A still in Worktree Tasks
    result = session_path.read_text()
    assert "## Worktree Tasks" in result
    assert "- [ ] **Task A** → `task-a` — `/design` | sonnet" in result
    # Other Task should still be in Pending Tasks
    assert "- [ ] **Other Task** — `/design` | sonnet" in result
