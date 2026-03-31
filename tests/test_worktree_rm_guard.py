"""Tests for _is_branch_merged guard function."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from edify.worktree.cli import _delete_branch, worktree
from edify.worktree.git_ops import _classify_branch, _is_branch_merged
from tests.fixtures_worktree import (
    BranchSpec,
    _run_git,
    add_worktree,
    make_repo_with_branch,
)


def _branch_exists(repo: Path, branch: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            check=False,
            cwd=repo,
            capture_output=True,
        ).returncode
        == 0
    )


def test_is_branch_merged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_is_branch_merged returns True for merged, False for unmerged."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo, init_repo, branch="merged-branch", spec=BranchSpec(merge=True)
    )
    monkeypatch.chdir(repo)

    assert _is_branch_merged("merged-branch") is True

    # Create unmerged branch
    _run_git(repo, "checkout", "-b", "unmerged-branch")
    (repo / "unmerged-file.txt").write_text("unmerged content")
    _run_git(repo, "add", "unmerged-file.txt")
    _run_git(repo, "commit", "-m", "Commit on unmerged branch")
    _run_git(repo, "checkout", "-")

    assert _is_branch_merged("unmerged-branch") is False


def test_classify_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_classify_branch returns (count, is_focused) for various branch types."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    monkeypatch.chdir(repo)

    # Case 1: Focused-session-only branch (1 commit with marker)
    _run_git(repo, "checkout", "-b", "focused-session")
    _run_git(
        repo, "commit", "--allow-empty", "-m", "Focused session for focused-session"
    )
    _run_git(repo, "checkout", "-")
    count, is_focused = _classify_branch("focused-session")
    assert count == 1
    assert is_focused is True

    # Case 2: Real-history branch (1 user commit)
    _run_git(repo, "checkout", "-b", "real-history")
    (repo / "user-file.txt").write_text("user content")
    _run_git(repo, "add", "user-file.txt")
    _run_git(repo, "commit", "-m", "User commit")
    _run_git(repo, "checkout", "-")
    count, is_focused = _classify_branch("real-history")
    assert count == 1
    assert is_focused is False

    # Case 3: Multi-commit branch (3 commits)
    _run_git(repo, "checkout", "-b", "multi-commit")
    for i in range(3):
        (repo / f"file-{i}.txt").write_text(f"content {i}")
        _run_git(repo, "add", f"file-{i}.txt")
        _run_git(repo, "commit", "-m", f"Commit {i}")
    _run_git(repo, "checkout", "-")
    count, is_focused = _classify_branch("multi-commit")
    assert count == 3
    assert is_focused is False

    # Case 4: Marker with wrong format (missing "for")
    _run_git(repo, "checkout", "-b", "wrong-format")
    _run_git(repo, "commit", "--allow-empty", "-m", "Focused session wrong-format")
    _run_git(repo, "checkout", "-")
    count, is_focused = _classify_branch("wrong-format")
    assert count == 1
    assert is_focused is False


def test_classify_orphan_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """_classify_branch returns (0, False) for orphan branches."""
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    monkeypatch.chdir(repo)

    _run_git(repo, "checkout", "--orphan", "orphan-test")
    (repo / "orphan-file.txt").write_text("orphan content")
    _run_git(repo, "add", "orphan-file.txt")
    _run_git(repo, "commit", "-m", "Orphan commit")
    _run_git(repo, "checkout", "main")

    count, is_focused = _classify_branch("orphan-test")
    assert count == 0
    assert is_focused is False


def test_rm_refuses_unmerged_real_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Rm refuses unmerged branches with real history and orphan branches."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo, init_repo, branch="real-unmerged", spec=BranchSpec(n_commits=2)
    )
    monkeypatch.chdir(repo)
    runner = CliRunner()

    # Scenario A: Real history with 2 unmerged commits
    wt_path = add_worktree(repo, "real-unmerged")
    result = runner.invoke(worktree, ["rm", "real-unmerged"])

    assert result.exit_code == 2
    assert "has 2 unmerged commit(s). Merge first." in result.output
    assert wt_path.exists(), "Worktree directory should still exist"
    assert _branch_exists(repo, "real-unmerged"), "Branch should still exist"

    # Scenario B: Orphan branch
    _run_git(repo, "checkout", "--orphan", "orphan-branch")
    (repo / "orphan-file.txt").write_text("orphan content")
    _run_git(repo, "add", "orphan-file.txt")
    _run_git(repo, "commit", "-m", "Orphan commit")
    _run_git(repo, "checkout", "main")
    add_worktree(repo, "orphan-branch")

    result = runner.invoke(worktree, ["rm", "orphan-branch"])
    assert result.exit_code == 2
    assert "is orphaned (no common ancestor). Merge first." in result.output


def test_rm_allows_merged_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Rm allows merged branch removal with safe delete."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo, init_repo, branch="merged-branch", spec=BranchSpec(merge=True)
    )
    monkeypatch.chdir(repo)

    add_worktree(repo, "merged-branch")
    result = CliRunner().invoke(worktree, ["rm", "merged-branch"])

    assert result.exit_code == 0
    assert not _branch_exists(repo, "merged-branch"), "Branch should be deleted"
    assert "Removed merged-branch" in result.output


def test_rm_allows_focused_session_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Rm allows focused-session-only branch removal with force delete."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo,
        init_repo,
        branch="test-branch",
        spec=BranchSpec(empty_msg="Focused session for test-branch"),
    )
    monkeypatch.chdir(repo)

    add_worktree(repo, "test-branch")
    result = CliRunner().invoke(worktree, ["rm", "test-branch"])

    assert result.exit_code == 0
    assert not _branch_exists(repo, "test-branch"), "Branch should be deleted"
    assert "Removed test-branch (focused session only)" in result.output


def test_rm_guard_prevents_destruction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Guard refusal (exit 2) prevents all destructive operations.

    Regression: session.md task removal, worktree deletion,
    _probe_registrations, branch deletion must not execute.
    """
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo, init_repo, branch="guard-test", spec=BranchSpec(n_commits=2)
    )
    monkeypatch.chdir(repo)

    wt_path = add_worktree(repo, "guard-test")

    session_md = repo / "agents" / "session.md"
    session_md.parent.mkdir(parents=True, exist_ok=True)
    session_md.write_text(
        "# Session\n\n## Worktree Tasks\n\n- [ ] **Test Task** → `guard-test`\n"
    )

    result = CliRunner().invoke(worktree, ["rm", "guard-test"])
    assert result.exit_code == 2

    assert wt_path.exists(), "Worktree directory should survive guard refusal"
    assert _branch_exists(repo, "guard-test"), "Branch should survive"
    assert "→ `guard-test`" in session_md.read_text(), "Task should survive"
    wt_list = _run_git(repo, "worktree", "list", "--porcelain").stdout
    assert str(wt_path) in wt_list, "Worktree should remain registered"


