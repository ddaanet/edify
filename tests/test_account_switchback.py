"""Tests for switchback plist generation."""

import plistlib
from pathlib import Path
from unittest.mock import MagicMock, patch

from edify.account import create_switchback_plist
from edify.account.switchback import read_switchback_plist


def test_create_switchback_plist(tmp_path: Path) -> None:
    """Test that create_switchback_plist() generates a valid plist file."""
    # Create switchback plist at temp location
    plist_path = tmp_path / "test.plist"
    switchback_time = 3600  # 1 hour from now

    create_switchback_plist(plist_path, switchback_time)

    # Verify plist file was created
    assert plist_path.exists()

    # Verify plist can be loaded and has correct structure
    with plist_path.open("rb") as f:
        plist_data = plistlib.load(f)

    # Verify required plist keys
    assert "Label" in plist_data
    assert "ProgramArguments" in plist_data
    assert "StartCalendarInterval" in plist_data

    # Verify calendar interval is a dict with expected time fields
    calendar_interval = plist_data["StartCalendarInterval"]
    assert isinstance(calendar_interval, dict)
    assert "Hour" in calendar_interval
    assert "Minute" in calendar_interval
    assert "Second" in calendar_interval


def test_create_switchback_plist_includes_month_day(tmp_path: Path) -> None:
    """Test that create_switchback_plist() includes Month and Day fields.

    Verifies StartCalendarInterval dict contains Month and Day keys.
    """
    # Create switchback plist at temp location
    plist_path = tmp_path / "test.plist"
    switchback_time = 3600  # 1 hour from now

    create_switchback_plist(plist_path, switchback_time)

    # Verify plist file was created
    assert plist_path.exists()

    # Load and verify plist structure
    with plist_path.open("rb") as f:
        plist_data = plistlib.load(f)

    # Verify Month and Day fields are present in StartCalendarInterval
    calendar_interval = plist_data["StartCalendarInterval"]
    assert "Month" in calendar_interval, "Month not in StartCalendarInterval"
    assert "Day" in calendar_interval, "Day not in StartCalendarInterval"


def test_read_switchback_plist() -> None:
    """Test that read_switchback_plist() parses plist and returns datetime."""
    # Mock plist data
    mock_plist_data = {
        "Label": "com.anthropic.claude.switchback",
        "StartCalendarInterval": {
            "Month": 3,
            "Day": 15,
            "Hour": 14,
            "Minute": 30,
            "Second": 0,
        },
    }

    # Mock Path.home() and instance methods
    mock_path = MagicMock()
    mock_path.exists.return_value = True

    # Mock the open context manager
    mock_file_obj = MagicMock()
    mock_file_obj.__enter__.return_value = mock_file_obj
    mock_file_obj.__exit__.return_value = False

    with (
        patch("edify.account.switchback.Path.home", return_value=mock_path),
        patch(
            "edify.account.switchback.plistlib.load", return_value=mock_plist_data
        ),
        patch("builtins.open", return_value=mock_file_obj),
    ):
        result = read_switchback_plist()

    # Verify result is a datetime with correct month/day/hour/minute
    assert result is not None
    assert result.month == 3
    assert result.day == 15
    assert result.hour == 14
    assert result.minute == 30


def test_read_switchback_plist_missing(tmp_path: Path) -> None:
    """Test read_switchback_plist() returns None when plist doesn't exist."""
    # Create a mock home directory that doesn't contain the plist
    mock_home = tmp_path / "home"
    mock_home.mkdir()

    with patch("edify.account.switchback.Path.home", return_value=mock_home):
        result = read_switchback_plist()

    # Verify result is None when plist file doesn't exist
    assert result is None
