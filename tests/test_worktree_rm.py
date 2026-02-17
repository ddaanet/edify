"""Tests for worktree rm subcommand."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.utils import _is_merge_commit
from tests.fixtures_worktree import _branch_exists, _create_worktree


def test_rm_basic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Removes worktree directory and branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "removed" in result.output.lower()


def test_rm_dirty_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Warns about uncommitted changes but proceeds with removal."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    (worktree_path / "newfile.txt").write_text("uncommitted")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "uncommitted" in result.output.lower() or "warning" in result.output.lower()


def test_rm_branch_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Cleans up branch when directory removed externally."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert _branch_exists("test-feature")

    subprocess.run(["rm", "-rf", str(worktree_path)], check=True, capture_output=True)
    assert not worktree_path.exists()
    assert _branch_exists("test-feature")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 0
    assert not _branch_exists("test-feature")
    assert (
        "error" not in result.output.lower()
        or "no such file" not in result.output.lower()
    )


def test_rm_detects_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects merge commit via parent count."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Root commit (0 parents) is not a merge commit
    assert not _is_merge_commit()

    # Normal commit (1 parent) is not a merge commit
    (repo_path / "second.txt").write_text("second")
    subprocess.run(["git", "add", "second.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Second commit"], check=True, capture_output=True
    )
    assert not _is_merge_commit()

    # Create another branch and merge to create merge commit
    subprocess.run(
        ["git", "checkout", "-b", "feature"], check=True, capture_output=True
    )
    (repo_path / "feature.txt").write_text("feature content")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Feature commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "feature"], check=True, capture_output=True
    )

    # Merge commit has 2 parents
    assert _is_merge_commit()


def test_rm_amends_merge_commit_when_session_modified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """When rm() is called on merge commit, amends session.md if modified."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create a worktree task entry in session.md
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `test-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # Create test-feature branch with a commit, then merge it into main.
    # This makes test-feature a parent of the merge commit — realistic workflow.
    subprocess.run(
        ["git", "checkout", "-b", "test-feature"], check=True, capture_output=True
    )
    (repo_path / "feature.txt").write_text("feature content")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Feature commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "test-feature"], check=True, capture_output=True
    )

    assert _is_merge_commit()
    merge_msg = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Create worktree (branch already exists, worktree add attaches to it)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 0

    # Verify still on a merge commit (2+ parents)
    assert _is_merge_commit()

    # Verify commit message unchanged (--no-edit preserves message)
    current_msg = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert current_msg == merge_msg

    # Verify session.md was amended into HEAD commit
    session_content = subprocess.run(
        ["git", "show", "HEAD:agents/session.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "test-feature" not in session_content


def test_rm_does_not_amend_on_normal_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """When HEAD is a normal commit (not merge), rm() must NOT amend."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `test-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # HEAD is a normal commit (1 parent, not merge)
    assert not _is_merge_commit()

    # Create worktree and remove it
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])
    assert result.exit_code == 0

    # If amend happened incorrectly, the task removal would be in HEAD commit
    # Instead, verify session.md in HEAD still has the task (was NOT amended in)
    session_in_head = subprocess.run(
        ["git", "show", "HEAD:agents/session.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    # If no amend, HEAD:agents/session.md still contains the task
    # (the modification from remove_worktree_task is only in working tree)
    assert "Worktree Tasks" in session_in_head


def test_rm_output_indicates_amend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Output message indicates when merge commit was amended."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `test-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # Create test-feature as the merged branch (parent of merge commit)
    subprocess.run(
        ["git", "checkout", "-b", "test-feature"], check=True, capture_output=True
    )
    (repo_path / "feature.txt").write_text("feature content")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Feature commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "test-feature"], check=True, capture_output=True
    )

    assert _is_merge_commit()

    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 0
    assert "amended merge" in result.output.lower()
    assert "removed" in result.output.lower()
    assert "test-feature" in result.output.lower()

    # Now test non-merge case: create new worktree on normal commit
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task Two** → `another-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add another task"], check=True, capture_output=True
    )

    assert not _is_merge_commit()

    worktree_path2 = _create_worktree(repo_path, "another-feature", init_repo)
    assert worktree_path2.exists()

    result2 = runner.invoke(worktree, ["rm", "--confirm", "another-feature"])
    assert result2.exit_code == 0
    assert "amend" not in result2.output.lower()
    assert "removed" in result2.output.lower()
    assert "another-feature" in result2.output.lower()


def test_rm_refuses_without_confirm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Refuses removal without --confirm flag."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 2
    assert "confirm" in result.output.lower() or "skill" in result.output.lower()
    assert worktree_path.exists()


def test_rm_force_bypasses_confirm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Force flag bypasses confirm check."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--force", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "removed" in result.output.lower()