def test_rm_no_destructive_suggestions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Rm never suggests 'git branch -D' in output for any scenario.

    Regression test for FR-5: CLI should refuse destructive operations, not
    suggest them.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    monkeypatch.chdir(repo)
    runner = CliRunner()

    # Scenario 1: Merged branch removal (success)
    make_repo_with_branch(
        repo,
        init_repo,
        branch="merged-test",
        spec=BranchSpec(files={"merged.txt": "merged content"}, merge=True),
    )
    add_worktree(repo, "merged-test")
    result = runner.invoke(worktree, ["rm", "merged-test"])
    assert "git branch -D" not in result.output

    # Scenario 2: Focused-session-only removal (success)
    make_repo_with_branch(
        repo,
        init_repo,
        branch="focused-test",
        spec=BranchSpec(empty_msg="Focused session for focused-test"),
    )
    add_worktree(repo, "focused-test")
    result = runner.invoke(worktree, ["rm", "focused-test"])
    assert "git branch -D" not in result.output

    # Scenario 3: Guard refusal (error)
    make_repo_with_branch(
        repo,
        init_repo,
        branch="unmerged-test",
        spec=BranchSpec(files={"unmerged.txt": "unmerged content"}),
    )
    add_worktree(repo, "unmerged-test")
    result = runner.invoke(worktree, ["rm", "unmerged-test"])
    assert "git branch -D" not in result.output


def test_rm_guard_exits_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Rm exits 2 when guard refuses removal (safety gate)."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo, init_repo, branch="guard-test-br", spec=BranchSpec(n_commits=2)
    )
    monkeypatch.chdir(repo)

    add_worktree(repo, "guard-test-br")
    result = CliRunner().invoke(worktree, ["rm", "guard-test-br"])

    assert result.exit_code == 2
    assert "has 2 unmerged commit(s). Merge first." in result.output


def test_delete_branch_exits_1_on_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """_delete_branch raises SystemExit(1) when git branch -d fails."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo,
        init_repo,
        branch="unmerged-br",
        spec=BranchSpec(files={"f.txt": "content"}),
    )
    monkeypatch.chdir(repo)

    # git branch -d fails on unmerged branch (removal_type=None → uses -d)
    with pytest.raises(SystemExit) as exc_info:
        _delete_branch("unmerged-br", None)

    assert exc_info.value.code == 1
    assert "deletion failed" in capsys.readouterr().out


def test_rm_force_bypasses_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
) -> None:
    """Force flag bypasses guard check."""
    repo = tmp_path / "repo"
    make_repo_with_branch(
        repo, init_repo, branch="unmerged-force", spec=BranchSpec(n_commits=2)
    )
    monkeypatch.chdir(repo)

    wt_path = add_worktree(repo, "unmerged-force")
    result = CliRunner().invoke(worktree, ["rm", "--force", "unmerged-force"])

    assert result.exit_code == 0
    assert not wt_path.exists()
    assert not _branch_exists(repo, "unmerged-force")
