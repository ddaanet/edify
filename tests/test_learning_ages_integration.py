"""Integration tests for learning-ages.py script.

Full end-to-end pipeline testing with mocked git repository.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import module with hyphens in name
script_path = Path(__file__).parent.parent / "plugin" / "bin" / "learning-ages.py"
spec = importlib.util.spec_from_file_location("learning_ages", script_path)
assert spec is not None, "Failed to create module spec"
assert spec.loader is not None, "Module spec has no loader"
learning_ages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learning_ages)


@patch("subprocess.run")
def test_main_full_pipeline(
    mock_run: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Full pipeline with mocked git repo produces correct markdown output."""
    # Create temp learnings.md
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text(
        "# Learnings\n"
        "\n"
        "Preamble line 3\n"
        "Preamble line 4\n"
        "Preamble line 5\n"
        "Preamble line 6\n"
        "Preamble line 7\n"
        "Preamble line 8\n"
        "Preamble line 9\n"
        "Preamble line 10\n"
        "## Old learning\n"  # Line 11
        "- Content\n"
        "## Recent learning\n"  # Line 13
        "- More content\n"
    )

    # Mock git calls
    def mock_git_command(cmd: list[str], **kwargs: object) -> MagicMock:
        if "blame" in cmd:
            # Return porcelain format for line blame
            # Find -L argument which is in format "-L11,11"
            line_arg = next(arg for arg in cmd if arg.startswith("-L"))
            # Extract from -L<num>,<num>
            line_num = int(line_arg[2:].split(",")[0])
            timestamp = (
                1704067200 if line_num == 11 else 1706659200
            )  # 2024-01-01 : 2024-01-31
            return MagicMock(stdout=f"committer-time {timestamp}\n", returncode=0)
        if "log" in cmd and "-p" in cmd:
            # Mock git log -p for consolidation detection
            return MagicMock(
                stdout=(
                    "commit xyz789\n"
                    "Date:   Mon Jan 15 10:00:00 2024 -0800\n"
                    "\n"
                    "-## Consolidated learning\n"
                ),
                returncode=0,
            )
        if "log" in cmd:
            # Mock git log for active days calculation
            since_date = cmd[4].split("=")[1]  # Extract from --since=<date>
            if since_date == "2024-01-01":
                # 15 unique commit dates
                dates = [f"2024-01-{d:02d}" for d in range(1, 16)]
                return MagicMock(stdout="\n".join(dates) + "\n", returncode=0)
            if since_date == "2024-01-31":
                # 5 unique commit dates
                dates = [f"2024-01-{d:02d}" for d in range(31, 36)]
                return MagicMock(stdout="\n".join(dates) + "\n", returncode=0)
            if since_date == "2024-01-15":
                # 10 unique commit dates (for consolidation staleness)
                dates = [f"2024-01-{d:02d}" for d in range(15, 25)]
                return MagicMock(stdout="\n".join(dates) + "\n", returncode=0)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_git_command

    # Run main
    sys.argv = ["learning-ages.py", str(learnings_file)]
    learning_ages.main()

    # Verify output
    captured = capsys.readouterr()
    output = captured.out

    # Check report structure
    assert "# Learning Ages Report" in output
    assert "**File lines:** 14" in output
    assert "**Last consolidation:** 10 active days ago" in output
    assert "**Total entries:** 2" in output
    # Only "Old learning" with 15 days is ≥7
    assert "**Entries ≥7 active days:** 1" in output
    assert "## Entries by Age" in output

    # Check entries sorted by age (descending)
    lines = output.splitlines()
    entry_lines = [line for line in lines if line.startswith("- **")]
    assert len(entry_lines) == 2
    # Older entry should be first (more active days)
    assert "Old learning" in entry_lines[0]
    assert "Recent learning" in entry_lines[1]
    assert "15 days" in entry_lines[0]
    assert "5 days" in entry_lines[1]


@patch("subprocess.run")
def test_main_no_consolidation_message(
    mock_run: MagicMock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Display 'N/A' message when no prior consolidation detected."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("# Learnings\n" + "\n" * 9 + "## First learning\n")

    def mock_git_command(cmd: list[str], **kwargs: object) -> MagicMock:
        if "blame" in cmd:
            return MagicMock(stdout="committer-time 1704067200\n", returncode=0)
        if "log" in cmd and "-p" in cmd:
            # No removed headers
            return MagicMock(
                stdout=("commit abc\nDate: Mon Jan 1 10:00:00 2024 -0800\n+## New\n"),
                returncode=0,
            )
        if "log" in cmd:
            return MagicMock(stdout="2024-01-01\n", returncode=0)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_git_command

    sys.argv = ["learning-ages.py", str(learnings_file)]
    learning_ages.main()

    captured = capsys.readouterr()
    assert (
        "**Last consolidation:** N/A (no prior consolidation detected)" in captured.out
    )
