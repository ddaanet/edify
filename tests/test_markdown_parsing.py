"""Tests for markdown module."""

from edify.markdown import (
    fix_warning_lines,
    process_lines,
)


def test_segment_aware_processing_applies_fix_to_plain_text() -> None:
    """Test 9: Fix applies to plain text, skips protected blocks.

    When content is mixed (plain text + ```python block):
    - Plain text with metadata should be converted to lists
    - Content inside ```python block should be unchanged
    """
    input_lines = [
        "**File:** test.py\n",
        "**Model:** Sonnet\n",
        "\n",
        "```python\n",
        "config = {\n",
        '    "name": "test",\n',
        '    "version": "1.0"\n',
        "}\n",
        "```\n",
    ]
    expected = [
        "- **File:** test.py\n",
        "- **Model:** Sonnet\n",
        "\n",
        "```python\n",
        "config = {\n",
        '    "name": "test",\n',
        '    "version": "1.0"\n',
        "}\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_segment_aware_processing_skips_yaml_prolog() -> None:
    """Test 10: YAML prolog block content is completely unchanged.

    YAML prologs contain structured data that should not be processed.
    All fixes must skip content inside ---...--- prolog sections.
    """
    input_lines = [
        "---\n",
        "title: Document\n",
        "tasks: [ build, test ]\n",
        "---\n",
        "\n",
        "**File:** result.md\n",
        "**Model:** Sonnet\n",
    ]
    expected = [
        "---\n",
        "title: Document\n",
        "tasks: [ build, test ]\n",
        "---\n",
        "\n",
        "- **File:** result.md\n",
        "- **Model:** Sonnet\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_segment_aware_processing_skips_bare_fence_blocks() -> None:
    """Test 11: Bare ``` block content is completely unchanged.

    Bare code blocks (no language) should not have fixes applied.
    This prevents false positives from colon/bracket-prefixed content.
    """
    input_lines = [
        "```\n",
        "NOTE: Important\n",
        "TODO: Action item\n",
        "```\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_segment_aware_processing_skips_nested_markdown_in_python() -> None:
    """Test 12: Content in non-markdown blocks is fully protected.

    When content appears inside ```python block,
    all processing-sensitive patterns are protected.
    This prevents false positives from pipes, colons, and other patterns.
    """
    input_lines = [
        "```python\n",
        "config = {\n",
        "    # Table format example:\n",
        "    # | Column | Value |\n",
        "    # | ------ | ----- |\n",
        "    # | Build  | Done  |\n",
        "    # | Test   | Pass  |\n",
        "    'name': 'test'\n",
        "}\n",
        "```\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_inner_fence_in_python_block_passed_through() -> None:
    """Test 18: Inner fence in non-markdown block is upgraded to 4 backticks.

    Verify that `process_lines` fixes inner fences in non-markdown blocks
    by upgrading to 4 backticks (typical Claude output discussing code blocks).
    """
    input_lines = [
        "```python\n",
        "def foo():\n",
        '    """\n',
        "    Example:\n",
        "    ```\n",
        "    code\n",
        "    ```\n",
        '    """\n',
        "```\n",
    ]
    expected = [
        "````python\n",
        "def foo():\n",
        '    """\n',
        "    Example:\n",
        "    ```\n",
        "    code\n",
        "    ```\n",
        '    """\n',
        "````\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_inner_fence_detection_in_markdown_block() -> None:
    """Test 19: Inner fence detection in ```markdown block.

    Verify that markdown blocks with inner fences still nest correctly
    (converts outer fence from ``` to ````).
    """
    input_lines = [
        "```markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        "```\n",
        "```\n",
    ]
    expected = [
        "````markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        "```\n",
        "````\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_single_bold_label_not_converted_to_list() -> None:
    """Test: Single **Label:** line should NOT be converted to list item.

    User requirement: Single label line ≠ metadata list.
    Only 2+ consecutive labels are converted.
    """
    input_lines = [
        "**Commits:**\n",
        "- item 1\n",
        "\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_yaml_prolog_recognizes_keys_without_spaces() -> None:
    r"""Test: YAML prolog keys without trailing spaces are recognized.

    Phase 4: Fix YAML Prolog Detection
    Bug: Pattern r"^\w+:\s" requires space after colon
    Fix: Pattern r"^[a-zA-Z_][\w-]*:" allows keys without values

    Verify that nested YAML keys like "tier_structure:" and "critical:"
    (with no trailing space) are recognized as valid YAML prolog content.
    """
    input_lines = [
        "---\n",
        "tier_structure:\n",
        "  critical:\n",
        "    - item\n",
        "---\n",
        "Content here\n",
    ]
    # YAML prolog should not be processed by fix_warning_lines
    # So the keys should NOT be converted to list items
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_yaml_prolog_recognizes_keys_with_hyphens() -> None:
    """Test: YAML prolog keys with hyphens are recognized.

    Pattern should support keys like "author-model:", "semantic-type:"
    """
    input_lines = [
        "---\n",
        "author-model: claude-3-5-sonnet\n",
        "semantic-type: configuration\n",
        "---\n",
        "Content\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_regular_prose() -> None:
    r"""Test: Regular prose should NOT be converted to list items.

    Phase 5: Rewrite extract_prefix()
    Bug: Pattern r"^(\S+(?:\s|:))" matches regular text like "Task agent"
    Fix: Only match emojis, brackets, and uppercase word+colon

    Lines starting with regular words should NOT be converted to lists,
    even if they appear in pairs.
    """
    input_lines = [
        "Task agent prompt is a replacement.\n",
        "Task agent are interactive-only.\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_block_quotes() -> None:
    """Test: Block quotes should NOT be converted to lists.

    Lines starting with > should be protected.
    """
    input_lines = [
        "> Your subagent's system prompt goes here.\n",
        "> This can be multiple paragraphs.\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_tree_diagrams() -> None:
    """Test: Tree diagram symbols should NOT be converted to lists.

    Lines with tree branch symbols (├, └, │) should be protected.
    """
    input_lines = [
        "  ├─ fix_dunder_references\n",
        "  ├─ fix_metadata_blocks\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_preserves_uppercase_colon_prefixes() -> None:
    """Test: Uppercase word + colon prefixes (NOTE:, WARNING:) are still detected.

    These legitimate prefixes should still convert to lists when 2+.
    """
    input_lines = [
        "NOTE: This is important\n",
        "NOTE: Another note\n",
    ]
    expected = [
        "- NOTE: This is important\n",
        "- NOTE: Another note\n",
    ]
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_lowercase_colon_prefixes() -> None:
    """Test: Lowercase word + colon should NOT be converted.

    Only UPPERCASE word + colon are valid prefixes (NOTE:, WARNING:, etc.)
    Lowercase like "Implementation:" should not be treated as prefix.
    """
    input_lines = [
        "Implementation: Start here\n",
        "Implementation: Then that\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected
