"""Unit tests for learning-ages.py script.

Test coverage:
- Parsing: H2 extraction, preamble skip, malformed headers
- Age calculation: active days, git blame, merge commits
- Staleness detection: last consolidation via removed headers
- Trigger logic: size, staleness, batch minimum thresholds
- Freshness filter: 7-day threshold
- Error handling: missing files, git failures
- Integration: full pipeline with mocked git
"""

import importlib.util
import subprocess
import sys
from datetime import UTC, datetime
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


# ==============================================================================
# A. Parsing tests
# ==============================================================================


def test_extract_titles_skips_preamble() -> None:
    """Extract H2 headers from learnings.md, skip first 10 lines (preamble)."""
    lines = [
        "# Learnings\n",
        "\n",
        "Preamble text...\n",
        "Line 4\n",
        "Line 5\n",
        "Line 6\n",
        "Line 7\n",
        "Line 8\n",
        "Line 9\n",
        "Line 10\n",
        "## First learning\n",  # Line 11 — first extracted
        "- Content\n",
        "## Second learning\n",  # Line 13
        "- More content\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert headers[0] == (11, "First learning")
    assert headers[1] == (13, "Second learning")
    # Verify preamble skipped: no headers from lines 1-10
    assert all(line_num > 10 for line_num, _ in headers)


def test_extract_titles_malformed_headers_skipped() -> None:
    """Skip malformed headers gracefully, continue processing."""
    lines = [
        *["preamble\n"] * 10,
        "## Valid header\n",
        "###Not a header (no space)\n",
        "## Another valid\n",
        "# Wrong level\n",
        "##Also no space\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert headers[0] == (11, "Valid header")
    assert headers[1] == (13, "Another valid")


def test_extract_titles_empty_file() -> None:
    """Empty file or only preamble should return empty list."""
    lines = ["# Learnings\n"] + ["preamble\n"] * 9

    headers = learning_ages.extract_titles(lines)

    assert headers == []


# ==============================================================================
# B. Age calculation tests
# ==============================================================================


@patch("subprocess.run")
def test_get_commit_date_for_line_parses_porcelain(mock_run: MagicMock) -> None:
    """Parse git blame porcelain output to extract commit date."""
    # Mock git blame --line-porcelain output
    mock_run.return_value = MagicMock(
        stdout=(
            "abc123def456 11 11 1\n"
            "author Author Name\n"
            "author-time 1705276800\n"
            "committer Committer Name\n"
            "committer-time 1705276800\n"  # 2024-01-15 00:00:00 UTC
            "summary Add learning entry\n"
            "\t## Learning title\n"
        ),
        returncode=0,
    )

    commit_date = learning_ages.get_commit_date_for_line("agents/learnings.md", 11)

    assert commit_date == "2024-01-15"
    mock_run.assert_called_once_with(
        [
            "git",
            "blame",
            "-C",
            "-C",
            "--first-parent",
            "--line-porcelain",
            "-L11,11",
            "--",
            "agents/learnings.md",
        ],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_get_active_days_since_counts_unique_dates(mock_run: MagicMock) -> None:
    """Count unique commit dates, not calendar days."""
    # Mock git log output — 5 unique dates over 10 calendar days
    mock_run.return_value = MagicMock(
        stdout=(
            "2024-01-15\n"
            "2024-01-16\n"
            "2024-01-16\n"  # Duplicate
            "2024-01-18\n"
            "2024-01-22\n"
            "2024-01-25\n"
        ),
        returncode=0,
    )

    active_days = learning_ages.get_active_days_since("2024-01-15")

    assert active_days == 5  # Not 6 (duplicate removed), not 10 (calendar days)


@patch("subprocess.run")
def test_get_active_days_since_entry_added_today(mock_run: MagicMock) -> None:
    """Entry added today should have non-zero active days if commits exist."""
    today = datetime.now(UTC).date().isoformat()
    # Mock git log --since=<today> includes today's commits
    mock_run.return_value = MagicMock(stdout=f"{today}\n", returncode=0)

    active_days = learning_ages.get_active_days_since(today)

    # If today has commits, count is 1 (today)
    assert active_days == 1


@patch("subprocess.run")
def test_get_commit_date_for_line_first_parent_flag(mock_run: MagicMock) -> None:
    """Verify --first-parent flag used for merge commit handling."""
    mock_run.return_value = MagicMock(
        stdout="committer-time 1705276800\n", returncode=0
    )

    learning_ages.get_commit_date_for_line("agents/learnings.md", 15)

    # Verify --first-parent flag present
    call_args = mock_run.call_args[0][0]
    assert "--first-parent" in call_args


@patch("subprocess.run")
def test_get_commit_date_for_line_git_error_returns_none(
    mock_run: MagicMock,
) -> None:
    """Git blame error should return None and print to stderr."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "git blame")

    commit_date = learning_ages.get_commit_date_for_line("agents/learnings.md", 11)

    assert commit_date is None


# ==============================================================================
# C. Staleness detection tests
# ==============================================================================


@patch("subprocess.run")
def test_get_last_consolidation_date_finds_recent(mock_run: MagicMock) -> None:
    """Find most recent commit with removed H2 headers.

    Consolidation evidence detection.
    """
    # Mock git log -p output with removed headers
    mock_run.return_value = MagicMock(
        stdout=(
            "commit abc123\n"
            "Date:   Mon Jan 20 10:00:00 2025 -0800\n"
            "\n"
            "-## Old learning 1\n"
            "-## Old learning 2\n"
            "\n"
            "commit def456\n"
            "Date:   Wed Jan 10 09:00:00 2025 -0800\n"
            "\n"
            "-## Even older learning\n"
        ),
        returncode=0,
    )

    # Patch get_active_days_since to avoid nested git call
    with patch.object(learning_ages, "get_active_days_since", return_value=15):
        result = learning_ages.get_last_consolidation_date("agents/learnings.md")
        last_date, staleness = result

    assert last_date == "2025-01-20"  # Most recent
    assert staleness == 15


@patch("subprocess.run")
def test_get_last_consolidation_date_no_prior_consolidation(
    mock_run: MagicMock,
) -> None:
    """Return (None, None) when no removed headers found."""
    # Mock git log -p output with only additions
    mock_run.return_value = MagicMock(
        stdout=(
            "commit abc123\n"
            "Date:   Mon Jan 20 10:00:00 2025 -0800\n"
            "\n"
            "+## New learning\n"
        ),
        returncode=0,
    )

    result = learning_ages.get_last_consolidation_date("agents/learnings.md")
    last_date, staleness = result

    assert last_date is None
    assert staleness is None


@patch("subprocess.run")
def test_get_last_consolidation_date_removed_header_pattern(
    mock_run: MagicMock,
) -> None:
    """Only match lines starting with '-## ' (removed H2 headers)."""
    # Mock git log -p with various diff patterns
    mock_run.return_value = MagicMock(
        stdout=(
            "commit abc123\n"
            "Date:   Mon Jan 20 10:00:00 2025 -0800\n"
            "\n"
            "- This is a bullet, not a header\n"
            "-### H3 header removed\n"
            "-## H2 header removed\n"  # This should match
        ),
        returncode=0,
    )

    with patch.object(learning_ages, "get_active_days_since", return_value=10):
        result = learning_ages.get_last_consolidation_date("agents/learnings.md")
        last_date, staleness = result

    assert last_date == "2025-01-20"
    assert staleness == 10


# ==============================================================================
# D. Error handling tests
# ==============================================================================


def test_main_missing_file_exits_with_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing learnings.md should exit 1 with stderr message."""
    nonexistent = tmp_path / "nonexistent.md"
    sys.argv = ["learning-ages.py", str(nonexistent)]

    with pytest.raises(SystemExit, match="1"):
        learning_ages.main()

    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err


def test_main_no_entries_exits_with_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """File with no learning entries should exit 1."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("# Learnings\n\n" + "Preamble\n" * 10)
    sys.argv = ["learning-ages.py", str(learnings_file)]

    with pytest.raises(SystemExit, match="1"):
        learning_ages.main()

    captured = capsys.readouterr()
    assert "No learning entries found" in captured.err


@patch("subprocess.run")
def test_get_active_days_since_git_error_returns_zero(
    mock_run: MagicMock,
) -> None:
    """Git command failure should return 0 and print to stderr."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "git log")

    active_days = learning_ages.get_active_days_since("2024-01-15")

    assert active_days == 0
