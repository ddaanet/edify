"""Tests for _recall check subcommand."""

from pathlib import Path

from click.testing import CliRunner

from claudeutils.cli import cli


def test_check_valid_artifact() -> None:
    """Check exits 0 when artifact has valid Entry Keys section with entries."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create artifact with valid Entry Keys section
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

when test entry one — some annotation
when test entry two
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        result = runner.invoke(cli, ["_recall", "check", "test-job"])
        assert result.exit_code == 0


def test_check_missing_artifact() -> None:
    """Check exits 1 when artifact file is missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["_recall", "check", "test-job"])
        assert result.exit_code == 1
        assert "recall-artifact.md missing for test-job" in result.output


def test_check_no_entry_keys_section() -> None:
    """Check exits 1 when artifact has no Entry Keys section."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        artifact_content = """# Recall Artifact: Test Job

Some other content without Entry Keys section.
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        result = runner.invoke(cli, ["_recall", "check", "test-job"])
        assert result.exit_code == 1
        assert (
            "recall-artifact.md has no Entry Keys section for test-job" in result.output
        )


def test_check_empty_section() -> None:
    """Check exits 1 when Entry Keys section has no entries."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        result = runner.invoke(cli, ["_recall", "check", "test-job"])
        assert result.exit_code == 1
        assert "recall-artifact.md has no entries for test-job" in result.output


def test_check_null_entry_valid() -> None:
    """Check exits 0 when artifact has null entry.

    Null entry (no relevant entries found) counts as a valid entry.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        artifact_content = """# Recall Artifact: Test Job

## Entry Keys

null — no relevant entries found
"""
        artifact_dir = Path("plans/test-job")
        artifact_dir.mkdir(parents=True)
        artifact_path = artifact_dir / "recall-artifact.md"
        artifact_path.write_text(artifact_content)

        result = runner.invoke(cli, ["_recall", "check", "test-job"])
        assert result.exit_code == 0
