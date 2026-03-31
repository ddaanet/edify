"""Tests for segment parsing functionality."""

from edify.markdown import parse_segments, process_lines


def test_parse_segments_empty_input() -> None:
    """Test: parse_segments returns empty list for empty input."""
    assert parse_segments([]) == []


def test_parse_segments_plain_text_no_fences() -> None:
    """Test: parse_segments returns single processable segment for plain text."""
    lines = ["Line 1\n", "Line 2\n"]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True
    assert result[0].lines == lines


def test_parse_segments_python_block() -> None:
    """Test: parse_segments detects ```python block as protected."""
    lines = [
        "```python\n",
        "x = 1\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is False
    assert result[0].language == "python"


def test_parse_segments_markdown_block() -> None:
    """Test: parse_segments recursively parses ```markdown block content."""
    lines = [
        "```markdown\n",
        "# Title\n",
        "```\n",
    ]
    result = parse_segments(lines)
    # With recursive parsing: [opening fence, inner content, closing fence]
    assert len(result) == 3
    assert result[0].processable is True
    assert result[0].language == "markdown"
    assert result[0].lines == ["```markdown\n"]
    assert result[1].processable is True
    assert result[1].lines == ["# Title\n"]
    assert result[2].processable is True
    assert result[2].language == "markdown"
    assert result[2].lines == ["```\n"]


def test_parse_segments_bare_fence_block() -> None:
    """Test: parse_segments detects bare ``` block as protected."""
    lines = [
        "```\n",
        "raw text\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is False
    assert result[0].language is None


def test_parse_segments_text_before_and_after_fence() -> None:
    """Test: parse_segments returns 3 segments for text-fence-text."""
    lines = [
        "Text before\n",
        "```python\n",
        "code\n",
        "```\n",
        "Text after\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 3
    assert result[0].processable is True
    assert result[0].lines == ["Text before\n"]
    assert result[1].processable is False
    assert result[1].language == "python"
    assert result[2].processable is True
    assert result[2].lines == ["Text after\n"]


def test_parse_segments_consecutive_fenced_blocks() -> None:
    """Test: parse_segments handles consecutive fenced blocks."""
    lines = [
        "```bash\n",
        "echo hello\n",
        "```\n",
        "```python\n",
        "x = 1\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 2
    assert result[0].processable is False
    assert result[0].language == "bash"
    assert result[1].processable is False
    assert result[1].language == "python"


def test_parse_segments_nested_markdown_inside_python() -> None:
    """Test: Nested ```markdown inside ```python is NOT processable."""
    lines = [
        "```python\n",
        "# docstring with example:\n",
        "```markdown\n",
        "# Title\n",
        "```\n",
        "```\n",  # closes python block
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is False
    assert result[0].language == "python"


def test_parse_segments_yaml_prolog() -> None:
    """Test: YAML prolog section is detected as protected."""
    lines = [
        "---\n",
        "title: Test Document\n",
        "author: Claude\n",
        "---\n",
        "\n",
        "Content here\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 2
    assert result[0].processable is False
    assert result[0].language == "yaml-prolog"
    assert result[0].lines == lines[:4]
    assert result[1].processable is True
    assert result[1].lines == ["\n", "Content here\n"]


def test_parse_segments_yaml_prolog_not_ruler() -> None:
    """Test: --- with blank lines INSIDE is NOT a prolog (it's a ruler)."""
    lines = [
        "Content above\n",
        "\n",
        "---\n",
        "\n",
        "Content below\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True
    assert result[0].lines == lines


def test_parse_segments_yaml_prolog_must_have_key_value() -> None:
    """Test: --- section without key: value is NOT a prolog."""
    lines = [
        "---\n",
        "just some text\n",
        "no colons here\n",
        "---\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True


def test_parse_segments_yaml_prolog_mid_document() -> None:
    """Test: YAML prolog can appear mid-document after markdown content."""
    lines = [
        "# Previous content\n",
        "\n",
        "Some text here\n",
        "---\n",
        "stage: production\n",
        "version: 2.0\n",
        "---\n",
        "Content after\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 3
    assert result[0].processable is True
    assert result[0].lines == lines[:3]
    assert result[1].processable is False
    assert result[1].language == "yaml-prolog"
    assert result[1].lines == lines[3:7]
    assert result[2].processable is True
    assert result[2].lines == ["Content after\n"]


def test_bare_fence_protection_integration() -> None:
    """Test: process_lines protects emoji-prefixed content inside bare fences.

    This integration test verifies Phase 7: Bare Fence Protection.
    Content with emoji prefixes inside bare ``` fences should NOT be
    converted to list items.
    """
    lines = [
        "## Checklist Detection\n",
        "\n",
        "**Input:**\n",
        "\n",
        "```\n",
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
        "❌ Issue #3: Not fixed yet\n",
        "```\n",
        "\n",
        "**Output:**\n",
        "\n",
        "Plain text here\n",
    ]
    result = process_lines(lines)

    # Find the bare fence content in the result
    fence_start = None
    fence_end = None
    for i, line in enumerate(result):
        if line.strip() == "```":
            if fence_start is None:
                fence_start = i
            else:
                fence_end = i
                break

    # Verify fence markers are found
    assert fence_start is not None, "Opening fence not found"
    assert fence_end is not None, "Closing fence not found"

    # Verify content inside bare fence was NOT converted to list items
    content_inside_fence = result[fence_start + 1 : fence_end]
    assert len(content_inside_fence) == 3, (
        f"Expected 3 lines inside fence, got {len(content_inside_fence)}"
    )
    assert content_inside_fence[0] == "✅ Issue #1: XPASS tests visible\n"
    assert content_inside_fence[1] == "✅ Issue #2: Setup failures captured\n"
    assert content_inside_fence[2] == "❌ Issue #3: Not fixed yet\n"


def test_parse_segments_nested_bare_fence_in_markdown() -> None:
    """Test: parse_segments with nested bare fence inside ```markdown block.

    When a bare ``` fence appears inside a ```markdown block, recursive parsing
    should detect it and create nested segments where the inner bare fence is
    marked as processable=False (protected).
    """
    lines = [
        "````markdown\n",
        "\n",
        "```\n",
        "✅ Issue\n",
        "```\n",
        "\n",
        "````\n",
    ]
    result = parse_segments(lines)

    # With recursive parsing, we should have multiple segments:
    # 1. Opening fence line (``````markdown)
    # 2. Plain text before inner fence (\n)
    # 3. Inner bare fence (protected)
    # 4. Plain text after inner fence (\n)
    # 5. Closing fence line (```````)

    # Minimum: Should have more than 1 segment if recursively parsed
    assert len(result) > 1, (
        f"Expected multiple segments from recursive parsing, got {len(result)}"
    )

    # Find the inner bare fence segment
    bare_fence_segment = None
    for seg in result:
        if seg.language is None and "✅ Issue\n" in seg.lines:
            bare_fence_segment = seg
            break

    assert bare_fence_segment is not None, "Inner bare fence segment not found"
    assert bare_fence_segment.processable is False, (
        "Inner bare fence should be protected"
    )
