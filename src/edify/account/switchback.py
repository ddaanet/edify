"""Switchback plist generation using LaunchAgent."""

import plistlib
from datetime import UTC, datetime, timedelta
from pathlib import Path


def create_switchback_plist(plist_path: Path, switchback_time: int) -> None:
    """Create a macOS LaunchAgent plist for switchback scheduling.

    Args:
        plist_path: Path where plist file will be written
        switchback_time: Switchback time in seconds from now
    """
    # Calculate target time
    target_time = datetime.now(UTC) + timedelta(seconds=switchback_time)

    # Create plist structure
    plist_data = {
        "Label": "com.anthropic.claude.switchback",
        "ProgramArguments": ["/usr/local/bin/edify", "account", "switchback"],
        "StartCalendarInterval": {
            "Month": target_time.month,
            "Day": target_time.day,
            "Hour": target_time.hour,
            "Minute": target_time.minute,
            "Second": target_time.second,
        },
    }

    # Write plist file
    with plist_path.open("wb") as f:
        plistlib.dump(plist_data, f)


def read_switchback_plist() -> datetime | None:
    """Read switchback time from macOS LaunchAgent plist.

    Reads the plist file at ~/Library/LaunchAgents/
    com.anthropic.claude.switchback.plist, extracts the StartCalendarInterval
    fields (Month, Day, Hour, Minute), and constructs a datetime object. Handles
    past dates by adding the appropriate year.

    Returns:
        datetime with correct month/day/hour/minute, or None if plist doesn't exist
    """
    plist_path = (
        Path.home()
        / "Library"
        / "LaunchAgents"
        / "com.anthropic.claude.switchback.plist"
    )

    # Check if plist file exists
    if not plist_path.exists():
        return None

    # Read and parse plist
    with plist_path.open("rb") as f:
        plist_data = plistlib.load(f)

    # Extract StartCalendarInterval
    calendar_interval = plist_data.get("StartCalendarInterval", {})

    # Get current year (may need to adjust if date is in the past)
    now = datetime.now(UTC)
    target_year = now.year

    # Extract month, day, hour, minute
    month = calendar_interval.get("Month")
    day = calendar_interval.get("Day")
    hour = calendar_interval.get("Hour", 0)
    minute = calendar_interval.get("Minute", 0)

    # Create datetime
    result = datetime(target_year, month, day, hour, minute, tzinfo=UTC)

    # If the date is in the past, add a year
    if result < now:
        result = datetime(target_year + 1, month, day, hour, minute, tzinfo=UTC)

    return result
