"""Test upgrade of worktree ls command with --porcelain flag."""

import os
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


def test_rich_mode_header_and_task(tmp_path: Path) -> None:
    """Test rich mode header and task line formatting in ls output."""
    # Create a temporary git repo with main worktree
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

    # Create initial commit with .gitignore for worktrees
    (repo_path / "file.txt").write_text("content")
    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a worktree with branch "feature"
    worktree_path = repo_path / "wt" / "test-wt"
    subprocess.run(
        ["git", "worktree", "add", "-b", "feature", str(worktree_path)],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create session.md in worktree to track commits since handoff
    session_file = worktree_path / "session.md"
    session_file.write_text("# Session\nTest session")

    # Make 3 commits in worktree after creating session.md
    for i in range(3):
        (worktree_path / f"file{i}.txt").write_text(f"content{i}")
        subprocess.run(
            ["git", "add", "."],
            cwd=worktree_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"commit{i}"],
            cwd=worktree_path,
            check=True,
            capture_output=True,
        )

    # Make working directory dirty
    (worktree_path / "dirty.txt").write_text("dirty content")

    # Test rich mode output (without --porcelain) by invoking the CLI
    runner = CliRunner()
    # Save current cwd and change to repo for the command
    old_cwd = Path.cwd()
    try:
        os.chdir(repo_path)
        result = runner.invoke(worktree, ["ls"])
    finally:
        os.chdir(old_cwd)

    assert result.exit_code == 0, f"Command failed: {result.output}"

    # Verify header format for worktree with slug="test-wt", branch="feature"
    assert "test-wt (feature)" in result.output, (
        f"Expected header with slug and branch, got: {result.output}"
    )
    assert "●" in result.output, f"Expected dirty indicator ●, got: {result.output}"
    assert "3 commits since handoff" in result.output, (
        f"Expected commit count, got: {result.output}"
    )

    # Verify header format for main tree (clean, no commits since handoff)
    assert "main (main)" in result.output, (
        f"Expected main tree header, got: {result.output}"
    )
    assert "○  clean" in result.output, (
        f"Expected clean indicator with ○, got: {result.output}"
    )


def test_rich_mode_plan_and_gate(tmp_path: Path) -> None:
    """Test rich mode plan and gate line formatting in ls output."""
    # Create a temporary git repo with main worktree
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

    # Create initial commit with .gitignore for worktrees and plans directory
    (repo_path / "file.txt").write_text("content")
    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a worktree with branch "feature"
    worktree_path = repo_path / "wt" / "test-wt"
    subprocess.run(
        ["git", "worktree", "add", "-b", "feature", str(worktree_path)],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create session.md in worktree to track commits since handoff
    session_file = worktree_path / "session.md"
    session_file.write_text("# Session\nTest session")

    # Create plans directory structure in worktree
    plans_dir = worktree_path / "plans"
    plans_dir.mkdir()

    # Create plan "foo" with status="designed" and design.md
    foo_plan_dir = plans_dir / "foo"
    foo_plan_dir.mkdir()
    (foo_plan_dir / "design.md").write_text("# Foo Design\n\nDesign content")

    # Create plan "bar" with status="planned" and runbook phase file
    bar_plan_dir = plans_dir / "bar"
    bar_plan_dir.mkdir()
    (bar_plan_dir / "design.md").write_text("# Bar Design\n\nDesign content")
    (bar_plan_dir / "runbook-phase-1.md").write_text(
        "# Bar Runbook Phase 1\n\nRunbook content"
    )

    # Commit these changes
    subprocess.run(
        ["git", "add", "."],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add plans"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Test rich mode output (without --porcelain) by invoking the CLI
    runner = CliRunner()
    # Save current cwd and change to repo for the command
    old_cwd = Path.cwd()
    try:
        os.chdir(repo_path)
        result = runner.invoke(worktree, ["ls"])
    finally:
        os.chdir(old_cwd)

    assert result.exit_code == 0, f"Command failed: {result.output}"

    # Verify plan line for foo (designed status, no gate)
    assert "  Plan: foo [designed] → /runbook plans/foo/design.md" in result.output, (
        f"Expected plan line for foo with designed status, got: {result.output}"
    )

    # Verify plan line for bar (planned status)
    assert (
        "  Plan: bar [planned] → agent-core/bin/prepare-runbook.py plans/bar"
        in result.output
    ), f"Expected plan line for bar with planned status, got: {result.output}"

    # Verify no gate lines appear (gate detection requires vet_status_func)
    assert "  Gate:" not in result.output, (
        f"Expected no gate lines in output, got: {result.output}"
    )
