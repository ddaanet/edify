"""Tests for planstate aggregation module."""

import subprocess
import time
from pathlib import Path

from claudeutils.planstate.aggregation import (
    TreeInfo,
    _commits_since_handoff,
    _is_dirty,
    _latest_commit,
    _parse_worktree_list,
)


def test_parse_worktree_list_porcelain() -> None:
    """Parse git worktree list --porcelain output into TreeInfo objects."""
    porcelain = (
        "worktree /path/to/main\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /path/to/wt/slug\n"
        "branch refs/heads/slug\n"
        "\n"
    )

    result = _parse_worktree_list(porcelain)

    assert len(result) == 2
    assert result[0] == TreeInfo(
        path="/path/to/main", branch="main", is_main=True, slug=None
    )
    assert result[1] == TreeInfo(
        path="/path/to/wt/slug", branch="slug", is_main=False, slug="slug"
    )


def test_main_tree_detection() -> None:
    """Detect main tree (is_main=True) and worktree slugs."""
    porcelain = (
        "worktree /path/to/main\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /path/wt/worktree-1\n"
        "branch refs/heads/feature-1\n"
        "\n"
        "worktree /path/wt/worktree-2\n"
        "branch refs/heads/feature-2\n"
        "\n"
    )

    result = _parse_worktree_list(porcelain)

    assert len(result) == 3
    assert result[0].is_main is True
    assert result[0].slug is None
    assert result[1].is_main is False
    assert result[1].slug == "worktree-1"
    assert result[2].is_main is False
    assert result[2].slug == "worktree-2"


def test_dirty_state_detection(tmp_path: Path) -> None:
    """Detect dirty state via git status --porcelain."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo_str = str(repo_path)

    subprocess.run(
        ["git", "init"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )

    tracked_file = repo_path / "tracked.txt"
    tracked_file.write_text("initial content\n")
    subprocess.run(
        ["git", "add", "tracked.txt"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_str,
        check=True,
        capture_output=True,
    )

    # Clean state
    assert _is_dirty(repo_path) is False

    # Dirty: modify tracked file
    tracked_file.write_text("modified content\n")
    assert _is_dirty(repo_path) is True

    # Untracked files ignored
    tracked_file.write_text("initial content\n")
    (repo_path / "untracked.txt").write_text("untracked\n")
    assert _is_dirty(repo_path) is False


def test_git_metadata_helpers(tmp_path: Path) -> None:
    """Test _commits_since_handoff and _latest_commit."""
    repo_path = str(tmp_path)
    subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create session.md anchor
    session_file = Path(tmp_path) / "agents" / "session.md"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text("# Session\n")
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial session"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # 3 commits after session.md
    for i in range(3):
        test_file = Path(tmp_path) / f"file{i}.txt"
        test_file.write_text(f"Content {i}\n")
        subprocess.run(
            ["git", "add", f"file{i}.txt"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        time.sleep(0.01)
        subprocess.run(
            ["git", "commit", "-m", f"Test commit {i}"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    assert _commits_since_handoff(Path(repo_path)) == 3

    # No session.md in history → 0
    repo2 = str(tmp_path / "repo2")
    Path(repo2).mkdir()
    subprocess.run(["git", "init"], cwd=repo2, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo2,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo2,
        check=True,
        capture_output=True,
    )
    (Path(repo2) / "file.txt").write_text("Content\n")
    subprocess.run(
        ["git", "add", "file.txt"],
        cwd=repo2,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Test"],
        cwd=repo2,
        check=True,
        capture_output=True,
    )
    assert _commits_since_handoff(Path(repo2)) == 0

    # _latest_commit returns (subject, timestamp)
    latest = _latest_commit(Path(repo_path))
    assert isinstance(latest, tuple)
    assert len(latest) == 2
    assert latest[0] == "Test commit 2"
    assert isinstance(latest[1], int)
