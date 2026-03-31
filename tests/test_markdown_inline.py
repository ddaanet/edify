"""Tests for markdown module."""

from edify.markdown import (
    escape_inline_backticks,
    fix_backtick_spaces,
    process_lines,
)


def test_escape_inline_backticks_wraps_language_references() -> None:
    """Test: Escape ```language when it appears inline in text."""
    input_lines = [
        "Text about ```markdown blocks\n",
        "\n",
        "More text with ```python and ```javascript references\n",
    ]
    expected = [
        "Text about `` ```markdown `` blocks\n",
        "\n",
        "More text with `` ```python `` and `` ```javascript `` references\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_wraps_standalone_triple_backticks() -> None:
    """Test: Escape ``` without language when it appears inline."""
    input_lines = [
        "Text mentioning ``` fences\n",
        "\n",
        "Use ``` to create code blocks\n",
    ]
    expected = [
        "Text mentioning `` ``` `` fences\n",
        "\n",
        "Use `` ``` `` to create code blocks\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_preserves_real_fences() -> None:
    """Test: Don't escape ``` when it's a real fence at line start."""
    input_lines = [
        "```bash\n",
        "echo hello\n",
        "```\n",
    ]
    # Should not modify - these are real fences
    assert escape_inline_backticks(input_lines) == input_lines


def test_escape_inline_backticks_is_idempotent() -> None:
    """Test: Running escape multiple times produces the same result."""
    input_lines = [
        "Text about ```markdown blocks\n",
        "\n",
        "Use ``` to create code blocks\n",
        "More text with ```python and ```javascript references\n",
    ]

    # First run
    result1 = escape_inline_backticks(input_lines)

    # Second run should produce identical result
    result2 = escape_inline_backticks(result1)

    assert result1 == result2


def test_escape_inline_backticks_skips_content_inside_blocks() -> None:
    """Test: Don't escape ``` inside code blocks."""
    input_lines = [
        "Text with ```python reference\n",
        "\n",
        "```markdown\n",
        "Example showing ```bash usage\n",
        "```\n",
        "\n",
        "More ```javascript outside\n",
    ]
    expected = [
        "Text with `` ```python `` reference\n",
        "\n",
        "```markdown\n",
        "Example showing ```bash usage\n",
        "```\n",
        "\n",
        "More `` ```javascript `` outside\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_preserves_four_backticks() -> None:
    """Test: Four backticks in text are wrapped correctly."""
    input_lines = [
        "Output: ```` markdown block\n",
    ]
    expected = [
        "Output: `` ```` `` markdown block\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_preserves_five_backticks() -> None:
    """Test: Five backticks in text are wrapped correctly."""
    input_lines = [
        "Use ````` for special cases\n",
    ]
    expected = [
        "Use `` ````` `` for special cases\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_handles_mixed_backtick_counts() -> None:
    """Test: Text with both triple and quad backticks handled correctly."""
    input_lines = [
        "Use ``` for code and ```` for edge cases\n",
    ]
    expected = [
        "Use `` ``` `` for code and `` ```` `` for edge cases\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_four_backticks_idempotent() -> None:
    """Test: Escape backticks is idempotent with mixed 4-backtick and 3-backtick inline.

    Regression test for bug where having both ````markdown and ``` on the same
    line would cause non-idempotent behavior on second pass.
    """
    input_lines = [
        "Use a ````markdown block to include ``` blocks.\n",
    ]

    # First run - should wrap both sequences
    result1 = escape_inline_backticks(input_lines)
    expected_first = [
        "Use a `` ````markdown `` block to include `` ``` `` blocks.\n",
    ]
    assert result1 == expected_first, (
        f"First pass incorrect:\nGot: {result1}\nExpected: {expected_first}"
    )

    # Second run should produce identical result (must be idempotent)
    result2 = escape_inline_backticks(result1)
    assert result1 == result2, f"Not idempotent:\nPass 1: {result1}\nPass 2: {result2}"


def test_fix_backtick_spaces_quotes_trailing_space() -> None:
    """Test 13: Quote backticks with trailing space.

    When inline code has trailing whitespace, it's ambiguous in documentation.
    Quote the content to make the space explicit.
    """
    input_line = "`blah ` text\n"
    expected = '`"blah "` text\n'
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_quotes_leading_space() -> None:
    """Test 14: Quote backticks with leading space.

    When inline code has leading whitespace, quote it to make it explicit.
    """
    input_line = "` blah` text\n"
    expected = '`" blah"` text\n'
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_quotes_both_spaces() -> None:
    """Test 15: Quote backticks with both leading and trailing space.

    When inline code has both leading and trailing whitespace, quote both.
    """
    input_line = "` | ` text\n"
    expected = '`" | "` text\n'
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_skips_code_without_spaces() -> None:
    """Test 16: Skip backticks without leading/trailing spaces.

    Backticks without whitespace should remain unchanged.
    """
    input_line = "`code` text\n"
    expected = "`code` text\n"
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_via_segment_processing() -> None:
    """Test 17: Apply via segment-aware processing.

    When content is mixed (plain text + ```python block):
    - Plain text backticks with spaces should be quoted
    - Content inside ```python block should be unchanged
    """
    input_lines = [
        "This code ` has spaces ` in it.\n",
        "\n",
        "```python\n",
        "# This ` has spaces ` but should not be quoted\n",
        "text = '` also ` spaces'\n",
        "```\n",
    ]
    expected = [
        'This code `" has spaces "` in it.\n',
        "\n",
        "```python\n",
        "# This ` has spaces ` but should not be quoted\n",
        "text = '` also ` spaces'\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_escape_inline_backticks_preserves_single_backtick_spans() -> None:
    """Test: Single backtick spans not corrupted by escaping."""
    input_lines = ["Single `backtick` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Single `backtick` text\n"]


def test_escape_inline_backticks_preserves_double_backtick_spans() -> None:
    """Test: Double backtick spans not corrupted by escaping."""
    input_lines = ["Double ``backtick`` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Double ``backtick`` text\n"]


def test_escape_inline_backticks_preserves_double_containing_single() -> None:
    """Test: Double backtick spans containing single backtick preserved."""
    input_lines = ["Double ``Backtick ` char`` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Double ``Backtick ` char`` text\n"]


def test_escape_inline_backticks_preserves_multiple_spans() -> None:
    """Test: Multiple inline code spans on same line preserved."""
    input_lines = ["First `span1` and second `span2` here\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["First `span1` and second `span2` here\n"]


def test_escape_inline_backticks_preserves_mixed_delimiters() -> None:
    """Test: Mixed single and double backtick spans preserved."""
    input_lines = ["Single `a` and double ``b`` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Single `a` and double ``b`` text\n"]


def test_escape_inline_backticks_escapes_bare_triple_outside_spans() -> None:
    """Test: Bare triple backticks outside spans are escaped."""
    input_lines = ["Text with ```python outside\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Text with `` ```python `` outside\n"]


def test_escape_inline_backticks_mixed_bare_and_inline() -> None:
    """Test: Escapes bare fences but preserves inline code spans."""
    input_lines = ["Use `code` but escape ```python here\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Use `code` but escape `` ```python `` here\n"]


def test_escape_inline_backticks_preserves_quoted_doc_example() -> None:
    """Test: Documentation example with inline code preserved."""
    input_lines = ['Given: `"````markdown\\n"` (4 backticks with language)\n']
    result = escape_inline_backticks(input_lines)
    # Single-backtick span containing 4 backticks and text - preserved
    assert result == ['Given: `"````markdown\\n"` (4 backticks with language)\n']


def test_escape_inline_backticks_adjacent_spans() -> None:
    """Test: Adjacent inline code spans handled correctly."""
    input_lines = ["`first``second`text\n"]
    result = escape_inline_backticks(input_lines)
    # `first` is valid span, ``second` has mismatched delimiters (2 opening, 1 closing)
    # Should preserve the valid `first` span
    assert "`first`" in result[0]


def test_escape_inline_backticks_empty_span() -> None:
    """Test: Empty inline code spans preserved."""
    input_lines = ["Empty `` span\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Empty `` span\n"]


def test_escape_inline_backticks_span_at_boundaries() -> None:
    """Test: Spans at start/end of line preserved."""
    input_lines = ["`start` middle `end`\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["`start` middle `end`\n"]


def test_escape_inline_backticks_unclosed_not_corrupted() -> None:
    """Test: Unclosed backticks handled gracefully."""
    input_lines = ["Unclosed `backtick and ```python\n"]
    result = escape_inline_backticks(input_lines)
    # Unclosed ` is not a span, so ```python should be escaped
    assert "`` ```python ``" in result[0]


def test_escape_inline_backticks_preserves_one_four_one_with_spaces() -> None:
    """Test: Explicit single-backtick span with four backticks inside."""
    input_lines = ["Use ` ```` ` for blocks\n"]
    result = escape_inline_backticks(input_lines)
    # Single-backtick span with spaces - should be preserved
    assert result == ["Use ` ```` ` for blocks\n"]


def test_integration_python_fence_protection() -> None:
    """Integration: Content in ```python fences is protected."""
    input_lines = [
        "Here is ```python code:\n",
        "\n",
        "```python\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
        "```\n",
        "\n",
        "After the fence.\n",
    ]
    result = process_lines(input_lines)
    # Python fence content should NOT be converted to list items
    assert result[3] == "✅ Task 1\n"
    assert result[4] == "✅ Task 2\n"


def test_integration_yaml_fence_protection() -> None:
    """Integration: Content in ```yaml fences is protected."""
    input_lines = [
        "Configuration:\n",
        "\n",
        "```yaml\n",
        "✅ Check: true\n",
        "❌ Status: false\n",
        "```\n",
        "\n",
        "End of config.\n",
    ]
    result = process_lines(input_lines)
    # YAML fence content should NOT be converted to list items
    assert result[3] == "✅ Check: true\n"
    assert result[4] == "❌ Status: false\n"


def test_integration_markdown_fence_processing() -> None:
    """Integration: Content in ```markdown fences IS processed (intentional).

    Markdown blocks are processable=True to allow formatting doc examples.
    """
    input_lines = [
        "Example markdown:\n",
        "\n",
        "```markdown\n",
        "**File:** role.md\n",
        "**Model:** Sonnet\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    # Markdown fence content IS processed (intentional - for doc examples)
    assert result[3] == "- **File:** role.md\n"
    assert result[4] == "- **Model:** Sonnet\n"


def test_integration_bare_fence_protection() -> None:
    """Integration: Content in bare ``` fences is protected."""
    input_lines = [
        "Some code:\n",
        "\n",
        "```\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    # Bare fence content should NOT be converted to list items
    assert result[3] == "✅ Task 1\n"
    assert result[4] == "✅ Task 2\n"
