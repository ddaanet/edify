"""Tests for memory index format validation and fuzzy matching."""

from pathlib import Path

import pytest

from edify.validation.memory_index import (
    _extract_entry_key,
    extract_index_entries,
    validate,
)
from edify.validation.memory_index_helpers import EXEMPT_SECTIONS


@pytest.fixture
def decisions_dir(tmp_path: Path) -> Path:
    """Create agents/decisions directory structure."""
    d = tmp_path / "agents" / "decisions"
    d.mkdir(parents=True)
    return d


def _write_index(tmp_path: Path, content: str) -> Path:
    """Write memory-index.md and return path."""
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.parent.mkdir(parents=True, exist_ok=True)
    index_file.write_text(content)
    return index_file


def test_validator_parses_when_format(tmp_path: Path) -> None:
    """Validator parses /when and /how format entries correctly."""
    index_with_when_format = """# Memory Index

## Testing Decisions

/when writing mock tests | mock patch
/how structure fixtures | test fixtures
/when mocking subprocess | error injection

## Implementation Notes

/when choosing between approaches | design trade-offs
"""
    _write_index(tmp_path, index_with_when_format)

    entries = extract_index_entries("agents/memory-index.md", tmp_path)

    # Entry keyed by operator + trigger text (lowercase)
    assert "when writing mock tests" in entries
    assert entries["when writing mock tests"][2] == "Testing Decisions"

    # /how entries parsed with "how to" mapping
    assert "how to structure fixtures" in entries
    assert entries["how to structure fixtures"][2] == "Testing Decisions"

    # All /when and /how lines captured
    assert "when mocking subprocess" in entries
    assert "when choosing between approaches" in entries

    # Old em-dash format not parsed (should be empty for that line)
    entry_count = len(entries)
    assert entry_count == 4  # Exactly 4 /when or /how entries


def test_format_validation_rules(tmp_path: Path, decisions_dir: Path) -> None:
    """Format validation checks operator prefix, trigger, extras.

    Validates operator prefix, trigger non-empty, and extras format.
    """
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## Valid Trigger\nContent.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when valid trigger
/when valid | extra1, extra2
/what invalid operator
/when
/when trigger | ,,,
Old em-dash format — no operator prefix
Valid Trigger — Valid entry with em-dash
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)

    # Should flag invalid operator
    assert any("/what" in e and "invalid operator" in e for e in errors)

    # Should flag empty trigger
    assert any("/when" in e and "empty trigger" in e for e in errors)

    # Valid entries should NOT be flagged
    assert not any("valid trigger" in e and "error" in e for e in errors)
    assert not any("extra1, extra2" in e and "error" in e for e in errors)

    # Should flag old em-dash format (no operator prefix)
    assert any("no operator prefix" in e for e in errors)

    # Each error should include line number and message
    assert all(
        "memory-index.md:" in e
        for e in errors
        if "error" in e.lower() or "invalid" in e.lower() or "empty" in e.lower()
    )


def test_fuzzy_bidirectional_integrity(tmp_path: Path, decisions_dir: Path) -> None:
    """Fuzzy matching bridges compression in entry↔heading validation.

    Index entries are compressed (e.g., "write mock test") but must match
    headings that use full prose (e.g., "When Writing Mock Tests"). Fuzzy
    matching should bridge this gap.

    Assertions:
    - Index entry matches heading via fuzzy matching (compressed vs full text)
    - Index entry with no matching heading raises orphan entry error
    - Heading with no index entry raises orphan heading error
    - Fuzzy matching bridges compression between index trigger and heading text
    """
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n"
        "## When Writing Mock Tests\nContent.\n\n"
        "## When Auth Fails\nMore content.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when writing mock tests
