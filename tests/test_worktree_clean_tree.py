"""Tests for worktree clean-tree and add-commit commands."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_clean_tree_session_files_exempt(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean-tree exits 0 when only session context files are modified.

    Integration test verifying that agents/session.md, agents/jobs.md, and
    agents/learnings.md are exempted from dirty tree checks.
    """
    monkeypatch.chdir(repo_with_submodule)

    # Modify session files
    agents_dir = repo_with_submodule / "agents"
    (agents_dir / "session.md").write_text("# Session\nModified\n")
    (agents_dir / "jobs.md").write_text("# Jobs\nModified\n")
    (agents_dir / "learnings.md").write_text("# Learnings\nModified\n")

    # Run clean-tree command
    runner = CliRunner()
    result = runner.invoke(worktree, ["clean-tree"])

    # Should exit 0 silently (session files exempted)
    assert result.exit_code == 0
    assert result.output == ""


def test_clean_tree_clean(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean-tree exits 0 with no output in clean repo with submodule.

    Integration test creating real git repos with submodule to verify command
    behavior.
    """
    monkeypatch.chdir(repo_with_submodule)

    # Run clean-tree command
    runner = CliRunner()
    result = runner.invoke(worktree, ["clean-tree"])

    assert result.exit_code == 0
    assert result.output == ""


def test_clean_tree_dirty_source(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean-tree exits 1 and prints dirty source files.

    When source files are modified, clean-tree should print the dirty files in
    porcelain format and exit 1. Session context files are exempt.
    """
    monkeypatch.chdir(repo_with_submodule)

    # Add source file
    src_dir = repo_with_submodule / "src" / "claudeutils"
    src_dir.mkdir(parents=True)
    (src_dir / "cli.py").write_text('"""Main CLI module."""\n')
    subprocess.run(["git", "add", "src/"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add source"], check=True, capture_output=True
    )

    # Modify source file and session file
    (src_dir / "cli.py").write_text('"""Main CLI module."""\nprint("hello")\n')
    (repo_with_submodule / "agents" / "session.md").write_text("# Session\nModified\n")

    # Run clean-tree command
    runner = CliRunner()
    result = runner.invoke(worktree, ["clean-tree"])

    # Should exit 1 with dirty file list
    assert result.exit_code == 1
    assert " M src/claudeutils/cli.py" in result.output


def test_add_commit_nothing_staged(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Add-commit with no staged changes exits 0 with no output.

    In a clean repo with unchanged file, add-commit should exit 0 silently when
    nothing is staged. This idempotent behavior is critical for merge flow.
    """
    monkeypatch.chdir(repo_with_submodule)

    # Run add-commit with message from stdin (nothing staged - file unchanged)
    runner = CliRunner()
    result = runner.invoke(
        worktree,
        ["add-commit", "agents/session.md"],
        input="Test commit message\n",
    )

    # Should exit 0 with empty output (idempotent no-op when file unchanged)
    assert result.exit_code == 0
    assert result.output == ""


def test_merge_ours_clean_tree(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Merge command enforces clean tree with session file exemption.

    Verifies that the merge command:
    - Exits 1 when main repo has uncommitted changes (except session files)
    - Exits 1 when submodule has uncommitted changes
    - Allows session.md, jobs.md, learnings.md to be dirty
    - Both parent and submodule are checked
    """
    monkeypatch.chdir(repo_with_submodule)
    runner = CliRunner()

    # Test 1: Main repo dirty (source files) → should fail
    src_dir = repo_with_submodule / "src" / "claudeutils"
    src_dir.mkdir(parents=True)
    (src_dir / "cli.py").write_text('"""Module."""\n')
    subprocess.run(["git", "add", "src/"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add source"], check=True, capture_output=True
    )
    (src_dir / "cli.py").write_text('"""Module."""\nprint("changed")\n')

    result = runner.invoke(worktree, ["merge", "test-slug"])
    assert result.exit_code == 1
    assert "Clean tree required for merge (main)" in result.output

    # Restore clean state for next test
    subprocess.run(["git", "restore", "src/"], check=True, capture_output=True)

    # Test 2: Session files dirty → should pass (exempted)
    (repo_with_submodule / "agents" / "session.md").write_text("# Modified session\n")
    result = runner.invoke(worktree, ["merge", "test-slug"])
    assert result.exit_code != 1 or "Clean tree required" not in result.output

    # Test 3: Jobs file dirty → should pass (exempted)
    (repo_with_submodule / "agents" / "jobs.md").write_text("# Modified jobs\n")
    result = runner.invoke(worktree, ["merge", "test-slug"])
    assert result.exit_code != 1 or "Clean tree required" not in result.output

    # Test 4: Learnings dirty → should pass (exempted)
    (repo_with_submodule / "agents" / "learnings.md").write_text(
        "# Modified learnings\n"
    )
    result = runner.invoke(worktree, ["merge", "test-slug"])
    assert result.exit_code != 1 or "Clean tree required" not in result.output

    # Restore session files for submodule test
    subprocess.run(["git", "restore", "agents/"], check=True, capture_output=True)

    # Test 5: Submodule dirty → should fail
    (repo_with_submodule / "agent-core" / "README.md").write_text(
        "modified submodule\n"
    )
    result = runner.invoke(worktree, ["merge", "test-slug"])
    assert result.exit_code == 1
    assert "Clean tree required for merge (main submodule)" in result.output
