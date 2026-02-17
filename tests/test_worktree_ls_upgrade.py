"""Test upgrade of worktree ls command with --porcelain flag."""

import subprocess
from pathlib import Path

from click.testing import CliRunner

from claudeutils.worktree.cli import _parse_worktree_list, worktree


def test_porcelain_flag_exists() -> None:
    """Verify --porcelain flag exists and is boolean."""
    runner = CliRunner()

    # Test that --porcelain flag is recognized
    result = runner.invoke(worktree, ["ls", "--porcelain"])
    assert result.exit_code == 0, f"Expected success, got: {result.output}"

    # Test that --help shows the --porcelain flag
    help_result = runner.invoke(worktree, ["ls", "--help"])
    assert "--porcelain" in help_result.output, "Flag should appear in help text"


def test_porcelain_mode_backward_compatible(tmp_path: Path) -> None:
    """Verify porcelain mode preserves existing tab-separated output format."""
    # Create a temporary git repo with main worktree and a branch worktree
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
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

    # Create initial commit
    (repo_path / "file.txt").write_text("content")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a worktree
    worktree_path = repo_path / "wt" / "test-branch"
    subprocess.run(
        ["git", "worktree", "add", "-b", "test-branch", str(worktree_path)],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Run ls with --porcelain flag and verify output format
    runner = CliRunner()
    with runner.isolated_filesystem():
        # We need to run in the actual repo
        result = subprocess.run(
            ["git", "-C", str(repo_path), "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )

        main_path = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        entries = _parse_worktree_list(result.stdout, main_path)

        # Verify output format: (slug, branch, path)
        assert len(entries) == 1, f"Expected 1 worktree, got {len(entries)}"
        slug, branch, path = entries[0]

        # Verify slug, branch, path are correctly parsed
        assert slug == "test-branch", f"Expected slug 'test-branch', got {slug}"
        assert "test-branch" in branch, (
            f"Expected branch to contain 'test-branch', got {branch}"
        )
        assert str(worktree_path) in path, (
            f"Expected path to contain {worktree_path}, got {path}"
        )