/when writing mock tests with no heading match
""",
    )
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)

    # Should find orphan entry (no heading match)
    assert any("orphan index entry" in e for e in errors)

    # Should find orphan heading (no entry match)
    assert any("orphan semantic header" in e for e in errors)


def test_collision_detection(tmp_path: Path, decisions_dir: Path) -> None:
    """Multiple entries resolve to same heading → collision error.

    Assertions:
    - Two entries both fuzzy-matching same heading → collision error
    - Error identifies both colliding entries with line numbers
    - Error identifies the shared heading
    - Two entries matching different headings → no collision error
    """
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n"
        "## When Mock Testing\nContent.\n\n"
        "## Different Heading\nMore.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when mock test
/when mock testing
/when different heading
""",
    )
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)

    # Should find collision error
    assert any("collision" in e for e in errors)
    collision_error = next(e for e in errors if "collision" in e)

    # Should identify both colliding entries
    assert "mock test" in collision_error
    assert "mock testing" in collision_error

    # Should identify the shared heading
    assert "when mock testing" in collision_error.lower()

    # Should include line numbers for both entries
    assert "line 5" in collision_error
    assert "line 6" in collision_error


def test_word_count_removed(tmp_path: Path, decisions_dir: Path) -> None:
    """Word count validation removed per D-9 (short triggers are intentional).

    The /when format allows any word count for triggers. Validation previously
    rejected 2-word entries but now accepts them.

    Assertions:
    - /when a b (2 words) passes validation (previously would fail 8-word minimum)
    - /when very long trigger with many many many words in it (11 words) passes
      (no upper limit now)
    - No word count errors in validation output
    """
    (decisions_dir / "test-decision.md").write_text(
        "# Test Decision\n\n## When A B\nContent.\n\n"
        "## When Very Long Trigger With Many Many Many Words In It\nMore.\n"
    )
    _write_index(
        tmp_path,
        """# Memory Index

## agents/decisions/test-decision.md

/when a b
/when very long trigger with many many many words in it
""",
    )
    errors = validate("agents/memory-index.md", tmp_path)

    # Verify no word count errors
    assert not any("word" in e.lower() for e in errors), (
        f"Unexpected word count errors: {errors}"
    )
    # Both entries should pass validation
    assert errors == []


def test_exempt_sections_updated(tmp_path: Path, decisions_dir: Path) -> None:
    """After migration, EXEMPT_SECTIONS is empty and all sections validated.

    Assertions:
    - EXEMPT_SECTIONS is empty set (no exempt sections remain)
    - Validation runs on ALL sections (no skipping)
    - Old exempt section names are not in EXEMPT_SECTIONS
    - If index has old exempt sections, validated like any other section
    """
    # Verify EXEMPT_SECTIONS is empty
    assert set() == EXEMPT_SECTIONS, (
        f"EXEMPT_SECTIONS should be empty after migration, but found: {EXEMPT_SECTIONS}"
    )

    # Verify old exempt section names are not present
    old_exempt_names = {
        "Behavioral Rules (fragments — already loaded)",
        "Technical Decisions (mixed — check entry for specific file)",
    }
    assert EXEMPT_SECTIONS.isdisjoint(old_exempt_names), (
        f"Old exempt section names still in EXEMPT_SECTIONS: "
        f"{EXEMPT_SECTIONS & old_exempt_names}"
    )


def test_extract_entry_key_operator_inclusion() -> None:
    """Entry keys include operator prefix for disambiguation.

    Design D-6: `/when X` → "When X", `/how X` → "How to X"
    Entry keys must include operator to disambiguate same trigger with different
    operators.

    Assertions:
    - `/when trigger text` → key is "when trigger text"
    - `/how trigger text` → key is "how to trigger text" (maps /how → "how to")
    - Em-dash format backward compatible (no operator prefix)
    - Empty trigger returns None
    """
    # /when includes operator in key
    assert _extract_entry_key("/when trigger text") == "when trigger text"

    # /how maps to "how to" in key
    assert _extract_entry_key("/how trigger text") == "how to trigger text"

    # Em-dash format (no operator)
    assert _extract_entry_key("key — description") == "key"

    # Empty trigger
    assert _extract_entry_key("/when ") is None
    assert _extract_entry_key("/how ") is None
