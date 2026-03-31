"""Tests for hyphenated trigger case-insensitive matching."""

from pathlib import Path

from edify.when.resolver import resolve


def test_hyphenated_trigger_matches_title_case_heading(tmp_path: Path) -> None:
    """Hyphenated trigger should match title-cased heading.

    Bug: .capitalize() treats "agent-creator" as one word, producing
    "Agent-creator" but the actual heading has "Agent-Creator" (both parts
    capitalized). Line 245 uses case-sensitive endswith() which fails to match.
    """
    # Setup: Index entry with hyphenated trigger
    index_file = tmp_path / "memory-index.md"
    index_file.write_text(
        "## agents/decisions/project-config.md\n\n"
        "/when agent-creator reviews agents | plugin-dev write read fix\n"
    )

    # Setup: Decision file with properly title-cased heading
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    config_file = decisions_dir / "project-config.md"
    config_file.write_text(
        "### When Agent-Creator Reviews Agents\n\n"
        "Agent-creator runs in review mode when invoked with review flag.\n"
    )

    # Act: Resolve the trigger
    result = resolve(
        "agent-creator reviews agents", str(index_file), str(decisions_dir)
    )

    # Assert: Should find and extract the section
    assert "When Agent-Creator Reviews Agents" in result
    assert "review mode" in result
