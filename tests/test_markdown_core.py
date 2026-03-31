"""Tests for markdown module."""

from pathlib import Path

from edify.markdown import process_file, process_lines


def test_import_process_lines() -> None:
    """Test: Import process_lines function."""
    assert callable(process_lines)


def test_process_lines_fixes_dunder_references() -> None:
    """Test: process_lines fixes dunder references."""
    input_lines = ["## About __init__.py\n"]
    expected = ["## About `__init__.py`\n"]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_metadata_blocks() -> None:
    """Test: process_lines fixes metadata blocks."""
    input_lines = [
        "**File:** `role.md`\n",
        "**Model:** Sonnet\n",
        "\n",
    ]
    expected = [
        "- **File:** `role.md`\n",
        "- **Model:** Sonnet\n",
        "\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_warning_lines() -> None:
    """Test: process_lines fixes warning lines."""
    input_lines = [
        "⚠️ Warning one\n",
        "⚠️ Warning two\n",
    ]
    expected = [
        "- ⚠️ Warning one\n",
        "- ⚠️ Warning two\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_nested_lists() -> None:
    """Test: process_lines fixes nested lists."""
    input_lines = [
        "2. Parent:\n",
        "   a. Child 1\n",
        "   b. Child 2\n",
    ]
    expected = [
        "2. Parent:\n",
        "   1. Child 1\n",
        "   2. Child 2\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_numbered_list_spacing() -> None:
    """Test: 2+ consecutive metadata labels trigger list conversion and indentation.

    When 2+ consecutive **Label:** lines appear (with space after colon),
    they form a metadata list and following numbered list is indented.
    """
    input_lines = [
        "**Label:** content\n",
        "**Execution phase:**\n",
        "4. Batch reads\n",
    ]
    expected = [
        "- **Label:** content\n",
        "- **Execution phase:**\n",
        "  4. Batch reads\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_file_returns_true_when_modified(tmp_path: Path) -> None:
    """Test: process_file returns True when modified."""
    content = "## About __init__.py\n"
    filepath = tmp_path / "test.md"
    filepath.write_text(content)

    result = process_file(filepath)
    assert result is True
    assert filepath.read_text() == "## About `__init__.py`\n"


def test_process_file_returns_false_when_unchanged(tmp_path: Path) -> None:
    """Test: process_file returns False when unchanged."""
    content = "## About `__init__.py`\n"
    filepath = tmp_path / "test.md"
    filepath.write_text(content)

    result = process_file(filepath)
    assert result is False
    assert filepath.read_text() == content


def test_process_lines_is_idempotent() -> None:
    """Test: Running process_lines multiple times produces the same result."""
    input_lines = [
        "## About __init__.py\n",
        "\n",
        "Text mentioning ```python and ```bash code.\n",
        "\n",
        "**File:** test.py\n",
        "**Model:** Sonnet\n",
        "\n",
        "```bash\n",
        "echo hello\n",
        "```\n",
    ]

    # First run
    result1 = process_lines(input_lines)

    # Second run
    result2 = process_lines(result1)

    # Should be identical (idempotent)
    assert result1 == result2
