"""Tests for _recall diff subcommand."""

import subprocess
import time
from pathlib import Path

from click.testing import CliRunner

from claudeutils.cli import cli


def test_diff_lists_changed_files(tmp_path: Path) -> None:
    """Diff lists files changed since artifact mtime, excludes artifact itself.

    Creates a git repo with artifact and verifies output contains changed files
    but excludes the artifact.
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Create artifact file
    artifact_dir = tmp_path / "plans" / "test-job"
    artifact_dir.mkdir(parents=True)
    artifact_path = artifact_dir / "recall-artifact.md"
    artifact_content = """# Recall Artifact: Test Job

## Entry Keys

when test entry — annotation
"""
    artifact_path.write_text(artifact_content)

    # Commit artifact
    subprocess.run(
        ["git", "add", str(artifact_path)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add artifact"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Ensure time passes so next file has later mtime than artifact
    time.sleep(0.1)

    # Create another file in the job directory after artifact
    outline_path = artifact_dir / "outline.md"
    outline_path.write_text("# Outline\n\nSome content")

    # Commit the new file
    subprocess.run(
        ["git", "add", str(outline_path)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add outline"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Invoke diff subcommand
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_recall", "diff", "test-job"],
        env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
    )

    assert result.exit_code == 0
    # Output should contain the changed file path
    assert "plans/test-job/outline.md" in result.output
    # Output should NOT contain the artifact itself
    assert "plans/test-job/recall-artifact.md" not in result.output


def test_diff_not_git_repo(tmp_path: Path) -> None:
    """Diff exits 1 when not inside a git repository.

    Tests that the git check fails gracefully with error message to stdout.
    """
    # Create artifact but do NOT initialize git
    artifact_dir = tmp_path / "plans" / "test-job"
    artifact_dir.mkdir(parents=True)
    artifact_path = artifact_dir / "recall-artifact.md"
    artifact_path.write_text(
        "# Recall Artifact\n\n## Entry Keys\n\nwhen test — annotation\n"
    )

    # Invoke diff subcommand
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_recall", "diff", "test-job"],
        env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
    )

    assert result.exit_code == 1
    assert "not inside a git repository" in result.output


def test_diff_artifact_missing(tmp_path: Path) -> None:
    """Diff exits 1 when artifact file is missing.

    Tests that missing artifact check fails with error message to stdout.
    """
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Do NOT create artifact file

    # Invoke diff subcommand
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["_recall", "diff", "test-job"],
        env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
    )

    assert result.exit_code == 1
    assert "recall-artifact.md missing for test-job" in result.output
