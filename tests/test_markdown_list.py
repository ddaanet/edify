"""Tests for markdown module."""

from edify.markdown import (
    fix_metadata_blocks,
    fix_metadata_list_indentation,
    fix_warning_lines,
    process_lines,
)


def test_fix_warning_lines_handles_checkmark_emoji() -> None:
    """Test: fix_warning_lines converts consecutive ✅ lines to list."""
    input_lines = [
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
    ]
    expected = [
        "- ✅ Issue #1: XPASS tests visible\n",
        "- ✅ Issue #2: Setup failures captured\n",
    ]
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_handles_cross_emoji() -> None:
    """Test: fix_warning_lines converts consecutive ❌ lines to list."""
    input_lines = [
        "❌ Failed test 1\n",
        "❌ Failed test 2\n",
    ]
    expected = [
        "- ❌ Failed test 1\n",
        "- ❌ Failed test 2\n",
    ]
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_handles_mixed_emoji_prefix() -> None:
    """Test: fix_warning_lines converts mixed ✅/❌ lines to list."""
    input_lines = [
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
        "❌ Issue #3: Not fixed yet\n",
    ]
    expected = [
        "- ✅ Issue #1: XPASS tests visible\n",
        "- ✅ Issue #2: Setup failures captured\n",
        "- ❌ Issue #3: Not fixed yet\n",
    ]
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_skips_existing_lists() -> None:
    """Test: fix_warning_lines skips lines already formatted as lists."""
    input_lines = [
        "- ✅ Issue #1: Already a list\n",
        "- ✅ Issue #2: Already a list\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_skips_single_line() -> None:
    """Test: fix_warning_lines skips single line with emoji prefix."""
    input_lines = [
        "✅ Only one line\n",
        "\n",
        "Some other content\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_handles_bracket_and_colon_prefix() -> None:
    """Test: fix_warning_lines handles [TODO] and NOTE: patterns."""
    input_lines = [
        "[TODO] Implement feature X\n",
        "[TODO] Write tests\n",
        "\n",
        "NOTE: This is important\n",
        "NOTE: Remember this\n",
    ]
    expected = [
        "- [TODO] Implement feature X\n",
        "- [TODO] Write tests\n",
        "\n",
        "- NOTE: This is important\n",
        "- NOTE: Remember this\n",
    ]
    assert fix_warning_lines(input_lines) == expected


def test_fix_metadata_list_indentation_basic_case() -> None:
    """Test: Convert metadata label to list item and indent following list."""
    input_lines = [
        "**Plan Files:**\n",
        "- `plans/phase-1.md`\n",
        "- `plans/phase-2.md`\n",
        "\n",
    ]
    expected = [
        "- **Plan Files:**\n",
        "  - `plans/phase-1.md`\n",
        "  - `plans/phase-2.md`\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected


def test_fix_metadata_list_indentation_colon_outside() -> None:
    """Test: Handle **Label**: pattern (colon outside bold)."""
    input_lines = [
        "**Implementation Date**:\n",
        "- 2026-01-04\n",
        "\n",
    ]
    expected = [
        "- **Implementation Date**:\n",
        "  - 2026-01-04\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected


def test_fix_metadata_list_indentation_skips_label_with_content() -> None:
    """Test: Skip metadata label with content on same line."""
    input_lines = [
        "**File:** `role.md`\n",
        "- item1\n",
        "- item2\n",
    ]
    expected = input_lines.copy()
    assert fix_metadata_list_indentation(input_lines) == expected


def test_fix_metadata_list_indentation_handles_numbered_lists() -> None:
    """Test: Indent numbered lists following metadata label."""
    input_lines = [
        "**Steps:**\n",
        "1. First step\n",
        "2. Second step\n",
        "\n",
    ]
    expected = [
        "- **Steps:**\n",
        "  1. First step\n",
        "  2. Second step\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected


def test_fix_metadata_list_indentation_adds_to_existing_indent() -> None:
    """Test: Add 2 spaces to list items that already have indentation."""
    input_lines = [
        "  **Nested Label:**\n",
        "  - item1\n",
        "    - nested item\n",
        "\n",
    ]
    expected = [
        "  - **Nested Label:**\n",
        "    - item1\n",
        "      - nested item\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected


def test_fix_metadata_list_indentation_stops_at_non_list() -> None:
    """Test: Stop indenting at non-list content."""
    input_lines = [
        "**Items:**\n",
        "- item1\n",
        "- item2\n",
        "Regular paragraph\n",
    ]
    expected = [
        "- **Items:**\n",
        "  - item1\n",
        "  - item2\n",
        "Regular paragraph\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected


def test_metadata_list_indentation_works_with_metadata_blocks() -> None:
    """Test labels converted, following list indented, single label not."""
    input_lines = [
        "**File:** `role.md`\n",
        "**Model:** Sonnet\n",
        "\n",
        "**Plan Files:**\n",
        "- `plans/phase-1.md`\n",
        "- `plans/phase-2.md`\n",
    ]
    expected = [
        "- **File:** `role.md`\n",
        "- **Model:** Sonnet\n",
        "\n",
        "**Plan Files:**\n",
        "- `plans/phase-1.md`\n",
        "- `plans/phase-2.md`\n",
    ]
    lines = fix_metadata_blocks(input_lines)
    assert lines == expected


def test_fix_warning_lines_skips_table_rows() -> None:
    """Test: Tables should not be converted to lists by fix_warning_lines."""
    input_lines = [
        "| Header 1 | Header 2 |\n",
        "| -------- | -------- |\n",
        "| Value 1  | Value 2  |\n",
        "\n",
    ]
    result = fix_warning_lines(input_lines)
    assert result == input_lines


def test_integration_yaml_prolog_protection() -> None:
    """Integration: YAML prologs are protected and not processed."""
    input_lines = [
        "---\n",
        "author_model: claude-sonnet\n",
        "semantic_type: guide\n",
        "---\n",
        "\n",
        "Content starts here.\n",
    ]
    result = process_lines(input_lines)
    # YAML prolog should remain unchanged
    assert result[0] == "---\n"
    assert result[1] == "author_model: claude-sonnet\n"
    assert result[2] == "semantic_type: guide\n"
    assert result[3] == "---\n"


def test_integration_plain_text_still_processes() -> None:
    """Integration: Plain text (not in fences) is still processed correctly."""
    input_lines = [
        "Some content\n",
        "\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
    ]
    result = process_lines(input_lines)
    # Plain text emoji lines SHOULD be converted to list items
    assert result[2] == "- ✅ Task 1\n"
    assert result[3] == "- ✅ Task 2\n"


def test_nested_python_block_in_markdown_no_blank_line() -> None:
    """Test: Nested ```python block inside ```markdown doesn't get blank line.

    When ```python block appears inside ```markdown block, fix_markdown_code_blocks
    should NOT insert a blank line after the ```python fence (Bug #2 regression test).
    Requires recursive parsing to work correctly.
    """
    input_lines = [
        "````markdown\n",
        "# Example\n",
        "\n",
        "```python\n",
        "code_here\n",
        "```\n",
        "\n",
        "````\n",
    ]

    # Process the lines
    result = process_lines(input_lines)

    # Find the ```python fence in the output
    python_fence_idx = None
    for i, line in enumerate(result):
        if line.strip() == "```python":
            python_fence_idx = i
            break

    assert python_fence_idx is not None, "```python fence not found"

    # Verify next line is NOT blank (Bug #2 would insert a blank line here)
    assert python_fence_idx + 1 < len(result), "No line after python fence"
    next_line = result[python_fence_idx + 1]
    assert next_line.strip() != "", (
        f"Unexpected blank line after ```python fence: {next_line!r}"
    )
    assert next_line == "code_here\n", f"Expected code line, got: {next_line!r}"


def test_integration_nested_fences_in_markdown_block() -> None:
    """Integration test: Bare ``` fence inside ````markdown block.

    Tests Bug #1 fix: Bare ``` fences inside ````markdown blocks should be
    protected from processing. Emoji lines inside the bare fence should NOT
    be converted to list items.
    """
    input_lines = [
        "````markdown\n",
        "## Markdown Cleanup Examples\n",
        "\n",
        "### Checklist Detection\n",
        "\n",
        "**Input:**\n",
        "\n",
        "```\n",
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
        "❌ Issue #3: Not fixed yet\n",
        "```\n",
        "\n",
        "````\n",
    ]

    result = process_lines(input_lines)

    # Find the bare fence content
    bare_fence_start = None
    bare_fence_end = None
    for i, line in enumerate(result):
        stripped = line.strip()
        if stripped == "```":
            if bare_fence_start is None:
                bare_fence_start = i
            else:
                bare_fence_end = i
                break

    assert bare_fence_start is not None, "Opening bare fence not found"
    assert bare_fence_end is not None, "Closing bare fence not found"

    # Verify emoji lines inside bare fence were NOT converted to list items
    content_inside_fence = result[bare_fence_start + 1 : bare_fence_end]
    assert len(content_inside_fence) == 3, (
        f"Expected 3 lines, got {len(content_inside_fence)}"
    )

    # These lines should be unchanged (not prefixed with "- ")
    assert content_inside_fence[0] == "✅ Issue #1: XPASS tests visible\n"
    assert content_inside_fence[1] == "✅ Issue #2: Setup failures captured\n"
    assert content_inside_fence[2] == "❌ Issue #3: Not fixed yet\n"
